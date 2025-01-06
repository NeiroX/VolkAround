from io import BytesIO

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Update, InputMediaPhoto, InputMediaAudio
from telegram.ext import CallbackContext

from src.components.user.user_state import UserState
from src.constants import *
from src.components.excursion.point.point import Point
from src.components.excursion.point.information_part import InformationPart

from src.components.excursion.excursion import Excursion
from typing import Dict, List, Union

from src.data.s3bucket import s3_fetch_file


class MessageSender:
    """Handles message formatting and sending."""

    @staticmethod
    async def send_intro_message(update) -> None:
        """Sends the introductory message explaining trial and paid versions."""
        keyboard = [
            [InlineKeyboardButton(VIEW_EXCURSIONS_BUTTON, callback_data=SHOW_EXCURSIONS_CALLBACK)]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"{WELCOME_MESSAGE}\n\n{INTRO_ACCESS_MESSAGE}\n\nВыберите экскурсию из списка ниже:",
            reply_markup=reply_markup,
        )

    @staticmethod
    async def send_excursions_list(query: CallbackQuery, user_state: UserState,
                                   excursions: Dict[str, Excursion]) -> None:
        keyboard = []

        for excursion_name, excursion_obj in excursions.items():
            if excursion_obj.is_draft_excursion() and not user_state.does_have_admin_access():
                continue
            button_text = excursion_name
            # Disable button for paid excursions if user doesn't have paid access
            callback_data = f"{CHOOSE_CALLBACK}{excursion_obj.get_id()}"
            if excursion_obj.is_paid_excursion() and not user_state.does_have_access(excursion_obj):
                button_text = f"{BLOCK_EMOJI} {excursion_name}"
                callback_data = DISABLED_CALLBACK
            elif excursion_obj.is_paid_excursion() and user_state.does_have_access(excursion_obj):
                button_text = f"{MONEY_SACK_EMOJI} {button_text}"
            if excursion_obj.is_completed(user_state.get_user_id()):
                button_text = f"{CHECK_MARK_EMOJI} {button_text}"
            if user_state.does_have_admin_access():
                if excursion_obj.is_draft_excursion():
                    button_text = f"{DRAFT_EMOJI} {button_text}"
                else:
                    button_text = f"{PUBLISHED_EMOJI} {button_text}"

            keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])

        keyboard.append([InlineKeyboardButton(SYNC_BUTTON, callback_data=SHOW_EXCURSIONS_CALLBACK)])
        if user_state.does_have_admin_access():
            keyboard.append([InlineKeyboardButton(ADD_EXCURSION_BUTTON, callback_data=ADD_EXCURSION_CALLBACK)])
            if excursions:
                keyboard.append(
                    [InlineKeyboardButton(DELETE_ALL_COLLECTIONS_BUTTON, callback_data=DELETE_ALL_COLLECTIONS_CALLBACK)])

        reply_markup = InlineKeyboardMarkup(keyboard)

        if query.message:
            await query.message.reply_text(
                EXCURSIONS_LIST_MESSAGE,
                reply_markup=reply_markup
            )
        else:
            print("Error: query.message is None")

    @staticmethod
    async def send_excursion_start_message(query: CallbackQuery, excursion: Excursion, is_admin: bool) -> None:
        """Sends the starting information for the components."""
        await query.answer(f"Вы выбрали {excursion.get_name()}. Начнем наш тур!")
        keyboard = [[InlineKeyboardButton(START_TOUR_BUTTON, callback_data=NEXT_POINT_CALLBACK)]]
        if is_admin:
            points_number = len(excursion.get_points())
            keyboard.append([InlineKeyboardButton(EXCURSION_STATS_BUTTON, callback_data=EXCURSION_STATS_CALLBACK)])
            keyboard.append([InlineKeyboardButton(EXCURSION_SUMMARY_BUTTON, callback_data=EXCURSION_SUMMARY_CALLBACK)])
            keyboard.append([InlineKeyboardButton(EDIT_EXCURSION_BUTTON, callback_data=EDIT_EXCURSION_CALLBACK)])
            keyboard.append([InlineKeyboardButton(PUBLISH_EXCURSION_BUTTON,
                                                  callback_data=f"{PUBLISH_CHOSEN_EXCURSION_CALLBACK}"
                                                                f"{excursion.get_id()}")])
            keyboard.append([InlineKeyboardButton(EDIT_POINTS_BUTTON, callback_data=EDIT_POINTS_CALLBACK)])
            if points_number > 1:
                keyboard.append([InlineKeyboardButton(CHANGE_POINTS_ORDER_BUTTON,
                                                      callback_data=CHANGE_POINTS_ORDER_CALLBACK)])
            keyboard.append([InlineKeyboardButton(DELETE_EXCURSION_BUTTON, callback_data=DELETE_EXCURSION_CALLBACK)])
        keyboard.append([InlineKeyboardButton(BACK_TO_EXCURSIONS_BUTTON, callback_data=SHOW_EXCURSIONS_CALLBACK)])
        reply_markup = InlineKeyboardMarkup(keyboard)
        excursion_duration = excursion.get_duration()
        message = f"Добро пожаловать в {excursion.get_name()}! {STAR_EMOJI}\n\n{EXCURSION_START_MESSAGE}"
        if excursion_duration > 0:
            message += f"\n\n{TIME_EMOJI}Длительность экскурсии примерно: {excursion.get_duration()} минут"
        await query.message.reply_text(
            message,
            reply_markup=reply_markup,
        )

    @staticmethod
    async def send_error_message(query: CallbackQuery, error_message: str, is_alert: bool = False,
                                 is_admin: bool = False) -> None:
        """Sends the error message."""
        if is_admin and not is_admin and query.message:
            keyboard = [[InlineKeyboardButton(WRITE_TO_DEVELOPER_BUTTON, url=MESSAGE_TO_DEVELOPER_URL)]]
            reply_markup = InlineKeyboardMarkup(
                keyboard)
            await query.message.reply_text(error_message, parse_mode="Markdown",
                                           reply_markup=reply_markup)
        elif query:
            await query.answer(error_message, show_alert=is_alert)
        else:
            print("Error: query.message is None")

    @staticmethod
    async def delete_previous_buttons(query):
        """Removes buttons from the previous message."""
        try:
            await query.message.edit_reply_markup(reply_markup=None)
        except Exception as e:
            print(f"Error deleting buttons: {e}")

    @staticmethod
    async def send_point_location_info(query, point) -> None:
        """Sends location details (photo, name, address) for the current part."""
        keyboard = [[InlineKeyboardButton(IM_HERE_BUTTON, callback_data=ARRIVED_CALLBACK)]]
        point_location_link = point.get_location_link()
        if point_location_link:
            keyboard.append([InlineKeyboardButton(OPEN_LOCATION_IN_GOOGLE_MAPS, url=point_location_link)])
        reply_markup = InlineKeyboardMarkup(keyboard)

        if point.get_location_photo():
            try:
                # Fetch the photo from S3
                file_name = point.get_location_photo()  # Assume this is the S3 object key
                print(file_name)
                s3_file_obj = s3_fetch_file(file_name)

                if s3_file_obj:
                    # Read the file content into a BytesIO object
                    s3_file_obj.seek(0)

                    await query.message.reply_photo(
                        photo=s3_file_obj,
                        caption=(
                            f"{LOCATION_PIN_EMOJI} *{point.get_name()}*\n"
                            f"{LOCATION_PIN_EMOJI} Адрес: *{point.get_address()}*"
                        ),
                        parse_mode="Markdown",
                        reply_markup=reply_markup,
                    )
                else:
                    await query.message.reply_text("Ошибка: Фотография не найдена в S3.")
            except Exception as e:
                print(f"Error fetching photo from S3: {e}")
                await query.message.reply_text("Произошла ошибка при загрузке фотографии.")
        else:
            await query.message.reply_text(
                f"Ваш следующий пункт назначения:\n\n"
                f"{LOCATION_PIN_EMOJI} *{point.get_name()}*\n"
                f"{LOCATION_PIN_EMOJI} Адрес: *{point.get_address()}*",
                parse_mode="Markdown",
                reply_markup=reply_markup,
            )

    @staticmethod
    async def send_media_group(
            sender: Union[Update, CallbackQuery],
            files_paths: List[str] | None,
            is_photo: bool
    ) -> None:
        """Sends a group of media files (photos or audio) using URLs from S3."""
        if files_paths and sender:
            media_group = []

            for file_url in files_paths:
                print(f"Preparing media: {file_url}")
                try:
                    s3_file_obj = s3_fetch_file(file_url)

                    if not isinstance(s3_file_obj, BytesIO):
                        raise ValueError("s3_fetch_file did not return a BytesIO object.")
                    # Reset the BytesIO pointer to the beginning
                    s3_file_obj.seek(0)
                    # Create the appropriate media element (photo or audio)
                    new_media_element = (
                        InputMediaPhoto(media=s3_file_obj) if is_photo else InputMediaAudio(media=s3_file_obj)
                    )
                    print(f"Prepared media element: {new_media_element}")
                    media_group.append(new_media_element)
                except Exception as e:
                    # Handle any issues with creating media elements
                    print(f"Error processing media: {e}")
                    if hasattr(sender, "message") and sender.message:
                        await sender.message.reply_text(f"Ошибка загрузки медиа: {file_url}")
                    return

            if media_group:
                try:
                    await sender.message.reply_media_group(media=media_group)
                except Exception as e:
                    print(f"Failed to send media group: {e}")
                    if hasattr(sender, "message") and sender.message:
                        await sender.message.reply_text("Ошибка отправки медиа.")

    @staticmethod
    async def send_part(query: CallbackQuery, part: InformationPart | Point, mode: str) -> None:
        """Sends the current part (introduction, middle, or conclusion) of a part."""
        photos = part.get_photos()  # Assumes this returns a list of photo file paths
        media_group = []

        await MessageSender.send_media_group(query, part.get_photos(), is_photo=True)
        if mode == AUDIO_MODE:
            audio_files = part.get_audio()
            try:
                await MessageSender.send_media_group(query, audio_files, is_photo=False)
                if part.get_link():
                    await query.message.reply_text(part.get_link())
            except Exception as e:
                await MessageSender.send_error_message(query, AUDIO_IS_NOT_FOUND_ERROR)
        text_content = part.get_text()
        if part.get_link():
            text_content = f"{text_content}\n{LINK_EMOJI} {part.get_link()}"
        await query.message.reply_text(text_content)

    @staticmethod
    async def send_feedback_request(query: CallbackQuery) -> None:
        """Requests feedback from the user after completing a components."""
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
    async def send_move_on_request(query: CallbackQuery, point: Point, user_id: int) -> None:
        """Requests the user to confirm moving to the next part."""
        keyboard = [[InlineKeyboardButton(MOVE_ON_BUTTON, callback_data=NEXT_POINT_CALLBACK)]]

        if point.extra_information_points:
            extra_information_points = point.get_extra_information_points()
            for num, elem in enumerate(extra_information_points):
                print("Send move on request")
                print(num, elem.get_name())
                button_text = elem.get_name()
                if elem.is_completed(user_id):
                    button_text = f"{CHECK_MARK_EMOJI} {button_text}"
                keyboard.append([InlineKeyboardButton(button_text, callback_data=EXTRA_PART_CALLBACK + str(num))])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(MOVE_ON_REQUEST_MESSAGE, reply_markup=reply_markup)

    @staticmethod
    async def send_transition_warning(update: Update) -> None:
        keyboard = [[InlineKeyboardButton(TRANSITION_CONFIRMATION_BUTTON, callback_data=SHOW_EXCURSIONS_CALLBACK)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(TRANSITION_WARNING_MESSAGE, reply_markup=reply_markup)
