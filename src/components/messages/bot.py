from typing import List

from telegram import Update, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, filters, \
    MessageHandler

from src.components.excursion.point.information_part import InformationPart
from src.components.messages.admin_message_sender import AdminMessageSender
from src.components.messages.message_sender import MessageSender  # Assuming MessageSender is in a separate file
from src.components.excursion.excursion import Excursion
from src.components.excursion.point.point import Point
from src.components.user.user_state import UserState
from src.data.load_manager import LoadManager
from src.constants import *


def get_user_id_by_update(update: Update) -> int:
    return update.callback_query.from_user.id if update.callback_query else update.message.from_user.id


# TODO: Finish menu transitions

class Bot:
    """The main bot class coordinating everything."""

    def __init__(self, token):
        self.application = Application.builder().token(token).build()

        self.data_loader = LoadManager()
        self.user_states = self.data_loader.load_user_states()  # Keeps track of UserState objects for each user
        self.excursions = self.data_loader.load_excursions()  # Dictionary of all available excursions

    def get_user_state(self, user_id: int, username: str = None):
        """Gets or creates the user state for the given user."""
        if user_id not in self.user_states:
            is_admin = True if username in {"ivanezox", "ZeevVolk"} else False
            self.user_states[user_id] = UserState(username=username, user_id=user_id, is_admin=is_admin)
            self.data_loader.save_user_state(self.user_states[user_id])
        return self.user_states[user_id]

    def sync_data(self) -> None:
        self.user_states = self.data_loader.load_user_states()  # Keeps track of UserState objects for each user
        self.excursions = self.data_loader.load_excursions()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles the /start command."""
        user_state = self.get_user_state(update.message.from_user.id, update.message.from_user.username)
        user_state.reset_current_excursion()  # Reset any ongoing current_excursion for a fresh start

        # Explain the available versions
        await MessageSender.send_intro_message(update)

    async def show_excursions(self, update, context):
        """Displays the list of available excursions based on user access."""
        query = update.callback_query
        user_id = query.from_user.id
        print(query.data)
        if query.data == SHOW_EXCURSIONS_SYNC_CALLBACK:
            self.sync_data()
        user_state = self.get_user_state(user_id)
        user_state.reset_current_excursion()
        user_state.user_editor.disable_editing_mode()
        user_state.user_editor.disable_order_changing()
        await MessageSender.delete_previous_buttons(query)
        print(f"Sending excursions list for user {user_state.username}")
        print(f"Available excursions: {list(self.excursions.keys())}")
        print(user_state.does_have_admin_access())
        await MessageSender.send_excursions_list(query, user_state, self.excursions)
        await query.answer()  # Acknowledge the callback query to avoid "loading" state.

    @staticmethod
    async def disabled_button_handler(update, context):
        """Handles clicks on disabled buttons."""
        query = update.callback_query
        await MessageSender.send_error_message(query, ACCESS_ERROR, is_alert=True)

    async def choose_excursion(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles the selection of a components."""
        query = update.callback_query
        await MessageSender.delete_previous_buttons(query)

        user_id = query.from_user.id
        user_state = self.get_user_state(user_id)
        # Parse callback data to extract the action and current_excursion name
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
        print("Chosen components: " + chosen_excursion[0])
        if chosen_excursion is None:
            await MessageSender.send_error_message(query, EXCURSION_DOES_NOT_EXISTS_ERROR)
            return

        # If it's a paid current_excursion and the user doesn't have paid access
        if chosen_excursion[1].is_paid_excursion() and not user_state.does_have_access(chosen_excursion[1]):
            await MessageSender.send_error_message(query, ACCESS_ERROR)
            return

        # Set the user's current current_excursion and start it
        user_state.set_excursion(chosen_excursion[1])
        await self.start_excursion(update, chosen_excursion[1])

    async def start_excursion(self, update: Update, excursion: Excursion):
        """Starts the selected current_excursion."""

        query = update.callback_query
        # await MessageSender.delete_previous_buttons(query)

        user_id = query.from_user.id
        user_state = self.get_user_state(user_id)

        # point = user_state.get_point()  # Get the information for the current part

        # Send introduction information about the current_excursion
        await MessageSender.send_excursion_start_message(query, excursion, user_state.does_have_admin_access())
        # await self.send_point_information(update, part)

    @staticmethod
    async def send_point_information(update: Update, point: Point):
        """Send information about the current part."""
        query = update.callback_query
        await MessageSender.delete_previous_buttons(query)

        # Send location details (photo, name, address)
        await MessageSender.send_point_location_info(query, point)

    async def handle_arrival(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles the 'I'm Here!' button press."""
        query = update.callback_query
        await MessageSender.delete_previous_buttons(query)

        user_id = query.from_user.id
        user_state = self.get_user_state(user_id)

        point = user_state.get_point()  # Get the current part information
        point.increase_visitors_num()
        # Check if the user is in text or audio mode
        await MessageSender.send_part(query, point, user_state.mode)

        # Ask the user if they are ready to move on to the next part
        await MessageSender.send_move_on_request(query, point)

    async def handle_move_on(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles the 'Move On' button press."""
        query = update.callback_query
        await MessageSender.delete_previous_buttons(query)

        user_id = query.from_user.id
        user_state = self.get_user_state(user_id)
        user_state.excursion_next_step()

        # Move to the next part in the components
        next_point = user_state.get_point()  # Get the next part
        if next_point is not None:
            await self.send_point_information(update, next_point)
        else:
            await self.complete_excursion(update, context)

    async def handle_extra_part(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles the 'Extra Part' button press."""
        query = update.callback_query
        user_id = query.from_user.id
        user_state = self.get_user_state(user_id)
        current_point = user_state.get_point()
        extra_parts = current_point.get_extra_information_points()
        action, extra_part_id = query.data.split("_", 1)
        if extra_part_id.isdigit():
            extra_part_id = int(extra_part_id)
        else:
            await MessageSender.send_error_message(query, EXTRA_PART_DOES_NOT_EXISTS_ERROR, is_alert=False)

        if extra_part_id >= len(extra_parts):
            await MessageSender.send_error_message(query, EXTRA_PART_DOES_NOT_EXISTS_ERROR, is_alert=False)
        else:
            extra_parts[extra_part_id].increase_visitors_num()
            await MessageSender.send_part(query, extra_parts[extra_part_id], user_state.mode)
            await MessageSender.send_move_on_request(query, current_point)

    async def change_mode(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Allow the user to change the mode (audio/text) during the current_excursion."""
        user_id = update.message.from_user.id
        user_state = self.get_user_state(user_id)

        # Toggle the mode between 'audio' and 'text'
        user_state.change_mode()
        await update.message.reply_text(
            f"Режим изменен на {user_state.get_mode()}.")

        # Send the current part's information in the new mode
        point = user_state.get_point()  # Get the part info for the current part
        await MessageSender.send_part(update.callback_query, point, user_state.mode)

    async def complete_excursion(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles the completion of the current_excursion."""
        query = update.callback_query
        await MessageSender.delete_previous_buttons(query)

        user_id = query.from_user.id
        user_state = self.get_user_state(user_id)

        # Notify user of completion
        excursion_name = user_state.get_current_excursion().get_name()
        user_state.add_completed_excursion(user_state.get_current_excursion())
        current_excursion = user_state.get_current_excursion()
        current_excursion.increase_visitors_num()
        self.data_loader.save_excursion(current_excursion)
        self.data_loader.save_user_state(user_state)
        await query.message.reply_text(
            f"Поздравляю! Вы завершили {excursion_name}! {CONGRATULATIONS_EMOJI}")

        # Prepare feedback buttons
        await MessageSender.send_feedback_request(query)
        await query.answer()  # Acknowledge the callback query

    async def give_feedback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles feedback submission after a components."""
        query = update.callback_query
        await MessageSender.delete_previous_buttons(query)

        user_id = query.from_user.id
        user_state = self.get_user_state(user_id)

        # Handle button presses
        if query.data == FEEDBACK_POSITIVE_CALLBACK:
            user_state.get_current_excursion().increase_likes_num()
        else:
            user_state.get_current_excursion().increase_dislikes_num()
        # Save updated info
        self.data_loader.save_excursion(user_state.get_current_excursion())
        await MessageSender.send_feedback_response(query)

    async def change_chosen_excursion_visibility(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await MessageSender.delete_previous_buttons(query)

        excursion_id = query.data.split("_")[-1]
        if not excursion_id.isdigit():
            await MessageSender.send_error_message(query, INVALID_ACTION_ERROR, is_admin=True)
        excursion_id = int(excursion_id)

        for excursion in self.excursions.values():
            if excursion_id == excursion.get_id():
                excursion.change_visibility()
                break
        await AdminMessageSender.send_success_message(update)

    async def add_excursion(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        query = update.callback_query
        user_state = self.get_user_state(user_id=update.callback_query.from_user.id)
        await MessageSender.delete_previous_buttons(query)
        Excursion.excursion_id += 1
        new_id = Excursion.excursion_id

        new_excursion = Excursion(new_id)
        user_state.user_editor.enable_editing_mode(new_excursion)
        await self.handle_next_field(update, context)

    async def add_point(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        user_state = self.get_user_state(user_id=update.callback_query.from_user.id)
        await MessageSender.delete_previous_buttons(query)
        Point.point_id += 1
        new_point = Point(Point.point_id, user_state.get_current_excursion().get_id())
        user_state.user_editor.enable_editing_mode(new_point, return_callback=ADD_POINT_CALLBACK,
                                                   return_message=ADD_POINT_BUTTON,
                                                   return_to_previous_menu_callback=EDIT_POINTS_CALLBACK,
                                                   return_to_previous_menu_message=EDIT_POINTS_BUTTON)
        await self.handle_next_field(update, context)

    async def add_extra_information_point(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        user_state = self.get_user_state(user_id=update.callback_query.from_user.id)
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
        await self.handle_next_field(update, context)

    def save_editing_item(self, update: Update):
        user_id = get_user_id_by_update(update)
        user_state = self.get_user_state(user_id=user_id)
        if not user_state.user_editor.get_editing_mode():
            return  # Exit if not in editing mode
        excursion_to_save = None
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

    async def handle_messages(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_state = self.get_user_state(user_id=update.message.from_user.id)
        if user_state.user_editor.get_editing_mode() and user_state.user_editor.get_current_field_type() == str:
            await self.handle_next_field(update, context)
        elif user_state.user_editor.get_order_changing():
            await self.handle_order_changing(update, context)

    async def handle_next_field(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles the current field and moves to the next one."""
        user_id = get_user_id_by_update(update)
        user_state = self.get_user_state(user_id=user_id)

        if not user_state.user_editor.get_editing_mode():
            return  # Exit if not in editing mode
        # Handle the input for the current field
        print(user_state.user_editor.current_field_counter)
        if user_state.user_editor.is_counting_started() and not (
                update.callback_query and update.callback_query.data in {SKIP_FIELD_CALLBACK,
                                                                         DISABLE_SENDING_FILES_CALLBACK}):
            field_type = user_state.user_editor.get_current_field_type()
            await self.handle_input(update, field_type, context)

        if update.callback_query and (update.callback_query.data in [SKIP_FIELD_CALLBACK,
                                                                     DISABLE_SENDING_FILES_CALLBACK]
                                      and user_state.user_editor.get_current_field_type() in [
                                          AUDIO_TYPE, PHOTO_TYPE]):
            user_state.user_editor.disable_files_sending()
            files_buffer = user_state.user_editor.get_files_buffer()
            if update.callback_query.data == DISABLE_SENDING_FILES_CALLBACK:
                user_state.user_editor.add_editing_result(files_buffer)
            user_state.user_editor.clear_files_buffer()
        elif user_state.user_editor.get_files_sending_mode():
            return

        # Move to the next field
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
            await AdminMessageSender.send_form_photo_field_message(update, field_message,
                                                                   f"{len(photos)} фото",
                                                                   photos, one_photo=(field_type == ONE_PHOTO_TYPE))

        elif field_type == AUDIO_TYPE:
            user_state.user_editor.enable_files_sending()
            current_audio = user_state.user_editor.get_current_field_state()
            current_state_message = "Текущий аудио файл" if current_audio else "Нет текущего аудио файла"
            print("Sending message to get photos from query")
            await AdminMessageSender.send_form_audio_field_message(update, field_message,
                                                                   current_state_message,
                                                                   current_audio)

        elif field_type == str:
            current_state = user_state.user_editor.get_current_field_state()
            await AdminMessageSender.send_form_text_field_message(update, field_message,
                                                                  current_state)
        elif field_type == bool:
            print("Handling boolean field")
            current_state = user_state.user_editor.get_current_field_state()
            await AdminMessageSender.send_form_boolean_field_message(update, field_message,
                                                                     "Да" if current_state else "Нет")

    async def handle_input(self, update: Update, field_type, context: ContextTypes.DEFAULT_TYPE):

        user_id = get_user_id_by_update(update)
        user_state = self.get_user_state(user_id=user_id)

        if user_state.user_editor.get_editing_mode():
            if field_type == str:
                self.handle_text_field_input(update)
            elif field_type == bool:
                self.handle_boolean_field_input(update)
            elif field_type == PHOTO_TYPE or field_type == ONE_PHOTO_TYPE:
                await self.handle_photo_field_input(update, context, True if field_type == ONE_PHOTO_TYPE else False)
            elif field_type == AUDIO_TYPE:
                await self.handle_audio_field_input(update, context)

    def handle_text_field_input(self, update: Update):
        user_state = self.get_user_state(user_id=update.message.from_user.id)
        if user_state.user_editor.get_editing_mode():
            print("Handling text field input")
            field_type = user_state.user_editor.get_current_field_type()
            if field_type == str:
                user_state.user_editor.add_editing_result(update.message.text)

    async def handle_audio_field_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Fetch the user's state
        user_state = self.get_user_state(user_id=update.message.from_user.id)

        # Check if the user is in editing mode and editing the correct field
        if user_state.user_editor.get_editing_mode():
            field_type = user_state.user_editor.get_current_field_type()
            if field_type == AUDIO_TYPE:
                # Ensure the directory exists
                os.makedirs(AUDIO_PATH, exist_ok=True)

                try:
                    # Determine if this is a media group or a single audio message

                    if not update.message.audio:
                        raise ValueError("No audio files found in the message.")
                    # Process and save each audio file
                    # Get the file from Telegram servers
                    audio = update.message.audio
                    file = await context.bot.get_file(audio.file_id)

                    # Create a unique file name using the file's unique ID
                    file_name = f"{audio.file_unique_id}_{audio.file_name}"
                    file_path = os.path.join(AUDIO_PATH, file_name)

                    # Download the file to the specified location
                    await file.download_to_drive(file_path)
                    print(f"Audio file saved to {file_path}")

                    # Save the file path in the user's editing result
                    user_state.user_editor.add_file_to_files_buffer(file_path)

                except Exception as e:
                    print(f"Failed to handle audio: {e}")
                    await update.message.reply_text("Ошибка загрузки файлов.")

    async def handle_photo_field_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                       one_photo: bool = False):
        user_state = self.get_user_state(user_id=update.message.from_user.id)
        if user_state.user_editor.get_editing_mode():
            print("Handling photo field input")
            field_type = user_state.user_editor.get_current_field_type()
            if field_type == PHOTO_TYPE or field_type == ONE_PHOTO_TYPE:
                # Ensure the directory exists
                os.makedirs(IMAGES_PATH, exist_ok=True)

                print(update.message.photo)

                try:
                    # Fetch the file object
                    photo = update.message.photo[-1]
                    file = await context.bot.get_file(photo.file_id)

                    # Create a unique file name
                    file_name = f"{photo.file_unique_id}.jpg"  # Use `file_unique_id` for uniqueness
                    file_path = os.path.join(IMAGES_PATH, file_name)

                    # Download the file to the specified location
                    await file.download_to_drive(file_path)
                    print(f"Photo saved to {file_path}")

                    # Append file path to the list of saved files

                    # Update the editing result
                    if not one_photo:
                        user_state.user_editor.add_file_to_files_buffer(file_path)
                    else:
                        user_state.user_editor.add_editing_result(file_path)
                except Exception as e:
                    print(f"Failed to handle photos: {e}")
                    await update.message.reply_text("An error occurred while processing the photos.")

    def handle_boolean_field_input(self, update: Update):
        user_state = self.get_user_state(user_id=update.callback_query.from_user.id)
        if user_state.user_editor.get_editing_mode():
            data = update.callback_query.data.split("_")[-1]  # Get last element of callback
            if data == "yes":
                user_state.user_editor.add_editing_result(True)
            elif data == "no":
                user_state.user_editor.add_editing_result(False)

    async def edit_point(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_state = self.get_user_state(user_id=update.callback_query.from_user.id)
        point_id = int(update.callback_query.data.split("_")[-1])
        current_excursion = user_state.get_current_excursion()
        for point in current_excursion.get_points():
            if point.get_id() == point_id:
                await AdminMessageSender.send_point_edit_message(update.callback_query, point)
                return

    async def edit_points(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_state = self.get_user_state(user_id=update.callback_query.from_user.id)
        await MessageSender.delete_previous_buttons(update.callback_query)
        await AdminMessageSender.send_points_list(update.callback_query,
                                                  user_state.get_current_excursion().get_points())

    async def edit_excursion(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_state = self.get_user_state(user_id=update.callback_query.from_user.id)
        current_excursion = user_state.get_current_excursion()
        print(current_excursion.get_name())
        await MessageSender.delete_previous_buttons(update.callback_query)
        user_state.user_editor.enable_editing_mode(user_state.get_current_excursion())
        await self.handle_next_field(update, context)

    async def edit_point_fields(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_state = self.get_user_state(user_id=update.callback_query.from_user.id)
        await MessageSender.delete_previous_buttons(update.callback_query)
        point_id = int(update.callback_query.data.split("_")[-1])
        for point in user_state.get_current_excursion().get_points():
            if point.get_id() == point_id:
                user_state.user_editor.enable_editing_mode(point, point_id=point_id,
                                                           return_to_previous_menu_callback=EDIT_POINTS_CALLBACK,
                                                           return_to_previous_menu_message=EDIT_POINTS_BUTTON)
                await self.handle_next_field(update, context)
                return

    async def delete_point(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_state = self.get_user_state(user_id=update.callback_query.from_user.id)
        await MessageSender.delete_previous_buttons(update.callback_query)
        point_id = int(update.callback_query.data.split("_")[-1])
        current_excursion = user_state.get_current_excursion()
        for point in current_excursion.get_points():
            if point.get_id() == point_id:
                files_to_delete = list()
                points_photos = point.get_photos()
                if points_photos: files_to_delete.extend(points_photos)
                point_location_photo = point.get_location_photo()
                if point_location_photo: files_to_delete.append(point_location_photo)
                point_audio = point.get_audio()
                if point_audio: files_to_delete.extend(point_audio)
                for extra_point in point.get_extra_information_points():
                    extra_point_photos = extra_point.get_photos()
                    if extra_point_photos: files_to_delete.extend(extra_point_photos)
                    extra_point_audio = extra_point.get_audio()
                    if extra_point_audio: files_to_delete.extend(extra_point_audio)
                self.delete_files(files_to_delete)
                current_excursion.points.remove(point)
                self.data_loader.save_excursion(current_excursion)
                previous_menu_button = InlineKeyboardButton(EDIT_POINTS_BUTTON,
                                                            callback_data=f"{EDIT_POINTS_CALLBACK}")
                await AdminMessageSender.send_success_message(update)
                return

    async def delete_extra_point(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_state = self.get_user_state(user_id=update.callback_query.from_user.id)
        await MessageSender.delete_previous_buttons(update.callback_query)
        data_parts = update.callback_query.data.split("_")
        if len(data_parts) >= 2:
            point_id = int(data_parts[-2])
            extra_point_id = int(data_parts[-1])
        else:
            raise ValueError("Invalid callback query data format.")
        current_excursion = user_state.get_current_excursion()
        for point in current_excursion.get_points():
            if point.get_id() == point_id:
                for extra_point in point.get_extra_information_points():
                    if extra_point.get_id() == extra_point_id:
                        files_to_delete = list()
                        extra_point_photos = extra_point.get_photos()
                        if extra_point_photos: files_to_delete.extend(extra_point_photos)
                        extra_point_audio = extra_point.get_audio()
                        if extra_point_audio: files_to_delete.extend(extra_point_audio)
                        self.delete_files(files_to_delete)
                        point.extra_information_points.remove(extra_point)
                        self.data_loader.save_excursion(current_excursion)
                        # Return button
                        previous_menu_button = InlineKeyboardButton(EDIT_POINT_BUTTON,
                                                                    callback_data=f"{EDIT_POINT_CALLBACK}{point_id}")
                        await AdminMessageSender.send_success_message(update, previous_menu_button=previous_menu_button)
                        return

    async def edit_extra_point(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_state = self.get_user_state(user_id=update.callback_query.from_user.id)
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

    async def edit_extra_point_fields(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_state = self.get_user_state(user_id=update.callback_query.from_user.id)
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
                        await self.handle_next_field(update, context)
                        return

    async def send_excursion_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_state = self.get_user_state(user_id=update.callback_query.from_user.id)
        await MessageSender.delete_previous_buttons(update.callback_query)
        current_excursion = user_state.get_current_excursion()
        await AdminMessageSender.send_excursion_stats(update, current_excursion)

    async def send_excursion_summary(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_state = self.get_user_state(user_id=update.callback_query.from_user.id)
        await MessageSender.delete_previous_buttons(update.callback_query)
        current_excursion = user_state.get_current_excursion()
        await AdminMessageSender.send_excursion_summary_message(update, current_excursion)

    async def change_points_order(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_state = self.get_user_state(user_id=update.callback_query.from_user.id)
        await MessageSender.delete_previous_buttons(update.callback_query)
        current_excursion = user_state.get_current_excursion()
        current_state = list(
            map(lambda x: f"{x[0]}. {x[1].get_name()}", enumerate(current_excursion.get_points(), start=1)))
        current_state_message = "\n".join(current_state)
        user_state.user_editor.enable_order_changing()
        await AdminMessageSender.send_form_text_field_message(update, CHANGING_ORDER_MESSAGE,
                                                              current_state_message, skip_button=False)

    async def handle_order_changing(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_state = self.get_user_state(user_id=update.message.from_user.id)
        if user_state.user_editor.get_order_changing():
            print("Changing order")
            try:
                points_number = len(user_state.get_current_excursion().get_points())
                print("Points number: " + str(points_number))
                new_points_order = [int(point.strip()) for point in update.message.text.split(',')]
                print("New points order: ", new_points_order)
                for point_index in new_points_order:
                    if point_index < 0 or point_index > points_number:
                        raise IndexError
                old_points_order = {index: point for index, point in
                                    enumerate(user_state.get_current_excursion().get_points(), start=1)}
                current_excursion = user_state.get_current_excursion()
                current_excursion.points = [old_points_order[new_index] for new_index in new_points_order]
                self.data_loader.save_excursion(current_excursion)

                # Return button
                await AdminMessageSender.send_success_message(update)
            except Exception as e:
                print(f"Failed to handle order changing: {e}")
                await update.message.reply_text(WRONG_FORMAT_MESSAGE)
            except IndexError as e:
                print(f"Failed to handle order changing: {e}")
                await update.message.reply_text("Неправильный индекс, попробуйте еще раз")

    async def delete_excursion(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_state = self.get_user_state(user_id=update.callback_query.from_user.id)
        await MessageSender.delete_previous_buttons(update.callback_query)
        current_excursion = user_state.get_current_excursion()
        files_to_delete = list()
        for point in current_excursion.get_points():
            points_photos = point.get_photos()
            if points_photos: files_to_delete.extend(points_photos)
            point_location_photo = point.get_location_photo()
            if point_location_photo: files_to_delete.append(point_location_photo)
            point_audio = point.get_audio()
            if point_audio: files_to_delete.extend(point_audio)
            for extra_point in point.get_extra_information_points():
                extra_point_photos = extra_point.get_photos()
                if extra_point_photos: files_to_delete.extend(extra_point_photos)
                extra_point_audio = extra_point.get_audio()
                if extra_point_audio: files_to_delete.extend(extra_point_audio)

        self.delete_files(files_to_delete)
        del self.excursions[current_excursion.get_name()]
        self.data_loader.delete_excursion(current_excursion.excursion_id)
        await AdminMessageSender.send_success_message(update)

    @staticmethod
    def delete_files(files: List[str]):
        for file_path in files:
            if file_path is None:
                continue
            try:
                os.remove(file_path)  # Delete the file
                print(f"Deleted: {file_path}")
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")

    @staticmethod
    async def move_to_excursions_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles movement to components list"""
        await MessageSender.send_transition_warning(update)

    def run(self):
        """Start the bot."""
        # User callbacks handlers
        self.application.add_handler(CommandHandler(START_COMMAND, self.start))
        self.application.add_handler(CommandHandler(CHANGE_MODE_COMMAND, self.change_mode))
        self.application.add_handler(CommandHandler(VIEW_EXCURSIONS_COMMAND, self.move_to_excursions_list))
        self.application.add_handler(CallbackQueryHandler(self.show_excursions, pattern=f"^{SHOW_EXCURSIONS_CALLBACK}"))
        self.application.add_handler(
            CallbackQueryHandler(self.disabled_button_handler, pattern=f"^{DISABLED_CALLBACK}$"))
        self.application.add_handler(CallbackQueryHandler(self.choose_excursion, pattern=f"^{CHOOSE_CALLBACK}"))
        self.application.add_handler(CallbackQueryHandler(self.handle_arrival, pattern=f"^{ARRIVED_CALLBACK}$"))
        self.application.add_handler(CallbackQueryHandler(self.handle_move_on, pattern=f"^{NEXT_POINT_CALLBACK}$"))
        self.application.add_handler(CallbackQueryHandler(self.handle_extra_part, pattern=f"^{EXTRA_PART_CALLBACK}"))
        self.application.add_handler(CallbackQueryHandler(self.complete_excursion, pattern=f"^{FINISH_CALLBACK}"))
        self.application.add_handler(CallbackQueryHandler(self.give_feedback, pattern=f"^{FEEDBACK_CALLBACK}"))

        # ---- Admin callbacks handlers ----
        # Change visibility
        self.application.add_handler(CallbackQueryHandler(self.change_chosen_excursion_visibility,
                                                          pattern=f"^{PUBLISH_CHOSEN_EXCURSION_CALLBACK}"))
        #  Add excursion
        self.application.add_handler(CallbackQueryHandler(self.add_excursion, pattern=f"^{ADD_EXCURSION_CALLBACK}$"))

        # Handling fields
        self.application.add_handler(CallbackQueryHandler(self.handle_next_field, pattern=f"^{SKIP_FIELD_CALLBACK}$"))
        self.application.add_handler(
            CallbackQueryHandler(self.handle_next_field, pattern=f"^{BOOLEAN_FIELD_CALLBACK}"))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_messages))
        self.application.add_handler(MessageHandler(filters.PHOTO & ~filters.AUDIO, self.handle_next_field))
        self.application.add_handler(MessageHandler(filters.AUDIO & ~filters.PHOTO, self.handle_next_field))

        self.application.add_handler(CallbackQueryHandler(self.add_point, pattern=f"^{ADD_POINT_CALLBACK}$"))
        self.application.add_handler(CallbackQueryHandler(self.edit_excursion, pattern=f"^{EDIT_EXCURSION_CALLBACK}"))
        self.application.add_handler(CallbackQueryHandler(self.edit_points, pattern=f"^{EDIT_POINTS_CALLBACK}$"))
        self.application.add_handler(
            CallbackQueryHandler(self.edit_point_fields, pattern=f"^{EDIT_POINT_FIELDS_CALLBACK}"))
        self.application.add_handler(CallbackQueryHandler(self.edit_point, pattern=f"^{EDIT_POINT_CALLBACK}"))
        self.application.add_handler(
            CallbackQueryHandler(self.add_extra_information_point, pattern=f"^{ADD_EXTRA_POINT_CALLBACK}"))
        self.application.add_handler(
            CallbackQueryHandler(self.delete_point, pattern=f"^{DELETE_POINT_CALLBACK}"))
        self.application.add_handler(
            CallbackQueryHandler(self.delete_extra_point, pattern=f"^{DELETE_EXTRA_POINT_CALLBACK}"))
        self.application.add_handler(
            CallbackQueryHandler(self.edit_extra_point, pattern=f"^{EDIT_EXTRA_POINT_CALLBACK}"))
        self.application.add_handler(
            CallbackQueryHandler(self.edit_extra_point_fields, pattern=f"^{EDIT_EXTRA_POINT_FIELDS_CALLBACK}"))
        self.application.add_handler(
            CallbackQueryHandler(self.send_excursion_stats, pattern=f"^{EXCURSION_STATS_CALLBACK}$"))
        self.application.add_handler(
            CallbackQueryHandler(self.send_excursion_summary, pattern=f"^{EXCURSION_SUMMARY_CALLBACK}$"))
        self.application.add_handler(
            CallbackQueryHandler(self.change_points_order, pattern=f"^{CHANGE_POINTS_ORDER_CALLBACK}$"))
        self.application.add_handler(
            CallbackQueryHandler(self.delete_excursion, pattern=f"^{DELETE_EXCURSION_CALLBACK}"))
        self.application.add_handler(
            CallbackQueryHandler(self.handle_next_field, pattern=f"^{DISABLE_SENDING_FILES_CALLBACK}$"))
        # self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_order_changing))

        self.application.run_polling()
