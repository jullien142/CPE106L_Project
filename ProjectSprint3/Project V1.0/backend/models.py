from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum, Boolean
from sqlalchemy.orm import declarative_base, relationship
import enum
import datetime

Base = declarative_base()

class RequestStatus(enum.Enum):
    OPEN = "open"
    MATCHED = "matched"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True)
    password_hash = Column(String, nullable=False)
    skill_tag = Column(String, nullable=False)
    location = Column(String)  # New field for city/ZIP
    latitude = Column(Float)
    longitude = Column(Float)
    rating = Column(Float, default=0)
    rating_count = Column(Integer, default=0)
    help_requests = relationship("HelpRequest", back_populates="requester", foreign_keys='HelpRequest.requester_id')
    matches = relationship("MatchRecord", back_populates="helper", foreign_keys='MatchRecord.helper_id')

class HelpRequest(Base):
    __tablename__ = "help_requests"
    id = Column(Integer, primary_key=True)
    requester_id = Column(Integer, ForeignKey("users.id"))
    skill_needed = Column(String, nullable=False)
    status = Column(Enum(RequestStatus), default=RequestStatus.OPEN)
    assigned_helper_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    requester = relationship("User", back_populates="help_requests", foreign_keys=[requester_id])
    assigned_helper = relationship("User", foreign_keys=[assigned_helper_id])
    matches = relationship("MatchRecord", back_populates="help_request")

class MatchRecord(Base):
    __tablename__ = "match_records"
    id = Column(Integer, primary_key=True)
    help_request_id = Column(Integer, ForeignKey("help_requests.id"))
    helper_id = Column(Integer, ForeignKey("users.id"))
    accepted = Column(Boolean, default=False)
    completed = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    help_request = relationship("HelpRequest", back_populates="matches")
    helper = relationship("User", back_populates="matches") 