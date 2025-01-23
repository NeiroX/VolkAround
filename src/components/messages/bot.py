import re
from typing import List, Union
from urllib.parse import urlparse

import telegram
from telegram import Update, InlineKeyboardButton
from telegram.error import TelegramError
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, filters, \
    MessageHandler
from string import punctuation
from src.data.postgres_data_loader import PostgresLoadManager
from src.data.s3bucket import save_file_to_s3, s3_delete_file

from src.components.excursion.point.information_part import InformationPart
from src.components.messages.admin_message_sender import AdminMessageSender
from src.components.messages.message_sender import MessageSender
from src.components.excursion.excursion import Excursion
from src.components.excursion.point.point import Point
from src.components.user.user_state import UserState
import logging
from src.constants import *


def get_user_id_by_update(update: Update) -> int:
    return update.callback_query.from_user.id if update.callback_query else update.message.from_user.id


class Bot:
    """The main bot class coordinating everything."""

    def __init__(self, token, session):
        logging.info("Initializing bot...")
        self.application = Application.builder().token(token).build()
        self.session = session
        self.bot = telegram.Bot(token=token)
        self.data_loader = PostgresLoadManager(session)
        self.user_states = self.data_loader.load_user_states()  # Keeps track of UserState objects for each user
        self.excursions = self.data_loader.load_excursions()  # Dictionary of all available excursions

    def get_user_state(self, update: Update) -> UserState:
        """Gets or creates the user state for the given user."""
        user_id = update.callback_query.from_user.id if update.callback_query else update.message.from_user.id
        username = update.callback_query.from_user.username if update.callback_query else update.message.from_user.username
        chat_id = update.effective_chat.id
        print(chat_id)
        logging.info(f"Getting user state for user {username} with id {user_id}")
        if user_id not in self.user_states:
            logging.info(f"User state for username: {username}, user ID {user_id} not found. Creating new user state.")
            is_admin = True if (username is not None and username.lower() in ADMINS_LIST) else False
            self.user_states[user_id] = UserState(username=username, user_id=user_id, chat_id=chat_id,
                                                  is_admin=is_admin)
            self.data_loader.save_user_state(self.user_states[user_id])
        if not self.user_states[user_id].chat_id:
            self.user_states[user_id].chat_id = chat_id
        return self.user_states[user_id]

    def sync_data(self) -> None:
        logging.info("Syncing data")
        self.user_states = self.data_loader.load_user_states()  # Keeps track of UserState objects for each user
        self.excursions = self.data_loader.load_excursions()

    async def _start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles the /start command."""
        user_state = self.get_user_state(update)
        user_state.reset_current_excursion()  # Reset any ongoing current_excursion for a fresh start
        logging.info(f"Starting bot by user {user_state.get_username()}")

        # Explain the available versions
        await MessageSender.send_intro_message(update)

    async def _show_excursions(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Displays the list of available excursions based on user access."""
        query = update.callback_query
        if query.data == SHOW_EXCURSIONS_SYNC_CALLBACK:
            self.sync_data()
        user_state = self.get_user_state(update)
        user_state.reset_current_excursion()
        user_state.user_editor.disable_editing_mode()
        user_state.user_editor.disable_order_changing()
        await MessageSender.delete_previous_buttons(query)
        logging.info(
            f"Sending excursions list for user {user_state.username}\n"
            f"Admin status: {user_state.does_have_admin_access()}")
        logging.info(f"Available excursions: {list(self.excursions.keys())}")
        await MessageSender.send_excursions_list(query, user_state, self.excursions)
        await query.answer()  # Acknowledge the callback_data query to avoid "loading" state.

    @staticmethod
    async def _disabled_button_handler(update, context):
        """Handles clicks on disabled buttons."""
        query = update.callback_query
        logging.info(f"Handling click on disabled button for user {query.from_user.username}")
        await MessageSender.send_error_message(query, ACCESS_ERROR, is_alert=True)

    async def choose_excursion(self, update: Update):
        """Handles the selection of a components."""
        query = update.callback_query
        logging.info(f"Handling selection for user {query.from_user.username}")
        await MessageSender.delete_previous_buttons(query)

        user_state = self.get_user_state(update)
        # Parse callback_data data to extract the action and current_excursion name
        data = query.data.split("_", 1)
        if len(data) < 2:
            await MessageSender.send_error_message(query, INVALID_SELECTION_ERROR)
            return

        action, excursion_id = data
        if action != "choose":
            await MessageSender.send_error_message(query, INVALID_ACTION_ERROR)
            return

        # Find the chosen current_excursion from the list of excursions
        chosen_excursion = next(
            ((name, excursion) for name, excursion in self.excursions.items() if
             excursion.get_id() == int(excursion_id)), None)
        logging.info("Chosen components: " + chosen_excursion[0])
        if chosen_excursion is None:
            await MessageSender.send_error_message(query, EXCURSION_DOES_NOT_EXISTS_ERROR)
            return

        # If it's a paid current_excursion and the user doesn't have paid access
        if chosen_excursion[1].is_paid_excursion() and not user_state.does_have_access(chosen_excursion[1]):
            await MessageSender.send_error_message(query, ACCESS_ERROR)
            return

        # Set the user's current current_excursion and start it
        user_state.set_excursion(chosen_excursion[1])
        return chosen_excursion[1]
        # await self.start_excursion(update, chosen_excursion[1])

    async def _start_excursion(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Starts the selected current_excursion."""

        query = update.callback_query
        await MessageSender.delete_previous_buttons(query)
        excursion = await self.choose_excursion(update)
        user_state = self.get_user_state(update)

        logging.info(f"Starting excursion {excursion.get_name()} for user {user_state.username}")

        # point = user_state.get_point()  # Get the information for the current part

        # Send introduction information about the current_excursion
        await MessageSender.send_excursion_start_message(query, excursion, user_state.does_have_admin_access())
        # await self.send_point_information(update, part)

    async def send_point_information(self, update: Update, point: Point):
        """Send information about the current part."""
        query = update.callback_query
        await MessageSender.delete_previous_buttons(query)
        user_state = self.get_user_state(update)

        # Send location details (photo, name, address)
        await MessageSender.send_point_location_info(query, point, user_state.current_excursion_step + 1)

    async def _handle_arrival(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles the 'I'm Here!' button press."""
        query = update.callback_query
        await MessageSender.delete_previous_buttons(query)

        user_state = self.get_user_state(update)

        point = user_state.get_point()  # Get the current part information

        # Stats changes
        point.increase_views_num()
        point.add_new_visitor(user_state.get_user_id())
        self.data_loader.save_point(point)

        # Check if the user is in text or audio mode
        await MessageSender.send_part(query, point, user_state.mode)

        # Ask the user if they are ready to move on to the next part
        await MessageSender.send_move_on_request(query, point, user_state.get_user_id())

    async def _handle_move_on(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles the 'Move On' button press."""
        query = update.callback_query
        await MessageSender.delete_previous_buttons(query)

        user_state = self.get_user_state(update)
        user_state.excursion_next_step()

        # Move to the next part in the components
        next_point = user_state.get_point()  # Get the next part
        if next_point is not None:
            await self.send_point_information(update, next_point)
        else:
            await self._complete_excursion(update, context)

    async def _handle_extra_part(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles the 'Extra Part' button press."""
        query = update.callback_query
        user_state = self.get_user_state(update)
        current_point = user_state.get_point()
        extra_parts = current_point.get_extra_information_points()
        divided_query = query.data.split("_")
        extra_part_id = divided_query[-1]
        if extra_part_id.isdigit():
            extra_part_id = int(extra_part_id)
        else:
            await MessageSender.send_error_message(query, EXTRA_PART_DOES_NOT_EXISTS_ERROR, is_alert=False)
            return
        for extra_part in extra_parts:
            if extra_part_id == extra_part.get_id():
                extra_part.increase_views_num()
                extra_part.add_new_visitor(user_state.get_user_id())
                self.data_loader.save_information_part(extra_part)
                await MessageSender.send_part(query, extra_part, user_state.mode)
                await MessageSender.send_move_on_request(query, current_point, user_state.get_user_id())
                return
        await MessageSender.send_error_message(query, EXTRA_PART_DOES_NOT_EXISTS_ERROR, is_alert=False)

    async def _change_mode(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Allow the user to change the mode (audio/text) during the current_excursion."""
        user_state = self.get_user_state(update)

        # Toggle the mode between 'audio' and 'text'
        user_state.change_mode()
        await update.message.reply_text(
            f"Режим изменен на {user_state.get_mode()}.")

        # Send the current part's information in the new mode
        point = user_state.get_point()  # Get the part info for the current part
        await MessageSender.send_part(update.callback_query, point, user_state.mode)

    async def _complete_excursion(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles the completion of the current_excursion."""
        query = update.callback_query
        await MessageSender.delete_previous_buttons(query)

        user_state = self.get_user_state(update)

        # Notify user of completion
        current_excursion = user_state.get_current_excursion()
        excursion_name = current_excursion.get_name()

        # Stats changes
        current_excursion.increase_views_num()
        current_excursion.add_new_visitor(user_state.get_user_id())

        self.data_loader.save_excursion(current_excursion)
        self.data_loader.save_user_state(user_state)
        await query.message.reply_text(
            f"Поздравляю! Вы завершили {excursion_name}! {CONGRATULATIONS_EMOJI}")

        # Prepare feedback buttons
        await MessageSender.send_feedback_request(query)
        await query.answer()  # Acknowledge the callback_data query

    async def _give_feedback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles feedback submission after a components."""
        query = update.callback_query
        await MessageSender.delete_previous_buttons(query)

        user_state = self.get_user_state(update)

        # Handle button presses
        if query.data == FEEDBACK_POSITIVE_CALLBACK:
            user_state.get_current_excursion().increase_likes_num()
        else:
            user_state.get_current_excursion().increase_dislikes_num()
        # Save updated info
        self.data_loader.save_excursion(user_state.get_current_excursion())
        await MessageSender.send_feedback_response(query)

    async def _change_chosen_excursion_visibility(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await MessageSender.delete_previous_buttons(query)

        excursion_id = query.data.split("_")[-1]
        if not excursion_id.isdigit():
            await MessageSender.send_error_message(query, INVALID_ACTION_ERROR, is_admin=True)
        excursion_id = int(excursion_id)
        for excursion in self.excursions.values():
            if excursion_id == excursion.get_id():
                excursion.change_visibility()
                self.data_loader.save_excursion(excursion)
                previous_menu_button = InlineKeyboardButton(
                    f"{BACK_ARROW_EMOJI}{EXCURSION_EMOJI}{excursion.get_name()}",
                    callback_data=f"{CHOOSE_CALLBACK}{excursion_id}")
                await AdminMessageSender.send_success_message(update, previous_menu_button=previous_menu_button)
                return

    async def _add_excursion(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        query = update.callback_query
        user_state = self.get_user_state(update)
        await MessageSender.delete_previous_buttons(query)
        Excursion.excursion_id += 1
        new_id = Excursion.excursion_id

        new_excursion = Excursion(new_id, f"{DEFAULT_EXCURSION_NAME} {new_id}")
        user_state.user_editor.enable_editing_mode(new_excursion)
        await self._handle_next_field(update, context)

    async def _add_point(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        user_state = self.get_user_state(update)
        await MessageSender.delete_previous_buttons(query)
        Point.point_id += 1
        new_point = Point(Point.point_id, user_state.get_current_excursion().get_id())
        user_state.user_editor.enable_editing_mode(new_point, return_callback=ADD_POINT_CALLBACK,
                                                   return_message=ADD_POINT_BUTTON,
                                                   return_to_previous_menu_callback=EDIT_POINTS_CALLBACK,
                                                   return_to_previous_menu_message=EDIT_POINTS_BUTTON)
        await self._handle_next_field(update, context)

    async def _add_extra_information_point(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        user_state = self.get_user_state(update)
        point_id = int(query.data.split("_")[-1])
        await MessageSender.delete_previous_buttons(query)
        InformationPart.information_part_id += 1
        new_information_part = InformationPart(InformationPart.information_part_id, parent_id=point_id)
        user_state.user_editor.enable_editing_mode(new_information_part, point_id=point_id,
                                                   return_callback=ADD_EXTRA_POINT_CALLBACK,
                                                   return_message=ADD_EXTRA_POINT_BUTTON,
                                                   return_to_previous_menu_callback=EDIT_POINT_CALLBACK,
                                                   return_to_previous_menu_message=EDIT_POINT_BUTTON
                                                   )
        await self._handle_next_field(update, context)

    def save_editing_item(self, update: Update):
        user_state = self.get_user_state(update)
        if not user_state.user_editor.get_editing_mode():
            return  # Exit if not in editing mode
        editing_item = user_state.user_editor.get_editing_item()
        if editing_item.__class__ == Excursion:
            excursion_to_save = editing_item
            for excursion_name, excursion in self.excursions.items():
                if excursion.get_id() == editing_item.get_id():
                    del self.excursions[excursion_name]
                    self.excursions[editing_item.get_name()] = editing_item
                    break
            else:
                self.excursions[editing_item.get_name()] = editing_item
        else:
            print("Jumped to points saving")
            excursion_to_save = user_state.get_current_excursion()
            if editing_item.__class__ == Point:
                excursion_to_save.update_excursions_points(editing_item)
            elif editing_item.__class__ == InformationPart:
                print("Jumped to information_part saving")
                current_point_id = user_state.user_editor.get_point_id()
                for point in excursion_to_save.get_points():
                    print(point.get_id(), current_point_id, type(current_point_id))
                    if point.get_id() == current_point_id:
                        print("Found point")
                        point.update_extra_information_points(editing_item)
                        print("Updated extra points")
            self.excursions[excursion_to_save.get_name()] = excursion_to_save
        self.data_loader.save_excursion(excursion_to_save)

    async def _handle_messages(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_state = self.get_user_state(update)
        if user_state.user_editor.get_editing_mode() and user_state.user_editor.get_current_field_type() in [str, int,
                                                                                                             URL_TYPE]:
            await self._handle_next_field(update, context)
        elif user_state.user_editor.get_order_changing():
            await self.handle_order_changing(update, context)
        elif user_state.user_editor.get_sending_echo():
            await self._handle_echo_text(update, context)

    async def _handle_next_field(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles the current field and moves to the next one."""
        user_state = self.get_user_state(update)

        if not user_state.user_editor.get_editing_mode():
            return  # Exit if not in editing mode
        # Handle the input for the current field
        print(user_state.user_editor.current_field_counter)

        if user_state.user_editor.is_counting_started() and not (
                update.callback_query and update.callback_query.data in FILES_CALLBACKS):
            field_type = user_state.user_editor.get_current_field_type()
            print("Handling input")
            await self.handle_input(update, field_type, context)

        if update.callback_query and (update.callback_query.data in FILES_CALLBACKS
                                      and user_state.user_editor.get_current_field_type() in [
                                          AUDIO_TYPE, PHOTO_TYPE]):
            user_state.user_editor.disable_files_sending()
            files_buffer = user_state.user_editor.get_files_buffer()
            current_data = user_state.user_editor.get_current_field_state()
            if update.callback_query.data == REPLACE_EXISTING_FILES_CALLBACK:
                user_state.user_editor.add_editing_result(files_buffer)
                self._delete_files(current_data)
            elif update.callback_query.data == ADD_TO_EXISTING_FILES_CALLBACK:
                if current_data:
                    files_buffer.extend(current_data)
                user_state.user_editor.add_editing_result(files_buffer)
            elif update.callback_query.data == DELETE_EXISTING_FILES_CALLBACK:
                self._delete_files(current_data)
                user_state.user_editor.add_editing_result([])
            user_state.user_editor.clear_files_buffer()
        elif user_state.user_editor.get_files_sending_mode():
            return

        if (user_state.user_editor.get_editing_specific_field() and
                (update.callback_query and update.callback_query.data == SKIP_FIELD_CALLBACK)):
            user_state.user_editor.disable_editing_specific_field()
        elif user_state.user_editor.get_editing_specific_field():
            return

        # Move to the next field
        print("Increasing field counter")
        user_state.user_editor.increase_field_counter()
        if user_state.user_editor.is_form_finished():
            # All fields are processed; finalize
            user_state.user_editor.set_editing_result_to_item()

            return_button = user_state.user_editor.get_return_button()
            previous_menu_button = user_state.user_editor.get_previous_menu_button()

            await AdminMessageSender.send_success_message(update, return_button=return_button,
                                                          previous_menu_button=previous_menu_button)
            self.save_editing_item(update)
            user_state.user_editor.disable_editing_mode()
            return

        # Process next field message
        field_type = user_state.user_editor.get_current_field_type()
        field_message = user_state.user_editor.get_current_field_message()
        if field_type == PHOTO_TYPE or field_type == ONE_PHOTO_TYPE:
            if field_type == PHOTO_TYPE:
                user_state.user_editor.enable_files_sending()
            current_state = user_state.user_editor.get_current_field_state()
            photos = current_state if user_state.user_editor.get_current_field_state() else []
            print("Sending message to get photos from query")
            if field_type == PHOTO_TYPE:
                current_state_message = f"{len(photos)} фото"
            else:
                current_state_message = f"Текущее фото" if photos else "Нет фото"
            await AdminMessageSender.send_form_photo_field_message(update, field_message,
                                                                   current_state_message,
                                                                   photos, one_photo=(field_type == ONE_PHOTO_TYPE))

        elif field_type == AUDIO_TYPE:
            user_state.user_editor.enable_files_sending()
            current_audio = user_state.user_editor.get_current_field_state()
            current_state_message = f"{len(current_audio)} аудио файлов"
            print("Sending message to get photos from query")
            await AdminMessageSender.send_form_audio_field_message(update, field_message,
                                                                   current_state_message,
                                                                   current_audio)

        elif field_type == str or field_type == int or field_type == URL_TYPE:
            if field_type == URL_TYPE or field_type == int:
                user_state.user_editor.enable_editing_specific_field()
            current_state = user_state.user_editor.get_current_field_state()
            await AdminMessageSender.send_form_text_field_message(update, field_message,
                                                                  current_state,
                                                                  delete_link_button=(
                                                                          field_type == URL_TYPE and current_state))
        elif field_type == bool:
            print("Handling boolean field")
            current_state = user_state.user_editor.get_current_field_state()
            await AdminMessageSender.send_form_boolean_field_message(update, field_message,
                                                                     "Да" if current_state else "Нет")

    async def handle_input(self, update: Update, field_type, context: ContextTypes.DEFAULT_TYPE):

        user_state = self.get_user_state(update)

        if user_state.user_editor.get_editing_mode():
            if field_type == str or field_type == int or field_type == URL_TYPE:
                await self.handle_text_field_input(update)
            elif field_type == bool:
                self.handle_boolean_field_input(update)
            elif field_type == PHOTO_TYPE or field_type == ONE_PHOTO_TYPE:
                await self.handle_photo_field_input(update, context, True if field_type == ONE_PHOTO_TYPE else False)
            elif field_type == AUDIO_TYPE:
                await self.handle_audio_field_input(update, context)

    async def handle_text_field_input(self, update: Update):
        user_state = self.get_user_state(update)
        if user_state.user_editor.get_editing_mode():
            print("Handling text field input")
            field_type = user_state.user_editor.get_current_field_type()
            if field_type == URL_TYPE and update.callback_query and update.callback_query.data == DELETE_LINK_CALLBACK:
                user_state.user_editor.add_editing_result(None)
                user_state.user_editor.disable_editing_specific_field()
                return
            try:
                if field_type == str:
                    user_state.user_editor.add_editing_result(update.message.text)
                elif field_type == int:
                    user_state.user_editor.add_editing_result(int(update.message.text))
                    user_state.user_editor.disable_editing_specific_field()
                elif field_type == URL_TYPE:
                    parsed = urlparse(update.message.text)
                    # Ensure the scheme (http, https) and netloc (domain) are present
                    if bool(parsed.scheme and parsed.netloc):
                        user_state.user_editor.add_editing_result(update.message.text)
                        user_state.user_editor.disable_editing_specific_field()
                    else:
                        raise ValueError
            except ValueError as e:
                print("Error while handling text field input:", e)
                await update.message.reply_text(WRONG_FORMAT_MESSAGE)

    async def handle_audio_field_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Fetch the user's state
        user_state = self.get_user_state(update)

        # Check if the user is in editing mode and editing the correct field
        if user_state.user_editor.get_editing_mode():
            field_type = user_state.user_editor.get_current_field_type()
            sender = update if update.message else update.callback_query
            if field_type == AUDIO_TYPE:
                try:
                    if not update.message.audio:
                        raise ValueError("No audio files found in the message.")

                    # Get the file from Telegram servers
                    audio = update.message.audio
                    file = await context.bot.get_file(audio.file_id)

                    # Create a unique file name using the file's unique ID
                    file_name = f"{audio.file_unique_id}_{audio.file_name}"

                    # Download the file locally (temporarily)
                    temp_file_path = os.path.join(AUDIO_PATH, file_name)
                    await file.download_to_drive(temp_file_path)

                    # Upload the file to S3
                    s3_file_path = save_file_to_s3(temp_file_path, file_name, s3_directory="audio/")
                    # Append file URL to the list of saved files
                    if s3_file_path:
                        user_state.user_editor.increase_loading_file_index()
                        user_state.user_editor.add_file_to_files_buffer(s3_file_path)
                        await sender.message.reply_text(
                            f"Аудио {user_state.user_editor.get_loading_file_index()} загружено {CHECK_MARK_EMOJI}")
                    # Clean up the temporary file
                    os.remove(temp_file_path)

                except Exception as e:
                    print(f"Failed to handle audio: {e}")
                    await sender.message.reply_text("Ошибка при обработке присланных фотографий.")

    async def handle_photo_field_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                       one_photo: bool = False):
        # Fetch the user's state
        user_state = self.get_user_state(update)
        sender = update if update.message else update.callback_query
        if user_state.user_editor.get_editing_mode():
            print("Handling photo field input")
            field_type = user_state.user_editor.get_current_field_type()
            if field_type == PHOTO_TYPE or field_type == ONE_PHOTO_TYPE:
                try:
                    # Fetch the file object from Telegram
                    attachment = update.message.effective_attachment[-1]
                    if attachment.file_size > 6 * 1024 * 1024:
                        await update.message.reply_html(
                            f'<b>Файл слишком большой</b>'
                        )
                        return
                    file = await attachment.get_file()
                    file_name = f"{attachment.file_unique_id}.jpg"  # Use `file_unique_id` for uniqueness
                    # Create a unique file name
                    tmp_file_name = f'{IMAGES_PATH}/{file_name}'

                    # Download the file locally (temporarily)
                    file = await file.download_to_drive(tmp_file_name)
                    if not file:
                        raise ValueError("File download failed")
                    s3_file_path = save_file_to_s3(tmp_file_name, file_name, s3_directory="images/")
                    # Append file URL to the list of saved files
                    if s3_file_path:
                        user_state.user_editor.increase_loading_file_index()
                        if not one_photo:
                            user_state.user_editor.add_file_to_files_buffer(s3_file_path)
                        else:
                            user_state.user_editor.add_editing_result(s3_file_path)
                        await sender.message.reply_text(
                            f"Фото {user_state.user_editor.get_loading_file_index()} загружено {CHECK_MARK_EMOJI}")
                    # Clean up the temporary file
                    os.remove(tmp_file_name)

                except Exception as e:
                    print(f"Failed to handle photos: {e}")
                    await sender.message.reply_text("Ошибка при обработке присланных фотографий.")

    def handle_boolean_field_input(self, update: Update):
        user_state = self.get_user_state(update)
        if user_state.user_editor.get_editing_mode():
            data = update.callback_query.data.split("_")[-1]  # Get last element of callback_data
            if data == "yes":
                user_state.user_editor.add_editing_result(True)
            elif data == "no":
                user_state.user_editor.add_editing_result(False)

    async def _edit_point(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_state = self.get_user_state(update)
        point_id = int(update.callback_query.data.split("_")[-1])
        current_excursion = user_state.get_current_excursion()
        for point in current_excursion.get_points():
            if point.get_id() == point_id:
                await AdminMessageSender.send_point_edit_message(update.callback_query, point)
                return

    async def _edit_points(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_state = self.get_user_state(update)
        excursion = user_state.get_current_excursion()
        await MessageSender.delete_previous_buttons(update.callback_query)
        await AdminMessageSender.send_points_list(update.callback_query,
                                                  excursion.get_points(),
                                                  excursion)

    async def _edit_excursion(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_state = self.get_user_state(update)
        current_excursion = user_state.get_current_excursion()
        print(current_excursion.get_name())
        await MessageSender.delete_previous_buttons(update.callback_query)
        user_state.user_editor.enable_editing_mode(user_state.get_current_excursion())
        await self._handle_next_field(update, context)

    async def _edit_point_fields(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_state = self.get_user_state(update)
        await MessageSender.delete_previous_buttons(update.callback_query)
        point_id = int(update.callback_query.data.split("_")[-1])
        for point in user_state.get_current_excursion().get_points():
            if point.get_id() == point_id:
                # TODO: Fix buttons
                user_state.user_editor.enable_editing_mode(point, point_id=point_id,
                                                           return_to_previous_menu_callback=EDIT_POINTS_CALLBACK,
                                                           return_to_previous_menu_message=EDIT_POINTS_BUTTON)
                await self._handle_next_field(update, context)
                return

    async def delete_point(self, update: Update, callback_data: str):
        user_state = self.get_user_state(update)
        point_id = int(callback_data.split("_")[-1])
        current_excursion = user_state.get_current_excursion()
        for point in current_excursion.get_points():
            if point.get_id() == point_id:
                self._delete_element_files(point)
                for extra_point in point.get_extra_information_points():
                    self._delete_element_files(extra_point)
                    self.data_loader.delete_information_part(extra_point.get_id())
                current_excursion.points.remove(point)
                self.data_loader.delete_point(point_id)
                self.data_loader.save_excursion(current_excursion)
                previous_menu_button = InlineKeyboardButton(EDIT_POINTS_BUTTON,
                                                            callback_data=f"{EDIT_POINTS_CALLBACK}")
                await AdminMessageSender.send_success_message(update, previous_menu_button=previous_menu_button)
                return

    async def delete_extra_point(self, update: Update, callback_data: str):
        user_state = self.get_user_state(update)
        data_parts = callback_data.split("_")
        if len(data_parts) >= 2:
            point_id = int(data_parts[-2])
            extra_point_id = int(data_parts[-1])
        else:
            raise ValueError("Invalid callback_data query data format.")
        current_excursion = user_state.get_current_excursion()
        for point in current_excursion.get_points():
            if point.get_id() == point_id:
                for extra_point in point.get_extra_information_points():
                    if extra_point.get_id() == extra_point_id:
                        self._delete_element_files(extra_point)
                        point.extra_information_points.remove(extra_point)
                        self.data_loader.delete_information_part(extra_point_id)
                        self.data_loader.save_excursion(current_excursion)
                        # Return button
                        previous_menu_button = InlineKeyboardButton(EDIT_POINT_BUTTON,
                                                                    callback_data=f"{EDIT_POINT_CALLBACK}{point_id}")
                        await AdminMessageSender.send_success_message(update, previous_menu_button=previous_menu_button)
                        return

    async def _edit_extra_point(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_state = self.get_user_state(update)
        await MessageSender.delete_previous_buttons(update.callback_query)
        point_id, extra_point_id = update.callback_query.data.split("_")[-2:]
        point_id = int(point_id)
        extra_point_id = int(extra_point_id)
        for point in user_state.get_current_excursion().get_points():
            if point.get_id() == point_id:
                for extra_point in point.get_extra_information_points():
                    if extra_point.get_id() == extra_point_id:
                        await AdminMessageSender.send_point_edit_message(update.callback_query, extra_point,
                                                                         True, point_id)
                        return

    async def _edit_extra_point_fields(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_state = self.get_user_state(update)
        await MessageSender.delete_previous_buttons(update.callback_query)
        point_id, extra_point_id = update.callback_query.data.split("_")[-2:]
        point_id = int(point_id)
        extra_point_id = int(extra_point_id)
        current_excursion = user_state.get_current_excursion()
        for point in current_excursion.get_points():
            if point.get_id() == point_id:
                for extra_point in point.get_extra_information_points():
                    if extra_point.get_id() == extra_point_id:
                        user_state.user_editor.enable_editing_mode(extra_point, point_id=point_id,
                                                                   extra_information_point_id=extra_point_id,
                                                                   return_to_previous_menu_callback=EDIT_EXTRA_POINT_CALLBACK,
                                                                   return_to_previous_menu_message=EDIT_EXTRA_POINT_BUTTON)
                        await self._handle_next_field(update, context)
                        return

    async def _send_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_state = self.get_user_state(update)
        await MessageSender.delete_previous_buttons(update.callback_query)
        current_excursion = user_state.get_current_excursion()
        callback_data = update.callback_query.data
        if callback_data.startswith(EXCURSION_STATS_CALLBACK):
            previous_menu_button = InlineKeyboardButton(
                f"{BACK_ARROW_EMOJI}{EXCURSION_EMOJI}{current_excursion.get_name()}",
                callback_data=f"{CHOOSE_CALLBACK}{current_excursion.get_id()}")
            await AdminMessageSender.send_object_stats(update, current_excursion,
                                                       previous_menu_button=previous_menu_button)
        elif callback_data.startswith(POINT_STATS_CALLBACK):
            point_id = int(callback_data.split("_")[-1])
            for point in current_excursion.get_points():
                if point.get_id() == point_id:
                    previous_menu_button = InlineKeyboardButton(
                        f"{BACK_ARROW_EMOJI}{LOCATION_PIN_EMOJI}{point.get_name()}",
                        callback_data=f"{EDIT_POINT_CALLBACK}{point_id}")
                    await AdminMessageSender.send_object_stats(update, point,
                                                               previous_menu_button=previous_menu_button)
                    return
        elif callback_data.startswith(EXTRA_POINT_STATS_CALLBACK):
            point_id, extra_point_id = update.callback_query.data.split("_")[-2:]
            point_id = int(point_id)
            extra_point_id = int(extra_point_id)
            for point in current_excursion.get_points():
                if point.get_id() == point_id:
                    for extra_point in point.get_extra_information_points():
                        if extra_point.get_id() == extra_point_id:
                            previous_menu_button = InlineKeyboardButton(
                                f"{BACK_ARROW_EMOJI}{SUB_THEME_EMOJI}{extra_point.get_name()}",
                                callback_data=f"{EDIT_EXTRA_POINT_CALLBACK}{point_id}_{extra_point_id}")
                            await AdminMessageSender.send_object_stats(update, extra_point,
                                                                       previous_menu_button=previous_menu_button)
                            return

    async def _send_excursion_summary(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_state = self.get_user_state(update)
        await MessageSender.delete_previous_buttons(update.callback_query)
        current_excursion = user_state.get_current_excursion()
        await AdminMessageSender.send_excursion_summary_message(update, current_excursion)

    async def _change_points_order(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_state = self.get_user_state(update)
        await MessageSender.delete_previous_buttons(update.callback_query)
        current_excursion = user_state.get_current_excursion()
        current_state = list(
            map(lambda x: f"{x[0]}. {x[1].get_name()}", enumerate(current_excursion.get_points(), start=1)))
        current_state_message = "\n".join(current_state)
        user_state.user_editor.enable_order_changing()
        await AdminMessageSender.send_form_text_field_message(update, CHANGING_ORDER_MESSAGE,
                                                              current_state_message, skip_button=False)

    async def handle_order_changing(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_state = self.get_user_state(update)
        if user_state.user_editor.get_order_changing():
            print("Changing order")
            try:
                points_number = len(user_state.get_current_excursion().get_points())
                print("Points number: " + str(points_number))
                new_points_order = [int(point.strip()) for point in update.message.text.split(',')]
                print("New points order: ", new_points_order)
                for point_index in new_points_order:
                    if point_index < 0 or point_index > points_number or len(new_points_order) != points_number:
                        raise IndexError
                old_points_order = {index: point for index, point in
                                    enumerate(user_state.get_current_excursion().get_points(), start=1)}
                current_excursion = user_state.get_current_excursion()
                current_excursion.points = [old_points_order[new_index] for new_index in new_points_order]
                self.data_loader.save_excursion(current_excursion)
                # Return button
                previous_menu_button = InlineKeyboardButton(f"{BACK_ARROW_EMOJI}{current_excursion.get_name()}",
                                                            callback_data=f"{CHOOSE_CALLBACK}{current_excursion.get_id()}")
                await AdminMessageSender.send_success_message(update, previous_menu_button=previous_menu_button)
            except Exception as e:
                print(f"Failed to handle order changing: {e}")
                await update.message.reply_text(WRONG_FORMAT_MESSAGE)
            except IndexError as e:
                print(f"Failed to handle order changing: {e}")
                await update.message.reply_text("Неправильный индекс, попробуйте еще раз")

    async def delete_excursion(self, update: Update):
        user_state = self.get_user_state(update)
        current_excursion = user_state.get_current_excursion()
        excursion_id = current_excursion.get_id()
        for point in current_excursion.get_points():
            self._delete_element_files(point)
            for extra_point in point.get_extra_information_points():
                self.data_loader.delete_information_part(extra_point.get_id())
                self._delete_element_files(extra_point)
            self.data_loader.delete_point(point.get_id())
        del self.excursions[current_excursion.get_name()]
        self.data_loader.delete_excursion(excursion_id)
        await AdminMessageSender.send_success_message(update)

    async def clear_data(self, update: Update):
        user_state = self.get_user_state(update)
        if user_state.does_have_admin_access():
            for excursion in self.excursions.values():
                for point in excursion.get_points():
                    self._delete_element_files(point)
                    for extra_point in point.get_extra_information_points():
                        self._delete_element_files(extra_point)
                        self.data_loader.delete_information_part(extra_point.get_id())
                    self.data_loader.delete_point(point.get_id())
                self.data_loader.delete_excursion(excursion.get_id())
            # self.data_loader.clear_database()
            self.excursions.clear()
            await AdminMessageSender.send_success_message(update)

    async def _handle_deleting(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_state = self.get_user_state(update)
        await MessageSender.delete_previous_buttons(update.callback_query)
        if user_state.does_have_admin_access():
            callback_data = update.callback_query.data.split("|")[1]
            if callback_data.startswith(DELETE_EXCURSION_CALLBACK):
                await self.delete_excursion(update)
            elif callback_data.startswith(DELETE_POINT_CALLBACK):
                await self.delete_point(update, callback_data)
            elif callback_data.startswith(DELETE_EXTRA_POINT_CALLBACK):
                await self.delete_extra_point(update, callback_data)
            elif callback_data.startswith(DELETE_ALL_COLLECTIONS_CALLBACK):
                await self.clear_data(update)

    async def _handle_echo_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_state = self.get_user_state(update)
        if user_state.does_have_admin_access() and user_state.user_editor.get_sending_echo():
            text = update.message.text
            if not text:
                await update.message.reply_text(WRONG_FORMAT_MESSAGE)
            user_state.user_editor.set_echo_text(text)
            message = (f"{STOP_EMOJI}{WARNING_EMOJI} Вы подтверждаете, что хотите отправить новость?\n\n"
                       f"{TEXT_EMOJI}Текст, который будет разослан всем пользователям:\n"
                       f"{text}")
            await AdminMessageSender.approve_message(update, message, SEND_ECHO_CALLBACK, APPROVE_SENDING_BUTTON)

    async def _send_echo_to_users(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_state = self.get_user_state(update)
        if user_state.does_have_admin_access() and user_state.user_editor.get_sending_echo():
            message = user_state.user_editor.get_echo_text()
            message = f"{NEWS_EMOJI} Новость от VolkAround:\n{message}"
            message = self.escape_markdown(message)
            for user_state in self.user_states.values():
                chat_id = user_state.get_chat_id()
                if chat_id:
                    try:
                        await self.bot.send_message(chat_id=chat_id, text=message,
                                                    parse_mode=telegram.constants.ParseMode.MARKDOWN_V2)
                    except TelegramError as e:
                        logging.error(f"Failed to send message: {e}")
            user_state.user_editor.disable_sending_echo()
            await AdminMessageSender.send_success_message(update)

    async def _send_echo_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_state = self.get_user_state(update)
        if user_state.does_have_admin_access():
            user_state.user_editor.enable_sending_echo()
            await AdminMessageSender.send_echo_request(update.callback_query)

    async def _send_approving_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_state = self.get_user_state(update)
        if user_state.does_have_admin_access():
            callback = update.callback_query.data
            if callback in [DELETE_EXCURSION_CALLBACK, DELETE_POINT_CALLBACK, DELETE_EXTRA_POINT_CALLBACK,
                            DELETE_ALL_COLLECTIONS_CALLBACK]:
                message = f"{STOP_EMOJI}{WARNING_EMOJI} Вы подтверждаете, что хотите удалить элемент?"
                callback_data = f"{APPROVE_DELETING_CALLBACK}|{callback}"
                await AdminMessageSender.approve_message(update, message, callback_data, APPROVE_DELETING_BUTTON)

    def _delete_element_files(self, element: Union[Point, InformationPart]):
        files_to_delete = list()
        points_photos = element.get_photos()
        if points_photos: files_to_delete.extend(points_photos)
        point_audio = element.get_audio()
        if point_audio: files_to_delete.extend(point_audio)
        if isinstance(element, Point):
            location_photo = element.get_location_photo()
            if location_photo: files_to_delete.append(location_photo)
        self._delete_files(files_to_delete)

    @staticmethod
    def escape_markdown(text: str) -> str:
        """
        Escapes special characters for MarkdownV2 parse mode.
        """
        special_characters = r'[!"#$%&\'()*+,-./:;<=>?@\[\\\]^_`{|}~]'
        return re.sub(special_characters, r'\\\g<0>', text)

    @staticmethod
    def _delete_files(files: List[str]):
        for file_path in files:
            print(f"Deleting {file_path}")
            if file_path is None:
                continue
            try:
                s3_delete_file(file_path)
                print(f"Deleted: {file_path}")
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")

    @staticmethod
    async def _move_to_excursions_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles movement to components list"""
        await MessageSender.send_transition_warning(update)

    def run(self):
        """Start the bot."""
        # User callbacks handlers
        self.application.add_handler(CommandHandler(START_COMMAND, callback=self._start))
        self.application.add_handler(CommandHandler(CHANGE_MODE_COMMAND, self._change_mode))
        self.application.add_handler(CommandHandler(VIEW_EXCURSIONS_COMMAND, self._move_to_excursions_list))
        self.application.add_handler(CallbackQueryHandler(self._show_excursions,
                                                          pattern=f"^{SHOW_EXCURSIONS_CALLBACK}"))
        self.application.add_handler(
            CallbackQueryHandler(self._disabled_button_handler, pattern=f"^{DISABLED_CALLBACK}$"))
        self.application.add_handler(CallbackQueryHandler(self._start_excursion,
                                                          pattern=f"^{CHOOSE_CALLBACK}"))
        self.application.add_handler(CallbackQueryHandler(self._handle_arrival,
                                                          pattern=f"^{ARRIVED_CALLBACK}$"))
        self.application.add_handler(CallbackQueryHandler(self._handle_move_on,
                                                          pattern=f"^{NEXT_POINT_CALLBACK}$"))
        self.application.add_handler(CallbackQueryHandler(self._handle_extra_part,
                                                          pattern=f"^{EXTRA_PART_CALLBACK}"))
        self.application.add_handler(CallbackQueryHandler(self._complete_excursion, pattern=f"^{FINISH_CALLBACK}"))
        self.application.add_handler(CallbackQueryHandler(self._give_feedback, pattern=f"^{FEEDBACK_CALLBACK}"))

        # ---- Admin callbacks handlers ----
        # Change visibility
        self.application.add_handler(CallbackQueryHandler(self._change_chosen_excursion_visibility,
                                                          pattern=f"^{PUBLISH_CHOSEN_EXCURSION_CALLBACK}"))
        #  Add element
        self.application.add_handler(CallbackQueryHandler(self._add_excursion, pattern=f"^{ADD_EXCURSION_CALLBACK}$"))

        # Handling fields
        self.application.add_handler(CallbackQueryHandler(self._handle_next_field, pattern=f"^{SKIP_FIELD_CALLBACK}$"))
        self.application.add_handler(
            CallbackQueryHandler(self._handle_next_field, pattern=f"^{BOOLEAN_FIELD_CALLBACK}"))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_messages))
        self.application.add_handler(
            MessageHandler((filters.PHOTO | filters.AUDIO) & ~(filters.PHOTO & filters.AUDIO), self._handle_next_field)
        )

        self.application.add_handler(CallbackQueryHandler(self._add_point, pattern=f"^{ADD_POINT_CALLBACK}$"))
        self.application.add_handler(CallbackQueryHandler(self._edit_excursion,
                                                          pattern=f"^{EDIT_EXCURSION_CALLBACK}"))
        self.application.add_handler(CallbackQueryHandler(self._edit_points, pattern=f"^{EDIT_POINTS_CALLBACK}$"))
        self.application.add_handler(
            CallbackQueryHandler(self._edit_point_fields, pattern=f"^{EDIT_POINT_FIELDS_CALLBACK}"))
        self.application.add_handler(CallbackQueryHandler(self._edit_point, pattern=f"^{EDIT_POINT_CALLBACK}"))
        self.application.add_handler(
            CallbackQueryHandler(self._add_extra_information_point, pattern=f"^{ADD_EXTRA_POINT_CALLBACK}"))
        self.application.add_handler(
            CallbackQueryHandler(self._send_approving_message,
                                 pattern=f"^({DELETE_POINT_CALLBACK}|"
                                         f"{DELETE_EXTRA_POINT_CALLBACK}|"
                                         f"{DELETE_EXCURSION_CALLBACK}|"
                                         f"{DELETE_ALL_COLLECTIONS_CALLBACK})"))
        self.application.add_handler(
            CallbackQueryHandler(self._edit_extra_point, pattern=f"^{EDIT_EXTRA_POINT_CALLBACK}"))
        self.application.add_handler(
            CallbackQueryHandler(self._edit_extra_point_fields, pattern=f"^{EDIT_EXTRA_POINT_FIELDS_CALLBACK}"))
        self.application.add_handler(
            CallbackQueryHandler(self._send_stats,
                                 pattern=f"^({EXCURSION_STATS_CALLBACK}|{POINT_STATS_CALLBACK}|"
                                         f"{EXTRA_POINT_STATS_CALLBACK})"))
        self.application.add_handler(
            CallbackQueryHandler(self._send_excursion_summary, pattern=f"^{EXCURSION_SUMMARY_CALLBACK}$"))
        self.application.add_handler(
            CallbackQueryHandler(self._change_points_order, pattern=f"^{CHANGE_POINTS_ORDER_CALLBACK}$"))
        self.application.add_handler(
            CallbackQueryHandler(self._handle_next_field, pattern=f"^{ADD_TO_EXISTING_FILES_CALLBACK}$"))
        self.application.add_handler(
            CallbackQueryHandler(self._handle_next_field, pattern=f"^{REPLACE_EXISTING_FILES_CALLBACK}$"))
        self.application.add_handler(
            CallbackQueryHandler(self._handle_next_field, pattern=f"^{DELETE_EXISTING_FILES_CALLBACK}$"))
        self.application.add_handler(CallbackQueryHandler(self._handle_next_field, pattern=f"^{DELETE_LINK_CALLBACK}$"))
        self.application.add_handler(
            CallbackQueryHandler(self._handle_deleting, pattern=f"^{APPROVE_DELETING_CALLBACK}"))
        self.application.add_handler(CallbackQueryHandler(self._send_echo_request, pattern=f"^{ECHO_CALLBACK}$"))
        self.application.add_handler(CallbackQueryHandler(self._send_echo_to_users, pattern=f"^{SEND_ECHO_CALLBACK}$"))
        self.application.run_polling()
