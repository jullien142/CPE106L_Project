from community_skill_exchange.models import Request, Volunteer, Match
from community_skill_exchange.geo_service import GeoService
from community_skill_exchange.database import SessionLocal
from sqlalchemy.orm import joinedload

def find_best_volunteer_for_request(request: Request, session=None):
    """
    Greedy matching: prioritize urgency, skill match, and proximity.
    Returns the best Volunteer or None.
    """
    close_session = False
    if session is None:
        session = SessionLocal()
        close_session = True
    try:
        # Only available volunteers with matching skill
        volunteers = session.query(Volunteer).filter(
            Volunteer.skill == request.skill,
            Volunteer.status == 'available'
        ).options(joinedload(Volunteer.profile)).all()
        if not volunteers:
            return None
        # Score: urgency (request.urgency), proximity, volunteer recency
        def score(vol):
            # Lower distance is better
            req_loc = (request.profile.location_x, request.profile.location_y)
            vol_loc = (vol.profile.location_x, vol.profile.location_y)
            distance = GeoService.get_distance(req_loc, vol_loc)
            return (
                -request.urgency,  # Higher urgency first
                distance,          # Closer first
            )
        best_volunteer = min(volunteers, key=score)
        return best_volunteer
    finally:
        if close_session:
            session.close()

def create_match(request: Request, session=None):
    """
    Attempts to create a Match for the given Request.
    Returns the Match or None.
    """
    close_session = False
    if session is None:
        session = SessionLocal()
        close_session = True
    try:
        volunteer = find_best_volunteer_for_request(request, session)
        if not volunteer:
            return None
        match = Match(
            request_id=request.id,
            volunteer_id=volunteer.id,
            status='pending',
        )
        session.add(match)
        # Mark volunteer as matched
        volunteer.status = 'matched'
        request.status = 'matched'
        session.commit()
        return match
    finally:
        if close_session:
            session.close() 