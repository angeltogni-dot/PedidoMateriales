import flet as ft

def main(page: ft.Page):
    page.title = "Prueba"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.add(
        ft.Row(
            [ft.Text("¡Hola Ángel, la app abrió!", size=22, weight=ft.FontWeight.BOLD)],
            alignment=ft.MainAxisAlignment.CENTER
        )
    )

ft.app(target=main)