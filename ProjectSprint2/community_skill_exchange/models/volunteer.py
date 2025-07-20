from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from community_skill_exchange.database import Base
from datetime import datetime

class Volunteer(Base):
    __tablename__ = 'volunteers'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    profile_id = Column(Integer, ForeignKey('profiles.id'))
    skill = Column(String, nullable=False)
    status = Column(String, default='available')  # available, matched, unavailable
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship('User')
    profile = relationship('Profile') 