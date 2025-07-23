import flet as ft
import httpx
from typing import List, Optional
import asyncio

class SkillExchangeApp:
    def __init__(self):
        self.page = None
        self.client = httpx.AsyncClient(base_url="http://localhost:8000")
        self.current_user = None
        self.available_skills = []

    async def initialize(self):
        # Fetch available skills
        response = await self.client.get("/skills")
        self.available_skills = response.json()["skills"]

    def build_login_view(self):
        username = ft.TextField(label="Username", width=300)
        password = ft.TextField(label="Password", password=True, width=300)
        error_text = ft.Text(color="red")

        async def login_clicked(e):
            if not username.value or not password.value:
                error_text.value = "Both username and password are required."
                self.page.update()
                return
            try:
                response = await self.client.post(
                    "/token",
                    data={
                        "username": username.value,
                        "password": password.value,
                        "grant_type": "password"
                    }
                )
                if response.status_code == 200:
                    self.current_user = username.value
                    self.page.update()
                    await asyncio.sleep(1.5)
                    await self.show_dashboard()
                else:
                    try:
                        detail = response.json()["detail"]
                    except Exception:
                        detail = f"Server error: {response.text}"
                    error_text.value = detail
                    self.page.update()
            except Exception as e:
                error_text.value = str(e)
                self.page.update()

        def switch_to_register(e):
            self.page.clean()
            self.page.add(self.build_register_view())

        return ft.Column(
            controls=[
                ft.Text("Login", size=30, weight=ft.FontWeight.BOLD),
                username,
                password,
                error_text,
                ft.ElevatedButton("Login", on_click=login_clicked),
                ft.TextButton("Don't have an account? Register", on_click=switch_to_register)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

    def build_register_view(self):
        import os
        from app.config import GOOGLE_MAPS_API_KEY
        username = ft.TextField(label="Username", width=300)
        password = ft.TextField(label="Password", password=True, width=300)
        location = ft.TextField(label="Location", width=300, autofocus=True)
        error_text = ft.Text(color="red")
        suggestions = ft.Column([])

        async def fetch_suggestions(query):
            if not query:
                return []
            url = (
                f"https://maps.googleapis.com/maps/api/place/autocomplete/json?"
                f"input={query}&key={GOOGLE_MAPS_API_KEY}"
            )
            try:
                async with httpx.AsyncClient() as client:
                    resp = await client.get(url)
                    data = resp.json()
                    return [p["description"] for p in data.get("predictions", [])]
            except Exception:
                return []

        async def on_location_change(e):
            query = location.value
            suggs = await fetch_suggestions(query)
            suggestions.controls.clear()
            for s in suggs:
                def make_on_click(suggestion):
                    def on_click(ev):
                        location.value = suggestion
                        suggestions.controls.clear()
                        self.page.update()
                    return on_click
                suggestions.controls.append(
                    ft.TextButton(s, on_click=make_on_click(s))
                )
            self.page.update()

        location.on_change = on_location_change

        async def register_clicked(e):
            if not username.value or not password.value or not location.value:
                error_text.value = "All fields are required."
                self.page.update()
                return
            try:
                response = await self.client.post(
                    "/register",
                    params={
                        "username": username.value,
                        "password": password.value,
                        "location": location.value
                    }
                )
                if response.status_code == 200:
                    self.current_user = username.value
                    await self.show_main_view()
                else:
                    try:
                        detail = response.json()["detail"]
                    except Exception:
                        detail = f"Server error: {response.text}"
                    if "already registered" in detail or "Username already" in detail:
                        error_text.value = "Username is already taken."
                    else:
                        error_text.value = detail
                    self.page.update()
            except Exception as e:
                error_text.value = str(e)
                self.page.update()

        def switch_to_login(e):
            self.page.clean()
            self.page.add(self.build_login_view())

        return ft.Column(
            controls=[
                ft.Text("Register", size=30, weight=ft.FontWeight.BOLD),
                username,
                password,
                location,
                suggestions,
                error_text,
                ft.ElevatedButton("Register", on_click=register_clicked),
                ft.TextButton("Already have an account? Login", on_click=switch_to_login)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

    async def show_dashboard(self):
        self.page.clean()
        self.dashboard_tab_index = 0
        self.dashboard_tabs = None
        self.dashboard_tab_bodies = [None, None, None]
        self.dashboard_header_row = None
        self.dashboard_tab_content = ft.Column([])
        self.dashboard_error = ft.Text(color="red")
        self.dashboard_success = ft.Text(color="green")

        def logout(e):
            self.current_user = None
            self.page.clean()
            self.page.add(self.build_login_view())

        # Fetch user's skills for display
        user_skills = []
        location_name = ""
        try:
            skills_resp = await self.client.get(f"/users/{self.current_user}/skills")
            if skills_resp.status_code == 200:
                user_skills = skills_resp.json().get("skills", [])
            profile_resp = await self.client.get(f"/users/{self.current_user}/profile")
            if profile_resp.status_code == 200:
                profile = profile_resp.json()
                location_name = profile.get("location_name", "Unknown location")
        except Exception:
            pass
        skills_str = ", ".join(user_skills) if user_skills else "No skills set"

        self.dashboard_header_row = ft.Row([
            ft.Column([
                ft.Text(f"Welcome, {self.current_user}!", size=20),
                ft.Text(f"Location: {location_name}", size=14, color="green"),
                ft.Text(f"Your skills: {skills_str}", size=14, color="blue")
            ], spacing=2),
            ft.ElevatedButton("Logout", on_click=logout)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        def render_dashboard():
            self.page.clean()
            self.page.add(self.dashboard_header_row)
            self.page.add(self.dashboard_tabs)
            self.page.add(self.dashboard_tab_content)

        def on_tab_change(e):
            self.dashboard_tab_index = e.control.selected_index
            self.page.run_task(self.load_dashboard_tab)

        self.dashboard_tabs = ft.Tabs(
            selected_index=0,
            on_change=on_tab_change,
            tabs=[
                ft.Tab(text="Request Help"),
                ft.Tab(text="Open Requests"),
                ft.Tab(text="My Matches"),
                ft.Tab(text="Messages")
            ]
        )

        async def load_request_help_tab():
            # Fetch current open/matched request or match as volunteer
            self.dashboard_tab_content.controls.clear()
            self.dashboard_error.value = ""
            self.dashboard_success.value = ""
            try:
                resp = await self.client.get(f"/matches/{self.current_user}")
                history = resp.json() if resp.status_code == 200 else []
                # Find if user is a requester or volunteer in any 'pending' status
                has_pending = False
                req_id = None
                skill_text = ""
                for item in history:
                    if item.get("type") == "request" and item.get("status") == "pending":
                        has_pending = True
                        req_id = item["id"]
                        skill_text = item["skill"]
                        break
                req_skill = ft.Dropdown(
                    label="Skill Needed",
                    options=[ft.dropdown.Option(skill) for skill in self.available_skills],
                    width=300
                )
                req_desc = ft.TextField(label="Description (optional)", width=300, multiline=True, min_lines=2, max_lines=4)
                submit_btn = ft.ElevatedButton("Submit Request")
                if has_pending:
                    # Show current request and disable form
                    controls = [
                        ft.Text("You already have a request in progress:", size=16, weight=ft.FontWeight.BOLD),
                        ft.Text(f"Skill: {skill_text}", size=14),
                        ft.Text(f"Status: pending", size=13),
                        ft.Text("You cannot submit a new request until this one is cancelled.", size=13, color="red")
                    ]
                    # Add cancel button if requester
                    if req_id:
                        def cancel_clicked(e):
                            self.page.run_task(cancel_request)
                        cancel_btn = ft.ElevatedButton("Cancel Request", on_click=cancel_clicked, color="red")
                        controls.append(cancel_btn)
                    self.dashboard_tab_content.controls.append(
                        ft.Container(
                            ft.Column(controls, spacing=2),
                            border=ft.border.all(1, "#cccccc"), padding=10, margin=5
                        )
                    )
                    async def cancel_request(e=None):
                        await self.client.post(
                            f"/requests/{req_id}/cancel",
                            params={"username": self.current_user}
                        )
                        await self.load_dashboard_tab()
                else:
                    # Show request form
                    def submit_clicked(e):
                        self.page.run_task(submit_request)
                    submit_btn.on_click = submit_clicked
                    self.dashboard_tab_content.controls.append(
                        ft.Column([
                            ft.Text("Request Help", size=22, weight=ft.FontWeight.BOLD),
                            ft.Text("Need help? Create a request for a skill and let volunteers find you!", size=14),
                            req_skill,
                            req_desc,
                            ft.Row([submit_btn]),
                        ], spacing=10)
                    )
                self.dashboard_tab_content.controls.append(self.dashboard_error)
                self.dashboard_tab_content.controls.append(self.dashboard_success)
                self.page.update()

                async def submit_request(e=None):
                    if not req_skill.value:
                        self.dashboard_error.value = "Please select a skill."
                        self.dashboard_success.value = ""
                        self.page.update()
                        return
                    try:
                        response = await self.client.post(
                            "/requests",
                            params={
                                "username": self.current_user,
                                "skill": req_skill.value,
                                "description": req_desc.value or ""
                            }
                        )
                        if response.status_code == 200:
                            self.dashboard_success.value = "Request created!"
                            self.dashboard_error.value = ""
                            req_skill.value = None
                            req_desc.value = ""
                            await self.load_dashboard_tab()
                        else:
                            self.dashboard_error.value = response.json().get("detail", "Error creating request.")
                            self.dashboard_success.value = ""
                        self.page.update()
                    except Exception as ex:
                        self.dashboard_error.value = str(ex)
                        self.dashboard_success.value = ""
                        self.page.update()

                async def cancel_request(e=None):
                    try:
                        response = await self.client.post(
                            f"/requests/{req_id}/cancel",
                            params={"username": self.current_user}
                        )
                        if response.status_code == 200:
                            self.dashboard_success.value = "Request cancelled."
                            self.dashboard_error.value = ""
                            await self.load_dashboard_tab()
                        else:
                            self.dashboard_error.value = response.json().get("detail", "Error cancelling request.")
                            self.dashboard_success.value = ""
                        self.page.update()
                    except Exception as ex:
                        self.dashboard_error.value = str(ex)
                        self.dashboard_success.value = ""
                        self.page.update()
            except Exception as ex:
                self.dashboard_error.value = str(ex)
                self.dashboard_success.value = ""
                self.page.update()

        async def load_open_requests_tab():
            self.dashboard_tab_content.controls.clear()
            self.dashboard_error.value = ""
            self.dashboard_success.value = ""
            try:
                # Get current user's location directly from profile endpoint
                profile_resp = await self.client.get(f"/users/{self.current_user}/profile")
                user_lat, user_lng = None, None
                if profile_resp.status_code == 200:
                    profile = profile_resp.json()
                    user_lat = profile.get("latitude")
                    user_lng = profile.get("longitude")
                params = {"username": self.current_user}
                if user_lat is not None and user_lng is not None:
                    params["latitude"] = user_lat
                    params["longitude"] = user_lng
                resp = await self.client.get("/requests/open", params=params)
                requests = resp.json() if resp.status_code == 200 else []
                # Sort requests by distance (best/closest first) if distance is available
                requests = sorted(requests, key=lambda r: (r["distance_km"] if r["distance_km"] is not None else float('inf')))
                # Get volunteer status
                matches_resp = await self.client.get(f"/matches/{self.current_user}")
                history = matches_resp.json() if matches_resp.status_code == 200 else []
                has_active_volunteer = any(item.get("type") == "match" and item.get("status") == "matched" and item.get("volunteer") == self.current_user for item in history)
                user_skills_resp = await self.client.get(f"/users/{self.current_user}/skills")
                user_skills = user_skills_resp.json().get("skills", [])
                if not requests:
                    self.dashboard_tab_content.controls.append(ft.Text("No open requests at the moment.", italic=True, color="grey"))
                else:
                    self.dashboard_tab_content.controls.append(ft.Text("Sorted by closest to farthest", size=14, color="blue", italic=True))
                scroll_column = ft.Column([], scroll=ft.ScrollMode.ALWAYS, height=400, expand=True)
                for req in requests:
                    is_own = req["requester"] == self.current_user
                    if is_own:
                        continue  # Exclude own requests
                    can_volunteer = req["skill"] in user_skills and not has_active_volunteer
                    controls = [
                        ft.Text(f"Requester: {req['requester']}", size=14, weight=ft.FontWeight.BOLD),
                        ft.Text(f"Skill: {req['skill']}", size=14),
                        ft.Text(f"Description: {req['description']}", size=13),
                        ft.Text(f"Location: {req.get('location', 'Unknown')}", size=13, color="green"),
                        ft.Text(f"Created: {req['created_at']}", size=12, italic=True)
                    ]
                    if has_active_volunteer:
                        controls.append(ft.Text("You already have an active match. Complete or cancel it before volunteering again.", size=12, color="red"))
                    elif can_volunteer:
                        def make_volunteer_handler(req_id):
                            async def volunteer_clicked(e):
                                try:
                                    match_resp = await self.client.post(
                                        f"/requests/{req_id}/match",
                                        params={"volunteer_username": self.current_user}
                                    )
                                    if match_resp.status_code == 200:
                                        self.dashboard_success.value = "You have volunteered!"
                                        self.dashboard_error.value = ""
                                        await self.load_dashboard_tab()
                                    else:
                                        self.dashboard_error.value = match_resp.json().get("detail", "Error volunteering.")
                                        self.dashboard_success.value = ""
                                    self.page.update()
                                except Exception as ex:
                                    self.dashboard_error.value = str(ex)
                                    self.dashboard_success.value = ""
                                    self.page.update()
                            return volunteer_clicked
                        controls.append(ft.ElevatedButton("Volunteer", on_click=make_volunteer_handler(req["id"])))
                    scroll_column.controls.append(ft.Container(ft.Column(controls, spacing=2), border=ft.border.all(1, "#cccccc"), padding=10, margin=5))
                self.dashboard_tab_content.controls.append(scroll_column)
                self.dashboard_tab_content.controls.append(self.dashboard_error)
                self.dashboard_tab_content.controls.append(self.dashboard_success)
                self.page.update()
            except Exception as ex:
                self.dashboard_error.value = str(ex)
                self.dashboard_success.value = ""
                self.page.update()

        async def load_my_matches_tab():
            self.dashboard_tab_content.controls.clear()
            self.dashboard_tab_content.controls.append(ft.Text("My Matches & History", size=22, weight=ft.FontWeight.BOLD))
            self.dashboard_tab_content.controls.append(ft.Text("Track your requests and volunteering history.", size=14))
            try:
                resp = await self.client.get(f"/matches/{self.current_user}")
                history = resp.json() if resp.status_code == 200 else []
                def get_time(item):
                    if item.get("type") == "match":
                        return item.get("matched_at", "")
                    return item.get("created_at", "")
                history = sorted(history, key=get_time, reverse=True)
                scroll_column = ft.Column([], scroll=ft.ScrollMode.ALWAYS)
                if not history:
                    scroll_column.controls.append(ft.Text("No history yet.", italic=True, color="grey"))
                for item in history:
                    if item.get("type") == "match":
                        cancelled_by = item.get("cancelled_by")
                        status_line = f"Status: {item['status']}"
                        # Determine the other party and their location
                        other_party = item["volunteer"] if item["requester"] == self.current_user else item["requester"]
                        location_val = item.get("location", None)
                        # Always show other party's username and location, and if it's you, add (You)
                        location_obj = item.get("location", {})
                        other_username = location_obj.get("username", "?")
                        other_location = location_obj.get("location", None)
                        if not other_location or isinstance(other_location, dict):
                            other_location = other_location.get("name", "(No location)") if isinstance(other_location, dict) else "(No location)"
                        if other_username == self.current_user:
                            name_line = f"Name: {other_username} (You)"
                        else:
                            name_line = f"Name: {other_username}"
                        location_line = f"Location: {other_location}"
                        # Format distance
                        distance_val = item.get('distance_km', 'N/A')
                        if distance_val is None or str(distance_val).lower() == 'none' or not isinstance(distance_val, (int, float)):
                            distance_val = 'N/A'
                        scroll_column.controls.append(
                            ft.Container(
                                ft.Column([
                                    ft.Text(f"Matched Request", size=16, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"Skill: {item['skill']}", size=14),
                                    ft.Text(name_line, size=13, color="purple"),
                                    ft.Text(location_line, size=13, color="green"),
                                    ft.Text(f"Status: {item['status']}", size=13),
                                    ft.Text(f"Matched at: {item['matched_at']}", size=12, italic=True)
                                ]),
                                border=ft.border.all(1, "#cccccc"), padding=10, margin=5
                            )
                        )
                    elif item.get("type") == "request":
                        # For unmatched/pending requests you cancel, show <username> (You)
                        location_display = item.get('location', {}).get('name', 'Unknown')
                        if item.get("status") == "closed" and item.get("cancelled", False):
                            location_display = f"{self.current_user} (You)"
                        scroll_column.controls.append(
                            ft.Container(
                                ft.Column([
                                    ft.Text(f"Your Request", size=16, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"Skill: {item['skill']}", size=14),
                                    ft.Text(f"Location: {location_display}", size=13, color="green"),
                                    ft.Text(f"Status: {item['status']}", size=13),
                                    ft.Text(f"Created at: {item['created_at']}", size=12, italic=True)
                                ]),
                                border=ft.border.all(1, "#cccccc"), padding=10, margin=5
                            )
                        )
                self.dashboard_tab_content.controls.append(
                    ft.Container(scroll_column, height=400, expand=True)
                )
                self.page.update()
            except Exception as ex:
                self.dashboard_tab_content.controls.append(ft.Text(f"Error loading history: {ex}", color="red"))
                self.page.update()

        async def load_messages_tab():
            self.dashboard_tab_content.controls.clear()
            self.dashboard_tab_content.controls.append(ft.Text("Messages", size=22, weight=ft.FontWeight.BOLD))
            self.dashboard_tab_content.controls.append(ft.Text("Chat with your matches. Only active (matched) chats are shown.", size=14))
            try:
                resp = await self.client.get(f"/matches/{self.current_user}")
                history = resp.json() if resp.status_code == 200 else []
                active_chats = [item for item in history if item.get("type") == "match" and item.get("status") == "matched"]
                scroll_column = ft.Column([], scroll=ft.ScrollMode.ALWAYS)
                msg_status = ft.Text(color="green")
                if not active_chats:
                    scroll_column.controls.append(ft.Text("No active chats at the moment.", italic=True, color="grey"))
                for item in active_chats:
                    match_id = item["id"]
                    chat_box = ft.Column([], scroll=ft.ScrollMode.ALWAYS, height=200)
                    msg_input = ft.TextField(label="Type a message", width=300)
                    send_btn = ft.ElevatedButton("Send")
                    complete_btn = ft.ElevatedButton("Mark as Complete")
                    cancel_btn = ft.ElevatedButton("Cancel Match", color="red")
                    def make_complete_handler(mid):
                        async def mark_complete(e):
                            try:
                                resp = await self.client.post(
                                    f"/matches/{mid}/complete",
                                    params={"username": self.current_user}
                                )
                                if resp.status_code == 200:
                                    msg_status.value = "Marked as complete!"
                                    msg_status.color = "green"
                                else:
                                    msg_status.value = resp.json().get("detail", "Error marking as complete.")
                                    msg_status.color = "red"
                                await self.load_dashboard_tab()
                            except Exception as ex:
                                msg_status.value = str(ex)
                                msg_status.color = "red"
                                self.page.update()
                        return mark_complete
                    def make_cancel_handler(mid):
                        async def cancel_match(e):
                            await self.client.post(
                                f"/matches/{mid}/cancel",
                                params={"username": self.current_user}
                            )
                            await self.load_dashboard_tab()
                        return cancel_match
                    async def load_chat():
                        chat_box.controls.clear()
                        chat_resp = await self.client.get(f"/chats/{match_id}/messages")
                        messages = chat_resp.json() if chat_resp.status_code == 200 else []
                        for m in messages:
                            chat_box.controls.append(ft.Text(f"{m['sender']}: {m['content']} ({m['timestamp']})", size=12))
                        self.page.update()
                    async def send_message(e):
                        if not msg_input.value:
                            return
                        await self.client.post(
                            f"/chats/{match_id}/message",
                            params={"sender_username": self.current_user, "content": msg_input.value}
                        )
                        msg_input.value = ""
                        await load_chat()
                    send_btn.on_click = lambda e: self.page.run_task(send_message, e)
                    # Only requester can mark as complete
                    if self.current_user == item["requester"]:
                        complete_btn.on_click = lambda e, mid=match_id: self.page.run_task(make_complete_handler(mid), e)
                    else:
                        complete_btn.disabled = True
                    cancel_btn.on_click = lambda e, mid=match_id: self.page.run_task(make_cancel_handler(mid), e)
                    await load_chat()
                    scroll_column.controls.append(
                        ft.Container(
                            ft.Column([
                                ft.Text(f"Chat with {item['volunteer'] if self.current_user != item['volunteer'] else item['requester']}", size=14, weight=ft.FontWeight.BOLD),
                                chat_box,
                                ft.Row([msg_input, send_btn]),
                                complete_btn,
                                cancel_btn,
                                msg_status
                            ], spacing=5),
                            border=ft.border.all(1, "#888888"), padding=10, margin=5
                        )
                    )
                self.dashboard_tab_content.controls.append(
                    ft.Container(scroll_column, height=400, expand=True)
                )
                self.page.update()
            except Exception as ex:
                self.dashboard_tab_content.controls.append(ft.Text(f"Error loading messages: {ex}", color="red"))
                self.page.update()

        async def load_dashboard_tab():
            if self.dashboard_tab_index == 0:
                await load_request_help_tab()
            elif self.dashboard_tab_index == 1:
                await load_open_requests_tab()
            elif self.dashboard_tab_index == 2:
                await load_my_matches_tab()
            elif self.dashboard_tab_index == 3:
                await load_messages_tab()

        self.load_dashboard_tab = load_dashboard_tab
        render_dashboard()
        self.page.run_task(load_dashboard_tab)

    async def show_main_view(self):
        self.page.clean()
        
        # Fetch user's current skills
        response = await self.client.get(f"/users/{self.current_user}/skills")
        current_skills = response.json()["skills"]
        
        skill_checkboxes = []
        selected_skills = current_skills.copy()

        selected_count_text = ft.Text(f"Selected: {len(selected_skills)}/3", size=14)

        def update_checkbox_states():
            for checkbox in skill_checkboxes:
                if not checkbox.value:
                    checkbox.disabled = len(selected_skills) >= 3
            selected_count_text.value = f"Selected: {len(selected_skills)}/3"
            save_btn.disabled = not (1 <= len(selected_skills) <= 3)
            self.page.update()

        def on_skill_changed(e):
            if e.control.value:
                if len(selected_skills) >= 3:
                    e.control.value = False
                    self.page.update()
                    return
                selected_skills.append(e.control.data)
            else:
                if e.control.data in selected_skills:
                    selected_skills.remove(e.control.data)
            update_checkbox_states()

        # Multi-column layout for skills
        columns = 2
        skill_rows = []
        for i in range(0, len(self.available_skills), columns):
            row = []
            for j in range(columns):
                idx = i + j
                if idx < len(self.available_skills):
                    skill = self.available_skills[idx]
                    checkbox = ft.Checkbox(
                        label=skill,
                        value=skill in current_skills,
                        data=skill,
                        on_change=on_skill_changed,
                        disabled=len(current_skills) >= 3 and skill not in current_skills
                    )
                    skill_checkboxes.append(checkbox)
                    row.append(checkbox)
            skill_rows.append(ft.Row(row, spacing=20))

        error_text = ft.Text(color="red")
        success_text = ft.Text(color="green")

        async def save_skills(e):
            if len(selected_skills) == 0:
                error_text.value = "You must select at least one skill."
                success_text.value = ""
                self.page.update()
                return
            try:
                response = await self.client.post(
                    f"/users/{self.current_user}/skills",
                    json=selected_skills
                )
                if response.status_code == 200:
                    success_text.value = "Skills updated successfully!"
                    error_text.value = ""
                    self.page.update()
                    await asyncio.sleep(1.5)
                    await self.show_dashboard()
                    success_text.value = ""
                else:
                    error_text.value = response.json()["detail"]
                    success_text.value = ""
                self.page.update()
            except Exception as e:
                error_text.value = str(e)
                success_text.value = ""
                self.page.update()

        def reset_skills(e):
            for cb in skill_checkboxes:
                cb.value = False
            selected_skills.clear()
            update_checkbox_states()

        def logout(e):
            self.current_user = None
            self.page.clean()
            self.page.add(self.build_login_view())

        save_btn = ft.ElevatedButton("Save Skills", on_click=save_skills, disabled=not (1 <= len(selected_skills) <= 3))
        reset_btn = ft.TextButton("Clear All", on_click=reset_skills)

        self.page.add(
            ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(f"Welcome, {self.current_user}!", size=20),
                            ft.ElevatedButton("Logout", on_click=logout)
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Text("Select up to 3 skills:", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text("Choose the skills you can offer or want to share. You must select at least 1 and at most 3.", size=14),
                    selected_count_text,
                    ft.Column(skill_rows, spacing=5),
                    ft.Row([save_btn, reset_btn], spacing=10),
                    error_text,
                    success_text
                ],
                scroll=ft.ScrollMode.AUTO
            )
        )
        update_checkbox_states()

    async def main(self, page: ft.Page):
        self.page = page
        self.page.title = "Community Skill Exchange"
        self.page.window_width = 600
        self.page.window_height = 800
        self.page.window_resizable = False
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        
        await self.initialize()
        self.page.add(self.build_login_view())

def main():
    app = SkillExchangeApp()
    ft.app(app.main) 