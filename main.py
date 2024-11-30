from bot import Bot
from dotenv import load_dotenv
from os import getenv
import json
from typing import List
from excursion import Excursion
from point import Point


def load_excursions_from_json(file_path: str) -> List[Excursion]:
    """Loads excursions from a JSON file and returns a list of Excursion objects."""
    with open(file_path, "r") as file:
        data = json.load(file)

    excursions = []  # This will hold the list of Excursion objects

    for excursion_data in data:  # Iterate through each current_excursion in the JSON
        excursion_name = excursion_data.get("name", "Unnamed Excursion")
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
        excursion = Excursion(name=excursion_name, points=points)
        excursions.append(excursion)

    return excursions


if __name__ == "__main__":

    # Load environment variables from .env file
    load_dotenv()

    # Retrieve the token from the .env file
    TOKEN = getenv("TELEGRAM_BOT_TOKEN")

    if not TOKEN:
        raise ValueError("Missing TELEGRAM_BOT_TOKEN in .env file")  # Replace with your bot token

    excursions = load_excursions_from_json("excursions.json")
    print(len(excursions), type(excursions[0]))
    bot = Bot(TOKEN, excursions)
    bot.run()
