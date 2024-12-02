from bot import Bot
from dotenv import load_dotenv
from os import getenv
import json
from typing import List

from excursion import Excursion
from point import Point

if __name__ == "__main__":

    # Load environment variables from .env file
    load_dotenv()
    # TODO: admin solution to edit existing excursions

    # Retrieve the token from the .env file
    TOKEN = getenv("TELEGRAM_BOT_TOKEN")

    if not TOKEN:
        raise ValueError("Missing TELEGRAM_BOT_TOKEN in .env file")  # Replace with your bot token

    bot = Bot(TOKEN)
    bot.run()
