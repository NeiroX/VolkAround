from typing import Any


class Field:
    def __init__(self, field_message: str, field_name: str, field_type: Any):
        self.field_message = field_message
        self.field_name = field_name
        self.field_type = field_type

    def get_message(self) -> str:
        return self.field_message

    def get_name(self) -> str:
        return self.field_name

    def get_type(self) -> Any:
        return self.field_type
