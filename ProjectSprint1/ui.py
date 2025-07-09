import flet as ft
from models import *
from controllers import RequestController, MatchController, ConfirmationController
from datetime import datetime, timedelta

# --- UI State ---
current_user = None

# --- Helper Functions ---
def get_skill_names():
    all_skills = set()
    for v in volunteers:
        for s in v.profile.skills:
            all_skills.add(s.name)
    return list(all_skills) or ["First Aid", "Cooking", "Tutoring"]

def get_user_by_name(name):
    for u in users:
        if u.name == name:
            return u
    return None

# --- Screens ---
def registration_screen(page):
    name_field = ft.TextField(label="Name")
    city_field = ft.TextField(label="City")
    barangay_field = ft.TextField(label="Barangay")
    skill_field = ft.TextField(label="Skills (comma separated)")
    is_volunteer = ft.Checkbox(label="Register as Volunteer")
    msg = ft.Text("")

    def register(e):
        name = name_field.value.strip()
        city = city_field.value.strip()
        barangay = barangay_field.value.strip()
        skills = [Skill(s.strip()) for s in skill_field.value.split(",") if s.strip()]
        if not (name and city and barangay and skills):
            msg.value = "All fields required."
            page.update()
            return
        loc = Location(city, barangay, x=0, y=0)  # x/y can be set later
        avail = [AvailabilityWindow(datetime.now(), datetime.now() + timedelta(hours=2))]
        profile = Profile(skills, avail, loc)
        if is_volunteer.value:
            user = Volunteer(len(users) + len(volunteers) + 1, name, profile)
            volunteers.append(user)
        else:
            user = User(len(users) + len(volunteers) + 1, name, profile)
            users.append(user)
        global current_user
        current_user = user
        msg.value = f"Registered as {user.name}."
        page.update()
        page.go("/request")

    return ft.View(
        "/register",
        [
            ft.Text("Registration / Login", size=24),
            name_field,
            city_field,
            barangay_field,
            skill_field,
            is_volunteer,
            ft.ElevatedButton("Register / Login", on_click=register),
            msg,
        ],
    )

def request_screen(page):
    skill_options = get_skill_names()
    skill_dropdown = ft.Dropdown(
        label="Skill Needed",
        options=[ft.dropdown.Option(s) for s in skill_options],
    )
    time_field = ft.TextField(label="Preferred Time (hours from now)", value="1")
    msg = ft.Text("")

    def submit_request(e):
        skill_name = skill_dropdown.value
        hours = int(time_field.value or "1")
        skill = Skill(skill_name)
        start = datetime.now() + timedelta(minutes=1)
        end = start + timedelta(hours=hours)
        avail = AvailabilityWindow(start, end)
        try:
            req = RequestController.submit_request(current_user, skill, avail)
            msg.value = f"Request submitted for {skill_name}."
            MatchController.trigger_matching(req)
            page.go("/dashboard")
        except Exception as ex:
            msg.value = str(ex)
        page.update()

    return ft.View(
        "/request",
        [
            ft.Text(f"Welcome, {current_user.name}", size=20),
            skill_dropdown,
            time_field,
            ft.ElevatedButton("Submit Request", on_click=submit_request),
            msg,
        ],
    )

def dashboard_screen(page):
    pending = []
    past = []
    for m in matches:
        if m.request.requester == current_user:
            if m.status in ["proposed", "confirmed"]:
                pending.append(m)
            else:
                past.append(m)
    pending_list = ft.ListView(
        controls=[
            ft.Row([
                ft.Text(f"Volunteer: {m.volunteer.name} | Status: {m.status}"),
                ft.ElevatedButton("Confirm", on_click=lambda e, m=m: confirm_match(m, page)),
                ft.ElevatedButton("Decline", on_click=lambda e, m=m: decline_match(m, page)),
            ]) for m in pending
        ],
        expand=True,
    )
    past_list = ft.ListView(
        controls=[ft.Text(f"Volunteer: {m.volunteer.name} | Status: {m.status}") for m in past],
        expand=True,
    )
    return ft.View(
        "/dashboard",
        [
            ft.Text(f"Dashboard for {current_user.name}", size=20),
            ft.Text("Pending Matches:"),
            pending_list,
            ft.Text("Past Matches:"),
            past_list,
        ],
    )

def confirm_match(match, page):
    ConfirmationController.confirm_match(match)
    page.go("/dashboard")
    page.update()

def decline_match(match, page):
    ConfirmationController.decline_match(match)
    page.go("/dashboard")
    page.update()

# --- Main App ---
def main(page: ft.Page):
    page.title = "Volunteer Matching MVP"
    page.window_width = 500
    page.window_height = 700
    def route_change(route):
        if route == "/register":
            page.views.clear()
            page.views.append(registration_screen(page))
        elif route == "/request":
            page.views.clear()
            page.views.append(request_screen(page))
        elif route == "/dashboard":
            page.views.clear()
            page.views.append(dashboard_screen(page))
        page.update()
    page.on_route_change = lambda e: route_change(page.route)
    page.go("/register")

if __name__ == "__main__":
    ft.app(target=main) 