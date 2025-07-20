import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import flet as ft
from community_skill_exchange.views import (
    RegistrationView, LoginView, RequestView, VolunteerView, ConfirmationView, DashboardView, InfoView
)
from community_skill_exchange.controllers import create_user, get_user_by_credentials, create_request, get_user_by_username, get_all_skills, create_volunteer, update_user_info

def main(page: ft.Page):
    page.title = "Community Skill Exchange"
    show_login = {"value": True}
    was_logged_in = {"value": False}
    selected_tab = {"value": 0}
    skills = get_all_skills()

    nav = ft.Tabs(
        selected_index=0,
        tabs=[ft.Tab(text="Register/Login")],
        visible=True
    )
    body = ft.Column([])
    page.add(nav, body)

    # Fallback color codes if ft.colors is not available
    BLUE = "#1976d2"
    WHITE = "#ffffff"
    GRAY = "#e0e0e0"
    BLACK = "#000000"

    def do_register(username, password, skill, availability_start, availability_end, location, message):
        availability = f"{availability_start}:{availability_end}" if availability_start and availability_end else ""
        user, error = create_user(username, password, skill, availability, location)
        if user:
            message.value = "Registration successful! Please log in."
            show_login["value"] = True
        else:
            message.value = f"Registration failed: {error}" if error else "Registration failed."
        page.update()

    def do_login(username, password, message):
        user = get_user_by_credentials(username, password)
        if user:
            page.session.set("user", user.username)
            message.value = f"Welcome, {user.username}!"
            show_login["value"] = False
        else:
            message.value = "Invalid credentials."
        page.update()
        show_tab(None)

    def do_logout(e=None):
        page.session.remove("user")
        show_login["value"] = True
        was_logged_in["value"] = False
        selected_tab["value"] = 0
        show_tab(None)

    def do_request(skill, urgency, availability_start, availability_end, message):
        username = page.session.get("user")
        if not username:
            message.value = "You must be logged in."
            page.update()
            return
        user = get_user_by_username(username)
        if not user or not user.profile:
            message.value = "User or profile not found."
            page.update()
            return
        availability = f"{availability_start}:{availability_end}" if availability_start and availability_end else ""
        req = create_request(user.id, user.profile.id, skill, urgency, availability)
        if req:
            message.value = "Request submitted!"
        else:
            message.value = "Failed to submit request."
        page.update()

    def do_update_info(password, skill, availability_start, availability_end, location, message):
        username = page.session.get("user")
        user, error = update_user_info(username, password, skill, availability_start, availability_end, location)
        if user:
            message.value = "Info updated!"
        else:
            message.value = f"Update failed: {error}" if error else "Update failed."
        page.update()

    def set_tab(idx):
        selected_tab["value"] = idx
        show_tab(None)

    def show_tab(e):
        logged_in = page.session.get("user") is not None
        if not logged_in:
            nav.visible = True
            tabs = [ft.Tab(text="Register/Login")]
            nav.tabs = tabs
            if nav.selected_index != 0:
                nav.selected_index = 0
            selected_tab["value"] = 0
            was_logged_in["value"] = False
            if show_login["value"]:
                body.controls = [LoginView(do_login, lambda: switch_to_register())]
            else:
                body.controls = [RegistrationView(do_register, lambda: switch_to_login(), skills)]
        else:
            nav.visible = False
            # Custom navigation row
            nav_buttons = []
            tab_names = ["Request", "Info", "Confirm", "Dashboard"]
            for i, name in enumerate(tab_names):
                nav_buttons.append(
                    ft.ElevatedButton(
                        name,
                        on_click=lambda e, idx=i: set_tab(idx),
                        style=ft.ButtonStyle(
                            bgcolor=BLUE if selected_tab["value"] == i else GRAY,
                            color=WHITE if selected_tab["value"] == i else BLACK,
                        ),
                    )
                )
            logout_btn = ft.ElevatedButton("Logout", on_click=do_logout)
            nav_row = ft.Row(nav_buttons + [logout_btn], alignment=ft.MainAxisAlignment.CENTER)
            idx = selected_tab["value"]
            if idx == 0:
                body.controls = [nav_row, RequestView(do_request, skills)]
            elif idx == 1:
                user = get_user_by_username(page.session.get("user"))
                profile = user.profile if user else None
                if user and profile:
                    body.controls = [nav_row, InfoView(user, profile, skills, do_update_info)]
                else:
                    body.controls = [nav_row, ft.Text("User or profile not found.")]
            elif idx == 2:
                body.controls = [nav_row, ConfirmationView(lambda *a, **k: None, lambda *a, **k: None)]
            elif idx == 3:
                body.controls = [nav_row, DashboardView()]
        page.update()

    def switch_to_login():
        show_login["value"] = True
        show_tab(None)

    def switch_to_register():
        show_login["value"] = False
        show_tab(None)

    nav.on_change = show_tab
    show_tab(None)

if __name__ == "__main__":
    ft.app(target=main) 