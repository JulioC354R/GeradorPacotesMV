import os
import flet as ft
from ui.home import HomePage

def main(page: ft.Page):
    page.title = "Gerador de Pacotes HTML5"
    page.padding = 20
    page.window.resizable = True 
    page.window.width = 800
    page.window.height = 600

    # Cria a tela principal (importada de ui/home.py)
    home = HomePage(page)
    page.add(home)


ft.app(target=main)
