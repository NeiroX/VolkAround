from src.components.excursion.point.point import Point
from typing import List, Tuple, Dict, Any
import os

from src.components.field import Field
from src.constants import *


class Excursion:

    def __init__(self, excursion_id: int, name: str = DEFAULT_EXCURSION_NAME, points: List[Point] = None,
                 is_draft: bool = True, is_paid: bool = False,
                 likes_num: int = 0,
                 dislikes_num: int = 0) -> None:
        self.id = excursion_id
        self.is_draft = is_draft
        self.points = points if points is not None else list()
        self.name = name
        self.is_paid = is_paid  # True if paid, False if trial
        self.likes_num = likes_num
        self.dislikes_num = dislikes_num

    def get_id(self) -> int:
        return self.id

    def get_name(self) -> str:
        return self.name

    def change_name(self, new_name: str) -> None:
        self.name = new_name

    def like(self) -> None:
        self.likes_num += 1

    def dislike(self) -> None:
        self.dislikes_num += 1

    def get_likes_number(self) -> int:
        return self.likes_num

    def get_dislikes_number(self) -> int:
        return self.dislikes_num

    def get_point(self, step) -> Point | None:
        if step < len(self.points):
            Excursion._validate_location_info(self.points[step])
            Excursion._validate_info_files(self.points[step])
            return self.points[step]
        return None

    def is_paid_excursion(self) -> bool:
        return self.is_paid

    def change_payment_requirement(self, payment_requirement: bool) -> None:
        self.is_paid = payment_requirement

    def is_draft_excursion(self) -> bool:
        return self.is_draft

    def change_visibility(self) -> None:
        self.is_draft = not self.is_draft

    def get_points(self) -> List[Point]:
        return self.points

    def update_excursions_points(self, point: Point) -> None:
        for elem in self.points:
            if elem.get_id() == point.get_id():
                elem = point
                return
        self.points.append(point)

    def to_dict(self) -> Dict:
        """Convert the components to a dictionary for JSON serialization."""
        return {
            "id": self.id,
            NAME_FIELD: self.name,
            "is_draft": self.is_draft,
            EXCURSION_IS_PAID_FIELD: self.is_paid,
            "likes_num": self.likes_num,
            "dislikes_num": self.dislikes_num,
            "points": [point.to_dict() for point in self.points]
        }

    def get_fields(self) -> List[Field]:
        return [
            Field(EXCURSION_NAME_FIELD_MESSAGE, NAME_FIELD, str),
            Field(EXCURSION_PAYMENT_REQUIREMENT_FIELD_MESSAGE, EXCURSION_IS_PAID_FIELD, bool),
        ]

    def set_from_dict(self, data: Dict[str, Any]) -> None:
        self.name = data.get(NAME_FIELD)
        self.is_paid = data.get(EXCURSION_IS_PAID_FIELD)

    @staticmethod
    def _validate_info_files(point: Point) -> None:
        """Ensures that all file paths in the part are valid."""
        photos = point.get_photos()
        if photos is not None:
            for photo in photos:
                if not os.path.exists(photo):
                    raise FileNotFoundError(f"Photo file not found: {', '.join(point.get_photos())}")

        audio_file = point.get_audio()
        if audio_file is not None and not os.path.exists(audio_file):
            raise FileNotFoundError(f"Audio file not found: {audio_file}")

    @staticmethod
    def _validate_location_info(point: Point) -> None:
        """Ensures that all file paths in the part are valid."""
        location_photo = point.get_location_photo()
        if location_photo is not None and not os.path.exists(location_photo):
            raise FileNotFoundError(f"Location photo file not found: {location_photo}")
