import os
from dotenv import load_dotenv

load_dotenv()

# Telegram TOKEN
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Database settings
DATABASE_NAME = os.getenv("DATABASE_NAME")
DATABASE_URL = os.getenv("DATABASE_URL")
