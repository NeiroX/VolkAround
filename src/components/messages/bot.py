from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, ConversationHandler, filters, \
    MessageHandler

from src.components.excursion.point.information_part import InformationPart
from src.components.messages.admin_message_sender import AdminMessageSender
from src.components.messages.message_sender import MessageSender  # Assuming MessageSender is in a separate file
from src.components.excursion.excursion import Excursion
from src.components.excursion.point.point import Point
from src.components.user.user_state import UserState
from src.database.load_manager import LoadManager
from src.constants import *


def get_user_id_by_update(update: Update) -> int:
    return update.callback_query.from_user.id if update.callback_query else update.message.from_user.id

# TODO: Fix saving
# TODO: Add editing and adding extra information points
# TODO: Add order change

class Bot:
    """The main bot class coordinating everything."""

    def __init__(self, token):
        self.application = Application.builder().token(token).build()
        self.user_states = LoadManager.load_user_states_from_json()  # Keeps track of UserState objects for each user
        self.excursions = LoadManager.load_excursions_from_json()  # Dictionary of all available excursions

    def get_user_state(self, user_id: int, username: str = None):
        """Gets or creates the user state for the given user."""
        if user_id not in self.user_states:
            self.user_states[user_id] = UserState(username=username, user_id=user_id)
            self.user_states[user_id].add_paid_excursion(self.excursions["Мир Оксимирона: Комнаты творчества"])
            LoadManager.save_user_state(self.user_states[user_id])
        return self.user_states[user_id]

    def sync_data(self) -> None:
        self.user_states = LoadManager.load_user_states_from_json()  # Keeps track of UserState objects for each user
        self.excursions = LoadManager.load_excursions_from_json()

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
        LoadManager.save_user_state(user_state)
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
            user_state.get_current_excursion().like()
        else:
            user_state.get_current_excursion().dislike()
        # Save updated info
        LoadManager.save_excursion_data(user_state.get_current_excursion())
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
        await AdminMessageSender.send_success_message(query)

    async def add_excursion(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        query = update.callback_query
        user_state = self.get_user_state(user_id=update.callback_query.from_user.id)
        await MessageSender.delete_previous_buttons(query)
        new_id = 0
        if self.excursions:
            for excursion_name, excursion in self.excursions.items():
                if excursion.get_id() > new_id:
                    new_id = excursion.get_id()
        new_excursion = Excursion(new_id)
        user_state.user_editor.enable_editing_mode(new_excursion)
        await self.handle_next_field(update, context)

    async def add_point(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        user_state = self.get_user_state(user_id=update.callback_query.from_user.id)
        await MessageSender.delete_previous_buttons(query)
        new_id = 0
        if self.excursions:
            for excursion in self.excursions.values():
                for point in excursion.get_points():
                    if point.get_id() > new_id:
                        new_id = point.get_id()
        new_point = Point(new_id + 1)
        user_state.user_editor.enable_editing_mode(new_point)
        await self.handle_next_field(update, context)

    def save_editing_item(self, update: Update):
        user_id = get_user_id_by_update(update)
        user_state = self.get_user_state(user_id=user_id)
        excursion_to_save = None
        if not user_state.user_editor.get_editing_mode():
            return  # Exit if not in editing mode
        editing_item = user_state.user_editor.get_editing_item()
        if editing_item.__class__ == Excursion:
            excursion_to_save = editing_item
            for excursion in self.excursions.values():
                if excursion.get_id() == editing_item.get_id():
                    self.excursions[editing_item.get_name()] = editing_item
                    break
            else:
                self.excursions[editing_item.get_name()] = editing_item
        else:
            excursion_to_save = user_state.get_current_excursion()
            if editing_item.__class__ == Point:
                excursion_to_save.update_excursions_points(editing_item)
            elif editing_item.__class__ == InformationPart:
                current_point_id = user_state.user_editor.get_point_id()
                for point in excursion_to_save.get_points():
                    if point.get_id() == current_point_id:
                        point.update_extra_information_points(editing_item)
        LoadManager.save_excursion_data(excursion_to_save)

    async def handle_next_field(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles the current field and moves to the next one."""
        user_id = get_user_id_by_update(update)
        user_state = self.get_user_state(user_id=user_id)

        if not user_state.user_editor.get_editing_mode():
            return  # Exit if not in editing mode

        # Handle the input for the current field
        if user_state.user_editor.is_counting_started() and not (
                update.callback_query and update.callback_query.data == SKIP_FIELD_CALLBACK):
            field_type = user_state.user_editor.get_current_field_type()
            self.handle_input(update, field_type)

        # Move to the next field
        user_state.user_editor.increase_field_counter()
        if user_state.user_editor.is_form_finished():
            # All fields are processed; finalize
            user_state.user_editor.set_editing_result_to_item()
            await AdminMessageSender.send_success_message(update.callback_query)
            user_state.user_editor.disable_editing_mode()
            return

        # Process next field message
        field_type = user_state.user_editor.get_current_field_type()
        field_message = user_state.user_editor.get_current_field_message()
        if field_type == PHOTO_TYPE:
            await AdminMessageSender.send_form_text_field_message_query(update.callback_query,
                                                                        field_message, None)

        elif field_type == AUDIO_TYPE:
            await AdminMessageSender.send_form_text_field_message_query(update.callback_query,
                                                                        field_message, None)

        elif field_type == str:
            current_state = user_state.user_editor.get_current_field_state()

            if update.callback_query:
                await AdminMessageSender.send_form_text_field_message_query(update.callback_query, field_message,
                                                                            current_state)
            elif update.message:
                await AdminMessageSender.send_form_text_field_message_update(update, field_message, )
        elif field_type == bool:
            print("Handling boolean field")
            current_state = user_state.user_editor.get_current_field_state()
            if update.callback_query:
                await AdminMessageSender.send_form_boolean_field_message_query(update.callback_query, field_message,
                                                                               "Да" if current_state else "Нет")
            elif update.message:
                await AdminMessageSender.send_form_boolean_field_message_update(update, field_message,
                                                                                "Да" if current_state else "Нет")

    def handle_input(self, update: Update, field_type):

        user_id = get_user_id_by_update(update)
        user_state = self.get_user_state(user_id=user_id)

        if user_state.user_editor.get_editing_mode():
            if field_type == str:
                self.handle_text_field_input(update)
            elif field_type == bool:
                self.handle_boolean_field_input(update)

    def handle_text_field_input(self, update: Update):
        user_state = self.get_user_state(user_id=update.message.from_user.id)
        if user_state.user_editor.get_editing_mode():
            print("Handling text field input")
            # TODO: change to dict and add constants
            field_type = user_state.user_editor.get_current_field_type()
            if field_type == str:
                user_state.user_editor.add_editing_result(update.message.text)

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
        await MessageSender.delete_previous_buttons(update.callback_query)
        user_state.user_editor.enable_editing_mode(user_state.get_current_excursion())
        await self.handle_next_field(update, context)

    async def edit_point_fields(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_state = self.get_user_state(user_id=update.callback_query.from_user.id)
        await MessageSender.delete_previous_buttons(update.callback_query)
        point_id = int(update.callback_query.data.split("_")[-1])
        for point in user_state.get_current_excursion().get_points():
            if point.get_id() == point_id:
                user_state.user_editor.enable_editing_mode(point, point_id=point_id)
                await self.handle_next_field(update, context)
                return

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
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_next_field))
        self.application.add_handler(CallbackQueryHandler(self.add_point, pattern=f"^{ADD_POINT_CALLBACK}$"))
        self.application.add_handler(CallbackQueryHandler(self.edit_excursion, pattern=f"^{EDIT_EXCURSION_CALLBACK}"))
        self.application.add_handler(CallbackQueryHandler(self.edit_points, pattern=f"^{EDIT_POINTS_CALLBACK}$"))
        self.application.add_handler(
            CallbackQueryHandler(self.edit_point_fields, pattern=f"^{EDIT_POINT_FIELDS_CALLBACK}"))
        self.application.add_handler(CallbackQueryHandler(self.edit_point, pattern=f"^{EDIT_POINT_CALLBACK}"))

        self.application.run_polling()
