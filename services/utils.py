

import flet as ft

class Utils:

    def __init__(self):
        pass
    def show_message(page: ft.Page, message: str,  tittle: str = 'Erro!'):
            # Criar o diálogo de erro
        
        dlg_error = ft.AlertDialog(
            modal=True,
            title=ft.Text(tittle),
            content=ft.Text(message),
            actions=[
                ft.TextButton("OK", on_click=lambda e: page.close(dlg_error)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.open(dlg_error)