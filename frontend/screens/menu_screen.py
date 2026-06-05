"""
Pantalla del Menú Principal
"""
import flet as ft
import os
from config import BASE_DIR
from ui_styles import UIStyles

class MenuScreen:
    """Pantalla del menú principal después del login"""
    
    def __init__(self, page: ft.Page, usuario_nombre: str, on_logout=None):
        self.page = page
        self.usuario_nombre = usuario_nombre
        self.on_logout = on_logout
        
    def show(self):
        """Prepara y devuelve la vista del menú para el sistema de rutas"""
        
        def handle_logout(e):
            """Maneja el logout"""
            if self.on_logout:
                self.on_logout()
        
        def handle_despachos(e):
            """Maneja click en Despachos"""
            self.page.go("/despachos")
            
        def handle_cosecha(e):
            """Maneja click en Cosecha"""
            self.page.go("/cosecha")
        
        def handle_siembra(e):
            """Maneja click en Siembra"""
            self.page.go("/siembra")
            
        def handle_estadisticas(e):
            """Maneja click en Reportes"""
            # El sistema de navegación nativo ahora se dispara así:
            # self.page.go("/despachos")
            print("Navegando a Reportes")
        
        def handle_settings(e):
            """Maneja click en Configuración"""
            self.page.go("/config")
        
        def handle_perfil(e):
            """Maneja click en Mi Perfil"""
            print("Navegando a Perfil")

        # Helper para crear botones consistentes
        def menu_button2(text, icon, on_click):
            return ft.ElevatedButton(
                content=ft.Row(
                    [
                        ft.Icon(icon, size=22),
                        ft.Text(text, size=16, weight=ft.FontWeight.W_500),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                ),
                width=140,
                height=60,
                on_click=on_click,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=10),
                )
            )

        def menu_button(image, text, on_click):
            return ft.Container(
                content=ft.Column(
                    [
                        ft.Image(
                            src=os.path.join(BASE_DIR, image),
                            width=100,
                            height=100,
                            fit=ft.ImageFit.CONTAIN,
                        ),
                        ft.Text(
                            text,
                            size=14,
                            weight=ft.FontWeight.W_600,
                            color=ft.Colors.BLUE_GREY_900, # Texto siempre oscuro para fondo blanco
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                ),
                width=160,
                height=160,
                bgcolor=ft.Colors.WHITE,
                border_radius=15,
                ink=True,
                on_click=on_click,
                padding=10,
                shadow=ft.BoxShadow(
                    blur_radius=12,
                    color=ft.Colors.with_opacity(0.15, ft.Colors.BLACK),
                    offset=ft.Offset(0, 3),
                ),
            )
        
        # Definición de botones con etiquetas de texto y estilo de tarjeta
        btn_despachos = menu_button("assets/imagenes/btn_despachos.png", "Despachos", handle_despachos)
        btn_cosecha = menu_button("assets/imagenes/btn_cosecha.png", "Cosecha", handle_cosecha)
        btn_siembra = menu_button("assets/imagenes/btn_siembra.png", "Siembra", handle_siembra)
        btn_pulverizacion = menu_button("assets/imagenes/btn_pulverizacion.png", "Pulverización", lambda e: print("Navegando a Pulverización"))
        btn_fertilizacion = menu_button("assets/imagenes/btn_fertilizantes.png", "Fertilización", lambda e: print("Navegando a Fertilización"))
        btn_labranzas = menu_button("assets/imagenes/btn_labranzas.png", "Labranzas", lambda e: print("Navegando a Labranzas"))
        btn_semillero = menu_button("assets/imagenes/btn_semillero.png", "Semillero", lambda e: print("Navegando a Semillero"))
        btn_lotes = menu_button("assets/imagenes/btn_lotes.png", "Lotes", lambda e: print("Navegando a Lotes"))
        btn_estadisticas = menu_button("assets/imagenes/btn_estadisticas.png", "Estadísticas", handle_estadisticas)
        btn_consumidos = menu_button("assets/imagenes/btn_consumido.png", "Consumidos", lambda e: print("Navegando a Consumidos"))
        
        # === RETORNAMOS LA VISTA NATIVA ===
        return ft.View(
            route="/menu",
            appbar=UIStyles.get_appbar(
                title=ft.Text(
                    spans=[
                        ft.TextSpan("CAMPO", ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)),
                        ft.TextSpan("MOVIL", ft.TextStyle(weight=ft.FontWeight.BOLD, color="#caa43d")),
                    ],
                    size=20,
                ),
                leading=ft.Container(
                    content=ft.Image(
                        src=os.path.join(BASE_DIR, "assets/imagenes/logo_reportes.png"),
                        fit=ft.ImageFit.CONTAIN,
                    ),
                    padding=5,
                ),
                actions=[
                    ft.IconButton(ft.Icons.NOTIFICATIONS, icon_color=ft.Colors.WHITE, on_click=lambda _: print("Notificaciones")),
                    ft.IconButton(ft.Icons.LOGOUT, icon_color=ft.Colors.WHITE, on_click=handle_logout),
                ],
            ),
            vertical_alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                [btn_despachos, btn_cosecha],
                                alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                                spacing=10,
                            ),
                            ft.Row(
                                [btn_siembra, btn_pulverizacion],
                                alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                                spacing=10,
                            ),
                            ft.Row(
                                [btn_fertilizacion, btn_labranzas],
                                alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                                spacing=10,
                            ),
                            ft.Row(
                                [btn_semillero, btn_lotes],
                                alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                                spacing=10,
                            ),
                            ft.Row(
                                [btn_estadisticas, btn_consumidos],
                                alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                                spacing=10,
                            ),
                        ],
                        spacing=10,
                        expand=True,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                    expand=True,
                    padding=ft.padding.only(left=5, right=5, top=15, bottom=10)
                ),
                # Footer Fijo
                ft.Container(
                    height=85,  # Aumentamos para compensar el área segura de Android
                    bgcolor="surface", # Color adaptable al tema
                    padding=ft.padding.only(left=40, right=40, top=5, bottom=20),
                    border_radius=ft.border_radius.only(top_left=20, top_right=20),
                    border=ft.border.only(top=ft.BorderSide(0.5, "outlinevariant")),
                    shadow=ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=15,
                        color=ft.Colors.with_opacity(0.15, ft.Colors.BLACK),
                        offset=ft.Offset(0, -5),  # Desplaza la sombra hacia arriba
                        blur_style=ft.ShadowBlurStyle.NORMAL,
                    ),
                    content=ft.Row(
                        [
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Icon(ft.Icons.PERSON_OUTLINE, color="onsurface", size=28),
                                        ft.Text("Perfil", size=10, weight=ft.FontWeight.W_500, color="onsurface"),
                                    ],
                                    spacing=1,
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                                on_click=handle_perfil,
                                ink=True,
                                border_radius=10,
                                padding=ft.padding.symmetric(vertical=5, horizontal=15),
                                tooltip="Mi Perfil",
                            ),
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Icon(ft.Icons.SETTINGS_OUTLINED, color="onsurface", size=28),
                                        ft.Text("Ajustes", size=10, weight=ft.FontWeight.W_500, color="onsurface"),
                                    ],
                                    spacing=1,
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                                on_click=handle_settings,
                                ink=True,
                                border_radius=10,
                                padding=ft.padding.symmetric(vertical=5, horizontal=15),
                                tooltip="Ajustes",
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.START, # Alinea iconos arriba
                    ),
                )
            ]
        )