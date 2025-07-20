import flet as ft

def RequestView(on_submit, skills):
    skill = ft.Dropdown(
        label="Skill Needed",
        options=[ft.dropdown.Option(s) for s in skills],
        width=300
    )
    urgency = ft.Slider(min=1, max=5, divisions=4, label="Urgency (1-5)", value=3)
    availability_start = ft.TextField(label="Availability Start (YYYY-MM-DD)")
    availability_end = ft.TextField(label="Availability End (YYYY-MM-DD)")
    message = ft.Text(value="")

    def handle_submit(e):
        try:
            on_submit(
                skill.value,
                int(urgency.value),
                availability_start.value,
                availability_end.value,
                message
            )
        except Exception as ex:
            message.value = f"Error: {ex}"
            e.page.update()

    submit_btn = ft.ElevatedButton("Submit Request", on_click=handle_submit)

    return ft.Column([
        ft.Text("Submit Skill Request", style="headlineMedium"),
        skill, urgency, availability_start, availability_end, submit_btn, message
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER) 