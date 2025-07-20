import flet as ft

def LoginView(on_login, on_register):
    username = ft.TextField(label="Username")
    password = ft.TextField(label="Password", password=True)
    message = ft.Text(value="")

    def handle_login(e):
        try:
            on_login(username.value, password.value, message)
        except Exception as ex:
            message.value = f"Error: {ex}"
            e.page.update()

    login_btn = ft.ElevatedButton("Login", on_click=handle_login)
    register_btn = ft.TextButton("Don't have an account? Register", on_click=lambda e: on_register())

    return ft.Column([
        ft.Text("Login", style="headlineMedium"),
        username, password,
        login_btn, register_btn, message
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER) 