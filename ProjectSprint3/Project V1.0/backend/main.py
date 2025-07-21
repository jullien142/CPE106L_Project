from fastapi import FastAPI, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from backend import models, db
from passlib.context import CryptContext
from sqlalchemy import func
from pydantic import BaseModel

app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

class SignupRequest(BaseModel):
    username: str
    email: str
    password: str
    skill: str
    location: str = None

class LoginRequest(BaseModel):
    username: str
    password: str

class SkillChangeRequest(BaseModel):
    user_id: int
    new_skill: str

@app.get("/")
def root():
    return {"message": "Skill Sharing API running"}

@app.post("/signup")
def signup(req: SignupRequest, db: Session = Depends(db.get_db)):
    if db.query(models.User).filter((models.User.username == req.username) | (models.User.email == req.email)).first():
        raise HTTPException(status_code=400, detail="Username or email already in use.")
    user = models.User(
        username=req.username,
        email=req.email,
        password_hash=get_password_hash(req.password),
        skill_tag=req.skill,
        location=req.location,
        latitude=None,
        longitude=None
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"success": True, "user_id": user.id}

@app.post("/login")
def login(req: LoginRequest, db: Session = Depends(db.get_db)):
    user = db.query(models.User).filter(models.User.username == req.username).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    return {"success": True, "user_id": user.id, "skill": user.skill_tag}

