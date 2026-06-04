"""
Punto de entrada de la aplicación
Aplicación móvil Campo 2026 - Login y Menú
"""
import flet as ft
from config import BASE_DIR, APP_TITLE, THEME_MODE, WINDOW_WIDTH, WINDOW_HEIGHT
from screens.login_screen import LoginScreen
import sys
from screens.menu_screen import MenuScreen
from screens.config_screen import ConfigScreen
import os

class App:
    """Controlador principal de la aplicación"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        
        # Asegurar que el directorio raíz de frontend esté en el path
        if BASE_DIR not in sys.path:
            sys.path.append(BASE_DIR)
            
        self.usuario_actual = None
        
        # Configurar página usando la sintaxis moderna para Windows
        self.page.title = APP_TITLE
        self.page.theme_mode = THEME_MODE
        self.page.window.width = WINDOW_WIDTH
        self.page.window.height = WINDOW_HEIGHT
        self.page.window.resizable = False
        # Icono para la ventana de escritorio
        self.page.window.icon = os.path.join("assets", "icon.png")

        if self.page.platform == ft.PagePlatform.ANDROID:
            self.page.window.full_screen = True
        
        # Asignar eventos de navegación
        self.page.on_route_change = self.on_route_change
        self.page.on_view_pop = self.on_view_pop
        
    def on_login_success(self, usuario_nombre: str):
        """Callback cuando el login es exitoso"""
        self.usuario_actual = usuario_nombre
        self.page.go("/menu")
    
    def on_logout(self):
        """Callback cuando el usuario se desconecta"""
        self.usuario_actual = None
        self.page.go("/")
        
    def on_route_change(self, e):
        """Manejador central de cambios de pantalla"""
        # No limpiamos la pila si vamos al detalle, para permitir que se apile
        # sobre la pantalla de despachos principal.
        if self.page.route != "/despachos/detalle":
            self.page.views.clear()
        
        # 1. Pantalla de Login
        if self.page.route == "/":
            login_screen = LoginScreen(self.page, on_login_success=self.on_login_success)
            self.page.views.append(login_screen.show())
            
        # 2. Pantalla de Menú Principal
        elif self.page.route == "/menu":
            menu_screen = MenuScreen(self.page, self.usuario_actual, on_logout=self.on_logout)
            self.page.views.append(menu_screen.show())
        
        elif self.page.route == "/config":
            self.page.views.append(ConfigScreen(self.page).show())
        
        elif self.page.route == "/despachos":
            from screens.despachos_screen import DespachosScreen
            self.page.views.append(DespachosScreen(self.page).show())

        elif self.page.route == "/despachos/detalle":
            # La vista de detalle ya se construye desde DespachosScreen.
            # No agregamos una nueva vista aquí para evitar duplicados.
            pass

        self.page.update()
        
    def on_view_pop(self, e):
        """Maneja el retroceso de pantalla nativo"""
        if len(self.page.views) > 1:
            self.page.views.pop()
            top_view = self.page.views[-1]
            self.page.route = top_view.route
            self.page.update()
    
    def run(self):
        """Inicia la aplicación navegando a la raíz"""
        self.page.go("/")


def main(page: ft.Page):
    """Función principal - punto de entrada de Flet"""
    app = App(page)
    app.run()


if __name__ == "__main__":
    ft.app(target=main)