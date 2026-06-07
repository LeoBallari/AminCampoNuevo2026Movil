import flet as ft

class UIStyles:
    """Clase para estandarizar la interfaz en todas las pantallas"""
    
    @staticmethod
    def get_appbar(title, on_home_click=None, leading=None, actions=None):
        """Genera un AppBar estandarizado"""
        return ft.AppBar(
            leading=leading if leading else ft.IconButton(
                icon=ft.Icons.HOME,
                icon_color=ft.Colors.WHITE,
                on_click=on_home_click
            ),
            title=(
                title 
                if isinstance(title, ft.Control) 
                else ft.Text(str(title), size=18, weight="bold")
            ),
            bgcolor=ft.Colors.BLUE_GREY_900,
            color=ft.Colors.WHITE,
            center_title=False,
            actions=actions,
            elevation=4,  # Agrega la sombra (elevación)
            shadow_color=ft.Colors.BLACK, # Define el color de la sombra
        )

    @staticmethod
    def get_footer_container(content):
        """Genera un contenedor de pie de página estético"""
        return ft.Container(
            content=content,
            bgcolor=ft.Colors.BLUE_GREY_900,
            padding=ft.padding.only(left=20, right=20, top=15, bottom=60),
            border_radius=ft.border_radius.only(top_left=20, top_right=20),
            shadow=ft.BoxShadow(
                blur_radius=10, color=ft.Colors.with_opacity(0.3, "black")
            ),
        )

    @staticmethod
    def get_card_container(content, padding=10, margin=0):
        """Genera un contenedor con estilo de tarjeta estandarizado (Surface Variant)"""
        return ft.Container(
            content=content,
            bgcolor="surfacevariant",
            border_radius=8,
            padding=padding,
            margin=margin,
            border=ft.border.all(0.5, "outlinevariant"),
        )