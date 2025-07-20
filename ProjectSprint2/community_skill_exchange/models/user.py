from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from community_skill_exchange.database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

    profile = relationship('Profile', uselist=False, back_populates='user', cascade="all, delete-orphan")

class Profile(Base):
    __tablename__ = 'profiles'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    skills = Column(String)  # Comma-separated list for MVP
    availability = Column(String)  # YYYY-MM-DD
    location = Column(String)  # Location as a string

    user = relationship('User', back_populates='profile') 