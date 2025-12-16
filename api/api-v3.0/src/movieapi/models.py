from sqlalchemy import Column, Integer, String, Date
from .database import Base

class Movie(Base):
    __tablename__ = "movie"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    year = Column(Integer)
    duration = Column(Integer, nullable=True)  # Duration in minutes

class Person(Base):
    __tablename__ = "person"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    birthdate = Column(Date, nullable=True)
