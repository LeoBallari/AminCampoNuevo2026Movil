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
        self.loading = ft.ProgressBar(visible=False, color=ft.Colors.BLUE_400)
        self.lv_resumen = ft.ListView(expand=True, spacing=0, padding=ft.padding.only(bottom=20))
        
        # Contenedor para el gráfico
        self.chart_container = ft.Container(
            content=ft.Text("Seleccione filtros para visualizar el gráfico", color=ft.Colors.BLUE_GREY_400, italic=True),
            height=200,
            alignment=ft.alignment.center,
            padding=20,
            bgcolor="surfacevariant",
            border_radius=10,
        )
        
        # Controles para el footer (ahora por separado para dos renglones)
        self.txt_total_kg = ft.Text("0 kg", color=ft.Colors.WHITE, weight="bold", size=16)
        self.txt_avg_rinde = ft.Text("0.0 qq/ha", color=ft.Colors.BLUE_200, weight="w500", size=14)

    def on_filter_change(self, e):
        """Evento cuando cambia un filtro"""
        if self.dd_lote.value and self.dd_cultivo.value:
            threading.Thread(target=self.cargar_resumen, daemon=True).start()

    def cargar_resumen(self):
        """Carga las estadísticas históricas desde la API"""
        self.loading.visible = True
        self.lv_resumen.controls.clear()
        self.chart_container.content = ft.ProgressRing(width=30, height=30, stroke_width=3)
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
                        self.chart_container.content = ft.Text(
                            "Sin datos para el gráfico", 
                            color=ft.Colors.BLUE_GREY_400
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

                    # --- Lógica del Gráfico de Barras ---
                    bar_groups = []
                    chart_labels = []
                    max_rinde = 0

                    for i, it in enumerate(datos):
                        rinde = float(it.get('rinde', 0))
                        if rinde > max_rinde: max_rinde = rinde
                        
                        bar_groups.append(
                            ft.BarChartGroup(
                                x=i,
                                bar_rods=[
                                    ft.BarChartRod(
                                        from_y=0,
                                        to_y=rinde,
                                        width=16,
                                        color=ft.Colors.BLUE_400,
                                        tooltip=f"{it.get('campaña')}: {rinde:.2f} qq/ha",
                                        border_radius=10,
                                    )
                                ],
                            )
                        )
                        chart_labels.append(
                            ft.ChartAxisLabel(
                                value=i, 
                                label=ft.Container(ft.Text(it.get('campaña', '')[-5:], size=10), padding=5)
                            )
                        )

                    self.chart_container.content = ft.BarChart(
                        bar_groups=bar_groups,
                        bottom_axis=ft.ChartAxis(labels=chart_labels, labels_size=30),
                        left_axis=ft.ChartAxis(labels_size=0),
                        max_y=max_rinde * 1.2 if max_rinde > 0 else 100,
                        interactive=True,
                        expand=True,
                    )

                    for it in datos:
                        rinde = float(it.get('rinde', 0))
                        produccion = float(it.get('total_kg', 0))
                        has = float(it.get('has', 0))

                        # Fila de detalle (Fondo blanco con etiqueta resaltada para rinde)
                        self.lv_resumen.controls.append(
                            ft.Container(
                                content=ft.Row([
                                    ft.Text(it.get('campaña', 'S/D'), size=13, weight="bold", expand=1.2),
                                    ft.Text(f"{produccion:,.0f} kg", size=13, expand=1.5, text_align=ft.TextAlign.CENTER),
                                    ft.Text(f"{has:.1f} ha", size=13, expand=1, text_align=ft.TextAlign.CENTER),
                                    ft.Container(
                                        content=ft.Text(f"{rinde:.2f} qq", size=12, weight="bold", color=ft.Colors.WHITE),
                                        bgcolor=ft.Colors.BLUE_700,
                                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                        border_radius=5,
                                    ),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                                padding=ft.padding.symmetric(horizontal=10, vertical=12),
                                bgcolor=ft.Colors.WHITE,
                                border=ft.border.only(bottom=ft.BorderSide(0.5, ft.Colors.OUTLINE_VARIANT)),
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
                lotes = self.page.session.get("global_lotes_unificados")
                if not lotes:
                    res_lotes = client.get(f"{API_URL}/api/estadisticas/lotes", timeout=API_TIMEOUT)
                    if res_lotes.status_code == 200:
                        lotes = res_lotes.json()
                        self.page.session.set("global_lotes_unificados", lotes)

                if lotes:
                    # Limpiamos opciones previas antes de cargar nuevas
                    self.dd_lote.options = []
                    self.dd_lote.options = [
                        ft.dropdown.Option(key=str(l.get('id')), text=str(l.get('nombre'))) 
                        for l in lotes 
                        if l.get('nombre')
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
                        #ft.Text("Evolución de Rinde (qq/ha)", size=16, weight="bold"),
                        self.chart_container,
                        
                        #ft.Text("Detalle por Campaña", size=16, weight="bold"),
                        # Encabezado de la lista
                        ft.Container(
                            content=ft.Row([
                                ft.Text("Campaña", size=11, color=ft.Colors.BLUE_GREY_400, weight="bold", expand=1.2),
                                ft.Text("Producción", size=11, color=ft.Colors.BLUE_GREY_400, weight="bold", expand=1.5, text_align=ft.TextAlign.CENTER),
                                ft.Text("Has", size=11, color=ft.Colors.BLUE_GREY_400, weight="bold", expand=1, text_align=ft.TextAlign.CENTER),
                                ft.Text("Rinde", size=11, color=ft.Colors.BLUE_GREY_400, weight="bold", width=65, text_align=ft.TextAlign.CENTER),
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            padding=ft.padding.symmetric(horizontal=10, vertical=8),
                            bgcolor=ft.Colors.GREY_50,
                        ),
                        self.lv_resumen
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                    expand=True)
                ),
                # Footer Estetico con el resumen de totales
                UIStyles.get_footer_container(
                    ft.Column([
                        ft.Row([ft.Text("PRODUCCIÓN TOTAL", color=ft.Colors.BLUE_200, size=12, weight="bold"), self.txt_total_kg], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Row([ft.Text("RENDIMIENTO HISTÓRICO", color=ft.Colors.BLUE_200, size=12, weight="bold"), self.txt_avg_rinde], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ], spacing=2, tight=True)
                )
            ]
        )