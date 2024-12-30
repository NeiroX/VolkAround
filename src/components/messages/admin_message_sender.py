from telegram import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Update, InputMediaPhoto
from typing import Dict, List

from src.components.excursion.excursion import Excursion
from src.components.excursion.point.information_part import InformationPart
from src.components.excursion.point.point import Point
from src.components.messages.message_sender import MessageSender
from src.constants import *


class AdminMessageSender:

    @staticmethod
    def get_message_sender(update: Update):
        if update.message:
            return update
        if update.callback_query:
            return update.callback_query

    @staticmethod
    async def send_success_message(update: Update, return_button: InlineKeyboardButton = None,
                                   previous_menu_button: InlineKeyboardButton = None) -> None:
        keyboard = list()
        print("Return button: ", return_button)
        if return_button:
            keyboard.append([return_button])
        if previous_menu_button:
            keyboard.append([previous_menu_button])
        keyboard.append([InlineKeyboardButton(BACK_TO_EXCURSIONS_BUTTON, callback_data=SHOW_EXCURSIONS_CALLBACK)])
        reply_markup = InlineKeyboardMarkup(keyboard)
        if update.callback_query:
            await update.callback_query.message.reply_text(ACTION_COMPLETED_SUCCESSFULLY_MESSAGE,
                                                           reply_markup=reply_markup)
        elif update.message:
            await update.message.reply_text(ACTION_COMPLETED_SUCCESSFULLY_MESSAGE, reply_markup=reply_markup)
        else:
            print("Error: query is None")

    @staticmethod
    async def send_current_state(update: Update, field_current_state: str,
                                 photos: List[str] = None,
                                 audio_paths: List[str] = None) -> None:
        sender = AdminMessageSender.get_message_sender(update)
        await sender.message.reply_text(f"{CURRENT_FIELD_VALUE}\n{field_current_state}")
        if photos:
            await MessageSender.send_media_group(sender, photos, is_photo=True)
        elif audio_paths:
            await MessageSender.send_media_group(sender, audio_paths, is_photo=False)

    @staticmethod
    async def send_form_text_field_message(update: Update, field_message: str,
                                           field_current_state: str = None, skip_button: bool = True) -> None:
        await AdminMessageSender.send_current_state(update, field_current_state)
        sender = AdminMessageSender.get_message_sender(update)
        if sender:
            if skip_button:
                keyboard = [[InlineKeyboardButton(SKIP_FIELD_BUTTON, callback_data=SKIP_FIELD_CALLBACK)]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await sender.message.reply_text(field_message, reply_markup=reply_markup)
            else:
                await sender.message.reply_text(field_message)

    @staticmethod
    async def send_excursion_summary_message(update: Update, excursion: Excursion) -> None:
        sender = AdminMessageSender.get_message_sender(update)
        if excursion and sender:
            message = (f"Текущая экскурсия: {excursion.get_name()}\n"
                       f"Опубликована? {"Нет" if excursion.is_draft_excursion() else "Да"}\n"
                       f"Платная экскурсия? {"Нет" if not excursion.is_paid_excursion() else "Да"}\n\n"
                       f"Точки и их подтемы:\n")

            for index, point in enumerate(excursion.get_points(), start=1):
                message += f"{index}. {point.get_name()}\n"
                for extra_point in point.get_extra_information_points():
                    message += f"---{extra_point.get_name()}\n"
                message += "\n"
            keyboard = [[InlineKeyboardButton(BACK_TO_EXCURSIONS_BUTTON, callback_data=SHOW_EXCURSIONS_CALLBACK)]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await sender.message.reply_text(message, reply_markup=reply_markup)

    @staticmethod
    async def send_excursion_stats(update: Update, excursion: Excursion) -> None:
        sender = AdminMessageSender.get_message_sender(update)
        if excursion and sender:
            message = (f"Текущая экскурсия: {excursion.get_name()}\n"
                       f"{PERSON_EMOJI} Количество прошедших экскурсию: {excursion.get_visitors_number()}\n"
                       f"{LIKE_EMOJI} Количество лайков: {excursion.get_likes_number()}\n"
                       f"{DISLIKE_EMOJI} Количество дизлайков: {excursion.get_dislikes_number()}\n")
            keyboard = [[InlineKeyboardButton(BACK_TO_EXCURSIONS_BUTTON, callback_data=SHOW_EXCURSIONS_CALLBACK)]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await sender.message.reply_text(message, reply_markup=reply_markup)

    @staticmethod
    async def send_form_photo_field_message(update: Update, field_message: str,
                                            field_current_state: str = None,
                                            current_photos: List[str] = None, one_photo: bool = False) -> None:
        await AdminMessageSender.send_current_state(update, field_current_state, photos=current_photos)
        sender = AdminMessageSender.get_message_sender(update)
        if sender:
            keyboard = [[InlineKeyboardButton(SKIP_FIELD_BUTTON, callback_data=SKIP_FIELD_CALLBACK)]]
            if not one_photo:
                keyboard.append([InlineKeyboardButton(DISABLE_SENDING_FILES_BUTTON,
                                                      callback_data=DISABLE_SENDING_FILES_CALLBACK)])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await sender.message.reply_text(field_message, reply_markup=reply_markup)

    @staticmethod
    async def send_form_audio_field_message(update: Update, field_message: str,
                                            field_current_state: str = None,
                                            current_audios: List[str] = None) -> None:
        await AdminMessageSender.send_current_state(update, field_current_state, audio_paths=current_audios)
        sender = AdminMessageSender.get_message_sender(update)
        if sender:
            keyboard = [[InlineKeyboardButton(SKIP_FIELD_BUTTON, callback_data=SKIP_FIELD_CALLBACK)],
                        [InlineKeyboardButton(DISABLE_SENDING_FILES_BUTTON,
                                              callback_data=DISABLE_SENDING_FILES_CALLBACK)]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await sender.message.reply_text(field_message, reply_markup=reply_markup)

    @staticmethod
    async def send_form_boolean_field_message(update: Update, field_message: str,
                                              field_current_state) -> None:
        await AdminMessageSender.send_current_state(update, field_current_state)
        sender = AdminMessageSender.get_message_sender(update)
        if sender:
            keyboard = [[InlineKeyboardButton(YES_BUTTON, callback_data=BOOLEAN_FIELD_CALLBACK + "yes"),
                         InlineKeyboardButton(NO_BUTTON, callback_data=BOOLEAN_FIELD_CALLBACK + "no")]]
            keyboard_markup = InlineKeyboardMarkup(keyboard)
            await sender.message.reply_text(
                field_message,
                reply_markup=keyboard_markup,
            )

    @staticmethod
    async def send_points_list(query: CallbackQuery, points_list: List[Point]) -> None:
        if query:
            keyboard = list()
            for point in points_list:
                keyboard.append(
                    [InlineKeyboardButton(f"{LOCATION_PIN_EMOJI}{point.get_name()}",
                                          callback_data=f"{EDIT_POINT_CALLBACK}{point.get_id()}")])
            keyboard.append([InlineKeyboardButton(ADD_POINT_BUTTON, callback_data=ADD_POINT_CALLBACK)])
            keyboard_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text(
                EDIT_POINTS_MESSAGE,
                reply_markup=keyboard_markup,
            )

    @staticmethod
    async def send_point_edit_message(query: CallbackQuery,
                                      point: Point | InformationPart, is_extra_point: bool = False,
                                      point_id: int = None) -> None:
        if query:
            keyboard = list()
            if not is_extra_point:
                message = EDIT_POINT_MESSAGE
                extra_points = point.get_extra_information_points()
                if extra_points:
                    for extra_point in point.get_extra_information_points():
                        keyboard.append([InlineKeyboardButton(f"{SUB_THEME_EMOJI} {extra_point.get_name()}",
                                                              callback_data=f"{EDIT_EXTRA_POINT_CALLBACK}_"
                                                                            f"{point.get_id()}_"
                                                                            f"{extra_point.get_id()}")])
                keyboard.append([InlineKeyboardButton(EDIT_POINT_BUTTON,
                                                      callback_data=f"{EDIT_POINT_FIELDS_CALLBACK}{point.get_id()}")])
                keyboard.append([InlineKeyboardButton(ADD_EXTRA_POINT_BUTTON,
                                                      callback_data=f"{ADD_EXTRA_POINT_CALLBACK}{point.get_id()}")])
                keyboard.append([InlineKeyboardButton(DELETE_POINT_BUTTON,
                                                      callback_data=f"{DELETE_POINT_CALLBACK}{point.get_id()}")])
            else:
                message = EDIT_EXTRA_POINT_MESSAGE
                keyboard.append(
                    [InlineKeyboardButton(EDIT_EXTRA_POINT_BUTTON,
                                          callback_data=f"{EDIT_EXTRA_POINT_FIELDS_CALLBACK}{point_id}_{point.get_id()}")])
                keyboard.append([InlineKeyboardButton(DELETE_EXTRA_POINT_BUTTON,
                                                      callback_data=f"{DELETE_EXTRA_POINT_CALLBACK}{point_id}_{point.get_id()}")])

            keyboard_markup = InlineKeyboardMarkup(keyboard)

            await query.message.reply_text(message + point.get_name(), reply_markup=keyboard_markup)
