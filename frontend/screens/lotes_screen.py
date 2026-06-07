import flet as ft
import threading
import httpx
import time
from config import API_URL, API_TIMEOUT
from ui_styles import UIStyles

class LotesScreen:
    def __init__(self, page: ft.Page):
        self.page = page
        # Controles que necesitamos acceder desde distintos métodos
        self.dd_campana = ft.Dropdown(label="Campaña", expand=True, on_change=self.on_filter_change)
        self.loading = ft.ProgressBar(visible=False, color=ft.Colors.BLUE_400)
        self.lv_resumen = ft.ListView(expand=True, spacing=8, padding=ft.padding.only(bottom=20))
        
        # Controles para el footer (ahora por separado para dos renglones)
        self.txt_total_has = ft.Text("0 has", color=ft.Colors.WHITE, weight="bold", size=16)
        self.txt_total_lotes = ft.Text("0 lotes", color=ft.Colors.BLUE_200, weight="w500", size=14)

    def on_filter_change(self, e):
        """Evento cuando cambia un filtro"""
        if self.dd_campana.value:
            threading.Thread(target=self.cargar_resumen, daemon=True).start()

    def cargar_resumen(self):
        """Carga el listado de lotes desde la API"""
        self.loading.visible = True
        self.lv_resumen.controls.clear()
        self.page.update()

        try:
            params = {"id_campana": self.dd_campana.value}
            with httpx.Client() as client:
                res = client.get(f"{API_URL}/api/lotes", params=params, timeout=API_TIMEOUT)
                if res.status_code == 200:
                    datos = res.json()
                    if not datos:
                        self.lv_resumen.controls.append(
                            ft.Container(
                                content=ft.Text("No hay registros para mostrar.", size=16, color=ft.Colors.BLUE_GREY_400),
                                padding=30, alignment=ft.alignment.center
                            )
                        )
                        self.loading.visible = False
                        self.page.update()
                        return

                    # Calcular Totales para el Resumen del Resumen
                    total_has = sum(float(it.get('has', 0)) for it in datos)
                    total_lotes = len(datos)
                    
                    self.txt_total_has.value = f"{total_has:,.1f} has"
                    self.txt_total_lotes.value = f"{total_lotes} lotes"

                    for it in datos:
                        has = float(it.get('has', 0))
                        
                        # Calculamos los valores antes de armar la lista de controles
                        propio = int(round(float(it.get('propio') or 0)))
                        arrend = int(round(float(it.get('arrendado') or 0)))

                        # FILA DE DATOS EN DOS NIVELES (Estilo Tabla Mobile)
                        self.lv_resumen.controls.append(
                            ft.Container(
                                content=ft.Column([
                                    # Línea 1: BLOQUE Y HAS
                                    ft.Row([
                                        ft.Text(it.get('bloque', 'S/D'), size=15, weight="bold", expand=True),
                                        ft.Text(f"{has:.1f} has", size=15, weight="bold", color=ft.Colors.BLUE_700),
                                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                    # Línea 2: DETALLES (Porcentajes redondeados sin decimales)
                                    ft.Text(
                                        f"Renspa: {it.get('renspa') or '-'} | Propio: {propio}% | Arrend: {arrend}%",
                                        size=13, color=ft.Colors.BLUE_GREY_400, italic=True
                                    ),
                                ], spacing=2),
                                padding=ft.padding.symmetric(horizontal=12, vertical=10),
                                bgcolor="surfacevariant",
                                border_radius=8,
                                border=ft.border.all(0.5, ft.colors.OUTLINE_VARIANT),
                            )
                        )
                else:
                    print(f"Error API: {res.status_code}")
        except Exception as e:
            print(f"Error al cargar resumen: {e}")
        
        self.loading.visible = False
        self.page.update()


    def cargar_filtros(self):
        """Descarga los datos para los dropdowns desde la API"""
        self.loading.visible = True
        self.page.update()

        try:
            # Intentar obtener de la sesión global (precargado en main.py)
            campanas = self.page.session.get("global_campanas")

            # Si no están en sesión, pedirlos a la API
            if not campanas:
                with httpx.Client() as client:
                    res = client.get(f"{API_URL}/api/campañas", timeout=API_TIMEOUT)
                    if res.status_code == 200:
                        campanas = res.json()
                        self.page.session.set("global_campanas", campanas)

            if campanas:
                self.dd_campana.options = [
                    ft.dropdown.Option(key=str(c['id']), text=c['nombre']) for c in campanas
                ]

        except Exception as e:
            print(f"Error al cargar filtros: {e}")
        
        self.loading.visible = False
        self.page.update()

    def show(self):
        """Retorna la vista de Lotes"""
        
        # Solo cargamos filtros si la lista está vacía (evita perder selección al volver)
        if not self.dd_campana.options:
            threading.Thread(target=self.cargar_filtros, daemon=True).start()

        return ft.View(
            route="/lotes",
            appbar=UIStyles.get_appbar(
                "Gestión de Lotes", 
                on_home_click=lambda _: self.page.go("/menu")
            ),
            vertical_alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.loading,
                ft.Container(
                    expand=True,
                    padding=ft.padding.only(left=2, right=2, top=10, bottom=0),
                    content=ft.Column([
                        ft.Text("Filtros de Búsqueda", size=16, weight="bold"),
                        ft.Row([
                            self.dd_campana,
                        ], spacing=10),
                        
                        ft.Divider(),
                        
                        # Contenedor dinámico de vistas
                        ft.Text("Listado de Lotes", size=16, weight="bold"),
                        self.lv_resumen
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                    expand=True)
                ),
                # Footer Estetico con el resumen de totales
                UIStyles.get_footer_container(
                    ft.Column([
                        ft.Row([ft.Text("TOTAL SUPERFICIE", color=ft.Colors.BLUE_200, size=12, weight="bold"), self.txt_total_has], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Row([ft.Text("CANTIDAD BLOQUES", color=ft.Colors.BLUE_200, size=12, weight="bold"), self.txt_total_lotes], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ], spacing=2, tight=True)
                )
            ]
        )