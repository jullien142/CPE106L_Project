from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from community_skill_exchange.database import Base
from datetime import datetime

class Confirmation(Base):
    __tablename__ = 'confirmations'
    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey('matches.id'))
    status = Column(String, default='pending')  # pending, accepted, declined, expired
    responded_at = Column(DateTime, nullable=True)

    match = relationship('Match') 