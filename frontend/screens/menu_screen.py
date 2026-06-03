"""
Pantalla del Menú Principal
"""
import flet as ft
import os
from config import BASE_DIR

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
            # El sistema de navegación nativo ahora se dispara así:
            # self.page.go("/despachos")
            print("Navegando a Despachos")
            
        def handle_cosecha(e):
            """Maneja click en Cosecha"""
            # El sistema de navegación nativo ahora se dispara así:
            # self.page.go("/cosecha")
            print("Navegando a Cosecha")
            
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

        def menu_button(image, on_click):
            image_button = ft.Container(
                content=ft.Image(
                    src=os.path.join(BASE_DIR, image),
                    width=150,
                    height=150,
                ),
                ink=True,                  # Activa el efecto visual de onda al hacer clic
                on_click=on_click,         # Asigna la función de clic# Asigna la función de ejecución
                border_radius=8,           # Redondeado opcional para el área de clic
            )
           
            return image_button
        
        # Definición de botones
        btn_despachos = menu_button("assets/imagenes/btn_despachos.png", handle_despachos)
        btn_cosecha = menu_button("assets/imagenes/btn_cosecha.png", handle_cosecha)
        btn_siembra = menu_button("assets/imagenes/btn_siembra.png", lambda e: print("Navegando a Siembra"))
        btn_pulverizacion = menu_button("assets/imagenes/btn_pulverizacion.png", lambda e: print("Navegando a Pulverización"))
        btn_fertilizacion = menu_button("assets/imagenes/btn_fertilizantes.png", lambda e: print("Navegando a Fertilización"))
        btn_labranzas = menu_button("assets/imagenes/btn_labranzas.png", lambda e: print("Navegando a Labranzas"))
        btn_semillero = menu_button("assets/imagenes/btn_semillero.png", lambda e: print("Navegando a Semillero"))
        btn_lotes = menu_button("assets/imagenes/btn_lotes.png", lambda e: print("Navegando a Lotes"))
        btn_estadisticas = menu_button("assets/imagenes/btn_estadisticas.png", handle_estadisticas)
        btn_consumidos = menu_button("assets/imagenes/btn_consumido.png", lambda e: print("Navegando a Consumidos"))
        
        btn_settings = menu_button2("Ajustes", ft.Icons.SETTINGS, handle_settings)
        btn_perfil = menu_button2("Mi Perfil", ft.Icons.PERSON, handle_perfil)

        # === RETORNAMOS LA VISTA NATIVA ===
        return ft.View(
            route="/menu",
            appbar=ft.AppBar(
                leading=ft.Container(
                    content=ft.Image(
                        src=os.path.join(BASE_DIR, "assets/imagenes/logo_reportes.png"),
                        fit=ft.ImageFit.CONTAIN,
                    ),
                    padding=5,
                ),
                title=ft.Text("CAMPO MOVIL", size=20, weight="bold"),
                bgcolor=ft.Colors.BLUE_GREY_900,
                color=ft.Colors.WHITE,
                center_title=False,
                actions=[
                    ft.IconButton(ft.Icons.NOTIFICATIONS, icon_color=ft.Colors.WHITE, on_click=lambda _: print("Notificaciones")),
                    ft.IconButton(ft.Icons.LOGOUT, icon_color=ft.Colors.WHITE, on_click=handle_logout),
                ],
            ),
            vertical_alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(height=10),  # Espaciador superior
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                [btn_despachos, btn_cosecha],
                                alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                                spacing=15,
                            ),
                            ft.Row(
                                [btn_siembra, btn_pulverizacion],
                                alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                                spacing=15,
                            ),
                            ft.Row(
                                [btn_fertilizacion, btn_labranzas],
                                alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                                spacing=15,
                            ),
                            ft.Row(
                                [btn_semillero, btn_lotes],
                                alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                                spacing=15,
                            ),
                            ft.Row(
                                [btn_estadisticas, btn_consumidos],
                                alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                                spacing=15,
                            ),
                            ft.Divider(height=40, thickness=1, color=ft.Colors.BLUE_GREY_100),
                            ft.Row(
                                [btn_perfil, btn_settings],
                                alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                            ),
                        ],
                        spacing=10,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        scroll=ft.ScrollMode.HIDDEN,
                    ),
                    expand=True,
                    padding=20
                )
            ]
        )