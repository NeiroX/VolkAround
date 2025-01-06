from src.components.excursion.stats_object import StatsObject
from src.components.excursion.point.point import Point
from typing import List, Dict, Any
from src.components.field import Field
from src.constants import *
from src.data.s3bucket import s3_file_exists


class Excursion(StatsObject):
    excursion_id = 0

    def __init__(self, excursion_id: int, name: str = DEFAULT_EXCURSION_NAME, points: List[Point] = None,
                 is_draft: bool = True, is_paid: bool = False,
                 likes_num: int = 0,
                 dislikes_num: int = 0, views_num: int = 0, duration: int = 0, visitors: List[int] = None) -> None:
        super().__init__(views_num, likes_num, dislikes_num, visitors=visitors)
        self.id = excursion_id
        self.is_draft = is_draft
        self.points = points if points is not None else list()
        self.name = name
        self.is_paid = is_paid  # True if paid, False if trial
        self.duration = duration

    def get_id(self) -> int:
        return self.id

    def get_name(self) -> str:
        return self.name

    def get_duration(self) -> int:
        return self.duration

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
        for i in range(len(self.points)):
            if self.points[i].get_id() == point.get_id():
                self.points[i] = point
                return
        self.points.append(point)

    def to_dict(self) -> Dict:
        """Convert the components to a dictionary for JSON serialization."""
        excursion_to_dict = super().to_dict()
        additional_data = {
            "id": self.id,
            NAME_FIELD: self.name,
            "is_draft": self.is_draft,
            EXCURSION_IS_PAID_FIELD: self.is_paid,
            "points": [point.to_dict() for point in self.points],
            EXCURSION_DURATION_FIELD: self.duration,
        }
        excursion_to_dict.update(additional_data)
        return excursion_to_dict

    def get_fields(self) -> List[Field]:
        return [
            Field(EXCURSION_NAME_FIELD_MESSAGE, NAME_FIELD, str),
            Field(EXCURSION_PAYMENT_REQUIREMENT_FIELD_MESSAGE, EXCURSION_IS_PAID_FIELD, bool),
            Field(EXCURSION_DURATION_FIELD_MESSAGE, EXCURSION_DURATION_FIELD, str),
        ]

    def set_from_dict(self, data: Dict[str, Any]) -> None:
        self.name = data.get(NAME_FIELD, self.name)
        self.is_paid = data.get(EXCURSION_IS_PAID_FIELD, self.is_paid)
        self.duration = data.get(EXCURSION_DURATION_FIELD, self.duration)
        if type(self.duration) is str and self.duration.isdigit():
            self.duration = int(self.duration)

    @staticmethod
    def _validate_info_files(point: Point) -> None:
        """Ensures that all file paths in the part are valid."""
        photos = point.get_photos()
        if photos is not None:
            for photo in photos:
                if not s3_file_exists(photo):
                    raise FileNotFoundError(f"Photo file not found: {', '.join(point.get_photos())}")

        audio_files = point.get_audio()
        if audio_files:
            for audio_file in audio_files:
                if audio_file is not None and not s3_file_exists(audio_file):
                    raise FileNotFoundError(f"Audio file not found: {audio_file}")

    @staticmethod
    def _validate_location_info(point: Point) -> None:
        """Ensures that all file paths in the part are valid."""
        location_photo = point.get_location_photo()
        if location_photo is not None and not s3_file_exists(location_photo):
            raise FileNotFoundError(f"Location photo file not found: {location_photo}")
