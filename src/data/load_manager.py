from typing import Dict, List

from pymongo.synchronous.collection import Collection

from src.components.excursion.excursion import Excursion
from src.components.excursion.point.information_part import InformationPart
from src.components.excursion.point.point import Point
from pymongo import MongoClient
from src.constants import TEXT_MODE, DEFAULT_TEXT, DEFAULT_ADDRESS, \
    DEFAULT_EXCURSION_NAME, DEFAULT_INFORMATION_PART_NAME, USER_STATE_COLLECTION, EXCURSION_COLLECTION, \
    POINT_COLLECTION, EXTRA_INFO_COLLECTION, ADMINS_LIST
from src.settings import DATABASE_URL, DATABASE_NAME
from src.components.user.user_state import UserState


class LoadManager:
    def __init__(self) -> None:
        self.client = MongoClient(DATABASE_URL)
        self.db = self.client[DATABASE_NAME]
        self.excursions_collection: Collection = self.db[EXCURSION_COLLECTION]
        self.points_collection: Collection = self.db[POINT_COLLECTION]
        self.information_parts_collection: Collection = self.db[EXTRA_INFO_COLLECTION]
        self.user_states_collection: Collection = self.db[USER_STATE_COLLECTION]

    def load_information_part(self, point_id: int) -> List[InformationPart]:
        """Loads information parts related to a specific point."""
        data = self.information_parts_collection.find({"parent_id": point_id})
        information_parts = list()
        for extra_part in data:
            info_part = InformationPart(information_point_id=extra_part.get("point_id", 0),
                                        parent_id=point_id,
                                        part_name=extra_part.get("name", DEFAULT_INFORMATION_PART_NAME),
                                        photos=extra_part.get("photos", []),
                                        audio=extra_part.get("audio", []),
                                        text=extra_part.get("text", DEFAULT_TEXT),
                                        link=extra_part.get("link", None),
                                        views_num=extra_part.get("views_num", 0),
                                        likes_num=extra_part.get("likes_num", 0),
                                        dislikes_num=extra_part.get("dislikes_num", 0),
                                        visitors=extra_part.get("visitors", []), )
            if info_part.get_id() > InformationPart.information_part_id:
                InformationPart.information_part_id = info_part.get_id()
            information_parts.append(info_part)
        return information_parts

    def load_points(self, excursion_id: int) -> List[Point]:
        """Loads points related to a specific excursion."""
        data = self.points_collection.find({"parent_id": excursion_id})
        points = []
        for point_data in data:
            extra_parts = self.load_information_part(point_data["point_id"])
            point = Point(
                point_id=point_data.get("point_id", 0),
                excursion_id=excursion_id,
                part_name=point_data.get("name", DEFAULT_EXCURSION_NAME),
                address=point_data.get("address", DEFAULT_ADDRESS),
                location_photo=point_data.get("location_photo", None),
                location_link=point_data.get("location_link", None),
                photos=point_data.get("photos", []),
                audio=point_data.get("audio", []),
                text=point_data.get("text", DEFAULT_TEXT),
                link=point_data.get("link", None),
                views_num=point_data.get("views_num", 0),
                likes_num=point_data.get("likes_num", 0),
                dislikes_num=point_data.get("dislikes_num", 0),
                extra_information_points=extra_parts,
                visitors=point_data.get("visitors", []),
            )
            if point.get_id() > Point.point_id:
                Point.point_id = point.get_id()
            points.append(point)
        print(f"Loaded {len(points)} points from MongoDB.")
        return points

    def load_excursions(self) -> Dict[str, Excursion]:
        """Loads all excursions and their related points."""
        excursions = {}
        data = self.excursions_collection.find()
        for excursion_data in data:
            points = self.load_points(excursion_data["point_id"])
            excursion = Excursion(
                excursion_id=excursion_data["point_id"],
                name=excursion_data.get("name", DEFAULT_EXCURSION_NAME),
                points=points,
                is_paid=excursion_data.get("is_paid", False),
                likes_num=excursion_data.get("likes_num", 0),
                dislikes_num=excursion_data.get("dislikes_num", 0),
                is_draft=excursion_data.get("is_draft", False),
                views_num=excursion_data.get("views_num", 0),
                duration=excursion_data.get("duration", 0),
                visitors=excursion_data.get("visitors", []),
            )
            print(f"Loaded excursion: {excursion.to_dict()}")
            if excursion.get_id() > Excursion.excursion_id:
                Excursion.point_id = excursion.get_id()
            excursions[excursion.get_name()] = excursion
        print(f"Loaded {len(excursions)} excursions from MongoDB.")
        return excursions

    def load_user_states(self) -> Dict[int, UserState]:
        """Loads all user states."""
        user_states = {}
        data = self.user_states_collection.find()
        for user_data in data:
            print(f"Loaded user: {user_data}")
            username = user_data.get("username")
            user_id = user_data.get("user_id")
            mode = user_data.get("mode", TEXT_MODE)
            if username in ADMINS_LIST:
                is_admin = True
            else:
                is_admin = user_data.get("is_admin", False)
            paid_excursions = user_data.get("paid_excursions", [])
            user_state = UserState(username=username, user_id=user_id, mode=mode, is_admin=is_admin,
                                   paid_excursions=paid_excursions)
            user_states[user_state.user_id] = user_state
        print(f"Loaded {len(user_states)} user states from MongoDB.")
        return user_states

    def save_information_part(self, information_part: InformationPart) -> None:
        """Saves or updates an information part in the MongoDB collection."""
        existing_part = self.information_parts_collection.find_one({"point_id": information_part.get_id()})
        if existing_part:
            self.information_parts_collection.replace_one({"point_id": information_part.get_id()},
                                                          information_part.to_dict())
        else:
            self.information_parts_collection.insert_one(information_part.to_dict())
        print(f"Saved information part {information_part.part_name} to MongoDB.")

    def save_point(self, point: Point) -> None:
        """Saves or updates a point in the MongoDB collection."""
        existing_point = self.points_collection.find_one({"point_id": point.get_id()})
        if existing_point:
            self.points_collection.replace_one({"point_id": point.get_id()}, point.to_dict())
        else:
            self.points_collection.insert_one(point.to_dict())
        for extra_part in point.get_extra_information_points():
            self.save_information_part(extra_part)

    def save_excursion(self, excursion: Excursion) -> None:
        """Saves or updates an excursion in the MongoDB collection."""
        existing_excursion = self.excursions_collection.find_one({"point_id": excursion.get_id()})
        if existing_excursion:
            self.excursions_collection.replace_one({"point_id": excursion.get_id()}, excursion.to_dict())
        else:
            self.excursions_collection.insert_one(excursion.to_dict())
        print(f"Saved excursion {excursion.get_name()} to MongoDB. Points: {excursion.points}")
        for point in excursion.get_points():
            self.save_point(point)

    def save_user_state(self, user_state: UserState) -> None:
        """Saves or updates a user state in the MongoDB collection."""
        existing_user_state = self.user_states_collection.find_one({"user_id": user_state.get_user_id()})
        if existing_user_state:
            self.user_states_collection.replace_one({"user_id": user_state.get_user_id()}, user_state.to_dict())
        else:
            self.user_states_collection.insert_one(user_state.to_dict())
        print(f"Saved user state for user {user_state.username} to MongoDB.")

    def delete_excursion(self, excursion_id: int) -> None:
        """Deletes an excursion and all its related points and information parts."""
        points = self.points_collection.find({"excursion_id": excursion_id})
        for point in points:
            self.delete_point(point["point_id"])
        self.excursions_collection.delete_one({"point_id": excursion_id})
        print(f"Deleted excursion with point_id {excursion_id} from MongoDB.")

    def delete_point(self, point_id: int) -> None:
        """Deletes a point and all its related information parts."""
        self.information_parts_collection.delete_many({"point_id": point_id})
        self.points_collection.delete_one({"point_id": point_id})
        print(f"Deleted point with point_id {point_id} from MongoDB.")

    def delete_extra_information_point(self, extra_point_id: int) -> None:
        """Deletes an extra information point"""
        self.information_parts_collection.delete_one({"point_id": extra_point_id})
        print(f"Deleted extra information point with point_id {extra_point_id} from MongoDB.")

    def delete_user_state(self, user_id: int) -> None:
        """Deletes a user state from the MongoDB collection."""
        self.user_states_collection.delete_one({"user_id": user_id})
        print(f"Deleted user state with point_id {user_id} from MongoDB.")

    def clear_database(self) -> None:
        """Clears the MongoDB collection."""
        self.user_states_collection.delete_many({})
        self.information_parts_collection.delete_many({})
        self.points_collection.delete_many({})
        self.excursions_collection.delete_many({})


    # JSON USAGE
    #
    # @staticmethod
    # def load_excursions_from_json() -> Dict[str, Excursion]:
    #     """Loads excursions from a JSON file and returns a list of Excursion objects."""
    #     print(EXCURSIONS_INFO_PATH)
    #     with open(EXCURSIONS_INFO_PATH, "r") as file:
    #         data = json.load(file)
    #
    #     excursions = dict()  # This will hold the list of Excursion objects
    #
    #     for excursion_data in data:  # Iterate through each current_excursion in the JSON
    #         excursion_id = excursion_data["point_id"]
    #         if excursion_id > Excursion.excursion_id:
    #             Excursion.excursion_id = excursion_id
    #         excursion_name = excursion_data.get("name", DEFAULT_EXCURSION_NAME)
    #         is_paid_excursion = excursion_data.get("is_paid", False)
    #         is_draft_excursion = excursion_data.get("is_draft", False)
    #         likes_num = excursion_data.get("likes_num", 0)
    #         dislikes_num = excursion_data.get("dislikes_num", 0)
    #         points_data = excursion_data.get("points", [])
    #         visitors_data = excursion_data.get("views_num", 0)
    #         points = []
    #
    #         for point_data in points_data:  # Iterate through each part in the current_excursion
    #             extra_parts = list()
    #             if point_data.get("extra_information_points", False):
    #                 for extra_part in point_data["extra_information_points"]:
    #                     info_part = InformationPart(point_id=extra_part.get("point_id", 0),
    #                                                 part_name=extra_part.get("name", DEFAULT_INFORMATION_PART_NAME),
    #                                                 photos=extra_part.get("photos", []),
    #                                                 audio=extra_part.get("audio", []),
    #                                                 text=extra_part.get("text", DEFAULT_TEXT),
    #                                                 link=point_data.get("link", None),
    #                                                 views_num=point_data.get("views_num", 0),
    #                                                 likes_num=point_data.get("likes_num", 0),
    #                                                 dislikes_num=point_data.get("dislikes_num", 0),
    #                                                 )
    #                     if info_part.get_id() > InformationPart.information_part_id:
    #                         InformationPart.information_part_id = info_part.get_id()
    #                     extra_parts.append(info_part)
    #
    #             point = Point(
    #                 point_id=point_data.get("point_id", 0),
    #                 part_name=point_data.get("name", DEFAULT_EXCURSION_NAME),
    #                 address=point_data.get("address", DEFAULT_ADDRESS),
    #                 location_photo=point_data.get("location_photo", None),
    #                 location_link=point_data.get("location_link", None),
    #                 photos=point_data.get("photos", []),
    #                 audio=point_data.get("audio", []),
    #                 text=point_data.get("text", DEFAULT_TEXT),
    #                 link=point_data.get("link", None),
    #                 views_num=point_data.get("views_num", 0),
    #                 likes_num=point_data.get("likes_num", 0),
    #                 dislikes_num=point_data.get("dislikes_num", 0),
    #                 extra_information_points=extra_parts,
    #             )
    #             if point.get_id() > Point.point_id:
    #                 Point.point_id = point.get_id()
    #             points.append(point)
    #
    #         # Create the Excursion object and add it to the excursions list
    #         excursion = Excursion(excursion_id=excursion_id, name=excursion_name, points=points,
    #                               is_paid=is_paid_excursion, likes_num=likes_num,
    #                               dislikes_num=dislikes_num, is_draft=is_draft_excursion, views_num=visitors_data)
    #         excursions[excursion_name] = excursion
    #     print("Loaded {} excursions".format(len(excursions)))
    #
    #     return excursions
    #
    # @staticmethod
    # def load_user_states_from_json() -> dict[int, UserState]:
    #     """
    #     Load a list of user states from a JSON file.
    #     :return: List of UserState objects.
    #     """
    #     try:
    #         user_states = dict()
    #         print("Loading user states...")
    #
    #         with open(USER_STATES_PATH, "r") as file:
    #             data = json.load(file)
    #             print(data)
    #             for user in data:
    #                 print(f"Loading user {user['username']}")
    #                 print(user.get("is_admin", False), user.get("username"))
    #                 user_states_instance = UserState(username=user["username"],
    #                                                  user_id=user["user_id"],
    #                                                  is_admin=user.get("is_admin", False),
    #                                                  mode=user.get("mode", TEXT_MODE),
    #                                                  paid_excursions=user.get("paid_excursions", []),
    #                                                  completed_excursions=user.get("completed_excursions", []))
    #                 user_states[user["user_id"]] = user_states_instance
    #             print("Loaded {} users".format(len(user_states)))
    #             return user_states
    #     except FileNotFoundError:
    #         print(f"File {USER_STATES_PATH} not found.")
    #         return {}
    #     except json.JSONDecodeError:
    #         print(f"File {USER_STATES_PATH} could not be decoded.")
    #         return {}
    #
    # @staticmethod
    # def save_excursion_data(excursion: Excursion) -> None:
    #     """Saves or updates a components' information in the JSON file."""
    #     try:
    #
    #         # If the JSON file does not exist, create it with the new components
    #         if not os.path.exists(EXCURSIONS_INFO_PATH):
    #             with open(EXCURSIONS_INFO_PATH, "w", encoding="utf-8") as file:
    #                 data = [excursion.to_dict()]
    #                 json.dump(data, file, ensure_ascii=False, indent=4)
    #             return
    #
    #         # Load existing data from the JSON file
    #         with open(EXCURSIONS_INFO_PATH, "r", encoding="utf-8") as file:
    #             data = json.load(file)
    #
    #         # Check if the components already exists; if so, update it
    #         for index, existing_excursion in enumerate(data):
    #             if existing_excursion["name"] == excursion.name:
    #                 data[index] = excursion.to_dict()  # Update existing entry
    #                 break
    #         else:
    #             # If the components is not found, add it as a new entry
    #             data.append(excursion.to_dict())
    #
    #         # Write the updated data back to the JSON file
    #         with open(EXCURSIONS_INFO_PATH, "w", encoding="utf-8") as file:
    #             json.dump(data, file, ensure_ascii=False, indent=4)
    #
    #         print(f"Saved {excursion.get_name()} components")
    #
    #     except Exception as e:
    #         print(f"Error saving components data: {e}")
    #
    # @staticmethod
    # def save_user_state(user_state: UserState) -> None:
    #     """Saves or updates a user's state in the JSON file."""
    #     try:
    #         # If the JSON file doesn't exist, create it with the new user state
    #         if not os.path.exists(USER_STATES_PATH):
    #             with open(USER_STATES_PATH, "w", encoding="utf-8") as file:
    #                 data = [user_state.to_dict()]
    #                 json.dump(data, file, ensure_ascii=False, indent=4)
    #             return
    #
    #         # Load existing data from the JSON file
    #         with open(USER_STATES_PATH, "r", encoding="utf-8") as file:
    #             data = json.load(file)
    #
    #         # Check if the user already exists; if so, update their state
    #         for idx, existing_user in enumerate(data):
    #             if existing_user["user_id"] == user_state.user_id:
    #                 data[idx] = user_state.to_dict()  # Update existing entry
    #                 break
    #         else:
    #             # If the user is not found, add them as a new entry
    #             data.append(user_state.to_dict())
    #
    #         # Write the updated data back to the JSON file
    #         with open(USER_STATES_PATH, "w", encoding="utf-8") as file:
    #             json.dump(data, file, ensure_ascii=False, indent=4)
    #
    #         print(f"Saved {user_state.get_username()}|{user_state.get_user_id()} user state")
    #
    #     except Exception as e:
    #         print(f"Error saving user state: {e}")
    #
    # @staticmethod
    # def delete_excursion_data(excursion_id: int) -> None:
    #     """Deletes a components' information in the JSON file."""
    #     try:
    #         if not os.path.exists(EXCURSIONS_INFO_PATH):
    #             return
    #         with open(EXCURSIONS_INFO_PATH, 'r') as file:
    #             data = json.load(file)
    #
    #         # Example: Delete an instance with a specific key (e.g., a person with a specific 'point_id')
    #         data = [item for item in data if item.get('point_id') != excursion_id]
    #
    #         # Write the updated data back to the JSON file
    #         with open(EXCURSIONS_INFO_PATH, 'w') as file:
    #             json.dump(data, file, indent=4)
    #
    #         print(f"Instance with point_id {excursion_id} deleted.")
    #
    #     except Exception as e:
    #         print(f"Error deleting excursion {excursion_id} data: {e}")
