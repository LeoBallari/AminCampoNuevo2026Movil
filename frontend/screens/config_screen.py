import flet as ft
import os
from config import BASE_DIR

class ConfigScreen:
    def __init__(self, page: ft.Page):
        self.page = page

    def show(self):
        """Retorna la vista de Configuración"""
        return ft.View(
            route="/config",
            # El AppBar es clave: Flet detecta que hay pantallas "abajo" 
            # en la pila y pone la flecha de volver sola.
            appbar=ft.AppBar(
                leading=ft.Container(
                    content=
                        ft.IconButton(
                            icon=ft.Icons.HOME,
                            icon_color=ft.Colors.WHITE,
                            on_click=lambda _: self.page.go("/menu")
                        ),
                    padding=5,
                ),
                title=ft.Text("Configuración"),
                bgcolor=ft.Colors.BLUE_GREY_900,
                color=ft.Colors.WHITE,
                center_title=False,
            ),
            vertical_alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    padding=30,
                    content=ft.Column([
                        ft.Icon(ft.Icons.SETTINGS, size=50, color=ft.Colors.BLUE_GREY),
                        ft.Text("Ajustes del Sistema", size=20, weight="bold"),
                        ft.Divider(),
                        ft.Switch(label="Notificaciones de Despachos", value=True),
                        ft.Switch(label="Modo Oscuro", value=False),
                        ft.TextField(label="Servidor API", value="https://render.com..."),
                        ft.Divider(),
                        # Botón manual de regreso por si no quieres usar la flecha de arriba
                        ft.ElevatedButton(
                            "Guardar y Volver", 
                            icon=ft.Icons.SAVE,
                            on_click=lambda _: self.page.go("/menu")
                        )
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                )
            ]
        )