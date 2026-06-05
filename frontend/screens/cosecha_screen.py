import flet as ft
import threading
import httpx
import time
from config import API_URL
from ui_styles import UIStyles

class CosechaScreen:
    def __init__(self, page: ft.Page):
        self.page = page
        # Controles que necesitamos acceder desde distintos métodos
        self.dd_campana = ft.Dropdown(label="Campaña", expand=True, on_change=self.on_filter_change)
        self.dd_cultivo = ft.Dropdown(label="Cultivo", expand=True, on_change=self.on_filter_change)
        self.loading = ft.ProgressBar(visible=False, color=ft.Colors.BLUE_400)
        self.lv_resumen = ft.ListView(expand=True, spacing=10, padding=0)
        
        # Controles para el footer (ahora por separado para dos renglones)
        self.txt_total_qq = ft.Text("0 qq", color=ft.Colors.WHITE, weight="bold", size=16)
        self.txt_total_avg = ft.Text("0.0 qq/ha", color=ft.Colors.BLUE_200, weight="w-500", size=14)

    def on_filter_change(self, e):
        """Evento cuando cambia un filtro"""
        if self.dd_campana.value and self.dd_cultivo.value:
            threading.Thread(target=self.cargar_resumen, daemon=True).start()

    def cargar_resumen(self):
        """Carga el resumen cosecha"""
        self.loading.visible = True
        self.lv_resumen.controls.clear()
        self.page.update()

        try:
            params = {"id_campana": self.dd_campana.value, "id_cultivo": self.dd_cultivo.value}
            with httpx.Client() as client:
                res = client.get(f"{API_URL}/api/cosecha/resumen", params=params, timeout=15)
                if res.status_code == 200:
                    datos = res.json()
                    # Calcular Totales para el Resumen del Resumen
                    total_qq = sum(float(it.get('rinde', 0)) * float(it.get('has', 0)) for it in datos)
                    total_has = sum(float(it.get('has', 0)) for it in datos)
                    total_avg = total_qq / total_has if total_has > 0 else 0
                    self.txt_total_qq.value = f"{total_qq:,.0f} qq"
                    self.txt_total_avg.value = f"{total_avg:.1f} qq/ha"

                    # --- AGRUPAMIENTO POR ESTADIO ---
                    grupos = {}
                    for item in datos:
                        est = item.get('estadio', 'SIN CLASIFICAR').upper()
                        if est not in grupos:
                            grupos[est] = []
                        grupos[est].append(item)

                    # Construir la UI por cada grupo
                    for estadio, items in grupos.items():
                        # Título del Grupo (PRIMERA / SEGUNDA)
                        self.lv_resumen.controls.append(
                            ft.Container(
                                content=ft.Text(f"COSECHA DE {estadio}", weight="bold", color=ft.Colors.BLUE_700),
                                margin=ft.margin.only(top=10, bottom=5, left=5)
                            )
                        )

                        # Crear Filas de la Tabla para este grupo
                        filas_tabla = []
                        subtotal_qq = 0
                        subtotal_has = 0
                        for it in items:
                            rinde = float(it.get('rinde', 0))
                            has = float(it.get('has', 0))
                            subtotal_qq += (rinde * has)
                            subtotal_has += has
                            
                            filas_tabla.append(ft.DataRow(cells=[
                                ft.DataCell(ft.Text(it['bloque'], size=12)),
                                ft.DataCell(ft.Text(f"{rinde:.1f}", size=13, weight="bold")),
                                ft.DataCell(ft.Text(f"{float(it.get('humedad', 0)):.1f}%", size=13)),
                                ft.DataCell(ft.Text(f"{has:.0f}", size=13)),
                            ]))

                        # Crear la Tabla (Grilla)
                        rinde_promedio_estadio = subtotal_qq / subtotal_has if subtotal_has > 0 else 0
                        
                        tabla = ft.DataTable(
                            columns=[
                                ft.DataColumn(ft.Text("Lote", size=14)),
                                ft.DataColumn(ft.Text("Rinde", size=14)),
                                ft.DataColumn(ft.Text("Hum", size=14)),
                                ft.DataColumn(ft.Text("Has", size=14)),
                            ],
                            rows=filas_tabla,
                            column_spacing=22, # Más espacio entre columnas
                            heading_row_height=35,
                            data_row_min_height=35,
                            horizontal_margin=10,
                        )

                        # Envolver tabla en un scroll horizontal por si la pantalla es chica
                        self.lv_resumen.controls.append(ft.Row([tabla], scroll=ft.ScrollMode.AUTO))
                        
                        # Resumen del grupo (Subtotales resaltados)
                        self.lv_resumen.controls.append(
                            ft.Container(
                                content=ft.Text(
                                    f"SUBTOTAL {estadio}: {subtotal_qq:,.0f} qq  |  PROM: {rinde_promedio_estadio:.1f} qq/ha",
                                    size=12, weight="bold", color=ft.Colors.WHITE
                                ),
                                bgcolor=ft.Colors.BLUE_GREY_700,
                                padding=8,
                                border_radius=5,
                                margin=ft.margin.only(bottom=10)
                            )
                        )

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
                # Cargar Campañas
                res_camp = client.get(f"{API_URL}/api/campañas", timeout=10)
                if res_camp.status_code == 200:
                    campanas = res_camp.json()
                    # Usamos 'key' para el ID y 'text' para lo que se muestra
                    self.dd_campana.options = [
                        ft.dropdown.Option(key=str(c['id']), text=c['nombre']) for c in campanas
                    ]
                
                # Cargar Cultivos
                res_cult = client.get(f"{API_URL}/api/cultivos", timeout=10)
                if res_cult.status_code == 200:
                    cultivos = res_cult.json()
                    # Lo mismo para cultivos
                    self.dd_cultivo.options = [
                        ft.dropdown.Option(key=str(c['id']), text=c['nombre']) for c in cultivos
                    ]

        except Exception as e:
            print(f"Error cargando filtros: {e}")
        
        self.loading.visible = False
        self.page.update()

    def show(self):
        """Retorna la vista de Despachos"""
        
        # Solo cargamos filtros si la lista está vacía (evita perder selección al volver)
        if not self.dd_campana.options:
            threading.Thread(target=self.cargar_filtros, daemon=True).start()

        return ft.View(
            route="/cosecha",
            appbar=UIStyles.get_appbar(
                "Resumen de Cosecha", 
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
                        ft.Text("Lotes Cosechados", size=16, weight="bold"),
                        self.lv_resumen
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                    expand=True)
                ),
                # Footer Estetico con el resumen de totales
                UIStyles.get_footer_container(
                    ft.Column([
                        ft.Row([ft.Text("TOTAL GENERAL", color=ft.Colors.BLUE_200, size=12, weight="bold"), self.txt_total_qq], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Row([ft.Text("RENDIMIENTO", color=ft.Colors.BLUE_200, size=12, weight="bold"), self.txt_total_avg], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ], spacing=2, tight=True)
                )
            ]
        )