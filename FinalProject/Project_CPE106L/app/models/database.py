from sqlalchemy import create_engine, Column, Integer, String, Float, Table, ForeignKey, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from ..config import DATABASE_URL
from datetime import datetime

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Association table for user skills
user_skills = Table(
    'user_skills',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('skill_id', Integer, ForeignKey('skills.id'))
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    location_name = Column(String)
    skills = relationship("Skill", secondary=user_skills, backref="users")

class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

class Request(Base):
    __tablename__ = "requests"
    id = Column(Integer, primary_key=True, index=True)
    requester_id = Column(Integer, ForeignKey('users.id'))
    skill_id = Column(Integer, ForeignKey('skills.id'))
    description = Column(String)
    status = Column(String, default="open")  # open, matched, closed
    created_at = Column(DateTime, default=datetime.utcnow)
    requester = relationship("User", backref="requests_made")
    skill = relationship("Skill")

class Match(Base):
    __tablename__ = "matches"
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey('requests.id'))
    volunteer_id = Column(Integer, ForeignKey('users.id'))
    matched_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="matched")  # pending, matched, completed, cancelled
    requester_complete = Column(Boolean, default=False)
    volunteer_complete = Column(Boolean, default=False)
    cancelled_by = Column(String, nullable=True)  # 'requester' or 'volunteer'
    request = relationship("Request", backref="matches")
    volunteer = relationship("User")

class Chat(Base):
    __tablename__ = "chats"
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey('matches.id'))
    match = relationship("Match", backref="chat")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey('chats.id'))
    sender_id = Column(Integer, ForeignKey('users.id'))
    content = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    chat = relationship("Chat", backref="messages")
    sender = relationship("User")

# Create tables
def init_db():
    Base.metadata.create_all(bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 