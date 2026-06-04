"""
Pantalla de Login - Adaptada a Vistas Modernas y Segura para Android
"""
import flet as ft
import threading
import os
import json
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
        
        creds_path = os.path.join(BASE_DIR, "credentials.json")

        # Elementos de UI
        txt_user = ft.TextField(label="Usuario", width=300, prefix_icon=ft.Icons.PERSON)
        txt_pass = ft.TextField(
            label="Contraseña",
            width=300,
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK
        )
        chk_remember = ft.Checkbox(label="Recordar credenciales", value=False)

        # Cargar credenciales guardadas si existen
        if os.path.exists(creds_path):
            try:
                with open(creds_path, "r", encoding="utf-8") as f:
                    saved_data = json.load(f)
                    txt_user.value = saved_data.get("usuario", "")
                    txt_pass.value = saved_data.get("contraseña", "")
                    chk_remember.value = True
            except Exception:
                pass

        status_text = ft.Text(
            "",
            size=14,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER
        )
        loading = ft.ProgressRing(visible=False, width=24, height=24)

        def intentar_login(e):
            """Maneja el click en el botón de login"""
            user_val = txt_user.value
            pass_val = txt_pass.value
            remember_val = chk_remember.value

            # === MODO DESARROLLO (Bypass Local rápido) ===
            # Si ponés '13' y '13', entra directo sin ir a Render ni esperar 1 minuto
            if user_val == "13" and pass_val == "13":
                status_text.color = ft.Colors.GREEN
                status_text.value = "⚡ Modo Desarrollo: Acceso Local Directo"
                self.page.update()
                
                if remember_val:
                    with open(creds_path, "w", encoding="utf-8") as f:
                        json.dump({"usuario": user_val, "contraseña": pass_val}, f)
                else:
                    if os.path.exists(creds_path):
                        os.remove(creds_path)

                time.sleep(0.5)  # Un mini delay para ver el cartel
                
                if self.on_login_success:
                    self.on_login_success("Desarrollador")
                return
            # =============================================

            # Validación normal de campos
            if not user_val or not pass_val:
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
                result = AuthService.login(user_val, pass_val)
                
                loading.visible = False
                btn_login.disabled = False
                status_text.color = ft.Colors.GREEN if result['success'] else ft.Colors.RED
                status_text.value = result['message']
                self.page.update()
                
                if result['success']:
                    if remember_val:
                        with open(creds_path, "w", encoding="utf-8") as f:
                            json.dump({"usuario": user_val, "contraseña": pass_val}, f)
                    else:
                        if os.path.exists(creds_path):
                            os.remove(creds_path)

                    time.sleep(1.0)
                    if self.on_login_success:
                        self.on_login_success(user_val)

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
                ft.Row([chk_remember], alignment=ft.MainAxisAlignment.CENTER),
                loading,
                status_text,
                btn_login
            ]
        )