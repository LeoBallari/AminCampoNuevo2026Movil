import flet as ft
import httpx
import threading

API_URL = "https://amincamponuevo2026movil.onrender.com"

def main(page: ft.Page):
    page.title = "Test de Conexión"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    # === CONFIGURACIÓN MÓVIL NUEVA (FLET ACTUALIZADO) ===
    page.window.width = 380        # Ancho simulado de celular
    page.window.height = 680       # Alto simulado de celular
    page.window.resizable = False  # Bloquea el tamaño
    page.update()
    # ===================================================
    
    txt_user = ft.TextField(label="Usuario", width=300, prefix_icon=ft.Icons.PERSON)
    txt_pass = ft.TextField(label="Contraseña", width=300, password=True, can_reveal_password=True, prefix_icon=ft.Icons.LOCK)
    status_text = ft.Text("", size=14, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
    loading = ft.ProgressRing(visible=False, width=24, height=24)

    def intentar_login(e):
        if not txt_user.value or not txt_pass.value:
            status_text.value = "⚠️ Completa todos los campos"
            status_text.color = ft.Colors.ORANGE
            page.update()
            return

        # Modificación para avisar que el servidor en Render puede estar durmiendo
        loading.visible = True
        status_text.value = "Despertando servidor...\nEsto puede demorar hasta 1 minuto si estaba inactivo."
        status_text.color = ft.Colors.BLUE_700  # Color azul informativo
        btn_login.disabled = True
        page.update()

        def fetch():
            try:
                payload = {"usuario": txt_user.value, "contraseña": txt_pass.value}
                print(f"Enviando petición a: {API_URL}/api/login")
                
                # Aumentamos el timeout a 60 segundos por si Render está dormido
                response = httpx.post(f"{API_URL}/api/login", json=payload, timeout=60.0)
                
                if response.status_code == 200:
                    status_text.value = "✅ ¡Acceso Concedido!"
                    status_text.color = ft.Colors.GREEN
                elif response.status_code == 401:
                    status_text.value = "❌ Usuario o clave incorrectos"
                    status_text.color = ft.Colors.RED
                else:
                    status_text.value = f"⚠️ Error del servidor: {response.status_code}"
                    status_text.color = ft.Colors.ORANGE
            except httpx.TimeoutException:
                status_text.value = "❌ Tiempo de espera agotado.\nEl servidor demoró demasiado en responder."
                status_text.color = ft.Colors.RED
            except Exception as err:
                status_text.value = f"❌ Error de red: {str(err)}"
                status_text.color = ft.Colors.RED
            
            loading.visible = False
            btn_login.disabled = False
            page.update()

        threading.Thread(target=fetch, daemon=True).start()

    btn_login = ft.ElevatedButton("Entrar al Sistema", on_click=intentar_login, width=300)

    page.add(
        ft.Icon(ft.Icons.SECURITY, size=50, color=ft.Colors.BLUE),
        ft.Text("Campo Movil 2026", size=24, weight=ft.FontWeight.BOLD),
        ft.Divider(),
        txt_user,   
        txt_pass,
        loading,
        status_text,
        btn_login
    )

ft.app(target=main)