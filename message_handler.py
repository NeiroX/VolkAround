from telegram import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from constants import *
from point import Point


class MessageHandler:
    """Handles message formatting and sending."""

    @staticmethod
    async def send_intro_message(update, has_paid_access: bool):
        """Sends the introductory message explaining trial and paid versions."""
        keyboard = [
            [InlineKeyboardButton("View Excursions", callback_data="show_excursions")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        access_text = (
            "You have access to all paid excursions and trial versions!"
            if has_paid_access
            else "You can enjoy a free trial excursions or buy others on [link]."
        )

        await update.message.reply_text(
            f"Hello! I am your Excursion Bot. I guide you through exciting tours with landmarks and stories!\n\n"
            f"{access_text}\n\n"
            "Click below to see the available excursions:",
            reply_markup=reply_markup,
        )

    @staticmethod
    async def send_excursion_start_message(query, excursion):
        """Sends the starting information for the current_excursion."""
        keyboard = [[InlineKeyboardButton("Start Tour", callback_data="next_point")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.reply_text(
            f"Welcome to the {excursion.get_name()} current_excursion!{STAR_EMOJI}\n\n"
            "Get ready for an exciting journey.",
            reply_markup=reply_markup,
        )

    @staticmethod
    async def send_point_location_info(query, point):
        """Sends location details (photo, name, address) for the current point."""
        keyboard = [[InlineKeyboardButton("I'm Here!", callback_data="arrived")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        # TODO: add emojis' unicode
        # Send location photo (if available), address, and name in a single message
        if point.get_location_photo():
            with open(point.get_location_photo(), "rb") as photo:
                await query.message.reply_photo(
                    photo=photo,
                    caption=(
                        f"{LOCATION_PIN_EMOJI} *{point.get_name()}*\n"
                        f"{LOCATION_PIN_EMOJI} Address: *{point.get_address()}*",
                    ),
                    parse_mode="Markdown",
                    reply_markup=reply_markup,
                )
        else:
            await query.message.reply_text(
                f"Your next destination is:\n\n"
                f"{LOCATION_PIN_EMOJI} *{point.get_name()}*\n"
                f"{LOCATION_PIN_EMOJI} Address: *{point.get_address()}*",
                parse_mode="Markdown",
                reply_markup=reply_markup,
            )

    @staticmethod
    async def send_part(query, point: Point, mode: str):
        """Sends the current part (introduction, middle, or conclusion) of a point."""
        print(point == None)
        if mode == "audio":
            audio_file = point.get_audio()
            if audio_file:
                with open(audio_file, "rb") as audio:
                    await query.message.reply_audio(audio=audio)
            else:
                await query.message.reply_text("Sorry, audio is not available for this point.")
        else:
            text_content = point.get_text()
            await query.message.reply_text(text_content)

    @staticmethod
    async def send_feedback_request(update, excursion_name: str):
        """Requests feedback from the user after completing an current_excursion."""
        await update.callback_query.message.reply_text(
            f"Congratulations on completing the {excursion_name} current_excursion! {CONGRATULATIONS_EMOJI}\n\n"
            "We hope you enjoyed your journey. Please leave your feedback to help us improve.",
            reply_markup=None,  # No inline keyboard for feedback
        )

    @staticmethod
    async def send_feedback_response(query: CallbackQuery):
        """Thanks the user for feedback."""
        keyboard = [
            [InlineKeyboardButton("🔙 Back to excursions", callback_data="show_excursions")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        if query.data == "feedback_positive":
            await query.answer(f"Thank you for your positive feedback! {SMILING_FACE_EMOJI}")
            await query.message.reply_text("We're glad you enjoyed it!", reply_markup=reply_markup)
        elif query.data == "feedback_negative":
            await query.answer(f"Thank you for your feedback. We'll work to improve! {FOLDED_HANDS_EMOJI}")
            await query.message.reply_text("Sorry it didn’t meet your expectations. We’ll strive to do better.",
                                           reply_markup=reply_markup)
