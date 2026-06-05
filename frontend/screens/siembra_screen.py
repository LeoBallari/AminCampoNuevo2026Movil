import flet as ft
import threading
import httpx
import time
from config import API_URL
from ui_styles import UIStyles

class SiembraScreen:
    def __init__(self, page: ft.Page):
        self.page = page
        # Controles que necesitamos acceder desde distintos métodos
        self.dd_campana = ft.Dropdown(label="Campaña", expand=True, on_change=self.on_filter_change)
        self.dd_cultivo = ft.Dropdown(label="Cultivo", expand=True, on_change=self.on_filter_change)
        self.loading = ft.ProgressBar(visible=False, color=ft.Colors.BLUE_400)
        self.lv_resumen = ft.ListView(expand=True, spacing=10, padding=0)
        
        # Controles para el footer (ahora por separado para dos renglones)
        self.txt_total_has = ft.Text("0 has", color=ft.Colors.WHITE, weight="bold", size=16)
        self.txt_total_lotes = ft.Text("0 lotes", color=ft.Colors.BLUE_200, weight="w-500", size=14)

    def on_filter_change(self, e):
        """Evento cuando cambia un filtro"""
        if self.dd_campana.value and self.dd_cultivo.value:
            threading.Thread(target=self.cargar_resumen, daemon=True).start()

    def cargar_resumen(self):
        """Carga el resumen siembra"""
        self.loading.visible = True
        self.lv_resumen.controls.clear()
        self.page.update()

        try:
            params = {"id_campana": self.dd_campana.value, "id_cultivo": self.dd_cultivo.value}
            with httpx.Client() as client:
                res = client.get(f"{API_URL}/api/siembra/resumen", params=params, timeout=15)
                if res.status_code == 200:
                    datos = res.json()
                    if not datos:
                        self.lv_resumen.controls.append(
                            ft.Container(
                                content=ft.Text("No hay registros para mostrar.", size=14, color=ft.Colors.BLUE_GREY_400),
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

                    # --- AGRUPAMIENTO POR ESTADIO ---
                    grupos = {}
                    for item in datos:
                        est = (item.get('estadio') or 'SIN CLASIFICAR').upper()
                        if est not in grupos:
                            grupos[est] = []
                        grupos[est].append(item)
                    
                    # Construir la UI por cada grupo
                    for estadio, items in grupos.items():
                        # Título del Grupo (PRIMERA / SEGUNDA)
                        self.lv_resumen.controls.append(
                            ft.Container(
                                content=ft.Text(f"SIEMBRA DE {estadio}", weight="bold", color=ft.Colors.BLUE_700),
                                margin=ft.margin.only(top=10, bottom=5, left=5)
                            )
                        )

                        # Encabezado de la "tabla" simplificada
                        self.lv_resumen.controls.append(
                            ft.Container(
                                content=ft.Row([
                                    ft.Text("Fecha", size=12, weight="bold", width=70),
                                    ft.Text("Lote", size=12, weight="bold", expand=True),
                                    ft.Text("Has", size=12, weight="bold", width=50, text_align="right"),
                                ], spacing=10),
                                padding=ft.padding.symmetric(horizontal=10, vertical=5),
                                bgcolor=ft.Colors.BLUE_GREY_50
                            )
                        )

                        subtotal_has = 0
                        for it in items:
                            has = float(it.get('has', 0))
                            subtotal_has += has
                            fecha_str = it.get('fecha', '')[:10] if it.get('fecha') else ""
                            
                            # Fila de datos en dos niveles
                            self.lv_resumen.controls.append(
                                ft.Container(
                                    content=ft.Column([
                                        ft.Row([
                                            ft.Text(fecha_str, size=12, width=70),
                                            ft.Text(it.get('bloque', 'S/D'), size=12, weight="bold", expand=True),
                                            ft.Text(f"{has:.1f}", size=12, width=50, text_align="right"),
                                        ], spacing=10),
                                        ft.Text(it.get('insumos', ''), size=11, color=ft.Colors.BLUE_GREY_400, italic=True),
                                    ], spacing=2),
                                    padding=ft.padding.symmetric(horizontal=10, vertical=8),
                                    border=ft.border.only(bottom=ft.BorderSide(0.5, ft.Colors.BLUE_GREY_100))
                                )
                            )
                        
                        # Resumen del grupo (Subtotales resaltados)
                        self.lv_resumen.controls.append(
                            ft.Container(
                                content=ft.Text(
                                    f"SUBTOTAL {estadio}: {subtotal_has:,.1f} has",
                                    size=12, weight="bold", color=ft.Colors.WHITE
                                ),
                                bgcolor=ft.Colors.BLUE_GREY_700,
                                padding=8,
                                border_radius=5,
                                margin=ft.margin.only(bottom=10)
                            )
                        )

        except Exception as e:
            pass
        
        self.loading.visible = False
        self.page.update()


    def cargar_filtros(self):
        """Descarga los datos para los dropdowns desde la API"""
        self.loading.visible = True
        self.page.update()

        try:
            with httpx.Client() as client:
                # Cargar Campañas
                res_camp = client.get(f"{API_URL}/api/campañas", timeout=10)
                if res_camp.status_code == 200:
                    campanas = res_camp.json()
                    self.dd_campana.options = [
                        ft.dropdown.Option(key=str(c['id']), text=c['nombre']) for c in campanas
                    ]
                
                # Cargar Cultivos
                res_cult = client.get(f"{API_URL}/api/cultivos", timeout=10)
                if res_cult.status_code == 200:
                    cultivos = res_cult.json()
                    self.dd_cultivo.options = [
                        ft.dropdown.Option(key=str(c['id']), text=c['nombre']) for c in cultivos
                    ]

        except Exception as e:
            pass
        
        self.loading.visible = False
        self.page.update()

    def show(self):
        """Retorna la vista de Siembra"""
        
        # Solo cargamos filtros si la lista está vacía (evita perder selección al volver)
        if not self.dd_campana.options:
            threading.Thread(target=self.cargar_filtros, daemon=True).start()

        return ft.View(
            route="/siembra",
            appbar=UIStyles.get_appbar(
                "Resumen de Siembra", 
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
                            self.dd_cultivo,
                        ], spacing=10),
                        
                        ft.Divider(),
                        
                        # Contenedor dinámico de vistas
                        ft.Text("Lotes Sembrados", size=16, weight="bold"),
                        self.lv_resumen
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                    expand=True)
                ),
                # Footer Estetico con el resumen de totales
                UIStyles.get_footer_container(
                    ft.Column([
                        ft.Row([ft.Text("TOTAL SUPERFICIE", color=ft.Colors.BLUE_200, size=12, weight="bold"), self.txt_total_has], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Row([ft.Text("CANTIDAD LOTES", color=ft.Colors.BLUE_200, size=12, weight="bold"), self.txt_total_lotes], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ], spacing=2, tight=True)
                )
            ]
        )