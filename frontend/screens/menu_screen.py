"""
Pantalla del Menú Principal
"""
import flet as ft


class MenuScreen:
    """Pantalla del menú principal después del login"""
    
    def __init__(self, page: ft.Page, usuario_nombre: str, on_logout=None):
        self.page = page
        self.usuario_nombre = usuario_nombre
        self.on_logout = on_logout
        
    def show(self):
        """Muestra la pantalla del menú"""
        self.page.clean()
        self.page.vertical_alignment = ft.MainAxisAlignment.START
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        
        def handle_logout(e):
            """Maneja el logout"""
            if self.on_logout:
                self.on_logout()
        
        def handle_reportes(e):
            """Maneja click en Reportes"""
            # TODO: Implementar pantalla de reportes
            print("Navegando a Reportes")
        
        def handle_settings(e):
            """Maneja click en Configuración"""
            # TODO: Implementar pantalla de configuración
            print("Navegando a Configuración")
        
        def handle_perfil(e):
            """Maneja click en Mi Perfil"""
            # TODO: Implementar pantalla de perfil
            print("Navegando a Perfil")
        
        # Crear botones del menú
        btn_reportes = ft.ElevatedButton(
            "📊 Reportes",
            width=300,
            height=60,
            style=ft.ButtonStyle(text_style=ft.TextStyle(size=16)),
            on_click=handle_reportes
        )
        
        btn_settings = ft.ElevatedButton(
            "⚙️ Configuración",
            width=300,
            height=60,
            style=ft.ButtonStyle(text_style=ft.TextStyle(size=16)),
            on_click=handle_settings
        )
        
        btn_perfil = ft.ElevatedButton(
            "👤 Mi Perfil",
            width=300,
            height=60,
            style=ft.ButtonStyle(text_style=ft.TextStyle(size=16)),
            on_click=handle_perfil
        )
        
        btn_logout = ft.ElevatedButton(
            "🚪 Cerrar Sesión",
            width=300,
            height=60,
            bgcolor=ft.Colors.RED_400,
            color=ft.Colors.WHITE,
            style=ft.ButtonStyle(text_style=ft.TextStyle(size=16)),
            on_click=handle_logout
        )
        
        # Use Container instead of Padding for broader compatibility
        self.page.add(
            ft.Container(
                content=ft.Text(
                    f"¡Bienvenido, {self.usuario_nombre}!",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER
                ),
                padding=20
            ),
            ft.Divider(),
            ft.Container(
                content=ft.Column(
                    controls=[
                        btn_reportes,
                        btn_settings,
                        btn_perfil,
                        ft.Divider(),
                        btn_logout
                    ],
                    spacing=10,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                ),
                padding=20
            )
        )
