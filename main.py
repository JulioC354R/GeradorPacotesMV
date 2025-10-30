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

    # Cria a tela principal (importada de ui/home.py)
    home = HomePage(page)
    page.add(home)


ft.app(target=main)
