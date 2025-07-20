from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from community_skill_exchange.database import Base
from datetime import datetime

class Request(Base):
    __tablename__ = 'requests'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    profile_id = Column(Integer, ForeignKey('profiles.id'))
    skill = Column(String, nullable=False)
    urgency = Column(Integer, nullable=False)  # 1 (low) to 5 (high)
    status = Column(String, default='pending')  # pending, matched, cancelled, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    availability = Column(String)  # YYYY-MM-DD:YYYY-MM-DD

    user = relationship('User')
    profile = relationship('Profile') 