from models import *
from controllers import RequestController, MatchController, ConfirmationController
from services import VisualizationService
from datetime import datetime, timedelta

# --- Mock Data Setup ---

def create_mock_users():
    skill_a = Skill("First Aid")
    skill_b = Skill("Cooking")
    avail1 = AvailabilityWindow(datetime.now(), datetime.now() + timedelta(hours=2))
    avail2 = AvailabilityWindow(datetime.now() + timedelta(hours=1), datetime.now() + timedelta(hours=3))
    loc1 = Location("CityA", "Barangay1", x=0, y=0)
    loc2 = Location("CityA", "Barangay2", x=3, y=4)
    profile1 = Profile([skill_a], [avail1], loc1)
    profile2 = Profile([skill_a, skill_b], [avail1, avail2], loc2)
    user1 = User(1, "Alice", profile1)
    volunteer1 = Volunteer(2, "Bob", profile2)
    users.append(user1)
    volunteers.append(volunteer1)
    return user1, volunteer1, skill_a, avail1

if __name__ == "__main__":
    user, volunteer, skill, avail = create_mock_users()
    print(f"Registered users: {[u.name for u in users]}")
    print(f"Registered volunteers: {[v.name for v in volunteers]}")

    # User submits a request
    req = RequestController.submit_request(user, skill, avail)
    print(f"Request submitted by {user.name} for skill {skill.name}")

    # Trigger matching
    match = MatchController.trigger_matching(req)
    if match:
        print(f"Match found: {match.request.requester.name} <-> {match.volunteer.name}")
        # Confirm the match
        ConfirmationController.confirm_match(match)
        print(f"Match status: {match.status}")
    else:
        print("No match found.")

    # Show metrics
    VisualizationService.generate_metrics(users, matches, requests) 