import flet as ft

def main(page: ft.Page):
    page.title = "Prueba Entorno Nuevo"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    
    page.add(
        ft.Row(
            [
                ft.Text("¡Entorno Nuevo Funcionando!", size=24, color="green", weight=ft.FontWeight.BOLD)
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
    )

if __name__ == "__main__":
    ft.app(target=main)