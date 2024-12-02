from point import Point
from typing import List, Dict
import os
import json
from constants import EXCURSIONS_INFO_PATH


class Excursion:
    def __init__(self, excursion_id: int, name: str, points: List[Point],  is_paid: bool = False, likes_num: int = 0,
                 dislikes_num: int = 0) -> None:
        self.id = excursion_id
        self.points = points
        self.name = name
        self.is_paid = is_paid  # True if paid, False if trial
        self.likes_num = likes_num
        self.dislikes_num = dislikes_num

    def get_id(self) -> int:
        return self.id

    def get_name(self) -> str:
        return self.name

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

    def get_points(self) -> List[Point]:
        return self.points

    def to_dict(self) -> dict:
        """Convert the excursion to a dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "is_paid": self.is_paid,
            "likes_num": self.likes_num,
            "dislikes_num": self.dislikes_num,
            "points": [point.to_dict() for point in self.points]
        }

    @staticmethod
    def _validate_info_files(point: Point) -> None:
        """Ensures that all file paths in the point are valid."""
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
        """Ensures that all file paths in the point are valid."""
        location_photo = point.get_location_photo()
        if location_photo is not None and not os.path.exists(location_photo):
            raise FileNotFoundError(f"Location photo file not found: {location_photo}")
