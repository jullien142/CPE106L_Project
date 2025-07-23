from datetime import datetime, timedelta
from typing import Optional
import bcrypt
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from ..models.database import User
from ..config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False, "User not found"
    if not verify_password(password, user.password):
        return False, "Incorrect password"
    return True, user

def register_user(db: Session, username: str, password: str, latitude: float, longitude: float, location_name: str):
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        return False, "Username already registered"
    
    hashed_password = get_password_hash(password)
    user = User(
        username=username,
        password=hashed_password,
        latitude=latitude,
        longitude=longitude,
        location_name=location_name
    )
    
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        return True, user
    except Exception as e:
        db.rollback()
        return False, str(e) 