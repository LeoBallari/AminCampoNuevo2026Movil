import flet as ft
import os
from config import BASE_DIR

class ConfigScreen:
    def __init__(self, page: ft.Page):
        self.page = page

    def show(self):
        """Retorna la vista de Configuración"""
        def toggle_theme(e):
            # Cambiamos el modo y lo guardamos en el almacenamiento local
            theme_val = "dark" if e.control.value else "light"
            self.page.theme_mode = theme_val
            self.page.client_storage.set("theme_mode", theme_val)
            self.page.update()

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
                elevation=4,  # Consistencia con el resto de la app
                shadow_color=ft.Colors.BLACK,
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
                        ft.Switch(
                            label="Modo Oscuro", 
                            value=self.page.theme_mode in (ft.ThemeMode.DARK, "dark", "DARK"),
                            on_change=toggle_theme
                        ),
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