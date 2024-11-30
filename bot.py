from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

from message_handler import MessageHandler  # Assuming MessageHandler is in a separate file
from excursion import Excursion
from point import Point
from user_state import UserState
from typing import List
from constants import *


class Bot:
    """The main bot class coordinating everything."""

    def __init__(self, token, excursions: List[Excursion]):
        self.application = Application.builder().token(token).build()
        self.user_states = {}  # Keeps track of UserState objects for each user
        self.excursions = excursions  # List of all available excursions

    def get_user_state(self, user_id: int, username: str = None):
        """Gets or creates the user state for the given user."""
        if user_id not in self.user_states:
            self.user_states[user_id] = UserState(username=username, user_id=user_id)
        return self.user_states[user_id]

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles the /start command."""
        user_state = self.get_user_state(update.message.from_user.id, update.message.from_user.username)
        user_state.reset_current_excursion()  # Reset any ongoing current_excursion for a fresh start

        # Explain the available versions
        await MessageHandler.send_intro_message(update)

    async def show_excursions(self, update, context):
        """Displays the list of available excursions based on user access."""
        query = update.callback_query
        user_id = query.from_user.id
        user_state = self.get_user_state(user_id)
        user_state.reset_current_excursion()
        await MessageHandler.delete_previous_buttons(query)
        await MessageHandler.send_excursions_list(query, user_state, self.excursions)
        await query.answer()  # Acknowledge the callback query to avoid "loading" state.

    @staticmethod
    async def disabled_button_handler(update, context):
        """Handles clicks on disabled buttons."""
        query = update.callback_query
        await MessageHandler.send_error_message(query, ACCESS_ERROR, is_alert=True)

    async def choose_excursion(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles the selection of an excursion."""
        query = update.callback_query
        await MessageHandler.delete_previous_buttons(query)

        user_id = query.from_user.id
        user_state = self.get_user_state(user_id)
        # Parse callback data to extract the action and current_excursion name
        data = query.data.split("_", 1)
        if len(data) < 2:
            await MessageHandler.send_error_message(query, INVALID_SELECTION_ERROR)
            return

        action, excursion_name = data
        if action != "choose":
            await MessageHandler.send_error_message(query, INVALID_ACTION_ERROR)
            return

        # Find the chosen current_excursion from the list of excursions
        chosen_excursion = next((e for e in self.excursions if e.get_name() == excursion_name), None)
        print("Chosen excursion: " + chosen_excursion.get_name())
        if chosen_excursion is None:
            await MessageHandler.send_error_message(query, EXCURSION_DOES_NOT_EXISTS_ERROR)
            return

        # If it's a paid current_excursion and the user doesn't have paid access
        if chosen_excursion.is_paid_excursion() and not user_state.has_paid_access:
            await MessageHandler.send_error_message(query, PAID_EXCURSION_ERROR)
            return

        # Set the user's current current_excursion and start it
        user_state.set_excursion(chosen_excursion)
        await self.start_excursion(update, chosen_excursion)

    async def start_excursion(self, update: Update, excursion: Excursion):
        """Starts the selected current_excursion."""

        query = update.callback_query
        # await MessageHandler.delete_previous_buttons(query)

        user_id = query.from_user.id
        user_state = self.get_user_state(user_id)

        user_state.point_index = 0  # Reset the point index
        point = user_state.get_point()  # Get the information for the current point

        # Send introduction information about the current_excursion
        await MessageHandler.send_excursion_start_message(query, excursion)
        # await self.send_point_information(update, point)

    @staticmethod
    async def send_point_information(update: Update, point: Point):
        """Send information about the current point."""
        query = update.callback_query
        await MessageHandler.delete_previous_buttons(query)

        # Send location details (photo, name, address)
        await MessageHandler.send_point_location_info(query, point)

    async def handle_arrival(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles the 'I'm Here!' button press."""
        query = update.callback_query
        await MessageHandler.delete_previous_buttons(query)

        user_id = query.from_user.id
        user_state = self.get_user_state(user_id)

        point = user_state.get_point()  # Get the current point information

        # Check if the user is in text or audio mode
        await MessageHandler.send_part(query, point, user_state.mode)

        # Ask the user if they are ready to move on to the next point
        await MessageHandler.send_move_on_request(query)

    async def handle_move_on(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles the 'Move On' button press."""
        query = update.callback_query
        await MessageHandler.delete_previous_buttons(query)

        user_id = query.from_user.id
        user_state = self.get_user_state(user_id)
        user_state.excursion_next_step()

        # Move to the next point in the excursion
        next_point = user_state.get_point()  # Get the next point
        if next_point is not None:
            print("Move to the next point")
            await self.send_point_information(update, next_point)
        else:
            await self.complete_excursion(update, context)

    async def change_mode(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Allow the user to change the mode (audio/text) during the current_excursion."""
        user_id = update.message.from_user.id
        user_state = self.get_user_state(user_id)

        # Toggle the mode between 'audio' and 'text'
        user_state.change_mode()
        await update.message.reply_text(
            f"Режим изменен на {user_state.get_mode()}.")

        # Send the current point's information in the new mode
        point = user_state.get_point()  # Get the point info for the current point
        await MessageHandler.send_part(update.callback_query, point, user_state.mode)

    async def complete_excursion(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles the completion of the current_excursion."""
        query = update.callback_query
        await MessageHandler.delete_previous_buttons(query)

        user_id = query.from_user.id
        user_state = self.get_user_state(user_id)

        # Notify user of completion
        excursion_name = user_state.get_current_excursion().get_name()
        user_state.add_completed_excursion(user_state.get_current_excursion())
        await query.message.reply_text(
            f"Поздравляю! Вы завершили {excursion_name}! {CONGRATULATIONS_EMOJI}")

        # Prepare feedback buttons
        await MessageHandler.send_feedback_request(query)
        await query.answer()  # Acknowledge the callback query

    async def give_feedback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles feedback submission after an excursion."""
        query = update.callback_query
        await MessageHandler.delete_previous_buttons(query)

        user_id = query.from_user.id
        user_state = self.get_user_state(user_id)

        # Handle button presses
        if query.data == FEEDBACK_POSITIVE_CALLBACK:
            user_state.get_current_excursion().like()
        else:
            user_state.get_current_excursion().dislike()
        # Save updated info
        user_state.get_current_excursion().save_info()
        await MessageHandler.send_feedback_response(query)

    @staticmethod
    async def move_to_excursions_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles movement to excursion list"""
        await MessageHandler.send_transition_warning(update)

    def run(self):
        """Start the bot."""
        self.application.add_handler(CommandHandler(START_COMMAND, self.start))
        self.application.add_handler(CommandHandler(CHANGE_MODE_COMMAND, self.change_mode))
        self.application.add_handler(CommandHandler(VIEW_EXCURSIONS_COMMAND, self.move_to_excursions_list))
        self.application.add_handler(CallbackQueryHandler(self.show_excursions, pattern=f"^{SHOW_EXCURSIONS_CALLBACK}"))
        self.application.add_handler(
            CallbackQueryHandler(self.disabled_button_handler, pattern=f"^{DISABLED_CALLBACK}$"))
        self.application.add_handler(CallbackQueryHandler(self.choose_excursion, pattern=f"^{CHOOSE_CALLBACK}"))
        self.application.add_handler(CallbackQueryHandler(self.handle_arrival, pattern=f"^{ARRIVED_CALLBACK}$"))
        self.application.add_handler(CallbackQueryHandler(self.handle_move_on, pattern=f"^{NEXT_POINT_CALLBACK}$"))
        self.application.add_handler(CallbackQueryHandler(self.complete_excursion, pattern=f"^{FINISH_CALLBACK}"))
        self.application.add_handler(CallbackQueryHandler(self.give_feedback, pattern=f"^{FEEDBACK_CALLBACK}"))
        self.application.run_polling()
