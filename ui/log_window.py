import flet as ft
import time
import threading


class LogWindow:
    """Janela separada para exibir logs."""

    def __init__(self, page: ft.Page):
        self.page = page
        self.text_area = ft.TextField(
            multiline=True,
            read_only=True,
            expand=True,
            min_lines=20,
            max_lines=40,
            border_color=ft.Colors.BLUE_GREY_100,
            text_style=ft.TextStyle(font_family="monospace"),
        )
        self.window = None

    def open(self):
        """Cria e mostra uma nova janela com área de logs."""
        if self.window:
            # já está aberta
            self.window.show()
            return

        self.window = ft.Window(
            title="Processamento de Artefatos",
            width=700,
            height=500,
            content=ft.Column(
                [
                    ft.Text("Logs do processamento", size=20, weight=ft.FontWeight.BOLD),
                    self.text_area,
                ],
                expand=True,
                spacing=10,
            ),
        )
        self.window.show()

    def write_log(self, message: str):
        """Escreve uma linha de log na área de texto."""
        self.text_area.value += f"{message}\n"
        self.text_area.update()

