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
        print(f"\n[DEBUG] Iniciando cargar_resumen...")
        self.loading.visible = True
        self.lv_resumen.controls.clear()
        self.page.update()

        try:
            params = {"id_campana": self.dd_campana.value, "id_cultivo": self.dd_cultivo.value}
            print(f"[DEBUG] Enviando GET a /api/siembra/resumen con params: {params}")
            
            with httpx.Client() as client:
                res = client.get(f"{API_URL}/api/siembra/resumen", params=params, timeout=15)
                print(f"[DEBUG] API Response Status: {res.status_code}")

                if res.status_code == 200:
                    datos = res.json()
                    print(f"[DEBUG] Datos recibidos: {len(datos)} registros.")
                    if len(datos) > 0:
                        print(f"[DEBUG] Muestra del primer registro: {datos[0]}")
                    
                    if not datos:
                        print("[DEBUG] La lista de datos está vacía.")
                        self.lv_resumen.controls.append(
                            ft.Container(
                                content=ft.Text("No hay datos para esta selección.", size=14, color=ft.Colors.BLUE_GREY_400),
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
                    
                    print(f"[DEBUG] Grupos detectados: {list(grupos.keys())}")

                    # Construir la UI por cada grupo
                    for estadio, items in grupos.items():
                        # Título del Grupo (PRIMERA / SEGUNDA)
                        self.lv_resumen.controls.append(
                            ft.Container(
                                content=ft.Text(f"SIEMBRA DE {estadio}", weight="bold", color=ft.Colors.BLUE_700),
                                margin=ft.margin.only(top=10, bottom=5, left=5)
                            )
                        )

                        # Crear Filas de la Tabla para este grupo
                        filas_tabla = []
                        subtotal_has = 0
                        for it in items:
                            has = float(it.get('has', 0))
                            subtotal_has += has
                            fecha_str = it.get('fecha', '')[:10] if it.get('fecha') else ""
                            
                            filas_tabla.append(ft.DataRow(cells=[
                                ft.DataCell(ft.Text(fecha_str, size=12)),
                                ft.DataCell(ft.Text(it['bloque'], size=12)),
                                ft.DataCell(ft.Text(f"{has:.1f}", size=13, weight="bold")),
                                ft.DataCell(ft.Container(
                                    content=ft.Text(it.get('insumos', ''), size=11, no_wrap=False),
                                    width=180, padding=ft.padding.only(top=5, bottom=5)
                                )),
                            ]))

                        # Crear la Tabla (Grilla)
                        tabla = ft.DataTable(
                            columns=[
                                ft.DataColumn(ft.Text("Fecha", size=14)),
                                ft.DataColumn(ft.Text("Lote", size=14)),
                                ft.DataColumn(ft.Text("Has", size=14)),
                                ft.DataColumn(ft.Text("Insumos", size=14)),
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
                                    f"SUBTOTAL {estadio}: {subtotal_has:,.1f} has",
                                    size=12, weight="bold", color=ft.Colors.WHITE
                                ),
                                bgcolor=ft.Colors.BLUE_GREY_700,
                                padding=8,
                                border_radius=5,
                                margin=ft.margin.only(bottom=10)
                            )
                        )
                    
                    print("[DEBUG] UI construida exitosamente.")
                else:
                    print(f"[DEBUG] Error en API: {res.text}")

        except Exception as e:
            print(f"[DEBUG] EXCEPCIÓN en cargar_resumen: {str(e)}")
        
        self.loading.visible = False
        self.page.update()


    def cargar_filtros(self):
        """Descarga los datos para los dropdowns desde la API"""
        print("[DEBUG] Cargando filtros (campañas y cultivos)...")
        self.loading.visible = True
        self.page.update()

        try:
            with httpx.Client() as client:
                # Cargar Campañas
                res_camp = client.get(f"{API_URL}/api/campañas", timeout=10)
                print(f"[DEBUG] Cargar Campañas Status: {res_camp.status_code}")
                if res_camp.status_code == 200:
                    campanas = res_camp.json()
                    # Usamos 'key' para el ID y 'text' para lo que se muestra
                    self.dd_campana.options = [
                        ft.dropdown.Option(key=str(c['id']), text=c['nombre']) for c in campanas
                    ]
                
                # Cargar Cultivos
                res_cult = client.get(f"{API_URL}/api/cultivos", timeout=10)
                print(f"[DEBUG] Cargar Cultivos Status: {res_cult.status_code}")
                if res_cult.status_code == 200:
                    cultivos = res_cult.json()
                    # Lo mismo para cultivos
                    self.dd_cultivo.options = [
                        ft.dropdown.Option(key=str(c['id']), text=c['nombre']) for c in cultivos
                    ]

        except Exception as e:
            print(f"[DEBUG] EXCEPCIÓN en cargar_filtros: {str(e)}")
        
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