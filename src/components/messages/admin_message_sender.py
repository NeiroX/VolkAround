from telegram import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Update
from typing import Dict, List

from src.components.excursion.excursion import Excursion
from src.components.excursion.point.information_part import InformationPart
from src.components.excursion.point.point import Point
from src.components.messages.message_sender import MessageSender
from src.constants import *


class AdminMessageSender:
    # TODO: Add back to menu button
    @staticmethod
    async def send_success_message(query: CallbackQuery) -> None:
        if query:
            await query.answer(ACTION_COMPLETED_SUCCESFULLY_MESSAGE)
        else:
            print("Error: query is None")

    @staticmethod
    async def send_current_state_query(query: CallbackQuery, field_current_state: str) -> None:
        if query and field_current_state:
            await query.answer(f"{CURRENT_FIELD_VALUE}\n{field_current_state}", show_alert=False)

    @staticmethod
    async def send_current_state_update(update: Update, field_current_state: str) -> None:
        if update.message and field_current_state:
            await update.message.reply_text(f"{CURRENT_FIELD_VALUE}\n{field_current_state}")

    @staticmethod
    async def send_form_text_field_message_query(query: CallbackQuery, field_message: str,
                                                 field_current_state: str = None) -> None:
        await AdminMessageSender.send_current_state_query(query, field_current_state)
        if query:
            keyboard = [[InlineKeyboardButton(SKIP_FIELD_BUTTON, callback_data=SKIP_FIELD_CALLBACK)]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text(field_message, reply_markup=reply_markup)

    @staticmethod
    async def send_form_text_field_message_update(update: Update, field_message: str,
                                                  field_current_state: str = None) -> None:
        await AdminMessageSender.send_current_state_update(update, field_current_state)
        if update.message:
            keyboard = [[InlineKeyboardButton(SKIP_FIELD_BUTTON, callback_data=SKIP_FIELD_CALLBACK)]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(field_message, reply_markup=reply_markup)

    @staticmethod
    async def send_form_boolean_field_message_query(query: CallbackQuery, field_message: str,
                                                    field_current_state) -> None:
        await AdminMessageSender.send_current_state_query(query, field_current_state)
        if query:
            keyboard = [[InlineKeyboardButton(YES_BUTTON, callback_data=BOOLEAN_FIELD_CALLBACK + "yes"),
                         InlineKeyboardButton(NO_BUTTON, callback_data=BOOLEAN_FIELD_CALLBACK + "no")]]
            keyboard_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text(
                field_message,
                reply_markup=keyboard_markup,
            )

    @staticmethod
    async def send_points_list(query: CallbackQuery, points_list: List[Point]) -> None:
        if query:
            keyboard = list()
            for point in points_list:
                keyboard.append(
                    [InlineKeyboardButton(point.get_name(), callback_data=f"{EDIT_POINT_CALLBACK}_{point.get_id()}")])
            keyboard.append([InlineKeyboardButton(ADD_POINT_BUTTON, callback_data=ADD_POINT_CALLBACK)])
            keyboard_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text(
                EDIT_POINTS_MESSAGE,
                reply_markup=keyboard_markup,
            )

    @staticmethod
    async def send_point_edit_message(query: CallbackQuery,
                                      point: Point) -> None:
        if query:
            keyboard = list()
            keyboard.append([InlineKeyboardButton(EDIT_POINT_BUTTON,
                                                  callback_data=f"{EDIT_POINT_FIELDS_CALLBACK}_{point.get_id()}")])
            keyboard.append([InlineKeyboardButton(ADD_POINT_BUTTON, callback_data=ADD_POINT_CALLBACK)])

            keyboard_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text(EDIT_POINT_MESSAGE + point.get_name(), reply_markup=keyboard_markup)

    @staticmethod
    async def send_form_boolean_field_message_update(update: Update, field_message: str,
                                                     field_current_state: object) -> None:
        await AdminMessageSender.send_current_state_update(update, field_current_state)
        if update.message:
            keyboard = [[InlineKeyboardButton(YES_BUTTON, callback_data=BOOLEAN_FIELD_CALLBACK + "yes"),
                         InlineKeyboardButton(NO_BUTTON, callback_data=BOOLEAN_FIELD_CALLBACK + "no")]]
            keyboard_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                text=field_message,
                reply_markup=keyboard_markup,
            )
