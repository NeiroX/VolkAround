from typing import Any

from src.components.excursion.excursion import Excursion
from src.components.excursion.point.information_part import InformationPart
from src.components.excursion.point.point import Point


class UserEditor:
    def __init__(self):
        self.is_editing_mode = False
        self.editing_item = None
        self.fields = None
        self.current_field_counter = None
        self.editing_result = None
        self.excursion_id = None
        self.point_id = None
        self.extra_information_point_id = None

    def enable_editing_mode(self, editing_object: Excursion | InformationPart | Point,
                            point_id: int = None, extra_information_point_id: int = None) -> None:
        self.is_editing_mode = True
        self.current_field_counter = -1
        self.editing_item = editing_object
        self.fields = editing_object.get_fields()
        self.editing_result = dict()
        self.point_id = point_id
        self.extra_information_point_id = extra_information_point_id

    def disable_editing_mode(self):
        self.is_editing_mode = False
        self.editing_item = None
        self.fields = None
        self.current_field_counter = None
        self.editing_result = None
        self.point_id = None
        self.extra_information_point_id = None

    def get_extra_information_point_id(self) -> int:
        return self.extra_information_point_id

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

    def get_editing_item(self):
        return self.editing_item
