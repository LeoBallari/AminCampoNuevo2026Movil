import flet as ft
import threading
import httpx
from config import API_URL

class DespachosScreen:
    def __init__(self, page: ft.Page):
        self.page = page
        # Controles que necesitamos acceder desde distintos métodos
        self.dd_campana = ft.Dropdown(label="Campaña", expand=True, on_change=self.on_filter_change)
        self.dd_cultivo = ft.Dropdown(label="Cultivo", expand=True, on_change=self.on_filter_change)
        self.loading = ft.ProgressBar(visible=False, color=ft.Colors.BLUE_400)
        self.tabla_datos = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Fecha")),
                ft.DataColumn(ft.Text("Lote")),
                ft.DataColumn(ft.Text("Kg Netos"), numeric=True),
                ft.DataColumn(ft.Text("Destino")),
            ],
            rows=[],
        )

    def on_filter_change(self, e):
        """Evento cuando cambia un filtro"""
        print(f"Filtrando por IDs -> Campaña: {self.dd_campana.value}, Cultivo: {self.dd_cultivo.value}")
        # Aquí llamaremos a la función de cargar tabla más adelante

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
            appbar=ft.AppBar(
                leading=ft.Container(
                    content=
                        ft.IconButton(
                            icon=ft.Icons.HOME,
                            icon_color=ft.Colors.WHITE,
                            on_click=lambda _: self.page.go("/menu")
                        ),
                    padding=5,
                ),
                title=ft.Text("Gestión de Despachos", size=20, weight="bold"),
                bgcolor=ft.Colors.BLUE_GREY_900,
                color=ft.Colors.WHITE,
                center_title=False,
            ),
            vertical_alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.loading,
                ft.Container(
                    padding=20,
                    content=ft.Column([
                        ft.Text("Filtros de Búsqueda", size=16, weight="bold"),
                        ft.Row([
                            self.dd_campana,
                            self.dd_cultivo,
                        ], spacing=10),
                        
                        ft.Divider(),
                        
                        ft.Text("Resultados", size=16, weight="bold"),
                        # El ListView permite que la tabla tenga scroll lateral/vertical
                        ft.Column(
                            controls=[
                                ft.Row([self.tabla_datos], scroll=ft.ScrollMode.AUTO)
                            ],
                            scroll=ft.ScrollMode.AUTO,
                            expand=True
                        )
                    ], horizontal_alignment=ft.CrossAxisAlignment.START, expand=True)
                )
            ]
        )