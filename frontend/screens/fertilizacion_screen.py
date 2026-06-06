import flet as ft
import flet.map as ft_map

from config import MAPTILER_API_KEY
from ui_styles import UIStyles

class FertilizacionScreen:
    """Pantalla de Fertilización con integración de MapTiler"""
    
    def __init__(self, page: ft.Page):
        self.page = page

    def show(self):
        # NOTA: Debes obtener tu propia API Key en https://www.maptiler.com/cloud/
        # El siguiente es un ejemplo de cómo configurar el TileLayer con MapTiler
        MAPTILER_KEY = MAPTILER_API_KEY
        
        # Configuración del mapa centrado en una ubicación agrícola de ejemplo
        map_control = ft_map.Map(
            expand=True,
            initial_center=ft_map.MapLatitudeLongitude(-34.588, -59.704), # Ejemplo: Chacabuco, Buenos Aires
            initial_zoom=13,
            interaction_configuration=ft_map.MapInteractionConfiguration(
                flags=ft_map.MapInteractiveFlag.ALL
            ),
            layers=[
                # Capa de satélite de MapTiler (Raster Tiles)
                ft_map.TileLayer(
                    # 'hybrid' incluye etiquetas de caminos y lugares sobre el satélite
                    url_template=f"https://api.maptiler.com/maps/hybrid/{{z}}/{{x}}/{{y}}.jpg?key={MAPTILER_KEY}",
                ),
                # Capa de marcadores para identificar puntos de interés o lotes
                ft_map.MarkerLayer(
                    markers=[
                        ft_map.Marker(
                            content=ft.Icon(ft.Icons.AGRICULTURE, color=ft.Colors.LIGHT_GREEN_ACCENT_400, size=35),
                            coordinates=ft_map.MapLatitudeLongitude(-34.588, -59.704),
                        ),
                    ]
                ),
            ],
        )

        return ft.View(
            "/fertilizacion",
            appbar=UIStyles.get_appbar(
                "Módulo de Fertilización",
                on_home_click=lambda _: self.page.go("/menu")
            ),
            controls=[
                ft.Column([
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.MAP_OUTLINED, color=ft.Colors.BLUE_700),
                        title=ft.Text("Monitoreo de Lotes", weight=ft.FontWeight.BOLD),
                        subtitle=ft.Text("Visualización satelital de áreas de aplicación"),
                        bgcolor=ft.Colors.SURFACE,
                    ),
                    # El mapa se expande para ocupar todo el espacio disponible
                    ft.Container(content=map_control, expand=True),
                ], expand=True),
            ],
            padding=0 # Padding cero para que el mapa se vea a pantalla completa si se desea
        )