from typing import Any, List

from telegram import InlineKeyboardButton

from src.components.excursion.excursion import Excursion
from src.components.excursion.point.information_part import InformationPart
from src.components.excursion.point.point import Point


class UserEditor:
    def __init__(self):
        self.echo_text = ''
        self.is_editing_mode = False
        self.editing_item = None
        self.fields = None
        self.current_field_counter = None
        self.editing_result = None
        self.excursion_id = None
        self.point_id = None
        self.extra_information_point_id = None
        self.is_order_changing = False
        self.return_callback = None
        self.return_message = None
        self.return_to_previous_menu_callback = None
        self.return_to_previous_menu_message = None
        self.files_sending_mode = False
        self.editing_specific_field = False
        self.sending_echo = False
        self.files_buffer = list()
        self.loading_file_index = 0

    def enable_editing_mode(self, editing_object: Excursion | InformationPart | Point, return_callback: str = None,
                            return_message: str = None,
                            point_id: int = None, extra_information_point_id: int = None,
                            return_to_previous_menu_callback: str = None,
                            return_to_previous_menu_message: str = None) -> None:
        self.is_editing_mode = True
        self.current_field_counter = -1
        self.editing_item = editing_object
        self.fields = editing_object.get_fields()
        self.editing_result = dict()
        self.point_id = point_id
        self.extra_information_point_id = extra_information_point_id
        self.return_callback = return_callback
        self.return_message = return_message
        self.return_to_previous_menu_callback = return_to_previous_menu_callback
        self.return_to_previous_menu_message = return_to_previous_menu_message
        self.loading_file_index = 0

    def disable_editing_mode(self):
        self.is_editing_mode = False
        self.editing_item = None
        self.fields = None
        self.current_field_counter = None
        self.editing_result = None
        self.point_id = None
        self.extra_information_point_id = None
        self.return_callback = None
        self.return_message = None
        self.return_to_previous_menu_callback = None
        self.return_to_previous_menu_message = None
        self.files_sending_mode = False
        self.editing_specific_field = False
        self.files_buffer = list()
        self.sending_echo = False
        self.echo_text = ''
        self.loading_file_index = 0

    def get_extra_information_point_id(self) -> int:
        return self.extra_information_point_id

    def enable_sending_echo(self):
        self.sending_echo = True

    def disable_sending_echo(self):
        self.sending_echo = False
        self.echo_text = ''

    def set_echo_text(self, text: str) -> None:
        self.echo_text = text

    def get_echo_text(self) -> str:
        return self.echo_text

    def get_sending_echo(self):
        return self.sending_echo

    def enable_files_sending(self) -> None:
        self.files_sending_mode = True

    def disable_files_sending(self) -> None:
        self.files_sending_mode = False

    def get_files_sending_mode(self) -> bool:
        return self.files_sending_mode

    def get_loading_file_index(self) -> int:
        return self.loading_file_index

    def get_editing_specific_field(self) -> bool:
        return self.editing_specific_field

    def increase_loading_file_index(self) -> None:
        self.loading_file_index += 1

    def clear_files_buffer(self) -> None:
        self.files_buffer = list()
        self.loading_file_index = 0

    def get_files_buffer(self) -> List[str]:
        return self.files_buffer

    def add_file_to_files_buffer(self, file: str) -> None:
        if file:
            self.files_buffer.append(file)

    def enable_order_changing(self) -> None:
        self.is_order_changing = True

    def enable_editing_specific_field(self) -> None:
        self.editing_specific_field = True

    def disable_editing_specific_field(self) -> None:
        self.editing_specific_field = False

    def disable_order_changing(self) -> None:
        self.is_order_changing = False

    def get_order_changing(self) -> bool:
        return self.is_order_changing

    def get_point_id(self) -> int:
        return self.point_id

    def get_editing_mode(self) -> bool:
        return self.is_editing_mode

    def increase_field_counter(self) -> None:
        self.current_field_counter += 1

    def is_counting_started(self) -> bool:
        return self.current_field_counter >= 0

    def get_current_field_type(self) -> Any:
        return self.fields[self.current_field_counter].get_type()

    def get_current_field_message(self) -> str:
        return self.fields[self.current_field_counter].get_message()

    def get_current_field_name(self) -> str:
        return self.fields[self.current_field_counter].get_name()

    def set_editing_result_to_item(self):
        self.editing_item.set_from_dict(self.editing_result)

    def add_editing_result(self, result: Any) -> None:
        field_name = self.get_current_field_name()
        self.editing_result[field_name] = result

    def get_current_field_state(self) -> Any:
        current_field_name = self.get_current_field_name()
        return self.editing_item.to_dict().get(current_field_name)

    def is_form_finished(self):
        return len(self.fields) <= self.current_field_counter

    def get_return_button(self) -> InlineKeyboardButton | None:
        if self.return_callback and self.return_message:
            callback = self.return_callback
            if self.point_id and not self.extra_information_point_id:
                callback += f"{self.point_id}"
            return InlineKeyboardButton(self.return_message, callback_data=callback)
        return None

    def get_previous_menu_button(self) -> InlineKeyboardButton | None:
        if self.return_to_previous_menu_callback and self.return_to_previous_menu_message:
            callback = self.return_to_previous_menu_callback
            if self.point_id and not self.extra_information_point_id:
                callback += f"{self.point_id}"
            elif self.point_id and self.extra_information_point_id:
                callback += f"{self.point_id}_{self.extra_information_point_id}"
            return InlineKeyboardButton(self.return_to_previous_menu_message, callback_data=callback)
        return None

    def get_editing_item(self):
        return self.editing_item
