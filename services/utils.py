

import flet as ft

class Utils:

    def __init__(self):
        pass
    def show_error(page: ft.Page, message: str):
            # Criar o diálogo de erro
        
        dlg_error = ft.AlertDialog(
            modal=True,
            title=ft.Text("Erro!"),
            content=ft.Text(message),
            actions=[
                ft.TextButton("OK", on_click=lambda e: page.close(dlg_error)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=lambda e: print("Erro fechado!"),
        )
        page.open(dlg_error)