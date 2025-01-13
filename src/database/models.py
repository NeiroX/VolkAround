from sqlalchemy import create_engine, Column, Integer, String, Boolean, Text, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.dialects.postgresql import JSONB

Base = declarative_base()


# Define Models
class ExcursionModel(Base):
    __tablename__ = 'excursions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    is_paid = Column(Boolean, default=False)
    likes_num = Column(Integer, default=0)
    dislikes_num = Column(Integer, default=0)
    is_draft = Column(Boolean, default=False)
    views_num = Column(Integer, default=0)
    duration = Column(Integer, default=0)
    visitors = Column(JSONB, default=[])  # JSONB field
    points = relationship("PointModel", back_populates="excursion")


class PointModel(Base):
    __tablename__ = 'points'
    id = Column(Integer, primary_key=True, autoincrement=True)
    parent_id = Column(Integer, ForeignKey('excursions.id'))
    name = Column(String, nullable=False)
    address = Column(String, default="")
    location_photo = Column(String)
    location_link = Column(String)
    photos = Column(JSONB, default=[])  # JSONB field
    audio = Column(JSONB, default=[])  # JSONB field
    text = Column(Text, default="")
    link = Column(String)
    views_num = Column(Integer, default=0)
    likes_num = Column(Integer, default=0)
    dislikes_num = Column(Integer, default=0)
    visitors = Column(JSONB, default=[])  # JSONB field
    extra_information_points = relationship("InformationPartModel", back_populates="point")
    excursion = relationship("ExcursionModel", back_populates="points")


class InformationPartModel(Base):
    __tablename__ = 'information_parts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    point_id = Column(Integer, ForeignKey('points.id'))
    parent_id = Column(Integer)
    name = Column(String, nullable=False)
    photos = Column(JSONB, default=[])  # JSONB field
    audio = Column(JSONB, default=[])  # JSONB field
    text = Column(Text, default="")
    link = Column(String)
    views_num = Column(Integer, default=0)
    likes_num = Column(Integer, default=0)
    dislikes_num = Column(Integer, default=0)
    visitors = Column(JSONB, default=[])  # JSONB field
    point = relationship("PointModel", back_populates="extra_information_points")


class UserStateModel(Base):
    __tablename__ = 'user_states'
    user_id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    mode = Column(String, default="TEXT_MODE")
    is_admin = Column(Boolean, default=False)
    paid_excursions = Column(JSONB, default=[])  # JSONB field
