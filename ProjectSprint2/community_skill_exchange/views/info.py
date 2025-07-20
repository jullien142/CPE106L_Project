import flet as ft

def InfoView(user, profile, skills, on_update):
    password = ft.TextField(label="New Password (leave blank to keep)", password=True)
    skill = ft.Dropdown(
        label="Skill",
        options=[ft.dropdown.Option(s) for s in skills],
        value=profile.skills,
        width=300
    )
    availability_start = ft.TextField(label="Availability Start (YYYY-MM-DD)", value=profile.availability.split(":")[0] if profile.availability else "")
    availability_end = ft.TextField(label="Availability End (YYYY-MM-DD)", value=profile.availability.split(":")[1] if profile.availability and ":" in profile.availability else "")
    location = ft.TextField(label="Location", value=profile.location)
    message = ft.Text(value="")

    def handle_update(e):
        try:
            on_update(
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

    update_btn = ft.ElevatedButton("Update Info", on_click=handle_update)

    return ft.Column([
        ft.Text(f"Edit Info for {user.username}", style="headlineMedium"),
        password, skill, availability_start, availability_end, location,
        update_btn, message
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER) 