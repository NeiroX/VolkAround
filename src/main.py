import os

from alembic import command
from alembic.config import Config
from sqlalchemy.orm import Session
import logging
from src.components.messages.bot import Bot
from src.database.session import create_session
from src.settings import TOKEN, DATABASE_URL
from src.database.session import get_db_connection

def apply_migrations():
    """
    Applies Alembic migrations to ensure the database schema is up-to-date.
    """
    # Get the current working directory
    cwd = os.getcwd()

    # Construct the absolute path to the alembic.ini file
    alembic_ini_path = os.path.join(cwd, "alembic.ini")
    alembic_cfg = Config(alembic_ini_path)  # Path to your Alembic configuration file
    logging.debug(f"Alembic ini path: {alembic_ini_path}")
    print(f"Alembic ini path: {alembic_ini_path}")
    logging.debug(f"Current sqlalchemy.url: {alembic_cfg.get_main_option('sqlalchemy.url')}")
    print(f"Current sqlalchemy.url: {alembic_cfg.get_main_option('sqlalchemy.url')}")
    alembic_cfg.set_main_option('sqlalchemy.url', DATABASE_URL)
    logging.debug(f"Set sqlalchemy.url parameter to: {DATABASE_URL}")
    print(f"Set sqlalchemy.url parameter to: {DATABASE_URL}")
    logging.debug(f"Current sqlalchemy.url: {alembic_cfg.get_main_option('sqlalchemy.url')}")
    print(f"Current sqlalchemy.url: {alembic_cfg.get_main_option('sqlalchemy.url')}")

    command.upgrade(alembic_cfg, "head")  # Apply all migrations up to the latest

def test_connection():
    logging.debug("Testing database connection")
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT version();")
                db_version = cursor.fetchone()
                print(f"Database version: {db_version[0]}")
        finally:
            conn.close()


if __name__ == "__main__":

    # Configure the logging system
    logging.basicConfig(
        level=logging.DEBUG,  # Log everything from DEBUG level and above
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    # Example log messages
    logging.debug("Running main file!!!")
    print("Running main file!!!")

    if not TOKEN:
        raise ValueError("Missing TELEGRAM_BOT_TOKEN in .env file")  # Replace with your bot token
    # Test connection to database and apply migrations
    test_connection()
    apply_migrations()




    # Start bot
    session: Session = create_session()
    bot = Bot(TOKEN, session)
    bot.run()
