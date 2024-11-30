from point import Point
from typing import List, Dict
import os
import json
from constants import EXCURSIONS_INFO_PATH


class Excursion:
    def __init__(self, name: str, points: List[Point], is_paid: bool = False, likes_num: int = 0,
                 dislikes_num: int = 0) -> None:
        self.points = points
        self.name = name
        self.is_paid = is_paid  # True if paid, False if trial
        self.likes_num = likes_num
        self.dislikes_num = dislikes_num

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

    def save_info(self) -> None:
        """Saves the excursion's updated information to the JSON file."""
        try:
            json_file = EXCURSIONS_INFO_PATH
            if not os.path.exists(json_file):
                raise FileNotFoundError(f"JSON file '{json_file}' does not exist.")

            # Read the existing data from the JSON file
            with open(json_file, "r", encoding="utf-8") as file:
                data = json.load(file)

            # Update the relevant excursion data
            for excursion in data:
                if excursion["name"] == self.name:
                    excursion["is_paid"] = self.is_paid
                    excursion["likes_num"] = self.likes_num
                    excursion["dislikes_num"] = self.dislikes_num
                    excursion["points"] = [
                        {
                            "name": point.get_name(),
                            "address": point.get_address(),
                            "location_photo": point.get_location_photo(),
                            "photos": point.get_photos(),
                            "audio": point.get_audio(),
                            "text": point.get_text(),
                        }
                        for point in self.points
                    ]
                    break
            else:
                raise ValueError(f"Excursion '{self.name}' not found in JSON file.")

            # Write the updated data back to the JSON file
            with open(json_file, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)

        except Exception as e:
            print(f"Error saving excursion data: {e}")

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