@app.post("/request")
def create_request(requester_id: int, skill: str, db: Session = Depends(db.get_db)):
    user = db.query(models.User).filter(models.User.id == requester_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Requester not found.")
    help_request = models.HelpRequest(
        requester_id=requester_id,
        skill_needed=skill,
        status=models.RequestStatus.OPEN
    )
    db.add(help_request)
    db.commit()
    db.refresh(help_request)
    return {"success": True, "request_id": help_request.id}

@app.post("/match")
def run_matching(request_id: int, db: Session = Depends(db.get_db)):
    help_request = db.query(models.HelpRequest).filter(models.HelpRequest.id == request_id).first()
    if not help_request:
        raise HTTPException(status_code=404, detail="Help request not found.")
    # Find users with matching skill and no active session (not assigned as helper in any IN_PROGRESS request)
    subq = db.query(models.HelpRequest.assigned_helper_id).filter(models.HelpRequest.status == models.RequestStatus.IN_PROGRESS)
    busy_helpers = [row[0] for row in subq if row[0] is not None]
    candidates = db.query(models.User).filter(
        models.User.skill_tag == help_request.skill_needed,
        ~models.User.id.in_(busy_helpers)
    ).all()
    result = [
        {"id": u.id, "username": u.username, "skill": u.skill_tag, "rating": u.rating, "email": u.email}
        for u in candidates
    ]
    return {"candidates": result}

@app.post("/accept")
def accept_match(request_id: int, helper_id: int, db: Session = Depends(db.get_db)):
    help_request = db.query(models.HelpRequest).filter(models.HelpRequest.id == request_id).first()
    if not help_request:
        raise HTTPException(status_code=404, detail="Help request not found.")
    if help_request.status != models.RequestStatus.OPEN and help_request.status != models.RequestStatus.MATCHED:
        raise HTTPException(status_code=400, detail="Request is not open for acceptance.")
    # Assign helper and set status
    help_request.assigned_helper_id = helper_id
    help_request.status = models.RequestStatus.IN_PROGRESS
    # Create match record
    match = models.MatchRecord(
        help_request_id=request_id,
        helper_id=helper_id,
        accepted=True,
        completed=False
    )
    db.add(match)
    db.commit()
    return {"success": True}

@app.post("/complete")
def complete_session(request_id: int, rating: int = None, db: Session = Depends(db.get_db)):
    help_request = db.query(models.HelpRequest).filter(models.HelpRequest.id == request_id).first()
    if not help_request:
        raise HTTPException(status_code=404, detail="Help request not found.")
    if help_request.status != models.RequestStatus.IN_PROGRESS:
        raise HTTPException(status_code=400, detail="Request is not in progress.")
    help_request.status = models.RequestStatus.COMPLETED
    # Update match record
    match = db.query(models.MatchRecord).filter(models.MatchRecord.help_request_id == request_id, models.MatchRecord.helper_id == help_request.assigned_helper_id).first()
    if match:
        match.completed = True
    # Update helper rating if provided
    if rating is not None and help_request.assigned_helper_id:
        helper = db.query(models.User).filter(models.User.id == help_request.assigned_helper_id).first()
        if helper:
            if helper.rating_count is None:
                helper.rating_count = 0
            if helper.rating is None:
                helper.rating = 0
            helper.rating = (helper.rating * helper.rating_count + rating) / (helper.rating_count + 1)
            helper.rating_count += 1
    db.commit()
    return {"success": True}

@app.post("/cancel")
def cancel(request_id: int, db: Session = Depends(db.get_db)):
    help_request = db.query(models.HelpRequest).filter(models.HelpRequest.id == request_id).first()
    if not help_request:
        raise HTTPException(status_code=404, detail="Help request not found.")
    if help_request.status in [models.RequestStatus.COMPLETED, models.RequestStatus.CANCELLED]:
        raise HTTPException(status_code=400, detail="Request already completed or cancelled.")
    help_request.status = models.RequestStatus.CANCELLED
    # Update match record if exists
    match = db.query(models.MatchRecord).filter(models.MatchRecord.help_request_id == request_id, models.MatchRecord.helper_id == help_request.assigned_helper_id).first()
    if match:
        match.completed = False
    db.commit()
    return {"success": True}

@app.get("/history")
def get_history(user_id: int, db: Session = Depends(db.get_db)):
    # Get all requests where user is requester or assigned helper
    requests = db.query(models.HelpRequest).filter(
        (models.HelpRequest.requester_id == user_id) | (models.HelpRequest.assigned_helper_id == user_id)
    ).all()
    history = []
    for req in requests:
        # Find rating if completed
        rating = None
        if req.status == models.RequestStatus.COMPLETED and req.assigned_helper_id:
            # Find match record
            match = db.query(models.MatchRecord).filter(
                models.MatchRecord.help_request_id == req.id,
                models.MatchRecord.helper_id == req.assigned_helper_id
            ).first()
            if match and match.completed:
                # For simplicity, assume rating is stored in match (extend model if needed)
                rating = None  # Not stored in DB yet
        history.append({
            "id": req.id,
            "skill": req.skill_needed,
            "status": req.status.value,
            "date": req.timestamp.isoformat(),
            "partner": req.assigned_helper_id if user_id == req.requester_id else req.requester_id,
            "rating": rating
        })
    return {"history": history}

@app.get("/analytics")
def get_analytics(db: Session = Depends(db.get_db)):
    # Completed/cancelled counts
    completed = db.query(models.HelpRequest).filter(models.HelpRequest.status == models.RequestStatus.COMPLETED).count()
    cancelled = db.query(models.HelpRequest).filter(models.HelpRequest.status == models.RequestStatus.CANCELLED).count()
    # Skill demand
    skill_counts = db.query(models.HelpRequest.skill_needed, func.count(models.HelpRequest.id)).group_by(models.HelpRequest.skill_needed).all()
    skill_demand = {skill: count for skill, count in skill_counts}
    # Weekly match counts (by ISO week)
    week_counts = db.query(
        func.strftime('%Y-%W', models.HelpRequest.timestamp),
        func.count(models.HelpRequest.id)
    ).filter(models.HelpRequest.status == models.RequestStatus.COMPLETED).group_by(func.strftime('%Y-%W', models.HelpRequest.timestamp)).all()
    weekly_matches = {week: count for week, count in week_counts}
    return {
        "completed": completed,
        "cancelled": cancelled,
        "skill_demand": skill_demand,
        "weekly_matches": weekly_matches
    }

@app.post("/change_skill")
def change_skill(req: SkillChangeRequest, db: Session = Depends(db.get_db)):
    user = db.query(models.User).filter(models.User.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user.skill_tag = req.new_skill
    # Clear all requests as requester
    db.query(models.HelpRequest).filter(models.HelpRequest.requester_id == req.user_id).delete()
    # Clear all requests as helper
    db.query(models.HelpRequest).filter(models.HelpRequest.assigned_helper_id == req.user_id).delete()
    db.commit()
    return {"success": True, "new_skill": req.new_skill} 