from models import User, Volunteer, Request, Match, Confirmation, Skill, AvailabilityWindow, users, volunteers, requests, matches
from matching import MatchingEngine

class RequestController:
    @staticmethod
    def submit_request(user: User, skill: Skill, preferred_time: AvailabilityWindow):
        req = user.submit_request(skill, preferred_time)
        return req

class MatchController:
    @staticmethod
    def trigger_matching(request: Request):
        return MatchingEngine.match_request(request)

class ConfirmationController:
    @staticmethod
    def confirm_match(match: Match):
        if not match.confirmation:
            match.confirmation = Confirmation(match)
        match.confirmation.confirm()
        return match

    @staticmethod
    def decline_match(match: Match):
        if not match.confirmation:
            match.confirmation = Confirmation(match)
        match.confirmation.decline()
        return match 