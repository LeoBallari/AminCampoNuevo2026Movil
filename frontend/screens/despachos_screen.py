import flet as ft
import threading
import httpx
from config import API_URL
from ui_styles import UIStyles



class DespachosScreen:
    def __init__(self, page: ft.Page):
        self.page = page
        # Controles que necesitamos acceder desde distintos métodos
        self.dd_campana = ft.Dropdown(label="Campaña", expand=True, on_change=self.on_filter_change)
        self.dd_cultivo = ft.Dropdown(label="Cultivo", expand=True, on_change=self.on_filter_change)
        self.loading = ft.ProgressBar(visible=False, color=ft.Colors.BLUE_400)
        self.lv_resumen = ft.ListView(expand=True, spacing=10, padding=10)
        
        # Texto dinámico para el footer
        self.txt_total_footer = ft.Text("0 qq  --  0 despachos", color=ft.Colors.WHITE, weight="bold")
        
        # Contenedores para alternar vistas
        self.view_resumen = ft.Column(
            controls=[
                ft.Text("Resumen por Entregado", size=16, weight="bold"),
                self.lv_resumen
            ],
            visible=True, 
            expand=True
        )
        self.view_detalle = ft.Column(visible=False, expand=True)
        
        self.tabla_datos = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Fec.")),
                ft.DataColumn(ft.Text("Lote")),
                ft.DataColumn(ft.Text("Kg")),
                ft.DataColumn(ft.Text("Dest.")),
            ],
            rows=[],
            column_spacing=15,
            heading_row_height=40,
        )

    def on_filter_change(self, e):
        """Evento cuando cambia un filtro"""
        if self.dd_campana.value and self.dd_cultivo.value:
            self.view_resumen.visible = True
            self.view_detalle.visible = False
            threading.Thread(target=self.cargar_resumen, daemon=True).start()

    def cargar_resumen(self):
        """Carga el resumen agrupado por entidad"""
        self.loading.visible = True
        self.lv_resumen.controls.clear()
        self.page.update()

        try:
            params = {"id_campana": self.dd_campana.value, "id_cultivo": self.dd_cultivo.value}
            with httpx.Client() as client:
                res = client.get(f"{API_URL}/api/despachos/resumen", params=params, timeout=15)
                if res.status_code == 200:
                    datos = res.json()
                    # Calcular Totales para el Resumen del Resumen
                    total_qq = sum(item['qq'] for item in datos)
                    total_cant = sum(item['cantidad'] for item in datos)
                    self.txt_total_footer.value = f"{total_qq:,.0f} qq   --   {total_cant} despachos"
                    
                    for item in datos:
                        self.lv_resumen.controls.append(
                            ft.ListTile(
                                title=ft.Text(item['entidad'], weight="bold"),
                                subtitle=ft.Text(f"{item['qq']:.0f} qq — {item['cantidad']} despachos"),
                                trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT),
                                bgcolor=ft.Colors.BLUE_GREY_50,
                                on_click=lambda e, id_ent=item['id'], nom=item['entidad']: self.ver_detalle(id_ent, nom)
                            )
                        )
        except Exception as e:
            print(f"Error al cargar resumen: {e}")
        
        self.loading.visible = False
        self.page.update()

    def ver_detalle(self, id_entidad, nombre_entidad):
        """Carga y muestra la tabla de detalles para una entidad específica"""
        self.loading.visible = True
        self.page.update()
        
        try:
            params = {
                "id_campana": self.dd_campana.value,
                "id_cultivo": self.dd_cultivo.value,
                "id_entidad": id_entidad
            }
            with httpx.Client() as client:
                res = client.get(f"{API_URL}/api/despachos/detalle", params=params, timeout=15)
                if res.status_code == 200:
                    detalles = res.json()
                    self.tabla_datos.rows = [
                        ft.DataRow(cells=[
                            ft.DataCell(ft.Text(d['fecha'], size=12)),
                            ft.DataCell(ft.Text(d['lote'], size=12)),
                            ft.DataCell(ft.Text(f"{d['neto']:,.0f}", size=12)),
                            ft.DataCell(ft.Text(d['destino'], size=12)),
                        ]) for d in detalles
                    ]
                    
                    # Cambiar visibilidad de vistas
                    self.view_resumen.visible = False
                    self.view_detalle.visible = True
                    self.view_detalle.controls = [
                        ft.Row([
                            ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: self.volver_al_resumen()),
                            ft.Text(nombre_entidad, weight="bold", size=16, overflow=ft.TextOverflow.ELLIPSIS),
                        ], alignment=ft.MainAxisAlignment.START),
                        ft.Row([self.tabla_datos], scroll=ft.ScrollMode.AUTO)
                    ]
        except Exception as e:
            print(f"Error al cargar detalle: {e}")
            
        self.loading.visible = False
        self.page.update()

    def volver_al_resumen(self):
        self.view_resumen.visible = True
        self.view_detalle.visible = False
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
        
        # Iniciamos la carga de datos en un hilo separado
        # para que la pantalla abra instantáneamente
        threading.Thread(target=self.cargar_filtros, daemon=True).start()

        return ft.View(
            route="/despachos",
            appbar=UIStyles.get_appbar(
                "Gestión de Despachos", 
                on_home_click=lambda _: self.page.go("/menu")
            ),
            vertical_alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.loading,
                ft.Container(
                    expand=True,
                    padding=ft.padding.only(left=20, right=20, top=10, bottom=0),
                    content=ft.Column([
                        ft.Text("Filtros de Búsqueda", size=16, weight="bold"),
                        ft.Row([
                            self.dd_campana,
                            self.dd_cultivo,
                        ], spacing=10),
                        
                        ft.Divider(),
                        
                        # Contenedor dinámico de vistas
                        ft.Column([
                            self.view_resumen,
                            self.view_detalle
                        ], expand=True, scroll=ft.ScrollMode.AUTO)
                    ], 
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                    expand=True)
                ),
                # Footer Estetico con el resumen de totales
                UIStyles.get_footer_container(
                    ft.Row([
                        ft.Text("TOTAL GENERAL", color=ft.Colors.BLUE_200, size=12, weight="bold"),
                        self.txt_total_footer
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                )
            ]
        )