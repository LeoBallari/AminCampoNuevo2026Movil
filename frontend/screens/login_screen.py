"""
Pantalla de Login
"""
import flet as ft
import threading
import os
from config import BASE_DIR
from services.auth_service import AuthService


class LoginScreen:
    """Pantalla de login de la aplicación"""
    
    def __init__(self, page: ft.Page, on_login_success=None):
        self.page = page
        self.on_login_success = on_login_success
        
    def show(self):
        """Muestra la pantalla de login"""
        self.page.clean()
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        
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
            if not txt_user.value or not txt_pass.value:
                status_text.value = "⚠️ Completa todos los campos"
                status_text.color = ft.Colors.ORANGE
                self.page.update()
                return

            # Mostrar carga
            loading.visible = True
            status_text.value = "Despertando servidor...\nEsto puede demorar hasta 1 minuto si estaba inactivo."
            status_text.color = ft.Colors.BLUE_700
            btn_login.disabled = True
            self.page.update()

            def fetch():
                """Realiza el login en background"""
                result = AuthService.login(txt_user.value, txt_pass.value)
                
                loading.visible = False
                btn_login.disabled = False
                status_text.color = ft.Colors.GREEN if result['success'] else ft.Colors.RED
                status_text.value = result['message']
                self.page.update()
                
                if result['success']:
                    # Llamar callback después de 1 segundo
                    if self.on_login_success:
                        threading.Timer(1.0, lambda: self.on_login_success(txt_user.value)).start()

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
        
        self.page.add(
            imagen,
            ft.Text("Campo Movil 2026", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            txt_user,
            txt_pass,
            loading,
            status_text,
            btn_login
        )
