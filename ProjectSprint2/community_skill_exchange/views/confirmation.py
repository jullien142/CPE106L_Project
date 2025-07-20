import flet as ft

def ConfirmationView(on_confirm, on_decline):
    message = ft.Text(value="You have a pending match. Confirm within 48 hours.")
    confirm_btn = ft.ElevatedButton("Confirm", on_click=lambda e: on_confirm(message))
    decline_btn = ft.ElevatedButton("Decline", on_click=lambda e: on_decline(message))
    return ft.Column([
        ft.Text("Match Confirmation", style="headlineMedium"),
        message,
        ft.Row([confirm_btn, decline_btn], alignment=ft.MainAxisAlignment.CENTER)
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER) 