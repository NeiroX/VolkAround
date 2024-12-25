from typing import List, Dict, Any, Tuple

from src.components.field import Field
from src.constants import *
from src.components.excursion.point.information_part import InformationPart


class Point(InformationPart):

    def __init__(self, id: int, address: str = DEFAULT_ADDRESS, location_photo: str = None,
                 photos: List[str] = None, audio: str = None, text: str = DEFAULT_TEXT,
                 part_name: str = DEFAULT_INFORMATION_PART_NAME,
                 extra_information_points: List[InformationPart] = None):
        super().__init__(id, part_name, photos, audio, text)
        # Location info
        self.address = address
        self.location_photo = location_photo
        if self.location_photo:
            self.location_photo = os.path.join(IMAGES_PATH, location_photo.split("/")[-1])

        # Optional information
        self.extra_information_points = extra_information_points

    def get_address(self) -> str:
        """Returns the address of the part."""
        return self.address

    def get_location_photo(self) -> str:
        """Returns the photo of the part location."""
        return self.location_photo

    def does_have_extra_information_points(self) -> bool:
        """Returns a boolean answer to the quest if the part has extra information."""
        return self.extra_information_points is None

    def get_extra_information_points(self) -> List[InformationPart]:
        """Returns a list of extra information points."""
        return self.extra_information_points

    def get_location_info(self) -> Dict[str, str]:
        """Returns the full location information about the part."""
        return {"name": self.part_name, "address": self.address, "location_photo": self.location_photo}

    def add_extra_information_point(self, extra_information_point: InformationPart) -> None:
        """Adds a new extra information point."""
        self.extra_information_points.append(extra_information_point)

    def set_from_dict(self, data: Dict[str, Any]):
        super().set_from_dict(data)
        self.address = data.get(POINT_ADDRESS_FIELD, self.address)
        self.location_photo = data.get(POINT_LOCATION_PHOTO_FIELD, self.location_photo)

    def get_fields(self) -> List[Field]:
        fields = super().get_fields()
        fields.append(Field(POINT_ADDRESS_FIELD_MESSAGE, POINT_ADDRESS_FIELD, str))
        fields.append(Field(POINT_LOCATION_PHOTO_FIELD_MESSAGE, POINT_LOCATION_PHOTO_FIELD, PHOTO_TYPE))
        return fields

    def update_extra_information_points(self, extra_information_point: InformationPart) -> None:
        """Updates the extra information point."""
        for elem in self.extra_information_points:
            if elem.get_id() == extra_information_point.get_id():
                elem = extra_information_point
                return
        # If it's a new Information Point
        self.extra_information_points.append(extra_information_point)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the part to a dictionary for JSON serialization."""
        point_to_dictionary = super().to_dict()
        point_to_dictionary[POINT_ADDRESS_FIELD] = self.address
        point_to_dictionary[POINT_LOCATION_PHOTO_FIELD] = self.location_photo
        if self.extra_information_points:
            point_to_dictionary["extra_information_points"] = [elem.to_dict() for elem in self.extra_information_points]
        else:
            point_to_dictionary["extra_information_points"] = []
        return point_to_dictionary
