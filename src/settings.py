import os
from dotenv import load_dotenv

load_dotenv()

# Telegram TOKEN
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Database settings
DATABASE_NAME = os.getenv("DATABASE_NAME")
DATABASE_URL = os.getenv("DATABASE_URL")
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