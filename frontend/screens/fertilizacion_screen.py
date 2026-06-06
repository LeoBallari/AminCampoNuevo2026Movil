import flet as ft
import flet.map as ft_map

from ui_styles import UIStyles

class FertilizacionScreen:
    def __init__(self, page: ft.Page):
        self.page = page

    def show(self):
        try:
            map_control = ft_map.Map(
                expand=True,
                initial_center=ft_map.MapLatitudeLongitude(-34.588, -59.704),
                initial_zoom=13,
                keep_alive=True,
                interaction_configuration=ft_map.MapInteractionConfiguration(
                    flags=ft_map.MapInteractiveFlag.ALL
                ),
                layers=[
                    ft_map.TileLayer(
                        url_template="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
                        subdomains=["a", "b", "c"],
                        error_image_src="https://upload.wikimedia.org/wikipedia/commons/8/89/No_image_available.svg",
                        additional_options={
                            "userAgentPackageName": "com.amin.campomovil"
                        },
                        on_image_error=lambda e: print(f"TileLayer error: {e.data}"),
                    ),
                    ft_map.MarkerLayer(
                        markers=[
                            ft_map.Marker(
                                content=ft.Icon(ft.Icons.AGRICULTURE, color=ft.Colors.LIGHT_GREEN_ACCENT_400, size=35),
                                coordinates=ft_map.MapLatitudeLongitude(-34.588, -59.704),
                            ),
                        ]
                    ),
                    ft_map.SimpleAttribution(
                        text="OpenStreetMap contributors",
                        text_style=ft.TextStyle(color=ft.Colors.WHITE, size=10),
                    ),
                ],
            )
        except Exception as ex:
            map_control = ft.Container(
                expand=True,
                alignment=ft.alignment.center,
                content=ft.Text(
                    "No se pudo cargar el mapa en este dispositivo. Verifica la conexión o la configuración de MapTiler.",
                    color=ft.Colors.RED,
                    size=16,
                    text_align=ft.TextAlign.CENTER,
                ),
            )

        return ft.View(
            "/fertilizacion",
            appbar=UIStyles.get_appbar(
                "Módulo de Fertilización",
                on_home_click=lambda _: self.page.go("/menu"),
                leading=ft.IconButton(ft.Icons.ARROW_BACK, icon_color=ft.Colors.WHITE, on_click=lambda _: self.page.go("/menu"))
            ),
            controls=[
                ft.Column([
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.MAP_OUTLINED, color=ft.Colors.BLUE_700),
                        title=ft.Text("Monitoreo de Lotes", weight=ft.FontWeight.BOLD),
                        subtitle=ft.Text("Visualización satelital de áreas de aplicación"),
                        bgcolor=ft.Colors.SURFACE,
                    ),
                    ft.Container(content=ft.SafeArea(expand=True, content=map_control), expand=True),
                ], expand=True, spacing=0),
            ],
            padding=0
        )