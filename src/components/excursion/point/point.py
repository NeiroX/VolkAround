from typing import List, Dict, Any

from src.components.field import Field
from src.constants import *
from src.components.excursion.point.information_part import InformationPart


class Point(InformationPart):
    point_id = 0

    def __init__(self, point_id: int, excursion_id: int, address: str = DEFAULT_ADDRESS, location_photo: str = None,
                 photos: List[str] = None, audio: str = None, text: str = DEFAULT_TEXT,
                 part_name: str = DEFAULT_INFORMATION_PART_NAME,
                 link: str = None,
                 extra_information_points: List[InformationPart] = None, location_link: str = None,
                 views_num: int = 0, likes_num: int = 0, dislikes_num: int = 0, visitors: List[str] = None):
        super().__init__(information_point_id=point_id, parent_id=excursion_id, part_name=part_name, photos=photos, audio=audio, text=text,
                         link=link,
                         views_num=views_num, likes_num=likes_num, dislikes_num=dislikes_num, visitors=visitors)
        # Location info
        self.address = address
        self.location_photo = location_photo
        self.location_link = location_link

        # Optional information
        self.extra_information_points = extra_information_points if extra_information_points else []

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

    def get_location_link(self) -> str:
        """Returns the location link of the part."""
        return self.location_link

    def add_extra_information_point(self, extra_information_point: InformationPart) -> None:
        """Adds a new extra information point."""
        self.extra_information_points.append(extra_information_point)

    def set_from_dict(self, data: Dict[str, Any]):
        super().set_from_dict(data)
        self.address = data.get(POINT_ADDRESS_FIELD, self.address)
        self.location_photo = data.get(POINT_LOCATION_PHOTO_FIELD, self.location_photo)
        self.location_link = data.get(POINT_LOCATION_LINK_FIELD, self.location_link)

    def get_fields(self) -> List[Field]:
        fields = super().get_fields()
        fields.append(Field(POINT_ADDRESS_FIELD_MESSAGE, POINT_ADDRESS_FIELD, str))
        fields.append(Field(POINT_LOCATION_PHOTO_FIELD_MESSAGE, POINT_LOCATION_PHOTO_FIELD, ONE_PHOTO_TYPE))
        fields.append(Field(POINT_LOCATION_LINK_FIELD_MESSAGE, POINT_LOCATION_LINK_FIELD, str))
        return fields

    def update_extra_information_points(self, extra_information_point: InformationPart) -> None:
        """Updates the extra information point."""
        for i in range(len(self.extra_information_points)):
            elem = self.extra_information_points[i]
            if elem.get_id() == extra_information_point.get_id():
                self.extra_information_points[i] = extra_information_point
                return
        # If it's a new Information Point
        self.extra_information_points.append(extra_information_point)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the part to a dictionary for JSON serialization."""
        point_to_dictionary = super().to_dict()
        point_to_dictionary[POINT_ADDRESS_FIELD] = self.address
        point_to_dictionary[POINT_LOCATION_PHOTO_FIELD] = self.location_photo
        point_to_dictionary[POINT_LOCATION_LINK_FIELD] = self.location_link
        if self.extra_information_points:
            point_to_dictionary["extra_information_points"] = [elem.to_dict() for elem in self.extra_information_points]
        else:
            point_to_dictionary["extra_information_points"] = []
        return point_to_dictionary
