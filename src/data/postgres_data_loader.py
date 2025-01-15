from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Dict
from src.database.models import InformationPartModel, ExcursionModel, UserStateModel, PointModel, Base
from src.components.excursion.excursion import Excursion
from src.components.excursion.point.point import Point
from src.components.excursion.point.information_part import InformationPart
from src.components.user.user_state import UserState
from src.constants import *
import logging


class PostgresLoadManager:
    def __init__(self, session) -> None:
        """
        Initializes the MongoLoadManager with a SQLAlchemy session.
        """
        logging.info("Initializing PostgresLoadManager")
        self.session = session

    def load_information_part(self, point_id: int) -> List[InformationPart]:
        """Loads information parts related to a specific point."""
        logging.info(f"Loading information parts for point {point_id}")
        try:
            data = self.session.query(InformationPartModel).filter_by(parent_id=point_id).all()
            information_parts = list()
            for part in data:
                information_part = InformationPart(
                    information_point_id=part.id,
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
                if part.id > InformationPart.information_part_id:
                    InformationPart.information_part_id = part.id
                information_parts.append(information_part)
            logging.info(f"Found {len(information_parts)} information parts for point {point_id}")
            return information_parts
        except SQLAlchemyError as e:
            logging.error(f"Error loading information parts: {e}")
            return []

    def load_points(self, excursion_id: int) -> List[Point]:
        """Loads points related to a specific excursion."""
        logging.info(f"Loading points for excursion {excursion_id}")
        try:
            data = self.session.query(PointModel).filter_by(parent_id=excursion_id).all()
            points = list()
            for point in data:
                point_obj = Point(
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
                if point.id > Point.point_id:
                    Point.point_id = point.id
                points.append(point_obj)
            logging.info(f"Found {len(points)} points for excursion {excursion_id}")
            return points
        except SQLAlchemyError as e:
            logging.error(f"Error loading points: {e}")
            return []

    def load_excursions(self) -> Dict[str, Excursion]:
        """Loads all excursions and their related points."""
        logging.info("Loading excursions")
        try:
            excursions = {}
            data = self.session.query(ExcursionModel).all()
            for excursion_data in data:
                excursion = Excursion(
                    excursion_id=excursion_data.id,
                    name=excursion_data.name or f"{DEFAULT_EXCURSION_NAME} {excursion_data.id}",
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
                if excursion.id > Excursion.excursion_id:
                    Excursion.excursion_id = excursion.id
            logging.info(f"Found {len(excursions)} excursions")
            return excursions
        except SQLAlchemyError as e:
            logging.error(f"Error loading excursions: {e}")
            return {}

    def load_user_states(self) -> Dict[int, UserState]:
        """Loads all user states."""
        logging.info("Loading user states")
        try:
            user_states = {}
            data = self.session.query(UserStateModel).all()
            for user_data in data:
                user_state = UserState(
                    username=user_data.username,
                    chat_id=user_data.chat_id,
                    user_id=user_data.user_id,
                    mode=user_data.mode or TEXT_MODE,
                    is_admin=user_data.username in ADMINS_LIST or user_data.is_admin or False,
                    paid_excursions=user_data.paid_excursions or [],
                )
                user_states[user_state.user_id] = user_state
            logging.info(f"Found {len(user_states)} user states")
            return user_states
        except SQLAlchemyError as e:
            logging.error(f"Error loading user states: {e}")
            return {}

    def save_entity(self, table, entity, entity_id):
        """Generic save method for any table."""
        logging.info(f"Saving entity {entity_id} for table {table}")
        try:
            entity_model = entity.to_model()
            existing = self.session.query(table).filter_by(id=entity_id).first()
            if existing:
                self.session.merge(entity_model)
            else:
                self.session.add(entity_model)
            self.session.commit()
            logging.info(f"Saved entity with ID {entity_id} to the database.")
        except SQLAlchemyError as e:
            logging.error(f"Error saving entity with ID {entity_id}: {e}")
            self.session.rollback()

    def delete_entity(self, table, entity_id):
        """Generic delete method for any table."""
        logging.info(f"Deleting entity with ID: {entity_id}")
        try:
            self.session.query(table).filter_by(id=entity_id).delete()
            self.session.commit()
            logging.info(f"Deleted entity with ID: {entity_id} from the database.")
        except SQLAlchemyError as e:
            logging.error(f"Error deleting entity with ID: {entity_id}: {e}")
            self.session.rollback()

    # ExcursionModel
    def save_excursion(self, excursion: Excursion) -> None:
        logging.info(f"Saving excursion {excursion.get_name()} with ID {excursion.get_id()}")
        self.save_entity(ExcursionModel, excursion, excursion.get_id())

    def delete_excursion(self, excursion_id: int) -> None:
        logging.info(f"Deleting excursion with ID: {excursion_id}")
        self.delete_entity(ExcursionModel, excursion_id)

    def save_information_part(self, information_part: InformationPart) -> None:
        logging.info(f"Saving information part {information_part.get_name()} with ID: {information_part.get_id()}")
        self.save_entity(InformationPartModel, information_part, information_part.get_id())

    def delete_information_part(self, information_part_id: int) -> None:
        logging.info(f"Deleting information part with ID: {information_part_id}")
        self.delete_entity(InformationPartModel, information_part_id)

    # PointModel
    def save_point(self, point: Point) -> None:
        logging.info(f"Saving point {point.get_name()} with ID: {point.get_id()}")
        self.save_entity(PointModel, point, point.get_id())

    def delete_point(self, point_id: int) -> None:
        logging.info(f"Deleting point with ID: {point_id}")
        self.delete_entity(PointModel, point_id)

    # UserStateModel
    def save_user_state(self, user_state: UserState) -> None:

        # self.save_entity(UserStateModel, user_state, user_state.get_user_id())
        logging.info(f"Saving user {user_state.get_username()} state with ID: {user_state.get_user_id()}")
        try:
            user_state_model = user_state.to_model()  # Convert to database model
            existing = self.session.query(UserStateModel).filter_by(user_id=user_state.get_user_id()).first()
            if existing:
                self.session.merge(user_state_model)
            else:
                self.session.add(user_state_model)
            self.session.commit()
            logging.info(f"Saved user state with ID {user_state.get_user_id()} to the database.")
        except SQLAlchemyError as e:
            logging.error(f"Error saving user state with ID {user_state.get_user_id()}: {e}")
            self.session.rollback()

    def delete_user_state(self, user_id: int) -> None:
        logging.info(f"Deleting user state with ID: {user_id}")
        self.delete_entity(UserStateModel, user_id)

    def clear_database(self) -> None:
        logging.info("Clearing database")
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
            logging.info("All tables cleared successfully.")
        except Exception as e:
            self.session.rollback()
            logging.error(f"Error clearing tables: {e}")
        # finally:
        #     self.session.close()
