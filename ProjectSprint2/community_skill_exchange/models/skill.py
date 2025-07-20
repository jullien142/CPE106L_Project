from sqlalchemy import Column, Integer, String
from community_skill_exchange.database import Base

class Skill(Base):
    __tablename__ = 'skills'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False) 