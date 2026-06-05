import flet as ft
import threading
import httpx
import time
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
        
        self.tabla_datos = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("FECHA", size=14)),
                ft.DataColumn(ft.Text("CP", size=14)),
                ft.DataColumn(ft.Text("CTG", size=14)),
                ft.DataColumn(ft.Text("KG", size=14)),
                ft.DataColumn(ft.Text("DESTINO", size=14)),
                ft.DataColumn(ft.Text("TRANSPORTE", size=14)),
                ft.DataColumn(ft.Text("PATENTE", size=14)),
                ft.DataColumn(ft.Text("ESTADO", size=14)),
            ],
            rows=[],
            column_spacing=22,
            heading_row_height=40,
            horizontal_margin=10,
        )

    def on_filter_change(self, e):
        """Evento cuando cambia un filtro"""
        if self.dd_campana.value and self.dd_cultivo.value:
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
                "id_entidad": id_entidad,
                "t": time.time()  # Cache buster
            }
            with httpx.Client() as client:
                res = client.get(f"{API_URL}/api/despachos/detalle", params=params, timeout=15)
                if res.status_code == 200:
                    detalles = res.json()
                    self.tabla_datos.rows = [
                        ft.DataRow(cells=[
                            ft.DataCell(ft.Text(d.get('fecha', ''), size=14)),
                            ft.DataCell(ft.Text(str(d.get('cp', ''))[-5:] if d.get('cp') else "", size=14)),
                            ft.DataCell(ft.Text(d.get('ctg', ''), size=14)),
                            ft.DataCell(ft.Text(f"{d.get('neto', 0):,.0f}", size=14)),
                            ft.DataCell(ft.Text(d.get('destino', 'N/A'), size=14)),
                            ft.DataCell(ft.Text(d.get('transporte', 'N/A'), size=14)),
                            ft.DataCell(ft.Text(d.get('patente', ''), size=14)),
                            ft.DataCell(ft.Text(d.get('estado', '-'), size=14, weight="bold")),
                        ]) for d in detalles
                    ]
                    
                    detalle_controls = [
                        ft.Text(nombre_entidad, weight="bold", size=18, color=ft.Colors.BLUE_GREY_800),
                        ft.Divider(),
                    ]

                    if detalles:
                        # Envolvemos la tabla en un Row con scroll para permitir desplazamiento horizontal
                        detalle_controls.append(
                            ft.Container(
                                content=ft.Row(
                                    [self.tabla_datos],
                                    scroll=ft.ScrollMode.AUTO,
                                ),
                                padding=ft.padding.only(bottom=20)
                            )
                        )
                    else:
                        detalle_controls.append(
                            ft.Container(
                                padding=20,
                                content=ft.Text(
                                    "No se encontraron despachos para esta entidad.",
                                    color=ft.Colors.BLUE_GREY_700,
                                    size=14,
                                )
                            )
                        )

                    detalle_view = ft.View(
                        route="/despachos/detalle",
                        appbar=UIStyles.get_appbar(
                            "Detalle de despachos",
                            leading=ft.IconButton(
                                icon=ft.Icons.ARROW_BACK,
                                icon_color=ft.Colors.WHITE,
                                on_click=lambda _: (
                                    self.page.views.pop(), 
                                    setattr(self.page, "route", "/despachos"),
                                    self.page.update()
                                )
                            )
                        ),
                        controls=[
                            ft.Container(
                                expand=True,
                                padding=ft.padding.only(left=2, right=2, top=15, bottom=10),
                                content=ft.Column(
                                    detalle_controls,
                                    scroll=ft.ScrollMode.AUTO,
                                    expand=True
                                )
                            )
                        ]
                    )
                    self.page.views.append(detalle_view)
                    self.page.go("/despachos/detalle")
                    self.page.update()
                else:
                    print(f"Error API: {res.text}") # Debug en consola
                    try:
                        error_msg = res.json().get("error", res.text)
                    except Exception:
                        error_msg = res.text
                    self.page.snack_bar = ft.SnackBar(
                        ft.Text(f"Error cargando detalle: {error_msg}", size=12),
                        bgcolor=ft.Colors.RED_600,
                        open=True,
                    )
                    error_view = ft.View(
                        route="/despachos/detalle",
                        appbar=UIStyles.get_appbar(
                            "Detalle de despachos",
                            leading=ft.IconButton(
                                icon=ft.Icons.ARROW_BACK,
                                icon_color=ft.Colors.WHITE,
                                on_click=lambda _: (
                                    self.page.views.pop(),
                                    setattr(self.page, "route", "/despachos"),
                                    self.page.update()
                                )
                            )
                        ),
                        controls=[
                            ft.Container(
                                expand=True,
                                padding=ft.padding.only(left=2, right=2, top=10, bottom=10),
                                content=ft.Column([
                                    ft.Text(nombre_entidad, weight="bold", size=18, color=ft.Colors.BLUE_GREY_800),
                                    ft.Divider(),
                                    ft.Text(
                                        f"No se pudo cargar el detalle: {error_msg}",
                                        color=ft.Colors.RED_700,
                                        size=14,
                                    )
                                ], scroll=ft.ScrollMode.AUTO, expand=True)
                            )
                        ]
                    )
                    self.page.views.append(error_view)
                    self.page.go("/despachos/detalle")
                    self.page.update()
        except Exception as e:
            print(f"Error al cargar detalle: {e}")
            self.page.snack_bar = ft.SnackBar(
                ft.Text(f"Error cargando detalle: {e}", size=12),
                bgcolor=ft.Colors.RED_600,
                open=True,
            )
            error_view = ft.View(
                route="/despachos/detalle",
                appbar=UIStyles.get_appbar(
                    "Detalle de despachos",
                    leading=ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        icon_color=ft.Colors.WHITE,
                        on_click=lambda _: (
                            self.page.views.pop(),
                            setattr(self.page, "route", "/despachos"),
                            self.page.update()
                        )
                    )
                ),
                controls=[
                    ft.Container(
                        expand=True,
                        padding=ft.padding.only(left=2, right=2, top=10, bottom=10),
                        content=ft.Column([
                            ft.Text(nombre_entidad, weight="bold", size=18, color=ft.Colors.BLUE_GREY_800),
                            ft.Divider(),
                            ft.Text(
                                f"No se pudo cargar el detalle: {e}",
                                color=ft.Colors.RED_700,
                                size=14,
                            )
                        ], scroll=ft.ScrollMode.AUTO, expand=True)
                    )
                ]
            )
            self.page.views.append(error_view)
            self.page.go("/despachos/detalle")
            self.page.update()
        finally:
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
                    padding=ft.padding.only(left=10, right=10, top=10, bottom=0),
                    content=ft.Column([
                        ft.Text("Filtros de Búsqueda", size=16, weight="bold"),
                        ft.Row([
                            self.dd_campana,
                            self.dd_cultivo,
                        ], spacing=10),
                        
                        ft.Divider(),
                        
                        # Contenedor dinámico de vistas
                        ft.Text("Resumen por Entregado", size=16, weight="bold"),
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