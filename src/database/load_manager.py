from typing import Dict
from src.components.excursion.excursion import Excursion
from src.components.excursion.point.information_part import InformationPart
from src.components.excursion.point.point import Point
import os
import json
from src.constants import EXCURSIONS_INFO_PATH, USER_STATES_PATH, TEXT_MODE, DEFAULT_TEXT, DEFAULT_ADDRESS, \
    DEFAULT_EXCURSION_NAME, DEFAULT_INFORMATION_PART_NAME
from src.components.user.user_state import UserState


class LoadManager:
    def __init__(self):
        pass

    @staticmethod
    def load_excursions_from_json() -> Dict[str, Excursion]:
        """Loads excursions from a JSON file and returns a list of Excursion objects."""
        print(EXCURSIONS_INFO_PATH)
        with open(EXCURSIONS_INFO_PATH, "r") as file:
            data = json.load(file)

        excursions = dict()  # This will hold the list of Excursion objects

        for excursion_data in data:  # Iterate through each current_excursion in the JSON
            excursion_id = excursion_data["id"]
            excursion_name = excursion_data.get("name", DEFAULT_EXCURSION_NAME)
            is_paid_excursion = excursion_data.get("is_paid", False)
            is_draft_excursion = excursion_data.get("is_draft", False)
            likes_num = excursion_data.get("likes_num", 0)
            dislikes_num = excursion_data.get("dislikes_num", 0)
            points_data = excursion_data.get("points", [])
            points = []

            for point_data in points_data:  # Iterate through each part in the current_excursion
                extra_parts = list()
                if point_data.get("extra_information_points", False):
                    print(point_data.get("extra_information_points", False))
                    for extra_part in point_data["extra_information_points"]:
                        print(extra_part)
                        info_part = InformationPart(id=extra_part.get("id", 0),
                                                    part_name=extra_part.get("name", DEFAULT_INFORMATION_PART_NAME),
                                                    photos=extra_part.get("photos", []),
                                                    audio=extra_part.get("audio", None),
                                                    text=extra_part.get("text", DEFAULT_TEXT)
                                                    )
                        extra_parts.append(info_part)

                point = Point(
                    id=point_data.get("id", 0),
                    part_name=point_data.get("name", DEFAULT_EXCURSION_NAME),
                    address=point_data.get("address", DEFAULT_ADDRESS),
                    location_photo=point_data.get("location_photo"),
                    photos=point_data.get("photos", []),
                    audio=point_data.get("audio", None),
                    text=point_data.get("text", DEFAULT_TEXT),
                    extra_information_points=extra_parts,
                )
                points.append(point)

            # Create the Excursion object and add it to the excursions list
            excursion = Excursion(excursion_id=excursion_id, name=excursion_name, points=points,
                                  is_paid=is_paid_excursion, likes_num=likes_num,
                                  dislikes_num=dislikes_num, is_draft=is_draft_excursion)
            excursions[excursion_name] = excursion
        print("Loaded {} excursions".format(len(excursions)))

        return excursions

    @staticmethod
    def load_user_states_from_json() -> dict[int, UserState]:
        """
        Load a list of user states from a JSON file.
        :return: List of UserState objects.
        """
        try:
            user_states = dict()
            print("Loading user states...")

            with open(USER_STATES_PATH, "r") as file:
                print("File opened")
                data = json.load(file)
                print(data)
                for user in data:
                    print(f"Loading user {user['username']}")
                    print(user.get("is_admin", False), user.get("username"))
                    user_states_instance = UserState(username=user["username"],
                                                     user_id=user["user_id"],
                                                     is_admin=user.get("is_admin", False),
                                                     mode=user.get("mode", TEXT_MODE),
                                                     paid_excursions=user.get("paid_excursions", []),
                                                     completed_excursions=user.get("completed_excursions", []))
                    user_states[user["user_id"]] = user_states_instance
                    print(f"Loaded user: {user_states_instance.to_dict()}")
                print("Loaded {} users".format(len(user_states)))
                return user_states
        except FileNotFoundError:
            print(f"File {USER_STATES_PATH} not found.")
            return {}
        except json.JSONDecodeError:
            print(f"File {USER_STATES_PATH} could not be decoded.")
            return {}

    @staticmethod
    def save_excursion_data(excursion: Excursion) -> None:
        """Saves or updates a components' information in the JSON file."""
        try:

            # If the JSON file does not exist, create it with the new components
            if not os.path.exists(EXCURSIONS_INFO_PATH):
                with open(EXCURSIONS_INFO_PATH, "w", encoding="utf-8") as file:
                    data = [excursion.to_dict()]
                    json.dump(data, file, ensure_ascii=False, indent=4)
                return

            # Load existing data from the JSON file
            with open(EXCURSIONS_INFO_PATH, "r", encoding="utf-8") as file:
                data = json.load(file)

            # Check if the components already exists; if so, update it
            for index, existing_excursion in enumerate(data):
                if existing_excursion["name"] == excursion.name:
                    data[index] = excursion.to_dict()  # Update existing entry
                    break
            else:
                # If the components is not found, add it as a new entry
                data.append(excursion.to_dict())

            # Write the updated data back to the JSON file
            with open(EXCURSIONS_INFO_PATH, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)

            print(f"Saved {excursion.get_name()} components")

        except Exception as e:
            print(f"Error saving components data: {e}")

    @staticmethod
    def save_user_state(user_state: UserState) -> None:
        """Saves or updates a user's state in the JSON file."""
        try:
            # If the JSON file doesn't exist, create it with the new user state
            if not os.path.exists(USER_STATES_PATH):
                with open(USER_STATES_PATH, "w", encoding="utf-8") as file:
                    data = [user_state.to_dict()]
                    json.dump(data, file, ensure_ascii=False, indent=4)
                return

            # Load existing data from the JSON file
            with open(USER_STATES_PATH, "r", encoding="utf-8") as file:
                data = json.load(file)

            # Check if the user already exists; if so, update their state
            for idx, existing_user in enumerate(data):
                if existing_user["user_id"] == user_state.user_id:
                    data[idx] = user_state.to_dict()  # Update existing entry
                    break
            else:
                # If the user is not found, add them as a new entry
                data.append(user_state.to_dict())

            # Write the updated data back to the JSON file
            with open(USER_STATES_PATH, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)

            print(f"Saved {user_state.get_username()}|{user_state.get_user_id()} user state")

        except Exception as e:
            print(f"Error saving user state: {e}")
