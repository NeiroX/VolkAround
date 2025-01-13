import os
from urllib.parse import urlparse

from dotenv import load_dotenv

load_dotenv()

# Telegram TOKEN
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Debug
DEBUG = os.getenv("DEBUG")
# Mongo and Database settings
# DATABASE_NAME = os.getenv("DATABASE_NAME")
# DATABASE_URL = os.getenv("DATABASE_URL")

# PosgreSQL database settings
# Local
if DEBUG:
    DATABASE_USER = os.getenv("DATABASE_USER")
    DATABASE_NAME = os.getenv("DATABASE_NAME")
    DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
    DATABASE_HOST = os.getenv("DATABASE_HOST")
    DATABASE_PORT = os.getenv("DATABASE_PORT")
    DATABASE_URL = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

# Heroku
else:
    DATABASE_URL = os.environ['DATABASE_URL']
    if DATABASE_URL:
        DATABASE_DATA = DATABASE_URL.split(':')
        DATABASE_USER = DATABASE_DATA[1].replace('//', '')
        DATABASE_PASSWORD = DATABASE_DATA[2].split('@')[0]
        DATABASE_HOST = DATABASE_DATA[2].split('@')[1]
        # DATABASE_PORT = DATABASE_DATA[3].split('/')[0] if DATABASE_DATA[3].split('/')[0] else 5432
        DATABASE_PORT = "5432"
        DATABASE_NAME = DATABASE_DATA[3].split('/')[1]
        DATABASE_URL = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
    else:
        raise ValueError("DATABASE_URL is not set in the environment variables")

AWS_SERVER_PUBLIC_KEY = os.getenv('AWS_SERVER_PUBLIC_KEY')
AWS_SERVER_SECRET_KEY = os.getenv('AWS_SERVER_SECRET_KEY')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
BUCKET_NAME = None
if os.getenv('BUCKET_NAME', '').strip():
    BUCKET_NAME = os.getenv('BUCKET_NAME')
ENDPOINT_URL = None
if os.getenv('ENDPOINT_URL', '').strip():
    ENDPOINT_URL = os.getenv('ENDPOINT_URL')
EDGE_ENDPOINT_URL = None
if os.getenv('EDGE_ENDPOINT_URL', '').strip():
    EDGE_ENDPOINT_URL = os.getenv('EDGE_ENDPOINT_URL')
CUSTOM_ENDPOINT_URL = None
if os.getenv('CUSTOM_ENDPOINT_URL', '').strip():
    CUSTOM_ENDPOINT_URL = os.getenv('CUSTOM_ENDPOINT_URL')
