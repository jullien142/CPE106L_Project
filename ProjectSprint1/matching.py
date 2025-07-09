from models import User, Volunteer, Request, Match, Skill, AvailabilityWindow, matches, volunteers
from services import GeoService
from datetime import datetime

class MatchingEngine:
    @staticmethod
    def find_candidates(request: Request):
        candidates = []
        for volunteer in volunteers:
            # Skill match
            if not any(s.name == request.skill.name for s in volunteer.profile.skills):
                continue
            # Availability match
            for avail in volunteer.profile.availability:
                if (avail.start <= request.preferred_time.start and avail.end >= request.preferred_time.end):
                    candidates.append(volunteer)
                    break
        return candidates

    @staticmethod
    def match_request(request: Request):
        candidates = MatchingEngine.find_candidates(request)
        if not candidates:
            print("No candidates found.")
            return None
        # Sort by proximity
        candidates.sort(key=lambda v: GeoService.calculate_distance(v.profile.location, request.requester.profile.location))
        chosen = candidates[0]
        match = Match(request, chosen)
        match.propose_match()
        request.match = match
        print(f"Match proposed: {request.requester.name} <-> {chosen.name}")
        return match 