import os
import sys
import flet as ft
from ui.home import HomePage

def main(page: ft.Page):
    page.title = "Gerador de Pacotes HTML5"
    page.padding = 20
    page.window.resizable = True 
    page.window.width = 800
    page.window.height = 600
    if getattr(sys, 'frozen', False):
    # Caminho quando o app está empacotado pelo PyInstaller
        base_path = sys._MEIPASS
    else:
        # Caminho normal durante o desenvolvimento
        base_path = os.path.dirname(__file__)
    icon_path = os.path.join(base_path, "assets/icone_menhera-kun.ico")
    page.window.icon = icon_path

    def reload_page(e):
        page.controls.clear()
        home = HomePage(page, btn_clear)  # captura o retorno
        page.add(home)                     # adiciona à página
        page.update()

    # Cria a tela principal (importada de ui/home.py)

    # Botão de Limpar
    btn_clear = ft.ElevatedButton(
        text="Limpar",
        icon=ft.Icons.CLEAR,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.RED_600,
        ),
        on_click=reload_page,
    )
    home = HomePage(page, btn_clear)
    page.add(home)


ft.app(target=main)
