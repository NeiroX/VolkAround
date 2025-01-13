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
    try:
        # Get the current working directory
        cwd = os.getcwd()

        # Construct the absolute path to the alembic.ini file
        alembic_ini_path = os.path.join(cwd, "alembic.ini")
        alembic_cfg = Config(alembic_ini_path)  # Path to your Alembic configuration file
        logging.info(f"Alembic ini path: {alembic_ini_path}")
        logging.info(f"Current sqlalchemy.url: {alembic_cfg.get_main_option('sqlalchemy.url')}")
        alembic_cfg.set_main_option('sqlalchemy.url', DATABASE_URL)
        logging.info(f"Set sqlalchemy.url parameter to: {DATABASE_URL}")
        logging.info(f"Current sqlalchemy.url: {alembic_cfg.get_main_option('sqlalchemy.url')}")
        # Log Alembic version before running the upgrade
        # logging.info(f"Current Alembic version: {command.current(alembic_cfg)}")

        # Apply all migrations up to the latest
        logging.info("Applying migrations...")
        # command.upgrade(alembic_cfg, "head")
        logging.info("Migrations applied successfully")
    except Exception as e:
        logging.error(f"Error applying migrations: {e}")
        raise RuntimeError(f"Error applying migrations: {e}")


def test_connection():
    logging.info("Testing database connection")
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT version();")
                db_version = cursor.fetchone()
                logging.info(f"Database version: {db_version[0]}")
        finally:
            conn.close()


if __name__ == "__main__":
    # Example log messages
    logging.info("Running main file!!!")
    if not TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN is not set in the environment or .env file")
    else:
        logging.info(f"Using token: {TOKEN[:5]}...")  # Replace with your bot token
    # Test connection to database and apply migrations
    test_connection()
    apply_migrations()
    logging.info("Creating session...")
    session = create_session()
    logging.info("Session created successfully")

    logging.info("Initializing Bot...")
    bot = Bot(TOKEN, session)
    logging.info("Bot initialized, starting bot...")

    bot.run()
