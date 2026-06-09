import flet as ft
import threading
import httpx
from config import API_URL, API_TIMEOUT
from ui_styles import UIStyles

class EstadisticasScreen:
    def __init__(self, page: ft.Page):
        self.page = page
        self.campos_master = []  # Lista de campos físicos: [{"id": 1, "nombre": "TORRISSI"}, ...]
        self.campos_seleccionados_ids = []  # Guardamos IDs seleccionados
        self.campos_seleccionados_nombres = []  # Guardamos nombres para mostrar
        
        # Campo de texto que simula un dropdown para selección múltiple
        self.txt_campos = ft.TextField(
            label="Campos Físicos (Múltiple)",
            value="Seleccionar...",
            read_only=True,
            expand=True,
            on_click=self.abrir_selector_campos,
            prefix_icon=ft.Icons.LIST_ALT_OUTLINED
        )
        
        self.dd_cultivo = ft.Dropdown(
            label="Cultivo", 
            expand=True, 
            on_change=self.on_filter_change
        )
        
        self.loading = ft.ProgressBar(visible=False, color=ft.Colors.BLUE_400)
        self.lv_resumen = ft.ListView(expand=True, spacing=0, padding=ft.padding.only(bottom=20))
        
        # Título dinámico para mostrar campos seleccionados
        self.txt_campos_titulo = ft.Text(
            "",
            size=14,
            color=ft.Colors.BLUE_700,
            weight="bold",
            visible=False
        )

        # Contenedor para el gráfico
        self.chart_container = ft.Container(
            content=ft.Text("Seleccione filtros para visualizar el gráfico", color=ft.Colors.BLUE_GREY_400, italic=True),
            height=200,
            alignment=ft.alignment.center,
            padding=20,
            bgcolor="surfacevariant",
            border_radius=10,
        )
        
        # Totales en footer
        self.txt_total_kg = ft.Text("0 kg", color=ft.Colors.WHITE, weight="bold", size=16)
        self.txt_avg_rinde = ft.Text("0.0 qq/ha", color=ft.Colors.BLUE_200, weight="w500", size=14)

    def on_filter_change(self, e):
        """Evento cuando cambia un filtro"""
        if self.campos_seleccionados_ids and self.dd_cultivo.value:
            threading.Thread(target=self.cargar_resumen, daemon=True).start()

    def abrir_selector_campos(self, e):
        """Abre un diálogo para seleccionar múltiples campos físicos"""
        if not self.campos_master:
            cache = self.page.session.get("global_campos_fisicos")
            if cache:
                self.campos_master = cache

        def toggle_campo(e, campo_id, campo_nombre):
            if e.control.value:
                if campo_id not in self.campos_seleccionados_ids:
                    self.campos_seleccionados_ids.append(campo_id)
                    self.campos_seleccionados_nombres.append(campo_nombre)
            else:
                if campo_id in self.campos_seleccionados_ids:
                    idx = self.campos_seleccionados_ids.index(campo_id)
                    self.campos_seleccionados_ids.pop(idx)
                    self.campos_seleccionados_nombres.pop(idx)

        def confirmar_seleccion(e):
            dialog.open = False
            cant = len(self.campos_seleccionados_ids)
            self.txt_campos.value = f"{cant} campos seleccionados" if cant > 0 else "Seleccionar..."
            
            if self.campos_seleccionados_nombres:
                self.txt_campos_titulo.value = f"Campos: {', '.join(self.campos_seleccionados_nombres)}"
                self.txt_campos_titulo.visible = True
            else:
                self.txt_campos_titulo.visible = False
                
            self.page.update()
            self.on_filter_change(None)

        # Crear lista de checkboxes
        checks = []
        for c in self.campos_master:
            campo_id = c['id']
            campo_nombre = c['nombre']
            checks.append(
                ft.Checkbox(
                    label=campo_nombre,
                    value=campo_id in self.campos_seleccionados_ids,
                    on_change=lambda e, cid=campo_id, cnom=campo_nombre: toggle_campo(e, cid, cnom)
                )
            )

        dialog = ft.AlertDialog(
            title=ft.Text("Seleccionar Campos Físicos"),
            content=ft.Container(
                content=ft.Column(checks, scroll=ft.ScrollMode.AUTO, tight=True),
                height=350,
                width=300,
            ),
            actions=[
                ft.TextButton("Confirmar", on_click=confirmar_seleccion)
            ],
        )
        self.page.open(dialog)

    def cargar_resumen(self):
        """Carga las estadísticas históricas desde la API"""
        self.loading.visible = True
        self.lv_resumen.controls.clear()
        self.chart_container.content = ft.ProgressRing(width=30, height=30, stroke_width=3)
        self.page.update()

        try:
            # Enviar IDs de campos físicos (no nombres)
            lotes_ids_str = ",".join(str(cid) for cid in self.campos_seleccionados_ids)
            params = {
                "lotes_ids": lotes_ids_str,
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

                    # Calcular Totales
                    total_kg = sum(float(it.get('total_kg', 0)) for it in datos)
                    total_has = sum(float(it.get('has', 0)) for it in datos)
                    avg_rinde = (total_kg / 100.0) / total_has if total_has > 0 else 0
                    
                    self.txt_total_kg.value = f"{total_kg:,.0f} kg"
                    self.txt_avg_rinde.value = f"Promedio: {avg_rinde:.2f} qq/ha"

                    # Gráfico de Barras
                    bar_groups = []
                    chart_labels = []
                    max_rinde = 0

                    for i, it in enumerate(datos):
                        rinde = float(it.get('rinde', 0))
                        if rinde > max_rinde:
                            max_rinde = rinde
                        
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
                    
                    # Título de detalle
                    self.lv_resumen.controls.append(
                        ft.Container(
                            content=ft.Text("DETALLE POR CAMPAÑA", weight="bold", color=ft.Colors.BLUE_700),
                            margin=ft.margin.only(top=10, bottom=5, left=5)
                        )
                    )

                    filas_tabla = []
                    for it in datos:
                        rinde = float(it.get('rinde', 0))
                        produccion = float(it.get('total_kg', 0))
                        has = float(it.get('has', 0))

                        filas_tabla.append(ft.DataRow(cells=[
                            ft.DataCell(ft.Text(it.get('campaña', 'S/D'), size=13, weight="bold")),
                            ft.DataCell(ft.Text(f"{produccion:,.0f} kg", size=13)),
                            ft.DataCell(ft.Text(f"{has:.1f} ha", size=13)),
                            ft.DataCell(
                                ft.Container(
                                    content=ft.Text(f"{rinde:.2f} qq", size=12, weight="bold", color=ft.Colors.WHITE),
                                    bgcolor=ft.Colors.BLUE_700,
                                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                    border_radius=5,
                                )
                            ),
                        ]))

                    tabla = ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("Campaña", size=14)),
                            ft.DataColumn(ft.Text("Producción", size=14)),
                            ft.DataColumn(ft.Text("Has", size=14)),
                            ft.DataColumn(ft.Text("Rinde", size=14)),
                        ],
                        rows=filas_tabla,
                        column_spacing=15,
                        heading_row_height=35,
                        horizontal_margin=10,
                    )

                    self.lv_resumen.controls.append(
                        UIStyles.get_card_container(
                            ft.Row([tabla], scroll=ft.ScrollMode.AUTO)
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
                # 1. Obtener Campos Físicos
                campos = self.page.session.get("global_campos_fisicos")
                if not campos:
                    res_campos = client.get(f"{API_URL}/api/estadisticas/lotes", timeout=API_TIMEOUT)
                    if res_campos.status_code == 200:
                        campos = res_campos.json()
                        self.page.session.set("global_campos_fisicos", campos)

                if campos:
                    self.campos_master = campos

                # 2. Obtener Cultivos
                cultivos = self.page.session.get("global_cultivos")
                if not cultivos:
                    res_cul = client.get(f"{API_URL}/api/cultivos", timeout=API_TIMEOUT)
                    if res_cul.status_code == 200:
                        cultivos = res_cul.json()
                        self.page.session.set("global_cultivos", cultivos)
                
                if cultivos:
                    self.dd_cultivo.options = [
                        ft.dropdown.Option(key=str(c['id']), text=c['nombre']) for c in cultivos
                    ]

        except Exception as e:
            print(f"Error al cargar filtros: {e}")
        
        self.loading.visible = False
        self.page.update()

    def show(self):
        """Retorna la vista de Estadísticas"""
        
        # Sincronizar desde sesión
        campos_cache = self.page.session.get("global_campos_fisicos")
        if campos_cache:
            self.campos_master = campos_cache
            
        cultivos_cache = self.page.session.get("global_cultivos")
        if cultivos_cache:
            self.dd_cultivo.options = [
                ft.dropdown.Option(key=str(c['id']), text=c['nombre']) for c in cultivos_cache
            ]
            
        # Si falta algo, cargar
        if not self.campos_master or not self.dd_cultivo.options:
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
                            self.txt_campos,
                            self.dd_cultivo,
                        ], spacing=10),
                        
                        ft.Divider(),
                        self.txt_campos_titulo,
                        self.chart_container,
                        self.lv_resumen
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                    expand=True)
                ),
                UIStyles.get_footer_container(
                    ft.Column([
                        ft.Row([ft.Text("PRODUCCIÓN TOTAL", color=ft.Colors.BLUE_200, size=12, weight="bold"), self.txt_total_kg], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Row([ft.Text("RENDIMIENTO HISTÓRICO", color=ft.Colors.BLUE_200, size=12, weight="bold"), self.txt_avg_rinde], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ], spacing=2, tight=True)
                )
            ]
        )