import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.database.models import Base
from src.settings import DATABASE_PASSWORD, DATABASE_USER, DATABASE_NAME, DATABASE_HOST, DATABASE_PORT


def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname=DATABASE_NAME,
            user=DATABASE_USER,
            password=DATABASE_PASSWORD,
            host=DATABASE_HOST,
            port=DATABASE_PORT
        )
        print("Connection established successfully.")
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        return None

def create_session() -> Session:
    """
    Creates and returns a new SQLAlchemy session.

    Returns:
        Session: A new SQLAlchemy session.
    """
    # Construct the connection string manually
    connection_string = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
    engine = create_engine(connection_string)
    SessionLocal = sessionmaker(bind=engine)
    # Base.metadata.create_all(engine)

    return SessionLocal()