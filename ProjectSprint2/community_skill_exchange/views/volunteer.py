import flet as ft

def VolunteerView(on_submit, skills, label="Skill to Offer"):
    skill = ft.Dropdown(
        label=label,
        options=[ft.dropdown.Option(s) for s in skills],
        width=300
    )
    message = ft.Text(value="")

    def handle_submit(e):
        try:
            on_submit(skill.value, message)
        except Exception as ex:
            message.value = f"Error: {ex}"
            e.page.update()

    submit_btn = ft.ElevatedButton("Volunteer", on_click=handle_submit)

    return ft.Column([
        ft.Text("Volunteer Your Skill", style="headlineMedium"),
        skill, submit_btn, message
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER) 