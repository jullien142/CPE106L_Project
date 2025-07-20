import flet as ft

def RegistrationView(on_register, on_login, skills):
    username = ft.TextField(label="Username")
    password = ft.TextField(label="Password", password=True)
    skill = ft.Dropdown(
        label="Skill",
        options=[ft.dropdown.Option(s) for s in skills],
        width=300
    )
    availability_start = ft.TextField(label="Availability Start (YYYY-MM-DD)")
    availability_end = ft.TextField(label="Availability End (YYYY-MM-DD)")
    location = ft.TextField(label="Location")
    message = ft.Text(value="")

    def handle_register(e):
        try:
            on_register(
                username.value,
                password.value,
                skill.value,
                availability_start.value,
                availability_end.value,
                location.value,
                message
            )
        except Exception as ex:
            message.value = f"Error: {ex}"
            e.page.update()

    register_btn = ft.ElevatedButton("Register", on_click=handle_register)
    login_btn = ft.TextButton("Already have an account? Login", on_click=lambda e: on_login())

    return ft.Column([
        ft.Text("Register New User", style="headlineMedium"),
        username, password, skill, availability_start, availability_end, location,
        register_btn, login_btn, message
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER) 