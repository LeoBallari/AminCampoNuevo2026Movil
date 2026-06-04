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
        self.lv_resumen = ft.ListView(expand=True, spacing=10, padding=10)
        
        # Texto dinámico para el footer
        self.txt_total_footer = ft.Text("0 qq", color=ft.Colors.WHITE, weight="bold")
        
        self.tabla_datos = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("BLQUE")),
                ft.DataColumn(ft.Text("ESTADIO")),
                ft.DataColumn(ft.Text("VARIEDAD")),
                ft.DataColumn(ft.Text("RINDE")),
                ft.DataColumn(ft.Text("HUMEDAD")),
                ft.DataColumn(ft.Text("HAS")),
            ],
            rows=[],
            column_spacing=20,
            heading_row_height=40,
        )

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
                    total_qq = sum(float(item.get('rinde', 0)) * float(item.get('has', 0)) for item in datos)
                    self.txt_total_footer.value = f"{total_qq:,.0f} qq"
                    
                    for item in datos:
                        self.lv_resumen.controls.append(
                            ft.ListTile(
                                title=ft.Text(f"{item['bloque']} - {item['variedad']}", weight="bold"),
                                subtitle=ft.Text(
                                    f"Rinde: {float(item.get('rinde', 0)):.1f} qq/ha - "
                                    f"Hum: {float(item.get('humedad', 0)):.1f}%"
                                ),
                                trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT),
                                bgcolor=ft.Colors.BLUE_GREY_50,
                                on_click=lambda e: print("Detalle no implementado")
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
                    padding=ft.padding.only(left=10, right=10, top=10, bottom=0),
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
                    ft.Row([
                        ft.Text("TOTAL GENERAL", color=ft.Colors.BLUE_200, size=13, weight="bold"),
                        self.txt_total_footer
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                )
            ]
        )