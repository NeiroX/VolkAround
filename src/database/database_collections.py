from typing import Any, Mapping

from pymongo import MongoClient
from pymongo.synchronous.database import Database

from src.constants import DATABASE_NAME, DATABASE_URL


def get_collection(collection_name: str) -> Database[Mapping[str, Any] | Any]:
    """
    Function that returns a Database collection based on name
    :param collection_name: a name of the collection
    :return: dictionary of fields
    """
    db = get_database()
    return db[collection_name]


def get_database():
    """
    Function that connects to the client and returns a database itself
    :return: database
    """
    client = MongoClient(DATABASE_URL)
    if DATABASE_NAME in client.list_database_names():
        return MongoClient(DATABASE_URL)
    raise Exception("Database not found")
