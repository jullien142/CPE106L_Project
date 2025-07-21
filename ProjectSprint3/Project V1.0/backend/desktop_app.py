import flet as ft
from functools import partial
import datetime
import backend.api_client as api
import random

# --- Screen Definitions ---
def welcome_screen(page, go_to_login, go_to_signup):
    return ft.Container(
        ft.Column([
            ft.Text("Community Skill Exchange", size=26, weight="bold", text_align=ft.TextAlign.CENTER, color="black"),
            ft.Text("Share and request skills in your community.", size=16, italic=True, text_align=ft.TextAlign.CENTER, color="black"),
            ft.Container(height=30),
            ft.ElevatedButton("Sign Up", on_click=lambda _: go_to_signup(), width=200),
            ft.ElevatedButton("Log In", on_click=lambda _: go_to_login(), width=200),
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=30, border=ft.border.all(1), border_radius=8, bgcolor="#fff"
    )

def login_screen(page, go_to_dashboard, go_to_welcome):
    username = ft.TextField(label="Username", width=250, color="black")
    password = ft.TextField(label="Password", password=True, width=250, color="black")
    error = ft.Text(visible=False, color="red")
    def on_login(e):
        if not username.value or not password.value:
            error.value = "Please enter both username and password."
            error.visible = True
            page.update()
            return
        try:
            resp = api.login(username.value, password.value)
            page.user = {"user_id": resp["user_id"], "username": username.value, "skill": resp["skill"]}
            if hasattr(page, 'offers_state'):
                del page.offers_state
            go_to_dashboard()
        except Exception as ex:
            msg = str(ex)
            if "401" in msg:
                error.value = "Invalid username or password."
            else:
                error.value = "Login failed. Please try again."
            error.visible = True
            page.update()
    return ft.Container(
        ft.Column([
            ft.Text("Log In", size=22, weight="bold", color="black"),
            ft.Container(height=10),
            username,
            password,
            error,
            ft.Container(height=10),
            ft.Row([
                ft.ElevatedButton("Log In", on_click=on_login, width=120),
                ft.TextButton("Back", on_click=lambda _: go_to_welcome()),
            ], alignment=ft.MainAxisAlignment.CENTER)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=30, border=ft.border.all(1), border_radius=8, bgcolor="#fff"
    )

skills_list = [
    "Bicycle Repair", "Tutoring", "Gardening", "Cooking",
    "Programming", "Carpentry", "Painting", "Pet Care"
]

def signup_screen(page, go_to_dashboard, go_to_welcome):
    username = ft.TextField(label="Username", width=250, color="black")
    password = ft.TextField(label="Password", password=True, width=250, color="black")
    skill = ft.Dropdown(label="Your Skill", options=[ft.dropdown.Option(s) for s in skills_list], width=250, color="black")
    location = ft.TextField(label="City or ZIP", width=250, color="black")
    error = ft.Text(visible=False, color="red")
    def on_signup(e):
        if not username.value or not password.value or not skill.value or not location.value:
            error.value = "Please fill all fields."
            error.visible = True
            page.update()
            return
        try:
            resp = api.signup(username.value, username.value + "@example.com", password.value, skill.value, location.value)
            page.user = {"user_id": resp["user_id"], "username": username.value, "skill": skill.value, "location": location.value}
            go_to_dashboard()
        except Exception as ex:
            msg = str(ex)
            if "400" in msg and "already in use" in msg:
                error.value = "Username or email already in use."
            elif "422" in msg:
                error.value = "Please fill all fields."
            else:
                error.value = "Sign up failed. Please try again."
            error.visible = True
            page.update()
    return ft.Container(
        ft.Column([
            ft.Text("Sign Up", size=22, weight="bold", color="black"),
            ft.Container(height=10),
            username,
            password,
            skill,
            location,
            error,
            ft.Container(height=10),
            ft.Row([
                ft.ElevatedButton("Sign Up", on_click=on_signup, width=120),
                ft.TextButton("Back", on_click=lambda _: go_to_welcome()),
            ], alignment=ft.MainAxisAlignment.CENTER)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=30, border=ft.border.all(1), border_radius=8, bgcolor="#fff"
    )

def statistics_screen(page, go_to_dashboard):
    error = ft.Text(visible=False, color="red")
    stats = {}
    try:
        stats = api.get_analytics()
    except Exception as ex:
        error.value = str(ex)
        error.visible = True
    return ft.Container(
        ft.Column([
            ft.Text("My Statistics", size=20, weight="bold", color="black"),
            error,
            ft.Text(f"Completed: {stats.get('completed', 0)}", color="black"),
            ft.Text(f"Cancelled: {stats.get('cancelled', 0)}", color="black"),
            ft.Text(f"Skill Demand: {stats.get('skill_demand', {})}", color="black"),
            ft.Text(f"Weekly Matches: {stats.get('weekly_matches', {})}", color="black"),
            ft.Container(height=10),
            ft.TextButton("Back", on_click=lambda _: go_to_dashboard()),
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=20, border=ft.border.all(1), border_radius=8, bgcolor="#fff"
    )

def dashboard_screen(page, go_to_new_request, go_to_history, go_to_offers, go_to_active, go_to_statistics, logout):
    if not hasattr(page, 'current_request'):
        page.current_request = None
    if not hasattr(page, 'history'):
        page.history = []
    skill_text = ft.Text(f"Your Skill: {page.user['skill']}", color="black", size=16)
    def cancel_request(e):
        if page.current_request:
            page.history.append({
                "name": "(You)",
                "skill": page.current_request["skill"],
                "date": get_today(),
                "status": "CANCELLED",
                "rating": None
            })
            page.current_request = None
        # Instead of calling render_dashboard, use go_to to re-render dashboard
        go_to_dashboard()
    current_req = page.current_request
    if current_req:
        req_section = ft.Container(
            ft.Row([
                ft.Text(f"Current Request: {current_req['skill']} (Status: {current_req['status']})", color="black"),
                ft.TextButton("Cancel", on_click=cancel_request)
            ]),
            border=ft.border.all(1), border_radius=6, padding=8, margin=5, bgcolor="#f8f8f8"
        )
    else:
        req_section = ft.Container(
            ft.Text("No active request.", color="black"),
            border=ft.border.all(1), border_radius=6, padding=8, margin=5, bgcolor="#f8f8f8"
        )
    return ft.Container(
        ft.Column([
            ft.Text("Dashboard", size=22, weight="bold", color="black"),
            skill_text,
            req_section,
            ft.Container(height=10),
            ft.ElevatedButton("Request", on_click=lambda _: go_to_new_request(), width=220),
            ft.ElevatedButton("Incoming Offers", on_click=lambda _: go_to_offers(), width=220),
            ft.ElevatedButton("Active Session", on_click=lambda _: go_to_active(), width=220),
            ft.ElevatedButton("History", on_click=lambda _: go_to_history(), width=220),
            ft.ElevatedButton("My Statistics", on_click=lambda _: go_to_statistics(), width=220),
            ft.Container(height=10),
            ft.TextButton("Log Out", on_click=lambda _: logout()),
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=30, border=ft.border.all(1), border_radius=8, bgcolor="#fff"
    )

def new_request_screen(page, go_to_dashboard):
    skill = ft.Dropdown(label="Skill Needed", options=[ft.dropdown.Option(s) for s in skills_list], width=250, color="black")
    error = ft.Text(visible=False, color="red")
    def on_submit(e):
        try:
            resp = api.create_request(page.user["user_id"], skill.value)
            page.current_request = {"skill": skill.value, "status": "OPEN", "request_id": resp["request_id"]}
            go_to_dashboard()
        except Exception as ex:
            error.value = str(ex)
            error.visible = True
            page.update()
    return ft.Container(
        ft.Column([
            ft.Text("New Request", size=20, weight="bold", color="black"),
            skill,
            error,
            ft.Container(height=10),
            ft.Row([
                ft.ElevatedButton("Submit Request", on_click=on_submit, width=140),
                ft.TextButton("Back", on_click=lambda _: go_to_dashboard()),
            ], alignment=ft.MainAxisAlignment.CENTER)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=30, border=ft.border.all(1), border_radius=8, bgcolor="#fff"
    )

def get_today():
    return datetime.date.today().isoformat()

def offers_screen(page, go_to_dashboard, go_to_active):
    error = ft.Text(visible=False, color="red")
    offers = []
    def load_offers():
        nonlocal offers
        offers = []
        if getattr(page, 'current_request', None) and page.current_request.get('request_id'):
            try:
                resp = api.run_matching(page.current_request['request_id'])
                offers = resp.get('candidates', [])
                for offer in offers:
                    offer['distance'] = round(random.uniform(1, 10), 1)
                offers.sort(key=lambda o: o['distance'])
            except Exception as ex:
                error.value = str(ex)
                error.visible = True
    load_offers()
    def accept_offer(offer):
        try:
            api.accept_match(page.current_request['request_id'], offer['id'])
            page.active_volunteer_session = {
                'name': offer['username'],
                'skill': offer['skill'],
                'distance': f"{offer['distance']} km",
                'id': offer['id'],
                'request_id': page.current_request['request_id']
            }
            page.current_request = None
            go_to_dashboard()
        except Exception as ex:
            error.value = str(ex)
            error.visible = True
            page.update()
    def ignore_offer(offer):
        nonlocal offers
        offers = [o for o in offers if o['id'] != offer['id']]
        page.controls.clear()
        offer_controls = []
        for o in offers:
            rating_str = f" | Rating: {o['rating']}" if o.get('rating') else ""
            offer_controls.append(
                ft.Container(
                    ft.Row([
                        ft.Text(f"{o['username']} ({o['skill']}) | Distance: {o['distance']} km{rating_str}", color="black"),
                        ft.ElevatedButton("Accept", on_click=lambda e, oo=o: accept_offer(oo), width=80),
                        ft.TextButton("Ignore", on_click=lambda e, oo=o: ignore_offer(oo)),
                    ]),
                    border=ft.border.all(1), border_radius=6, padding=8, margin=5, bgcolor="#f8f8f8"
                )
            )
        page.add(ft.Container(
            ft.Column([
                ft.Text("Incoming Offers", size=20, weight="bold", color="black"),
                error,
                ft.ListView(offer_controls, expand=1, spacing=5),
                ft.Container(height=10),
                ft.TextButton("Back", on_click=lambda _: go_to_dashboard()),
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=20, border=ft.border.all(1), border_radius=8, bgcolor="#fff", expand=True
        ))
        page.update()
        return
    offer_controls = []
    for offer in offers:
        rating_str = f" | Rating: {offer['rating']}" if offer.get('rating') else ""
        offer_controls.append(
            ft.Container(
                ft.Row([
                    ft.Text(f"{offer['username']} ({offer['skill']}) | Distance: {offer['distance']} km{rating_str}", color="black"),
                    ft.ElevatedButton("Accept", on_click=lambda e, o=offer: accept_offer(o), width=80),
                    ft.TextButton("Ignore", on_click=lambda e, o=offer: ignore_offer(o)),
                ]),
                border=ft.border.all(1), border_radius=6, padding=8, margin=5, bgcolor="#f8f8f8"
            )
        )
    return ft.Container(
        ft.Column([
            ft.Text("Incoming Offers", size=20, weight="bold", color="black"),
            error,
            ft.ListView(offer_controls, expand=1, spacing=5),
            ft.Container(height=10),
            ft.TextButton("Back", on_click=lambda _: go_to_dashboard()),
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=20, border=ft.border.all(1), border_radius=8, bgcolor="#fff", expand=True
    )

def active_session_screen(page, go_to_dashboard, go_to_rating):
    session = getattr(page, 'active_volunteer_session', None)
    error = ft.Text(visible=False, color="red")
    def mark_complete(e):
        page.session_to_rate = session
        go_to_rating()
    def cancel_session(e):
        try:
            api.cancel(session.get('request_id'))
            page.active_volunteer_session = None
            go_to_dashboard()
        except Exception as ex:
            error.value = str(ex)
            error.visible = True
            page.update()
    if session:
        return ft.Container(
            ft.Column([
                ft.Text("Active Session", size=20, weight="bold", color="black"),
                ft.Text(f"Partner: {session['name']}", color="black"),
                ft.Text(f"Skill: {session['skill']}", color="black"),
                ft.Text(f"Distance: {session['distance']}", color="black"),
                error,
                ft.Container(height=10),
                ft.Row([
                    ft.ElevatedButton("Cancel", on_click=cancel_session, width=100),
                    ft.ElevatedButton("Mark Complete", on_click=mark_complete, width=140),
                    ft.TextButton("Back", on_click=lambda _: go_to_dashboard()),
                ], alignment=ft.MainAxisAlignment.CENTER),
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=20, border=ft.border.all(1), border_radius=8, bgcolor="#fff"
        )
    else:
        return ft.Container(
            ft.Column([
                ft.Text("Active Session", size=20, weight="bold", color="black"),
                ft.Text("No active session.", color="black"),
                ft.Container(height=10),
                ft.TextButton("Back", on_click=lambda _: go_to_dashboard()),
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=20, border=ft.border.all(1), border_radius=8, bgcolor="#fff"
        )

def rating_screen(page, go_to_dashboard):
    rating = ft.Dropdown(label="Rate your helper (1-5)", options=[ft.dropdown.Option(str(i)) for i in range(1,6)], width=100, color="black")
    error = ft.Text(visible=False, color="red")
    def on_submit(e):
        if rating.value:
            try:
                session = getattr(page, 'session_to_rate', None)
                if session:
                    api.complete_session(session.get('request_id'), int(rating.value))
                page.active_volunteer_session = None
                page.session_to_rate = None
                go_to_dashboard()
            except Exception as ex:
                error.value = str(ex)
                error.visible = True
                page.update()
        else:
            error.value = "Please select a rating between 1 and 5."
            error.visible = True
            page.update()
    return ft.Container(
        ft.Column([
            ft.Text("Rate Your Helper", size=20, weight="bold", color="black"),
            rating,
            error,
            ft.Container(height=10),
            ft.Row([
                ft.ElevatedButton("Submit Rating", on_click=on_submit, width=140),
            ], alignment=ft.MainAxisAlignment.CENTER)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=20, border=ft.border.all(1), border_radius=8, bgcolor="#fff"
    )

def history_screen(page, go_to_dashboard):
    error = ft.Text(visible=False, color="red")
    history = []
    try:
        resp = api.get_history(page.user["user_id"])
        history = resp.get("history", [])
    except Exception as ex:
        error.value = str(ex)
        error.visible = True
    def partner_name(item):
        # Try to get the partner's name from the backend if possible
        # For now, just show the partner's user ID (item['partner'])
        return f"User {item['partner']}" if item.get('partner') else "-"
    return ft.Container(
        ft.Column([
            ft.Text("History", size=20, weight="bold", color="black"),
            error,
            ft.ListView([
                ft.Container(
                    ft.Row([
                        ft.Text(f"{partner_name(item)} - {item['skill']} - {item['status']} on {item['date']}" + (f" | Rating: {item['rating']}" if item['rating'] else ""), color="black"),
                    ]),
                    border=ft.border.all(1), border_radius=6, padding=8, margin=5, bgcolor="#f8f8f8"
                ) for item in history
            ], expand=1, spacing=5),
            ft.Container(height=10),
            ft.TextButton("Back", on_click=lambda _: go_to_dashboard()),
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=20, border=ft.border.all(1), border_radius=8, bgcolor="#fff", expand=True
    )

def analytics_screen(page, go_to_dashboard):
    return ft.Container(
        ft.Column([
            ft.Text("Analytics", size=20, weight="bold", color="black"),
            ft.Text("[Charts would be shown here]", color="black"),
            ft.Container(height=10),
            ft.TextButton("Back", on_click=lambda _: go_to_dashboard()),
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=20, border=ft.border.all(1), border_radius=8, bgcolor="#fff"
    )

# --- Main App Logic ---
def main(page: ft.Page):
    page.title = "Community Skill Exchange"
    page.window_width = 420
    page.window_height = 640
    page.bgcolor = "#f4f4f4"
    state = {"screen": "welcome"}

    def go_to(screen):
        state["screen"] = screen
        render()

    def render():
        page.controls.clear()
        if state["screen"] == "welcome":
            page.add(welcome_screen(page, lambda: go_to("login"), lambda: go_to("signup")))
        elif state["screen"] == "login":
            page.add(login_screen(page, lambda: go_to("dashboard"), lambda: go_to("welcome")))
        elif state["screen"] == "signup":
            page.add(signup_screen(page, lambda: go_to("dashboard"), lambda: go_to("welcome")))
        elif state["screen"] == "dashboard":
            page.add(dashboard_screen(
                page,
                lambda: go_to("new_request"),
                lambda: go_to("history"),
                lambda: go_to("offers"),
                lambda: go_to("active"),
                lambda: go_to("statistics"),
                lambda: go_to("welcome")
            ))
        elif state["screen"] == "new_request":
            page.add(new_request_screen(page, lambda: go_to("dashboard")))
        elif state["screen"] == "offers":
            page.add(offers_screen(page, lambda: go_to("dashboard"), lambda: go_to("active")))
        elif state["screen"] == "active":
            page.add(active_session_screen(page, lambda: go_to("dashboard"), lambda: go_to("rating")))
        elif state["screen"] == "rating":
            page.add(rating_screen(page, lambda: go_to("dashboard")))
        elif state["screen"] == "history":
            page.add(history_screen(page, lambda: go_to("dashboard")))
        elif state["screen"] == "analytics":
            page.add(analytics_screen(page, lambda: go_to("dashboard")))
        elif state["screen"] == "statistics":
            page.add(statistics_screen(page, lambda: go_to("dashboard")))
        page.update()

    render()

ft.app(target=main) 