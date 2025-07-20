from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from community_skill_exchange.database import Base
from datetime import datetime, timedelta

class Match(Base):
    __tablename__ = 'matches'
    id = Column(Integer, primary_key=True)
    request_id = Column(Integer, ForeignKey('requests.id'))
    volunteer_id = Column(Integer, ForeignKey('volunteers.id'))
    status = Column(String, default='pending')  # pending, confirmed, cancelled, expired
    created_at = Column(DateTime, default=datetime.utcnow)
    confirmed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)  # 48h window

    request = relationship('Request')
    volunteer = relationship('Volunteer') 