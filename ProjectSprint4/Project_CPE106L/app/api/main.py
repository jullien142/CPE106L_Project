from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from ..models.database import get_db, User, Skill, Request, Match, Chat, Message
from ..services.auth import authenticate_user, register_user, create_access_token
from ..config import ACCESS_TOKEN_EXPIRE_MINUTES, AVAILABLE_SKILLS, MAX_SKILLS
from datetime import timedelta
import googlemaps
from ..config import GOOGLE_MAPS_API_KEY
from sqlalchemy import or_

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    success, user_or_error = authenticate_user(db, form_data.username, form_data.password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=user_or_error,
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_or_error.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register")
async def register(
    username: str,
    password: str,
    location: str,
    db: Session = Depends(get_db)
):
    try:
        # Geocode the location
        geocode_result = gmaps.geocode(location)
        if not geocode_result:
            raise HTTPException(status_code=400, detail="Invalid location")
        
        location_data = geocode_result[0]
        latitude = location_data['geometry']['location']['lat']
        longitude = location_data['geometry']['location']['lng']
        formatted_address = location_data['formatted_address']
        
        success, result = register_user(
            db, username, password, latitude, longitude, formatted_address
        )
        
        if not success:
            raise HTTPException(status_code=400, detail=result)
            
        return {
            "message": "Registration successful",
            "username": username,
            "location": formatted_address
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/skills")
async def get_available_skills():
    return {"skills": AVAILABLE_SKILLS}

@app.post("/users/{username}/skills")
async def add_user_skills(username: str, skills: List[str], db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if len(skills) > MAX_SKILLS:
        raise HTTPException(status_code=400, detail=f"Maximum {MAX_SKILLS} skills allowed")
    
    invalid_skills = [skill for skill in skills if skill not in AVAILABLE_SKILLS]
    if invalid_skills:
        raise HTTPException(status_code=400, detail=f"Invalid skills: {invalid_skills}")
    
    # Clear existing skills
    user.skills = []
    
    # Add new skills
    for skill_name in skills:
        skill = db.query(Skill).filter(Skill.name == skill_name).first()
        if not skill:
            skill = Skill(name=skill_name)
            db.add(skill)
        user.skills.append(skill)
    
    try:
        db.commit()
        return {"message": "Skills updated successfully", "skills": skills}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/users/{username}/skills")
async def get_user_skills(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"skills": [skill.name for skill in user.skills]}

@app.post("/requests")
async def create_request(
    username: str,
    skill: str,
    description: str = "",
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Prevent more than one open request per user
    existing_open = db.query(Request).filter(Request.requester_id == user.id, Request.status == "open").first()
    if existing_open:
        raise HTTPException(status_code=400, detail="You already have an open request.")
    skill_obj = db.query(Skill).filter(Skill.name == skill).first()
    if not skill_obj:
        skill_obj = Skill(name=skill)
        db.add(skill_obj)
        db.commit()
        db.refresh(skill_obj)
    req = Request(requester_id=user.id, skill_id=skill_obj.id, description=description)
    db.add(req)
    db.commit()
    db.refresh(req)
    return {"message": "Request created", "request_id": req.id}

@app.get("/requests/open")
async def list_open_requests(latitude: float = None, longitude: float = None, username: str = None, db: Session = Depends(get_db)):
    print(f"[DEBUG] /requests/open called with latitude={latitude}, longitude={longitude}, username={username}")
    reqs = db.query(Request).filter(Request.status == "open").all()
    results = []
    for r in reqs:
        distance_km = None
        if latitude is not None and longitude is not None:
            import googlemaps
            from ..config import GOOGLE_MAPS_API_KEY
            gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
            distance_result = gmaps.distance_matrix(
                origins=[(latitude, longitude)],
                destinations=[(r.requester.latitude, r.requester.longitude)],
                mode="driving",
                units="metric"
            )
            if distance_result['rows'][0]['elements'][0]['status'] == 'OK':
                distance_km = distance_result['rows'][0]['elements'][0]['distance']['value'] / 1000
            print(f"[DEBUG] Calculated distance for request {r.id}: {distance_km} km (to {r.requester.username} at {r.requester.latitude}, {r.requester.longitude})")
        results.append({
            "id": r.id,
            "requester": r.requester.username,
            "skill": r.skill.name,
            "description": r.description,
            "created_at": r.created_at.isoformat(),
            "distance_km": round(distance_km, 2) if distance_km is not None else None,
            "location": r.requester.location_name
        })
    results.sort(key=lambda x: (x["distance_km"] is None, x["distance_km"]))
    return results

@app.post("/requests/{request_id}/match")
async def match_request(request_id: int, volunteer_username: str, latitude: float = None, longitude: float = None, db: Session = Depends(get_db)):
    volunteer = db.query(User).filter(User.username == volunteer_username).first()
    if not volunteer:
        raise HTTPException(status_code=404, detail="Volunteer not found")
    # Prevent volunteering if user is already a volunteer in a matched (not completed/cancelled) match
    existing_match = db.query(Match).filter(Match.volunteer_id == volunteer.id, Match.status == "matched").first()
    if existing_match:
        raise HTTPException(status_code=400, detail="You already have an active match. Complete or cancel it before volunteering again.")
    # Find all open requests for which the volunteer has the skill
    open_reqs = db.query(Request).filter(Request.status == "open").all()
    eligible_reqs = [r for r in open_reqs if any(s.name == r.skill.name for s in volunteer.skills)]
    if not eligible_reqs:
        raise HTTPException(status_code=404, detail="No eligible open requests found")
    # Greedy: find the closest eligible request
    closest_req = None
    min_distance = float('inf')
    if latitude is not None and longitude is not None:
        import googlemaps
        from ..config import GOOGLE_MAPS_API_KEY
        gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
        for r in eligible_reqs:
            distance_result = gmaps.distance_matrix(
                origins=[(latitude, longitude)],
                destinations=[(r.requester.latitude, r.requester.longitude)],
                mode="driving",
                units="metric"
            )
            if distance_result['rows'][0]['elements'][0]['status'] == 'OK':
                distance_km = distance_result['rows'][0]['elements'][0]['distance']['value'] / 1000
                if distance_km < min_distance:
                    min_distance = distance_km
                    closest_req = r
    else:
        closest_req = eligible_reqs[0]  # fallback: just pick the first
    if not closest_req:
        raise HTTPException(status_code=404, detail="No eligible open requests found (distance calculation failed)")
    req = closest_req
    # Create match and chat
    match = Match(request_id=req.id, volunteer_id=volunteer.id, status="matched")
    req.status = "matched"
    db.add(match)
    db.commit()
    db.refresh(match)
    chat = Chat(match_id=match.id)
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return {"message": "Match created and chat started", "match_id": match.id, "chat_id": chat.id, "matched_request_id": req.id}

@app.post("/chats/{chat_id}/message")
async def send_message(chat_id: int, sender_username: str, content: str, db: Session = Depends(get_db)):
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    sender = db.query(User).filter(User.username == sender_username).first()
    if not sender:
        raise HTTPException(status_code=404, detail="Sender not found")
    msg = Message(chat_id=chat.id, sender_id=sender.id, content=content)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return {"message": "Message sent", "msg_id": msg.id, "timestamp": msg.timestamp.isoformat()}

@app.get("/chats/{chat_id}/messages")
async def get_chat_messages(chat_id: int, db: Session = Depends(get_db)):
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    messages = db.query(Message).filter(Message.chat_id == chat_id).order_by(Message.timestamp).all()
    return [
        {
            "sender": m.sender.username,
            "content": m.content,
            "timestamp": m.timestamp.isoformat()
        }
        for m in messages
    ]

@app.post("/matches/{match_id}/complete")
async def mark_match_complete(match_id: int, username: str, db: Session = Depends(get_db)):
    print(f"[DEBUG] /matches/{match_id}/complete called by {username}")
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    req = match.request
    if user.id != req.requester_id:
        raise HTTPException(status_code=403, detail="Only the requester can mark as complete")
    match.requester_complete = True
    match.status = "completed"
    req.status = "closed"
    db.commit()
    return {"message": "Marked as complete", "status": match.status}

@app.get("/matches/{username}")
async def get_user_matches(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    matches = db.query(Match).join(Request).filter(
        or_(Request.requester_id == user.id, Match.volunteer_id == user.id)
    ).all()
    own_requests = db.query(Request).filter(Request.requester_id == user.id).all()
    import googlemaps
    from ..config import GOOGLE_MAPS_API_KEY
    gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
    user_lat = user.latitude
    user_lng = user.longitude
    def calc_distance(lat1, lng1, lat2, lng2):
        if None in (lat1, lng1, lat2, lng2):
            return None
        try:
            distance_result = gmaps.distance_matrix(
                origins=[(lat1, lng1)],
                destinations=[(lat2, lng2)],
                mode="driving",
                units="metric"
            )
            if distance_result['rows'][0]['elements'][0]['status'] == 'OK':
                return round(distance_result['rows'][0]['elements'][0]['distance']['value'] / 1000, 2)
        except Exception:
            pass
        return None
    history = [
        {
            "type": "match",
            "id": m.id,
            "request_id": m.request_id,
            "volunteer": m.volunteer.username,
            "requester": m.request.requester.username,
            "skill": m.request.skill.name,
            "status": m.status,
            "matched_at": m.matched_at.isoformat(),
            "cancelled_by": m.cancelled_by,
            "location": {
                "username": (m.volunteer.username if user.username == m.request.requester.username else m.request.requester.username),
                "location": (m.volunteer.location_name if user.username == m.request.requester.username else m.request.requester.location_name)
            },
            "distance_km": calc_distance(user_lat, user_lng, (
                m.volunteer.latitude if user.username == m.request.requester.username else m.request.requester.latitude
            ), (
                m.volunteer.longitude if user.username == m.request.requester.username else m.request.requester.longitude
            ))
        }
        for m in matches
    ]
    for r in own_requests:
        if not any(h.get("request_id") == r.id for h in history):
            if r.status == "open":
                display_status = "pending"
            elif r.status == "closed":
                has_match = any(m.request_id == r.id for m in matches)
                display_status = "completed" if has_match else "closed"
            else:
                display_status = r.status
            history.append({
                "type": "request",
                "id": r.id,
                "requester": user.username,
                "volunteer": None,
                "skill": r.skill.name,
                "status": display_status,
                "created_at": r.created_at.isoformat(),
                "cancelled": display_status == "closed",
                "location": {
                    "name": r.requester.location_name,
                    "latitude": r.requester.latitude,
                    "longitude": r.requester.longitude
                },
                "distance_km": 0
            })
    return history

@app.post("/matches/{match_id}/status")
async def update_match_status(match_id: int, status: str, db: Session = Depends(get_db)):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    match.status = status
    db.commit()
    return {"message": "Match status updated", "status": status}

@app.post("/requests/{request_id}/cancel")
async def cancel_request(request_id: int, username: str, db: Session = Depends(get_db)):
    req = db.query(Request).filter(Request.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    user = db.query(User).filter(User.username == username).first()
    if not user or req.requester_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to cancel this request")
    # If matched, also cancel the match
    match = db.query(Match).filter(Match.request_id == req.id, Match.status == "matched").first()
    if match:
        match.status = "cancelled"
        match.cancelled_by = "requester"
    req.status = "closed"
    db.commit()
    return {"message": "Request cancelled"}

@app.post("/matches/{match_id}/cancel")
async def cancel_match(match_id: int, username: str, db: Session = Depends(get_db)):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    req = match.request
    # Only requester or volunteer can cancel
    if user.id not in [req.requester_id, match.volunteer_id]:
        raise HTTPException(status_code=403, detail="Not authorized to cancel this match")
    match.status = "cancelled"
    req.status = "closed"
    if user.id == req.requester_id:
        match.cancelled_by = "requester"
    elif user.id == match.volunteer_id:
        match.cancelled_by = "volunteer"
    db.commit()
    return {"message": "Match cancelled", "cancelled_by": match.cancelled_by}

@app.get("/users/nearby")
async def get_nearby_users(
    latitude: float,
    longitude: float,
    skill: str,
    radius_km: float = 10,
    db: Session = Depends(get_db)
):
    if skill not in AVAILABLE_SKILLS:
        raise HTTPException(status_code=400, detail="Invalid skill")
    
    # Simple distance calculation (this is a simplified version)
    # In production, you'd want to use PostGIS or a more sophisticated geo-query
    users = db.query(User).all()
    nearby_users = []
    
    for user in users:
        # Calculate distance using Google Maps Distance Matrix API
        distance_result = gmaps.distance_matrix(
            origins=[(latitude, longitude)],
            destinations=[(user.latitude, user.longitude)],
            mode="driving",
            units="metric"
        )
        
        if distance_result['rows'][0]['elements'][0]['status'] == 'OK':
            distance_km = distance_result['rows'][0]['elements'][0]['distance']['value'] / 1000
            if distance_km <= radius_km:
                user_skills = [skill.name for skill in user.skills]
                if skill in user_skills:
                    nearby_users.append({
                        "username": user.username,
                        "distance_km": round(distance_km, 2),
                        "location": user.location_name
                    })
    
    return {"users": sorted(nearby_users, key=lambda x: x["distance_km"])} 

@app.get("/users/{username}/profile")
async def get_user_profile(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "username": user.username,
        "location_name": user.location_name,
        "latitude": user.latitude,
        "longitude": user.longitude
    } 