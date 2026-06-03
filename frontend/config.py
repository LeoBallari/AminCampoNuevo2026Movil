"""
Configuración global de la aplicación
"""
import os

# Rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# API
API_URL = "https://amincamponuevo2026movil.onrender.com"
API_TIMEOUT = 60.0

# Configuración de ventana
WINDOW_WIDTH = 380
WINDOW_HEIGHT = 680

# Temas
APP_TITLE = "Campo Movil 2026"
THEME_MODE = "LIGHT"
