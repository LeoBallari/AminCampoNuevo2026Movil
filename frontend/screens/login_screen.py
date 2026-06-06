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
        """Prepara y devuelve la vista de la pantalla del login"""
        # Eliminamos self.page.clean() ya que Flet maneja la limpieza mediante rutas
        
        creds_path = os.path.join(BASE_DIR, "credentials.json")

        # Elementos de UI
        txt_user = ft.TextField(
            label="Usuario",
            width=320,
            height=60,
            border_radius=16,
            filled=True,
            bgcolor="#FAFBFD",
            border_color="#D6E4F5",
            prefix_icon=ft.Icons.PERSON_OUTLINE,
        )
        txt_pass = ft.TextField(
            label="Contraseña",
            width=320,
            height=60,
            password=True,
            can_reveal_password=True,
            border_radius=16,
            filled=True,
            bgcolor="#FAFBFD",
            border_color="#D6E4F5",
            prefix_icon=ft.Icons.LOCK_OUTLINE,
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

        # Indicador de carga animado con el mensaje solicitado
        waiting_indicator = ft.Row(
            [
                ft.ProgressRing(width=20, height=20, stroke_width=2, color="#1565C0"),
                ft.Text(
                    "Despertando servidor, aguarde un momento",
                    size=13,
                    color="#406080",
                    italic=True
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            visible=False
        )

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
            waiting_indicator.visible = True
            status_text.value = "" # Limpiamos mensajes previos de error
            btn_login.disabled = True
            self.page.update()

            def fetch():
                """Realiza el login en background conectando a la API"""
                result = AuthService.login(user_val, pass_val)
                
                waiting_indicator.visible = False
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
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.LOGIN),
                    ft.Text(
                        "Entrar al Sistema",
                        size=18,
                        weight=ft.FontWeight.BOLD
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER
            ),
            width=320,
            height=60,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=18),
                bgcolor="#1565C0",
                color=ft.Colors.WHITE
            ),
            on_click=intentar_login
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
            #bgcolor="#1565C0",
            bgcolor=ft.Colors.WHITE,
            controls=[
                ft.Container(
                    expand=True,
                    alignment=ft.alignment.center,
                    content=ft.Container(
                        width=380,
                        padding=35,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=30,

                        shadow=ft.BoxShadow(
                            blur_radius=40,
                            spread_radius=0,
                            color=ft.Colors.with_opacity(0.15, ft.Colors.BLACK),
                            offset=ft.Offset(0, 10),
                        ),

                        content=ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=15,

                            controls=[

                                # LOGO
                                ft.Container(
                                    width=120,
                                    height=120,
                                    bgcolor="#F5F8FC",
                                    border_radius=60,
                                    shadow=ft.BoxShadow(
                                        blur_radius=20,
                                        spread_radius=1,
                                        color=ft.Colors.with_opacity(
                                            0.12,
                                            ft.Colors.BLACK
                                        ),
                                    ),

                                    content=ft.Image(
                                        src=os.path.join(
                                            BASE_DIR,
                                            "assets/imagenes/logo_reportes.png"
                                        ),
                                        fit=ft.ImageFit.CONTAIN,
                                    )
                                ),

                                ft.Text(
                                    "CAMPO MÓVIL",
                                    size=30,
                                    weight=ft.FontWeight.BOLD,
                                    color="#0D47A1"
                                ),

                                ft.Text(
                                    "GESTIÓN AGRÍCOLA INTELIGENTE",
                                    size=13,
                                    color="#406080",
                                    weight=ft.FontWeight.W_500
                                ),

                                ft.Container(height=20),
                              
                                txt_user,
                                txt_pass,

                                ft.Row(
                                    [chk_remember],
                                    alignment=ft.MainAxisAlignment.CENTER
                                ),

                                ft.Container(height=10),
                                btn_login,
                                waiting_indicator,
                                status_text,

                                ft.Divider(),
                                ft.Container(expand=True),
                                
                                ft.Row(
                                    [
                                        ft.Icon(
                                            ft.Icons.SHIELD_OUTLINED,
                                            color="#4A90E2"
                                        ),
                                        ft.Text(
                                            "Seguro",
                                            color="#7A8AA0"
                                        )
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER
                                ),

                                ft.Row(
                                    [
                                        ft.Icon(
                                            ft.Icons.VERIFIED_USER_OUTLINED,
                                            color="#2196F3"
                                        ),
                                        ft.Text(
                                            "Tus datos están protegidos",
                                            color="#607D8B"
                                        )
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER
                                ),

                                ft.Text(
                                    "Versión 2026",
                                    color="#1565C0",
                                    size=14,
                                ),
                                ft.Container(height=40), # Espacio para botones de Android
                            ]
                        )
                    )
                )
            ]
        )