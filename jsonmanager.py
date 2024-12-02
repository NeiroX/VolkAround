from typing import Dict
from excursion import Excursion
from point import Point
import os
import json
from constants import EXCURSIONS_INFO_PATH, USER_STATES_PATH, TEXT_MODE
from user_state import UserState


class JSONManager:
    def __init__(self):
        pass

    @staticmethod
    def load_excursions_from_json() -> Dict[str, Excursion]:
        """Loads excursions from a JSON file and returns a list of Excursion objects."""
        with open(EXCURSIONS_INFO_PATH, "r") as file:
            data = json.load(file)

        excursions = dict()  # This will hold the list of Excursion objects

        for excursion_data in data:  # Iterate through each current_excursion in the JSON
            excursion_id = excursion_data["id"]
            excursion_name = excursion_data.get("name", "Unnamed Excursion")
            is_paid_excursion = excursion_data.get("is_paid", False)
            likes_num = excursion_data.get("likes_num", 0)
            dislikes_num = excursion_data.get("dislikes_num", 0)
            points_data = excursion_data.get("points", [])
            points = []

            for point_data in points_data:  # Iterate through each point in the current_excursion
                point = Point(
                    name=point_data.get("name", "Unnamed Point"),
                    address=point_data.get("address", Point.DEFAULT_ADDRESS),
                    location_photo=point_data.get("location_photo"),
                    photos=point_data.get("photos", []),
                    audio=point_data.get("audio"),
                    text=point_data.get("text", Point.DEFAULT_TEXT)
                )
                points.append(point)

            # Create the Excursion object and add it to the excursions list
            excursion = Excursion(excursion_id=excursion_id, name=excursion_name, points=points,
                                  is_paid=is_paid_excursion, likes_num=likes_num,
                                  dislikes_num=dislikes_num)
            excursions[excursion_name] = excursion
        print("Loaded {} excursions".format(len(excursions)))

        return excursions

    @staticmethod
    def load_user_states_from_json() -> dict[int, UserState]:
        """
        Load a list of user states from a JSON file.

        :param file_path: Path to the JSON file to load data.
        :return: List of UserState objects.
        """
        try:
            user_states = dict()
            with open(USER_STATES_PATH, "r", encoding="utf-8") as file:
                data = json.load(file)
                print(data)
                for user in data:
                    user_states_instance = UserState(username=user["username"],
                                                     user_id=user["user_id"],
                                                     mode=user.get("mode", TEXT_MODE),
                                                     paid_excursions=user.get("paid_excursions", []),
                                                     completed_excursions=user.get("completed_excursions", []))
                    user_states[user["user_id"]] = user_states_instance
                    print(f"Loaded user: {user_states_instance.to_dict()}")
                print("Loaded {} users".format(len(user_states)))
                return user_states
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            return {}

    @staticmethod
    def save_excursion_data(excursion: Excursion) -> None:
        """Saves or updates an excursion's information in the JSON file."""
        try:

            # If the JSON file does not exist, create it with the new excursion
            if not os.path.exists(EXCURSIONS_INFO_PATH):
                with open(EXCURSIONS_INFO_PATH, "w", encoding="utf-8") as file:
                    data = [excursion.to_dict()]
                    json.dump(data, file, ensure_ascii=False, indent=4)
                return

            # Load existing data from the JSON file
            with open(EXCURSIONS_INFO_PATH, "r", encoding="utf-8") as file:
                data = json.load(file)

            # Check if the excursion already exists; if so, update it
            for index, existing_excursion in enumerate(data):
                if existing_excursion["name"] == excursion.name:
                    data[index] = excursion.to_dict()  # Update existing entry
                    break
            else:
                # If the excursion is not found, add it as a new entry
                data.append(excursion.to_dict())

            # Write the updated data back to the JSON file
            with open(EXCURSIONS_INFO_PATH, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)

            print(f"Saved {excursion.get_name()} excursion")

        except Exception as e:
            print(f"Error saving excursion data: {e}")

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
