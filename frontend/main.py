"""
Punto de entrada de la aplicación
Aplicación móvil Campo 2026 - Login y Menú
"""
import flet as ft
from config import APP_TITLE, THEME_MODE, WINDOW_WIDTH, WINDOW_HEIGHT
from screens.login_screen import LoginScreen
from screens.menu_screen import MenuScreen


class App:
    """Controlador principal de la aplicación"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.usuario_actual = None
        
        # Configurar página
        self.page.title = APP_TITLE
        self.page.theme_mode = THEME_MODE
        self.page.window.width = WINDOW_WIDTH
        self.page.window.height = WINDOW_HEIGHT
        self.page.window.resizable = False
        
    def on_login_success(self, usuario_nombre: str):
        """Callback cuando el login es exitoso"""
        self.usuario_actual = usuario_nombre
        self.mostrar_menu()
    
    def on_logout(self):
        """Callback cuando el usuario se desconecta"""
        self.usuario_actual = None
        self.mostrar_login()
    
    def mostrar_login(self):
        """Muestra la pantalla de login"""
        login_screen = LoginScreen(self.page, on_login_success=self.on_login_success)
        login_screen.show()
    
    def mostrar_menu(self):
        """Muestra el menú principal"""
        menu_screen = MenuScreen(self.page, self.usuario_actual, on_logout=self.on_logout)
        menu_screen.show()
    
    def run(self):
        """Inicia la aplicación mostrando login"""
        self.mostrar_login()


def main(page: ft.Page):
    """Función principal - punto de entrada de Flet"""
    app = App(page)
    app.run()


if __name__ == "__main__":
    ft.app(target=main)