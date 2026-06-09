import flet as ft
import time
import threading
import httpx
import os
from config import API_URL, BASE_DIR

class SplashScreen:
    """Pantalla de inicio con branding y verificación de servidor"""
    
    def __init__(self, page: ft.Page, on_complete):
        self.page = page
        self.on_complete = on_complete
        # Contenedor para múltiples mensajes uno debajo de otro
        self.status_messages = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5,
        )

    def show(self):
        """Retorna la vista del Splash Screen"""
        
        # Iniciamos el proceso de verificación en segundo plano
        threading.Thread(target=self._verificar_conexion, daemon=True).start()

        return ft.View(
            "/",
            bgcolor=ft.Colors.WHITE,
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    expand=True,
                    content=ft.Column(
                        [
                            ft.Container(expand=True),
                            # Logo de la empresa
                            ft.Image(
                                src=os.path.join(BASE_DIR, "assets/imagenes/logo_reportes.png"),
                                width=180,
                                height=180,
                                fit=ft.ImageFit.CONTAIN,
                            ),
                            ft.Container(height=20),
                            ft.ProgressBar(width=250, color="#1565C0", bgcolor="#E3F2FD"),
                            ft.Container(height=10),
                            self.status_messages,
                            ft.Container(expand=True),
                            ft.Text("CAMPO MÓVIL 2026", size=14, weight="bold", color="#1565C0"),
                            ft.Text("Gestión Logística Inteligente", size=12, color=ft.Colors.GREY_600),
                            ft.Container(height=50),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER,
                    )
                )
            ]
        )

    def _verificar_conexion(self):
        """Monitorea el estado del servidor y maneja los mensajes de carga"""
        inicio = time.time()
        conexion_ok = False

        def add_msg(text, color="#406080"):
            self.status_messages.controls.append(
                ft.Text(text, size=14, italic=True, color=color, animate_opacity=300)
            )
            self.page.update()

        add_msg("Conectando con servidor seguro...")

        def ping():
            nonlocal conexion_ok
            try:
                # Intentamos un ping al endpoint de salud
                with httpx.Client() as client:
                    res = client.get(f"{API_URL}/api/health", timeout=15.0)
                    if res.status_code == 200:
                        conexion_ok = True
            except Exception:
                pass

        # Lanzar el ping en un hilo para no bloquear el contador de tiempo
        thread_ping = threading.Thread(target=ping, daemon=True)
        thread_ping.start()

        # Lista de mensajes cronometrados (segundos transcurridos, mensaje)
        mensajes_secuencia = [
            (2.5, "Cargando configuración de red..."),
            (5.0, "Sincronizando datos con la nube..."),
            (7.5, "Autenticando servicios de seguridad..."),
            (9.5, "Preparando interfaz de usuario...")
        ]

        msg_idx = 0
        # Bucle de monitoreo de hasta 10.5 segundos
        while time.time() - inicio < 10.5:
            if conexion_ok:
                break
            
            # Verificar si toca mostrar el siguiente mensaje
            tiempo_transcurrido = time.time() - inicio
            if msg_idx < len(mensajes_secuencia) and tiempo_transcurrido > mensajes_secuencia[msg_idx][0]:
                add_msg(mensajes_secuencia[msg_idx][1])
                msg_idx += 1
                
            time.sleep(0.5)

        if conexion_ok:
            add_msg("¡Conexión establecida!", color=ft.Colors.GREEN_700)
        else:
            add_msg("Servidor lento, iniciando de todos modos...", color=ft.Colors.ORANGE_700)

        time.sleep(1.0) # Pausa estética final
        self.on_complete()