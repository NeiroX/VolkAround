from point import Point
from typing import List, Dict
import os


class Excursion:
    def __init__(self, name: str, points: List[Point], is_paid: bool = False) -> None:
        self.points = points
        self.current_index = -1
        self.name = name
        self.is_paid = is_paid  # True if paid, False if trial
        self.likes_num = 0
        self.dislikes_num = 0

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

    def get_point(self) -> Point:
        Excursion._validate_location_info(self.points[self.current_index])
        Excursion._validate_info_files(self.points[self.current_index])
        return self.points[self.current_index]

    def move_to_next_point(self) -> bool:
        if self.current_index + 1 < len(self.points):
            self.current_index += 1
            return True
        return False  # Last point reached

    def is_paid_excursion(self) -> bool:
        return self.is_paid

    @staticmethod
    def _validate_info_files(point: Point) -> None:
        """Ensures that all file paths in the point are valid."""
        photos = point.get_photos()
        if photos is not None:
            for photo in photos:
                if not os.path.exists(photo):
                    raise FileNotFoundError(f"Photo file not found: {', '.join(point.get_photos())}")

        audio_file = point.get_audio()
        if not os.path.exists(audio_file) and audio_file is not None:
            raise FileNotFoundError(f"Audio file not found: {audio_file}")

    @staticmethod
    def _validate_location_info(point: Point) -> None:
        """Ensures that all file paths in the point are valid."""
        location_photo = point.get_location_photo()
        if location_photo is not None and not os.path.exists(location_photo):
            raise FileNotFoundError(f"Location photo file not found: {location_photo}")
