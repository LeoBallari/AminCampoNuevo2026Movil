import flet as ft
import threading
import httpx
import time
from config import API_URL, API_TIMEOUT
from ui_styles import UIStyles

class EstadisticasScreen:
    def __init__(self, page: ft.Page):
        self.page = page
        # Controles que necesitamos acceder desde distintos métodos
        self.dd_lote = ft.Dropdown(label="Lote / Bloque", expand=True, on_change=self.on_filter_change)
        self.dd_cultivo = ft.Dropdown(label="Cultivo", expand=True, on_change=self.on_filter_change)
        self.loading = ft.ProgressBar(visible=False, color=ft.Colors.AMBER_400)
        self.lv_resumen = ft.ListView(expand=True, spacing=8, padding=ft.padding.only(bottom=20))
        
        # Controles para el footer (ahora por separado para dos renglones)
        self.txt_total_kg = ft.Text("0 kg", color=ft.Colors.WHITE, weight="bold", size=16)
        self.txt_avg_rinde = ft.Text("0.0 qq/ha", color=ft.Colors.AMBER_200, weight="w-500", size=14)

    def on_filter_change(self, e):
        """Evento cuando cambia un filtro"""
        if self.dd_lote.value and self.dd_cultivo.value:
            threading.Thread(target=self.cargar_resumen, daemon=True).start()

    def cargar_resumen(self):
        """Carga las estadísticas históricas desde la API"""
        self.loading.visible = True
        self.lv_resumen.controls.clear()
        self.page.update()

        try:
            # id_campana en el backend espera el NOMBRE del lote, id_cultivo espera el NOMBRE del cultivo
            params = {
                "id_campana": self.dd_lote.value, 
                "id_cultivo": self.dd_cultivo.value
            }
            with httpx.Client() as client:
                res = client.get(f"{API_URL}/api/estadisticas", params=params, timeout=API_TIMEOUT)
                if res.status_code == 200:
                    datos = res.json()
                    if not datos:
                        self.lv_resumen.controls.append(
                            ft.Container(
                                content=ft.Text("Sin historial para esta combinación.", size=16, color=ft.Colors.BLUE_GREY_400),
                                padding=30, alignment=ft.alignment.center
                            )
                        )
                        self.loading.visible = False
                        self.page.update()
                        return

                    # Calcular Totales para el Resumen del Resumen
                    total_kg = sum(float(it.get('total_kg', 0)) for it in datos)
                    total_has = sum(float(it.get('has', 0)) for it in datos)
                    avg_rinde = (total_kg / 100.0) / total_has if total_has > 0 else 0
                    
                    self.txt_total_kg.value = f"{total_kg:,.0f} kg"
                    self.txt_avg_rinde.value = f"Promedio: {avg_rinde:.2f} qq/ha"

                    for it in datos:
                        rinde = float(it.get('rinde', 0))
                        produccion = float(it.get('total_kg', 0))
                        
                        # Tarjeta por Campaña
                        self.lv_resumen.controls.append(
                            ft.Container(
                                content=ft.Column([
                                    # Línea 1: CAMPAÑA Y RINDE
                                    ft.Row([
                                        ft.Text(it.get('campaña', 'S/D'), size=16, weight="bold", expand=True),
                                        ft.Container(
                                            content=ft.Text(f"{rinde:.2f} qq/ha", size=14, weight="bold", color=ft.Colors.WHITE),
                                            bgcolor=ft.Colors.GREEN_700,
                                            padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                            border_radius=5
                                        ),
                                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                    
                                    # Línea 2: Detalles técnicos
                                    ft.Row([
                                        ft.Column([
                                            ft.Text("Superficie", size=12, color=ft.Colors.BLUE_GREY_400),
                                            ft.Text(f"{float(it.get('has', 0)):.1f} has", size=14, weight="w-500"),
                                        ], spacing=1, expand=True),
                                        ft.Column([
                                            ft.Text("Producción Total", size=12, color=ft.Colors.BLUE_GREY_400),
                                            ft.Text(f"{produccion:,.0f} kg", size=14, weight="w-500"),
                                        ], spacing=1, expand=True, horizontal_alignment=ft.CrossAxisAlignment.END),
                                    ]),
                                    ft.Text(f"Bloque: {it.get('bloque')} • {it.get('cantidad')} registros", size=12, italic=True, color=ft.Colors.BLUE_GREY_300)
                                ], spacing=2),
                                padding=ft.padding.symmetric(horizontal=12, vertical=10),
                                bgcolor="surfacevariant",
                                border_radius=8,
                                border=ft.border.all(0.5, ft.Colors.OUTLINE_VARIANT),
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
            with httpx.Client() as client:
                # 1. Obtener Lotes/Bloques
                # Usamos la nueva ruta única para evitar conflictos
                res_lotes = client.get(f"{API_URL}/api/estadisticas/lotes", timeout=API_TIMEOUT)
                if res_lotes.status_code == 200:
                    lotes = res_lotes.json()
                    self.dd_lote.options = [
                        ft.dropdown.Option(key=str(l['id']), text=l['nombre']) for l in lotes
                    ]

                # 2. Obtener Cultivos
                # Intentamos usar la sesión global para cultivos
                cultivos = self.page.session.get("global_cultivos")
                if not cultivos:
                    res_cul = client.get(f"{API_URL}/api/cultivos", timeout=API_TIMEOUT)
                    if res_cul.status_code == 200:
                        cultivos = res_cul.json()
                        self.page.session.set("global_cultivos", cultivos)
                
                if cultivos:
                    # Usamos el NOMBRE como key porque el backend filtra por nombre_cultivo
                    self.dd_cultivo.options = [
                        ft.dropdown.Option(key=c['nombre'], text=c['nombre']) for c in cultivos
                    ]

        except Exception as e:
            print(f"Error al cargar filtros: {e}")
        
        self.loading.visible = False
        self.page.update()

    def show(self):
        """Retorna la vista de Estadísticas"""
        
        # Solo cargamos filtros si la lista está vacía (evita perder selección al volver)
        if not self.dd_lote.options:
            threading.Thread(target=self.cargar_filtros, daemon=True).start()

        return ft.View(
            route="/estadisticas",
            appbar=UIStyles.get_appbar(
                "Estadísticas de Rinde", 
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
                            self.dd_lote,
                            self.dd_cultivo,
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
                        ft.Row([ft.Text("PRODUCCIÓN TOTAL", color=ft.Colors.AMBER_200, size=12, weight="bold"), self.txt_total_kg], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Row([ft.Text("RENDIMIENTO HISTÓRICO", color=ft.Colors.AMBER_200, size=12, weight="bold"), self.txt_avg_rinde], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ], spacing=2, tight=True)
                )
            ]
        )