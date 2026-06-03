"""
Pantalla de Login - Adaptada a Vistas Modernas y Segura para Android
"""
import flet as ft
import threading
import os
import time
from config import BASE_DIR
from services.auth_service import AuthService


class LoginScreen:
    """Pantalla de login de la aplicación"""
    
    def __init__(self, page: ft.Page, on_login_success=None):
        self.page = page
        self.on_login_success = on_login_success
        
    def show(self):
        """Prepara y devuelve la vista de la pantalla de login"""
        # Eliminamos self.page.clean() ya que Flet maneja la limpieza mediante rutas
        
        # Elementos de UI
        txt_user = ft.TextField(label="Usuario", width=300, prefix_icon=ft.Icons.PERSON)
        txt_pass = ft.TextField(
            label="Contraseña",
            width=300,
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK
        )
        status_text = ft.Text(
            "",
            size=14,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER
        )
        loading = ft.ProgressRing(visible=False, width=24, height=24)

        def intentar_login(e):
            """Maneja el click en el botón de login"""
            # === MODO DESARROLLO (Bypass Local rápido) ===
            # Si ponés '13' y '13', entra directo sin ir a Render ni esperar 1 minuto
            if txt_user.value == "13" and txt_pass.value == "13":
                status_text.color = ft.Colors.GREEN
                status_text.value = "⚡ Modo Desarrollo: Acceso Local Directo"
                self.page.update()
                
                import time
                time.sleep(0.5) # Un mini delay para ver el cartel
                
                if self.on_login_success:
                    self.on_login_success("Desarrollador")
                return
            # =============================================

            # Validación normal de campos
            if not txt_user.value or not txt_pass.value:
                status_text.value = "⚠️ Completa todos los campos"
                status_text.color = ft.Colors.ORANGE
                self.page.update()
                return

            # Mostrar carga real (Conexión a Render)
            loading.visible = True
            status_text.value = "Despertando servidor...\nEsto puede demorar hasta 1 minuto si estaba inactivo."
            status_text.color = ft.Colors.BLUE_700
            btn_login.disabled = True
            self.page.update()

            def fetch():
                """Realiza el login en background conectando a la API"""
                result = AuthService.login(txt_user.value, txt_pass.value)
                
                loading.visible = False
                btn_login.disabled = False
                status_text.color = ft.Colors.GREEN if result['success'] else ft.Colors.RED
                status_text.value = result['message']
                self.page.update()
                
                if result['success']:
                    import time
                    time.sleep(1.0)
                    if self.on_login_success:
                        self.on_login_success(txt_user.value)

            threading.Thread(target=fetch, daemon=True).start()

        btn_login = ft.ElevatedButton(
            "Entrar al Sistema",
            on_click=intentar_login,
            width=300
        )
        
        # Imagen de bienvenida
        imagen = ft.Image(
            src=os.path.join(BASE_DIR, "assets/imagenes/candado.png"),
            width=100,
            height=100
        )
        
        # === RETORNO DE VISTA NATIVA ===
        return ft.View(
            route="/",
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                imagen,
                ft.Text("Campo Movil 2026", size=24, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                txt_user,
                txt_pass,
                loading,
                status_text,
                btn_login
            ]
        )