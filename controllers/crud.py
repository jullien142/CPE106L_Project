from community_skill_exchange.models import User, Profile, Request, Volunteer, Skill
from community_skill_exchange.database import SessionLocal
import hashlib
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password, skills, availability, location, session=None):
    close_session = False
    if session is None:
        session = SessionLocal()
        close_session = True
    try:
        user = User(username=username, password_hash=hash_password(password))
        profile = Profile(skills=skills, availability=availability, location=location)
        user.profile = profile
        session.add(user)
        session.commit()
        return user, None
    except SQLAlchemyError as e:
        if session:
            session.rollback()
        return None, str(e)
    finally:
        if close_session:
            session.close()

def get_user_by_username(username, session=None):
    close_session = False
    if session is None:
        session = SessionLocal()
        close_session = True
    try:
        return (
            session.query(User)
            .options(joinedload(User.profile))
            .filter_by(username=username)
            .first()
        )
    finally:
        if close_session:
            session.close()

def get_user_by_credentials(username, password, session=None):
    close_session = False
    if session is None:
        session = SessionLocal()
        close_session = True
    try:
        password_hash = hash_password(password)
        return session.query(User).filter_by(username=username, password_hash=password_hash).first()
    finally:
        if close_session:
            session.close()

def create_request(user_id, profile_id, skill, urgency, availability=None, session=None):
    close_session = False
    if session is None:
        session = SessionLocal()
        close_session = True
    try:
        request = Request(user_id=user_id, profile_id=profile_id, skill=skill, urgency=urgency, availability=availability)
        session.add(request)
        session.commit()
        return request
    finally:
        if close_session:
            session.close()

def create_volunteer(user_id, profile_id, skill, session=None):
    close_session = False
    if session is None:
        session = SessionLocal()
        close_session = True
    try:
        volunteer = Volunteer(user_id=user_id, profile_id=profile_id, skill=skill)
        session.add(volunteer)
        session.commit()
        return volunteer
    finally:
        if close_session:
            session.close()

def get_all_skills(session=None):
    close_session = False
    if session is None:
        session = SessionLocal()
        close_session = True
    try:
        skills = [s.name for s in session.query(Skill).all()]
        return sorted(skills)  # Return skills in alphabetical order
    finally:
        if close_session:
            session.close()

def update_user_info(username, password, skill, availability_start, availability_end, location, session=None):
    close_session = False
    if session is None:
        session = SessionLocal()
        close_session = True
    try:
        user = session.query(User).filter_by(username=username).first()
        if not user or not user.profile:
            return None, "User or profile not found."
        if password:
            user.password_hash = hash_password(password)
        if skill:
            user.profile.skills = skill
        if availability_start and availability_end:
            user.profile.availability = f"{availability_start}:{availability_end}"
        if location:
            user.profile.location = location
        session.commit()
        return user, None
    except Exception as e:
        if session:
            session.rollback()
        return None, str(e)
    finally:
        if close_session:
            session.close() 