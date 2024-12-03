from telegram import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Update, InputMediaPhoto
from constants import *
from excursion import Excursion
from point import Point
from user_state import UserState


class MessageHandler:
    """Handles message formatting and sending."""

    @staticmethod
    async def send_intro_message(update) -> None:
        """Sends the introductory message explaining trial and paid versions."""
        keyboard = [
            [InlineKeyboardButton(VIEW_EXCURSIONS_BUTTON, callback_data=SHOW_EXCURSIONS_CALLBACK)]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"{WELCOME_MESSAGE}\n\n{INTRO_NO_ACCESS_MESSAGE}\n\nВыберите экскурсию из списка ниже:",
            reply_markup=reply_markup,
        )

    @staticmethod
    async def send_excursions_list(query: CallbackQuery, user_state: UserState, excursions: dict[str, Excursion]) -> None:
        keyboard = []

        for excursion_name, excursion_obj in excursions.items():
            button_text = excursion_name
            # Disable button for paid excursions if user doesn't have paid access
            callback_data = f"{CHOOSE_CALLBACK}{excursion_obj.get_id()}"
            if excursion_obj.is_paid_excursion() and not user_state.does_have_access(excursion_obj):
                button_text = f"{BLOCK_EMOJI} {excursion_name}"
                callback_data = DISABLED_CALLBACK
            elif excursion_obj.is_paid_excursion() and user_state.does_have_access(excursion_obj):
                button_text = f"{MONEY_SACK_EMOJI} {button_text}"
            if user_state.is_excursion_completed(excursion_obj):
                button_text = f"{CHECK_MARK_EMOJI} {button_text}"

            keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])

        keyboard.append([InlineKeyboardButton(SYNC_BUTTON, callback_data=SHOW_EXCURSIONS_CALLBACK)])
        reply_markup = InlineKeyboardMarkup(keyboard)

        if query.message:
            await query.message.reply_text(
                EXCURSIONS_LIST_MESSAGE,
                reply_markup=reply_markup
            )
        else:
            print("Error: query.message is None")

    @staticmethod
    async def send_excursion_start_message(query, excursion) -> None:
        """Sends the starting information for the excursion."""
        await query.answer(f"Вы выбрали {excursion.get_name()}. Начнем наш тур!")
        keyboard = [[InlineKeyboardButton(START_TOUR_BUTTON, callback_data=NEXT_POINT_CALLBACK)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.reply_text(
            f"Добро пожаловать в {excursion.get_name()}! {STAR_EMOJI}\n\n{EXCURSION_START_MESSAGE}",
            reply_markup=reply_markup,
        )

    @staticmethod
    async def send_error_message(query: CallbackQuery, error_message: str, is_alert: bool = False) -> None:
        """Sends the error message."""
        await query.answer(error_message, show_alert=is_alert)

    @staticmethod
    async def delete_previous_buttons(query):
        """Removes buttons from the previous message."""
        try:
            await query.message.edit_reply_markup(reply_markup=None)
        except Exception as e:
            print(f"Error deleting buttons: {e}")

    @staticmethod
    async def send_point_location_info(query, point) -> None:
        """Sends location details (photo, name, address) for the current point."""
        keyboard = [[InlineKeyboardButton(IM_HERE_BUTTON, callback_data=ARRIVED_CALLBACK)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if point.get_location_photo():
            with open(point.get_location_photo(), "rb") as photo:
                await query.message.reply_photo(
                    photo=photo,
                    caption=(
                        f"{LOCATION_PIN_EMOJI} *{point.get_name()}*\n"
                        f"{LOCATION_PIN_EMOJI} Адрес: *{point.get_address()}*"
                    ),
                    parse_mode="Markdown",
                    reply_markup=reply_markup,
                )
        else:
            await query.message.reply_text(
                f"Ваш следующий пункт назначения:\n\n"
                f"{LOCATION_PIN_EMOJI} *{point.get_name()}*\n"
                f"{LOCATION_PIN_EMOJI} Адрес: *{point.get_address()}*",
                parse_mode="Markdown",
                reply_markup=reply_markup,
            )

    @staticmethod
    async def send_part(query, point: Point, mode: str) -> None:
        """Sends the current part (introduction, middle, or conclusion) of a point."""
        photos = point.get_photos()  # Assumes this returns a list of photo file paths
        media_group = []

        if photos:
            for photo_path in photos:
                try:
                    with open(photo_path, "rb") as photo:
                        media_group.append(
                            InputMediaPhoto(photo)
                        )
                except FileNotFoundError:
                    await query.message.reply_text(f"Photo not found: {photo_path}")
                    return

            if media_group:
                await query.message.reply_media_group(media_group)

        if mode == AUDIO_MODE:
            audio_file = point.get_audio()
            if audio_file:
                with open(audio_file, "rb") as audio:
                    await query.message.reply_audio(audio=audio)
                    return
            await MessageHandler.send_error_message(query, AUDIO_IS_NOT_FOUND_ERROR)
        text_content = point.get_text()
        await query.message.reply_text(text_content)

    @staticmethod
    async def send_feedback_request(query: CallbackQuery) -> None:
        """Requests feedback from the user after completing an excursion."""
        keyboard = [
            [InlineKeyboardButton(f"{LIKE_EMOJI} {LOVED_IT_BUTTON}", callback_data=FEEDBACK_POSITIVE_CALLBACK)],
            [InlineKeyboardButton(f"{DISLIKE_EMOJI} {COULD_BE_BETTER_BUTTON}",
                                  callback_data=FEEDBACK_NEGATIVE_CALLBACK)],
            [InlineKeyboardButton(VIEW_EXCURSIONS_BUTTON, callback_data=SHOW_EXCURSIONS_CALLBACK)],
            [InlineKeyboardButton(CONNECT_TO_VOLK, url=MESSAGE_TO_VOLK_URL)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.reply_text(
            FEEDBACK_REQUEST_MESSAGE,
            reply_markup=reply_markup,
        )

    @staticmethod
    async def send_feedback_response(query: CallbackQuery) -> None:
        """Thanks the user for feedback."""
        keyboard = [[InlineKeyboardButton(BACK_TO_EXCURSIONS_BUTTON, callback_data=SHOW_EXCURSIONS_CALLBACK)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if query.data == FEEDBACK_POSITIVE_CALLBACK:
            await query.answer(POSITIVE_FEEDBACK_RESPONSE)
            await query.message.reply_text(POSITIVE_FEEDBACK_MESSAGE, reply_markup=reply_markup)
        elif query.data == FEEDBACK_NEGATIVE_CALLBACK:
            await query.answer(NEGATIVE_FEEDBACK_RESPONSE)
            await query.message.reply_text(NEGATIVE_FEEDBACK_MESSAGE, reply_markup=reply_markup)

    @staticmethod
    async def send_move_on_request(query: CallbackQuery) -> None:
        """Requests the user to confirm moving to the next point."""
        keyboard = [[InlineKeyboardButton(MOVE_ON_BUTTON, callback_data=NEXT_POINT_CALLBACK)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.reply_text(MOVE_ON_REQUEST_MESSAGE, reply_markup=reply_markup)

    @staticmethod
    async def send_transition_warning(update: Update) -> None:
        keyboard = [[InlineKeyboardButton(TRANSITION_CONFIRMATION_BUTTON, callback_data=SHOW_EXCURSIONS_CALLBACK)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(TRANSITION_WARNING_MESSAGE, reply_markup=reply_markup)
