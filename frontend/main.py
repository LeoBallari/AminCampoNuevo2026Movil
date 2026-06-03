import flet as ft
import httpx
import threading

# === IMPORTANTE: Cambia esto por la IP real de tu computadora ===
# Puedes obtenerla ejecutando 'ipconfig' en la terminal de Windows.
API_URL = "http://192.168.0.102:5000" 

def main(page: ft.Page):
    page.title = "Test de Conexión"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window_width = 400
    
    txt_user = ft.TextField(label="Usuario", width=300, prefix_icon=ft.Icons.PERSON)
    txt_pass = ft.TextField(label="Contraseña", width=300, password=True, can_reveal_password=True, prefix_icon=ft.Icons.LOCK)
    status_text = ft.Text("", size=16, weight=ft.FontWeight.BOLD)
    loading = ft.ProgressRing(visible=False)

    def intentar_login(e):
        if not txt_user.value or not txt_pass.value:
            status_text.value = "⚠️ Completa todos los campos"
            status_text.color = ft.Colors.ORANGE
            page.update()
            return

        loading.visible = True
        status_text.value = "Conectando con SQL Server..."
        status_text.color = ft.Colors.BLACK
        btn_login.disabled = True
        page.update()

        def fetch():
            try:
                # Enviamos 'password' para que coincida con lo que el backend ahora busca
                payload = {"usuario": txt_user.value, "contraseña": txt_pass.value} 
                payload = {"usuario": txt_user.value, "contraseña": txt_pass.value}
                print(f"Enviando petición a: {API_URL}/api/login")
                response = httpx.post(f"{API_URL}/api/login", json=payload, timeout=12.0)
                
                if response.status_code == 200:
                    status_text.value = "✅ ¡Acceso Concedido!"
                    status_text.color = ft.Colors.GREEN
                elif response.status_code == 401:
                    status_text.value = "❌ Usuario o clave incorrectos"
                    status_text.color = ft.Colors.RED
                else:
                    status_text.value = f"⚠️ Error del servidor: {response.status_code}"
                    status_text.color = ft.Colors.ORANGE
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
        ft.Text("AminCampo 2026", size=24, weight=ft.FontWeight.BOLD),
        ft.Divider(),
        txt_user,
        txt_pass,
        loading,
        status_text,
        btn_login
    )

ft.app(target=main)