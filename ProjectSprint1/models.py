from typing import List, Optional
from datetime import datetime, timedelta

# --- Core Entities ---

class Skill:
    def __init__(self, name: str):
        self.name = name

class AvailabilityWindow:
    def __init__(self, start: datetime, end: datetime):
        self.start = start
        self.end = end

class Location:
    def __init__(self, city: str, barangay: str, x: float = 0.0, y: float = 0.0):
        self.city = city
        self.barangay = barangay
        self.x = x  # For mock distance
        self.y = y

class Profile:
    def __init__(self, skills: List[Skill], availability: List[AvailabilityWindow], location: Location):
        self.skills = skills
        self.availability = availability
        self.location = location

class User:
    def __init__(self, user_id: int, name: str, profile: Profile):
        self.user_id = user_id
        self.name = name
        self.profile = profile
        self.active_request: Optional['Request'] = None
        self.match_history: List['MatchHistory'] = []

    def submit_request(self, skill: Skill, preferred_time: AvailabilityWindow):
        if self.active_request:
            raise Exception("User already has an active request.")
        req = Request(self, skill, preferred_time)
        self.active_request = req
        requests.append(req)
        return req

class Volunteer(User):
    def __init__(self, user_id: int, name: str, profile: Profile):
        super().__init__(user_id, name, profile)
        self.is_volunteer = True

class Request:
    def __init__(self, requester: User, skill: Skill, preferred_time: AvailabilityWindow):
        self.requester = requester
        self.skill = skill
        self.preferred_time = preferred_time
        self.status = 'pending'  # pending, matched, cancelled, completed
        self.created_at = datetime.now()
        self.match: Optional['Match'] = None

class Match:
    def __init__(self, request: Request, volunteer: Volunteer):
        self.request = request
        self.volunteer = volunteer
        self.status = 'proposed'  # proposed, confirmed, declined, cancelled
        self.created_at = datetime.now()
        self.confirmation: Optional['Confirmation'] = None

    def propose_match(self):
        self.status = 'proposed'
        # Add to global matches
        matches.append(self)

class Confirmation:
    def __init__(self, match: Match):
        self.match = match
        self.status = 'pending'  # pending, confirmed, declined
        self.created_at = datetime.now()

    def confirm(self):
        self.status = 'confirmed'
        self.match.status = 'confirmed'
        self.match.request.status = 'matched'

    def decline(self):
        self.status = 'declined'
        self.match.status = 'declined'
        self.match.request.status = 'pending'

class MatchHistory:
    def __init__(self, user: User, match: Match, outcome: str):
        self.user = user
        self.match = match
        self.outcome = outcome  # confirmed, declined, cancelled
        self.timestamp = datetime.now()

class Cancellation:
    def __init__(self, match: Match, reason: str):
        self.match = match
        self.reason = reason
        self.cancelled_at = datetime.now()

    def cancel(self):
        self.match.status = 'cancelled'
        self.match.request.status = 'cancelled'

class ManualRequest(Request):
    def __init__(self, requester: User, skill: Skill, preferred_time: AvailabilityWindow, notes: str):
        super().__init__(requester, skill, preferred_time)
        self.notes = notes

# --- In-memory Storage ---
users: List[User] = []
volunteers: List[Volunteer] = []
requests: List[Request] = []
matches: List[Match] = []
match_histories: List[MatchHistory] = []
cancellations: List[Cancellation] = [] 