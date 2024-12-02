from typing import List, Dict


class Point:
    DEFAULT_TEXT = "Sorry, text is not provided for this point"
    DEFAULT_ADDRESS = "Sorry, address is not provided for this point"

    def __init__(self, address: str = DEFAULT_ADDRESS, location_photo: str = None, photos: List[str] = None,
                 audio: str = None, text: str = DEFAULT_TEXT, name: str = None):
        # Location info
        self.name = name
        self.address = address
        self.location_photo = location_photo

        # Point information
        self.text = text
        self.photos = photos
        self.audio = audio

    def get_name(self) -> str:
        return self.name

    def get_address(self) -> str:
        return self.address

    def get_location_photo(self) -> str:
        return self.location_photo

    def get_location_info(self) -> Dict[str, str]:
        return {"name": self.name, "address": self.address, "location_photo": self.location_photo}

    def get_photos(self) -> List[str]:
        return self.photos

    def get_text(self) -> str:
        return self.text

    def get_audio(self) -> str:
        return self.audio

    def get_info(self) -> Dict[str, str]:
        return {"text": self.text, "photos": self.photos, "audio": self.audio}

    def to_dict(self) -> dict:
        """Convert the point to a dictionary for JSON serialization."""
        return {
            "name": self.name,
            "address": self.address,
            "location_photo": self.location_photo,
            "photos": self.photos,
            "audio": self.audio,
            "text": self.text
        }
