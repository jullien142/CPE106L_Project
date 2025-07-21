from backend.db import SessionLocal
from backend.models import User, HelpRequest, RequestStatus
from passlib.context import CryptContext
import random
import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
skills = ["Bicycle Repair", "Tutoring", "Gardening", "Cooking", "Programming", "Carpentry", "Painting", "Pet Care"]
locations = ["CityA", "CityB", "CityC", "CityD", "CityE"]
statuses = [RequestStatus.OPEN, RequestStatus.MATCHED, RequestStatus.IN_PROGRESS, RequestStatus.COMPLETED, RequestStatus.CANCELLED]

def get_password_hash(password):
    return pwd_context.hash(password)

def seed_users_and_requests():
    db = SessionLocal()
    users = []
    for i in range(1, 51):
        username = f"user{i}"
        email = f"user{i}@example.com"
        password_hash = get_password_hash(f"pass{i}")
        skill = random.choice(skills)
        location = random.choice(locations)
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            skill_tag=skill,
            location=location,
            latitude=None,
            longitude=None
        )
        db.add(user)
        users.append(user)
    db.commit()
    db.refresh(users[0])  # Ensure users have IDs
    # Create help requests
    for user in users:
        for _ in range(random.randint(1, 3)):
            skill = random.choice(skills)
            status = random.choice(statuses)
            assigned_helper_id = None
            if status in [RequestStatus.MATCHED, RequestStatus.IN_PROGRESS, RequestStatus.COMPLETED]:
                # Assign a random helper (not the requester)
                helpers = [u for u in users if u.id != user.id and u.skill_tag == skill]
                if helpers:
                    assigned_helper_id = random.choice(helpers).id
            req = HelpRequest(
                requester_id=user.id,
                skill_needed=skill,
                status=status,
                assigned_helper_id=assigned_helper_id,
                timestamp=datetime.datetime.utcnow() - datetime.timedelta(days=random.randint(0, 30))
            )
            db.add(req)
    db.commit()
    db.close()

if __name__ == "__main__":
    seed_users_and_requests()
    print("Seeded 50 users and help requests.") 