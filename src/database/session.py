import psycopg2
from sqlalchemy import create_engine, inspect, Engine
from sqlalchemy.orm import Session, sessionmaker

from src.database.models import Base, ExcursionModel, PointModel, InformationPartModel, UserStateModel
from src.settings import DATABASE_URL
import logging


def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        logging.info("Connection established successfully.")
        return conn
    except psycopg2.Error as e:
        logging.error(f"Error connecting to the database: {e}")
        return None


def create_session() -> Session:
    """
    Creates and returns a new SQLAlchemy session.

    Returns:
        Session: A new SQLAlchemy session.
    """
    # Construct the connection string manually
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    is_missing_table: bool = check_tables(engine)
    if is_missing_table:
        Base.metadata.create_all(engine)
    return SessionLocal()


def check_tables(engine: Engine) -> bool:
    logging.info(f"Inspecting tables in database...")
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    logging.info(f"Existing tables: {existing_tables}")

    logging.info(f"Checking if Excursion table exists in database...")
    if ExcursionModel.__tablename__ not in existing_tables:
        logging.info("Excursion table does not exist. Creating table...")
        # ExcursionModel.__table__.create(engine)  # Create only the 'information_parts' table
        return True
    else:
        logging.info("Excursion table exists...")

    logging.info(f"Checking if Point table exists in database...")
    if PointModel.__tablename__ not in existing_tables:
        logging.info("Points table does not exist. Creating table...")
        # PointModel.__table__.create(engine)
        return True
    else:
        logging.info("Points table exists...")

    logging.info(f"Checking if InformationPart table exists in database...")
    if InformationPartModel.__tablename__ not in existing_tables:
        logging.info("Information part table does not exist. Creating table...")
        return True
    else:
        logging.info("Information part table exists...")

    logging.info(f"Checking if UserState table exists in database...")
    if UserStateModel.__tablename__ not in existing_tables:
        logging.info("User state table does not exist. Creating table...")
        return True
    else:
        logging.info("User state table exists...")

    logging.info(f"All tables exist in database. Finishing inspection...")
    return False
