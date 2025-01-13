from sqlalchemy import create_engine, Column, Integer, String, Boolean, Text, ForeignKey, Table, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from typing import List, Dict
from src.database.models import InformationPartModel, ExcursionModel, UserStateModel, PointModel, Base
from src.components.excursion.excursion import Excursion
from src.components.excursion.point.point import Point
from src.components.excursion.point.information_part import InformationPart
from src.components.user.user_state import UserState
from src.constants import *


class PostgresLoadManager:
    def __init__(self, session) -> None:
        """
        Initializes the MongoLoadManager with a SQLAlchemy session.
        """
        self.session = session

    def load_information_part(self, point_id: int) -> List[InformationPart]:
        """Loads information parts related to a specific point."""
        try:
            data = self.session.query(InformationPartModel).filter_by(parent_id=point_id).all()
            information_parts = [
                InformationPart(
                    information_point_id=part.point_id,
                    parent_id=point_id,
                    part_name=part.name or DEFAULT_INFORMATION_PART_NAME,
                    photos=part.photos or [],
                    audio=part.audio or [],
                    text=part.text or DEFAULT_TEXT,
                    link=part.link,
                    views_num=part.views_num or 0,
                    likes_num=part.likes_num or 0,
                    dislikes_num=part.dislikes_num or 0,
                    visitors=part.visitors or [],
                )
                for part in data
            ]
            return information_parts
        except SQLAlchemyError as e:
            print(f"Error loading information parts: {e}")
            return []

    def load_points(self, excursion_id: int) -> List[Point]:
        """Loads points related to a specific excursion."""
        try:
            data = self.session.query(PointModel).filter_by(parent_id=excursion_id).all()
            points = [
                Point(
                    point_id=point.id,
                    parent_id=excursion_id,
                    part_name=point.name or DEFAULT_EXCURSION_NAME,
                    address=point.address or DEFAULT_ADDRESS,
                    location_photo=point.location_photo,
                    location_link=point.location_link,
                    photos=point.photos or [],
                    audio=point.audio or [],
                    text=point.text or DEFAULT_TEXT,
                    link=point.link,
                    views_num=point.views_num or 0,
                    likes_num=point.likes_num or 0,
                    dislikes_num=point.dislikes_num or 0,
                    extra_information_points=self.load_information_part(point.id),
                    visitors=point.visitors or [],
                )
                for point in data
            ]
            return points
        except SQLAlchemyError as e:
            print(f"Error loading points: {e}")
            return []

    def load_excursions(self) -> Dict[str, Excursion]:
        """Loads all excursions and their related points."""
        try:
            excursions = {}
            data = self.session.query(ExcursionModel).all()
            for excursion_data in data:
                excursion = Excursion(
                    excursion_id=excursion_data.id,
                    name=excursion_data.name or DEFAULT_EXCURSION_NAME,
                    points=self.load_points(excursion_data.id),
                    is_paid=excursion_data.is_paid or False,
                    likes_num=excursion_data.likes_num or 0,
                    dislikes_num=excursion_data.dislikes_num or 0,
                    is_draft=excursion_data.is_draft or False,
                    views_num=excursion_data.views_num or 0,
                    duration=excursion_data.duration or 0,
                    visitors=excursion_data.visitors or [],
                )
                excursions[excursion.get_name()] = excursion
            return excursions
        except SQLAlchemyError as e:
            print(f"Error loading excursions: {e}")
            return {}

    def load_user_states(self) -> Dict[int, UserState]:
        """Loads all user states."""
        try:
            user_states = {}
            data = self.session.query(UserStateModel).all()
            for user_data in data:
                user_state = UserState(
                    username=user_data.username,
                    user_id=user_data.user_id,
                    mode=user_data.mode or TEXT_MODE,
                    is_admin=user_data.username in ADMINS_LIST or user_data.is_admin or False,
                    paid_excursions=user_data.paid_excursions or [],
                )
                user_states[user_state.user_id] = user_state
            return user_states
        except SQLAlchemyError as e:
            print(f"Error loading user states: {e}")
            return {}

    def save_entity(self, table, entity, entity_id):
        """Generic save method for any table."""
        try:
            entity_model = entity.to_model()
            existing = self.session.query(table).filter_by(id=entity_id).first()
            if existing:
                self.session.merge(entity_model)
            else:
                self.session.add(entity_model)
            self.session.commit()
            print(f"Saved entity with ID {entity_id} to the database.")
        except SQLAlchemyError as e:
            print(f"Error saving entity with ID {entity_id}: {e}")
            self.session.rollback()

    def delete_entity(self, table, entity_id):
        """Generic delete method for any table."""
        try:
            self.session.query(table).filter_by(id=entity_id).delete()
            self.session.commit()
            print(f"Deleted entity with ID {entity_id} from the database.")
        except SQLAlchemyError as e:
            print(f"Error deleting entity with ID {entity_id}: {e}")
            self.session.rollback()

    # ExcursionModel
    def save_excursion(self, excursion: Excursion) -> None:
        print("Saving excursion")
        self.save_entity(ExcursionModel, excursion, excursion.get_id())

    def delete_excursion(self, excursion_id: int) -> None:
        print("Deleting excursion")
        self.delete_entity(ExcursionModel, excursion_id)

    def save_information_part(self, information_part: InformationPart) -> None:
        print("Saving information part")
        self.save_entity(InformationPartModel, information_part, information_part.get_id())

    def delete_information_part(self, information_part_id: int) -> None:
        print("Deleting information part")
        self.delete_entity(InformationPartModel, information_part_id)

    # PointModel
    def save_point(self, point: Point) -> None:
        print("Saving point")
        self.save_entity(PointModel, point, point.get_id())

    def delete_point(self, point_id: int) -> None:
        print("Deleting point")
        self.delete_entity(PointModel, point_id)

    # UserStateModel
    def save_user_state(self, user_state: UserState) -> None:

        # self.save_entity(UserStateModel, user_state, user_state.get_user_id())
        try:
            user_state_model = user_state.to_model()  # Convert to database model
            existing = self.session.query(UserStateModel).filter_by(user_id=user_state.get_user_id()).first()
            if existing:
                self.session.merge(user_state_model)
            else:
                self.session.add(user_state_model)
            self.session.commit()
            print(f"Saved user state with ID {user_state.get_user_id()} to the database.")
        except SQLAlchemyError as e:
            print(f"Error saving user state with ID {user_state.get_user_id()}: {e}")
            self.session.rollback()

    def delete_user_state(self, user_id: int) -> None:
        print("Deleting user state")
        self.delete_entity(UserStateModel, user_id)

    def clear_database(self) -> None:
        print("Clearing database")
        try:
            # Disable foreign key checks if needed
            self.session.execute(text("SET session_replication_role = 'replica';"))

            # Iterate through all tables and clear them
            for table in reversed(Base.metadata.sorted_tables):
                print(f"Clearing table {table.name}...")
                self.session.execute(table.delete())

            # Re-enable foreign key checks
            self.session.execute(text("SET session_replication_role = 'origin';"))
            self.session.commit()
            print("All tables cleared successfully.")
        except Exception as e:
            self.session.rollback()
            print(f"Error clearing tables: {e}")
        finally:
            self.session.close()
