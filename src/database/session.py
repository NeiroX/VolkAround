import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from src.settings import DATABASE_URL


def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
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
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    # Base.metadata.create_all(engine)

    return SessionLocal()
