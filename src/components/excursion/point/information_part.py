from typing import Dict, List, Any, Tuple
import os

from src.constants import *
from src.components.field import Field


class InformationPart:
    """
    Information part is a general class for the information that contains text and/or audio and optionally photos.
    """

    def __init__(self, id: int, part_name: str = DEFAULT_INFORMATION_PART_NAME,
                 photos: List[str] = None,
                 audio: str = None,
                 text: str = DEFAULT_TEXT,
                 link: str = ""):
        """Initialize an information part."""
        # Set part's settings
        self.id = id
        self.part_name = part_name
        self.photos = photos
        if self.photos:
            self.photos = [os.path.join(IMAGES_PATH, photo_path.split("/")[-1]) for photo_path in photos]
        self.audio = audio
        if self.audio:
            self.audio = os.path.join(AUDIO_PATH, audio.split("/")[-1])
        self.text = text
        self.link = link

    def get_id(self):
        """Returns the unique id of the information part."""
        return self.id

    def get_name(self) -> str:
        """Returns the name of the information part."""
        return self.part_name

    def get_link(self) -> str:
        """Returns the link of the information part."""
        return self.link

    def get_photos(self) -> List[str]:
        """Returns the list of paths for photos provided for the information part."""
        return self.photos

    def get_audio(self) -> str:
        """Returns the audio path for the information part."""
        return self.audio

    def get_text(self) -> str:
        """Returns the text for the information part."""
        return self.text

    def set_from_dict(self, data: Dict[str, Any]):
        self.part_name = data.get(NAME_FIELD, self.part_name)
        self.link = data.get(INFORMATION_PART_LINK_FIELD, self.link)
        self.text = data.get(INFORMATION_PART_TEXT_FIELD, self.text)
        self.audio = data.get(INFORMATION_PART_AUDIO_FIELD, self.audio)
        self.photos = data.get(INFORMATION_PART_PHOTOS_FIELD, self.photos)

    def get_fields(self) -> List[Field]:
        """Returns the fields for the information part."""
        return [
            Field(INFORMATION_PART_NAME_FIELD_MESSAGE, NAME_FIELD, str),
            Field(INFORMATION_PART_LINK_FIELD_MESSAGE, INFORMATION_PART_LINK_FIELD, str),
            Field(INFORMATION_PART_TEXT_FIELD_MESSAGE, INFORMATION_PART_TEXT_FIELD, str),
            Field(INFORMATION_PART_AUDIO_FIELD_MESSAGE, INFORMATION_PART_AUDIO_FIELD, AUDIO_TYPE),
            Field(INFORMATION_PART_PHOTOS_FIELD_MESSAGE, INFORMATION_PART_PHOTOS_FIELD, PHOTO_TYPE)
        ]

    def to_dict(self) -> Dict[str, Any]:
        """Convert the information part to a dictionary for database serialization."""
        return {
            "id": self.id,
            "name": self.part_name,
            "photos": self.photos,
            "audio": self.audio,
            "text": self.text,
            "link": self.link
        }


