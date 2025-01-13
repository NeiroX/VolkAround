import os
from urllib.parse import urlparse
from decouple import config
from dotenv import load_dotenv
import logging

# Local environment
load_dotenv()

# Define log format
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

# Create a logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
# Create a single StreamHandler for logging to the console
info_logger = logging.StreamHandler()
# Create a formatter and assign it to the handler
formatter = logging.Formatter(LOG_FORMAT)
info_logger.setFormatter(formatter)
# Add the handler to the logger
logger.addHandler(info_logger)

# Telegram TOKEN
TOKEN = config("TELEGRAM_BOT_TOKEN")

# Debug
DEBUG = config("DEBUG", cast=bool, default=False)
# Mongo and Database settings
# DATABASE_NAME = os.getenv("DATABASE_NAME")
# DATABASE_URL = os.getenv("DATABASE_URL")

# PosgreSQL database settings
# Local
if DEBUG:
    DATABASE_USER = config("DATABASE_USER", default=None, cast=str)
    DATABASE_NAME = config("DATABASE_NAME", default=None, cast=str)
    DATABASE_PASSWORD = config("DATABASE_PASSWORD", default=None, cast=str)
    DATABASE_HOST = config("DATABASE_HOST", default=None, cast=str)
    DATABASE_PORT = config("DATABASE_PORT", default=None, cast=int)
    DATABASE_URL = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
# Heroku
else:
    DATABASE_URL = config('DATABASE_URL', default=None, cast=str)
    if DATABASE_URL:
        parsed_url = urlparse(DATABASE_URL)
        DATABASE_USER = parsed_url.username
        DATABASE_PASSWORD = parsed_url.password
        DATABASE_HOST = parsed_url.hostname
        DATABASE_PORT = parsed_url.port if parsed_url.port else "5432"  # Default to 5432 if no port is provided
        DATABASE_NAME = parsed_url.path.lstrip('/')  # Remove the leading '/' from the path
        DATABASE_URL = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
    else:
        raise ValueError("DATABASE_URL is not set in the environment variables")

AWS_SERVER_PUBLIC_KEY = config('AWS_ACCESS_KEY_ID', default=None, cast=str)
AWS_SERVER_SECRET_KEY = config('AWS_SECRET_ACCESS_KEY', default=None, cast=str)
AWS_REGION = config('AWS_REGION', default='eu-central-1')
BUCKET_NAME = None
if config('BUCKET_NAME', default='').strip():
    BUCKET_NAME = config('BUCKET_NAME')
ENDPOINT_URL = None
if config('ENDPOINT_URL', default='').strip():
    ENDPOINT_URL = config('ENDPOINT_URL')
EDGE_ENDPOINT_URL = None
if config('EDGE_ENDPOINT_URL', default='').strip():
    EDGE_ENDPOINT_URL = config('EDGE_ENDPOINT_URL')
CUSTOM_ENDPOINT_URL = None
if config('CUSTOM_ENDPOINT_URL', default='').strip():
    CUSTOM_ENDPOINT_URL = config('CUSTOM_ENDPOINT_URL')
