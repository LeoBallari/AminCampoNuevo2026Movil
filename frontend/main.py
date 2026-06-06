"""
Punto de entrada de la aplicación
Aplicación móvil Campo 2026 - Login y Menú
"""
import flet as ft
from config import (
    BASE_DIR, 
    APP_TITLE, 
    THEME_MODE, 
    WINDOW_WIDTH, 
    WINDOW_HEIGHT, 
    API_URL, 
    API_TIMEOUT
)
from screens.login_screen import LoginScreen
import sys
from screens.menu_screen import MenuScreen
from screens.config_screen import ConfigScreen
import os
import threading
import httpx

class App:
    """Controlador principal de la aplicación"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        
        # Asegurar que el directorio raíz de frontend esté en el path
        if BASE_DIR not in sys.path:
            sys.path.append(BASE_DIR)
            
        self.usuario_actual = None
        self.despachos_screen = None  # Cache para persistir el estado
        self.cosecha_screen = None
        self.siembra_screen = None
        self.lotes_screen = None
        self.fertilizacion_screen = None
        
        # Configurar página usando la sintaxis moderna para Windows
        self.page.title = APP_TITLE
        
        # Cargar tema guardado persistentemente
        saved_theme = self.page.client_storage.get("theme_mode")
        self.page.theme_mode = saved_theme if saved_theme else THEME_MODE

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

        # Iniciar carga de datos globales en segundo plano para acelerar los filtros
        threading.Thread(target=self._pre_cargar_filtros, daemon=True).start()

    def _pre_cargar_filtros(self):
        """Carga campañas y cultivos en la sesión para acceso rápido en toda la app"""
        try:
            with httpx.Client() as client:
                # Cargar Campañas
                res_camp = client.get(f"{API_URL}/api/campañas", timeout=API_TIMEOUT)
                if res_camp.status_code == 200:
                    self.page.session.set("global_campanas", res_camp.json())
                
                # Cargar Cultivos
                res_cult = client.get(f"{API_URL}/api/cultivos", timeout=API_TIMEOUT)
                if res_cult.status_code == 200:
                    self.page.session.set("global_cultivos", res_cult.json())
        except Exception as e:
            print(f"Error pre-cargando filtros globales: {e}")
        
    def on_login_success(self, usuario_nombre: str):
        """Callback cuando el login es exitoso"""
        self.usuario_actual = usuario_nombre
        self.page.go("/menu")
    
    def on_logout(self):
        """Callback cuando el usuario se desconecta"""
        self.usuario_actual = None
        self.despachos_screen = None
        self.fertilizacion_screen = None # Limpiar cache al salir
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
            if not self.despachos_screen:
                from screens.despachos_screen import DespachosScreen
                self.despachos_screen = DespachosScreen(self.page)
            self.page.views.append(self.despachos_screen.show())

        elif self.page.route == "/cosecha":
            if not self.cosecha_screen:
                from screens.cosecha_screen import CosechaScreen
                self.cosecha_screen = CosechaScreen(self.page)
            self.page.views.append(self.cosecha_screen.show())
            
        elif self.page.route == "/siembra":
            if not self.siembra_screen:
                from screens.siembra_screen import SiembraScreen
                self.siembra_screen = SiembraScreen(self.page)
            self.page.views.append(self.siembra_screen.show())

        elif self.page.route == "/lotes":
            if not self.lotes_screen:
                from screens.lotes_screen import LotesScreen
                self.lotes_screen = LotesScreen(self.page)
            self.page.views.append(self.lotes_screen.show())
            
        elif self.page.route == "/fertilizacion":
            if not self.fertilizacion_screen:
                from screens.fertilizacion_screen import FertilizacionScreen
                self.fertilizacion_screen = FertilizacionScreen(self.page)
            self.page.views.append(self.fertilizacion_screen.show())

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