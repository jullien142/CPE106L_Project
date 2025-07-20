from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from community_skill_exchange.database import Base
from datetime import datetime

class MatchHistory(Base):
    __tablename__ = 'match_history'
    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey('matches.id'))
    status = Column(String)  # success, failure, cancelled, expired
    timestamp = Column(DateTime, default=datetime.utcnow)

    match = relationship('Match') 