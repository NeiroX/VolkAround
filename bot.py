from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from message_handler import MessageHandler  # Assuming MessageHandler is in a separate file
from excursion import Excursion
from point import Point
from user_state import UserState
from typing import List
from constants import *


class Bot:
    """The main bot class coordinating everything."""
    #TODO: set current excursion to None when the user returns to list of excursions

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
        user_state.current_excursion = None  # Reset any ongoing current_excursion for a fresh start

        # Explain the available versions
        await MessageHandler.send_intro_message(update, user_state.has_paid_access)

    async def show_excursions(self, update, context):
        """Displays the list of available excursions based on user access."""
        query = update.callback_query
        user_id = query.from_user.id
        user_state = self.get_user_state(user_id)
        await self.delete_previous_buttons(query)

        keyboard = []

        for excursion in self.excursions:
            button_text = excursion.get_name()
            # Disable button for paid excursions if user doesn't have paid access
            if excursion.is_paid_excursion() and not user_state.does_have_access(excursion):
                button_text = f"{BLOCK_EMOJI} {excursion.get_name()}"
                callback_data = "disabled"
            else:
                if user_state.is_excursion_completed(excursion):
                    button_text = f"{CHECK_MARK_EMOJI} {excursion.get_name()}"
                callback_data = f"choose_{excursion.get_name()}"

            keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.reply_text(
            "Here are the available excursions. Select one to join:",
            reply_markup=reply_markup
        )
        await query.answer()  # Acknowledge the callback query to avoid "loading" state.

    async def disabled_button_handler(self, update, context):
        """Handles clicks on disabled buttons."""
        query = update.callback_query
        await query.answer("You don't have access to this current_excursion.", show_alert=True)

    async def delete_previous_buttons(self, query):
        """Removes buttons from the previous message."""
        try:
            await query.message.edit_reply_markup(reply_markup=None)
        except Exception as e:
            print(f"Error deleting buttons: {e}")

    async def choose_excursion(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles the selection of an current_excursion."""
        query = update.callback_query
        await self.delete_previous_buttons(query)

        user_id = query.from_user.id
        user_state = self.get_user_state(user_id)

        # Parse callback data to extract the action and current_excursion name
        data = query.data.split("_", 1)
        print(data[1])
        if len(data) < 2:
            await query.answer("Invalid selection. Please try again.")
            return

        action, excursion_name = data
        if action != "choose":
            await query.answer("Invalid action.")
            return

        # Find the chosen current_excursion from the list of excursions
        chosen_excursion = next((e for e in self.excursions if e.get_name() == excursion_name), None)

        if chosen_excursion is None:
            await query.answer("Sorry, this current_excursion does not exist.")
            return

        # If it's a paid current_excursion and the user doesn't have paid access
        if chosen_excursion.is_paid_excursion() and not user_state.has_paid_access:
            await query.answer("This current_excursion is paid. You need a paid subscription to join.")
            return

        # Set the user's current current_excursion and start it
        user_state.current_excursion = chosen_excursion
        await query.answer(f"You've chosen {excursion_name}. Let's start your tour!")
        await self.start_excursion(update, chosen_excursion)

    async def start_excursion(self, update: Update, excursion: Excursion):
        """Starts the selected current_excursion."""
        query = update.callback_query
        await self.delete_previous_buttons(query)

        user_id = query.from_user.id
        user_state = self.get_user_state(user_id)

        user_state.point_index = 0  # Reset the point index
        point = excursion.get_point()  # Get the information for the current point

        # Send introduction information about the current_excursion
        await MessageHandler.send_excursion_start_message(query, excursion)
        # await self.send_point_information(update, point)

    async def send_point_information(self, update: Update, point: Point):
        """Send information about the current point."""
        query = update.callback_query
        await self.delete_previous_buttons(query)

        user_id = query.from_user.id
        user_state = self.get_user_state(user_id)

        # Send location details (photo, name, address)
        await MessageHandler.send_point_location_info(query, point)

        # Ask the user if they've finished on this point and want to move on
        # keyboard = [
        #     [InlineKeyboardButton("Yes, I'm ready to move on!", callback_data="next_point")]
        # ]
        # reply_markup = InlineKeyboardMarkup(keyboard)
        # await query.message.reply_text(
        #     "Are you finished with this location and ready to move on?",
        #     reply_markup=reply_markup
        # )

    async def handle_arrival(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles the 'I'm Here!' button press."""
        query = update.callback_query
        await self.delete_previous_buttons(query)

        user_id = query.from_user.id
        user_state = self.get_user_state(user_id)

        excursion = user_state.current_excursion
        point = excursion.get_point()  # Get the current point information

        # Check if the user is in text or audio mode
        await MessageHandler.send_part(query, point, user_state.mode)

        # Ask the user if they are ready to move on to the next point
        keyboard = [
            [InlineKeyboardButton("Yes, I'm ready to move on!", callback_data="next_point")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            "Are you finished with this location and ready to move on?",
            reply_markup=reply_markup
        )

    async def handle_move_on(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles the 'Move On' button press."""
        query = update.callback_query
        await self.delete_previous_buttons(query)

        user_id = query.from_user.id
        user_state = self.get_user_state(user_id)

        excursion = user_state.current_excursion

        # Move to the next point in the current_excursion
        if excursion.move_to_next_point():
            next_point = excursion.get_point()  # Get the next point
            await self.send_point_information(update, next_point)
        else:
            await self.complete_excursion(update, context)

    async def change_mode(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Allow the user to change the mode (audio/text) during the current_excursion."""
        user_id = update.message.from_user.id
        user_state = self.get_user_state(user_id)

        # Toggle the mode between 'audio' and 'text'
        user_state.mode = "audio" if user_state.mode == "text" else "text"
        await update.message.reply_text(
            f"Mode changed to {user_state.mode}. Now receiving {user_state.mode} information.")

        # Send the current point's information in the new mode
        excursion = user_state.current_excursion
        point = excursion.get_point()  # Get the point info for the current point
        await MessageHandler.send_part(update.callback_query, point, user_state.mode)

    async def complete_excursion(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles the completion of the current_excursion."""
        query = update.callback_query
        await self.delete_previous_buttons(query)

        user_id = query.from_user.id
        user_state = self.get_user_state(user_id)

        # Notify user of completion
        excursion_name = user_state.current_excursion.get_name()
        user_state.add_completed_excursion(user_state.current_excursion)
        await query.message.reply_text(f"Congratulations! You've completed the {excursion_name} current_excursion!")

        # Prepare feedback buttons
        keyboard = [
            [InlineKeyboardButton(f"{LIKE_EMOJI} Loved it!", callback_data="feedback_positive")],
            [InlineKeyboardButton(f"{DISLIKE_EMOJI} Could be better", callback_data="feedback_negative")],
            [InlineKeyboardButton("View Excursions", callback_data="show_excursions")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Prompt for feedback
        await query.message.reply_text(
            "We’d love to hear your thoughts! How was your experience?",
            reply_markup=reply_markup
        )
        await query.answer()  # Acknowledge the callback query

    async def give_feedback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles feedback submission after an excursion."""
        query = update.callback_query
        await self.delete_previous_buttons(query)

        user_id = query.from_user.id
        user_state = self.get_user_state(user_id)

        # Handle button presses
        if query.data == "feedback_positive":
            user_state.current_excursion.like()
        else:
            user_state.current_excursion.dislike()
        await MessageHandler.send_feedback_response(query)

    def run(self):
        """Start the bot."""
        self.application.add_handler(CommandHandler(START_COMMAND, self.start))
        self.application.add_handler(CommandHandler(CHANGE_MODE_COMMAND, self.change_mode))
        self.application.add_handler(CallbackQueryHandler(self.show_excursions, pattern="^show_excursions$"))
        self.application.add_handler(CallbackQueryHandler(self.disabled_button_handler, pattern="^disabled$"))
        self.application.add_handler(CallbackQueryHandler(self.choose_excursion, pattern="^choose_"))
        self.application.add_handler(CallbackQueryHandler(self.handle_arrival, pattern="^arrived$"))
        self.application.add_handler(CallbackQueryHandler(self.handle_move_on, pattern="^next_point$"))
        self.application.add_handler(CallbackQueryHandler(self.complete_excursion, pattern="^finish_"))
        self.application.add_handler(CallbackQueryHandler(self.give_feedback, pattern="^feedback_"))
        self.application.run_polling()
