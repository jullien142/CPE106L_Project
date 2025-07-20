from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from community_skill_exchange.database import Base
from datetime import datetime

class Cancellation(Base):
    __tablename__ = 'cancellations'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    match_id = Column(Integer, ForeignKey('matches.id'))
    reason = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship('User')
    match = relationship('Match') 