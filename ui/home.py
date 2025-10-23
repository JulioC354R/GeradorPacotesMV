import flet as ft
from services.home_services import HomeService

class HomePage(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.repo_service = HomeService()

        # Campo de texto onde aparece a pasta escolhida
        self.repo_input = ft.TextField(
            label="Pasta do repositório",
            expand=True,
            read_only=True,
        )

        # Botão para selecionar pasta
        self.btn_select_repo = ft.IconButton(
            icon=ft.Icons.FOLDER,
            tooltip="Selecionar repositório",
            icon_color=ft.Colors.BLUE,
            on_click=self.on_select_repo,
        )

        # Campo de selecionar tipo de artefato:
        self.artefact_type = ft.Dropdown(
            label="Selecione o tipo",
            options=[
                ft.dropdown.Option("Forms"),
                ft.dropdown.Option("Reports"),
                ft.dropdown.Option("Libs")
            ],
            on_change=self.on_type_change
        )

        # Campo para pesquisar o artefato
        
        self.artefacts = ft.Dropdown(
            label="Selecione o artefato",
            editable=True,
            enable_search=True, # essas configs permitem que eu pesquise
            enable_filter=True,
            expand=True,
            options=[ft.dropdown.Option(artefact) for artefact in self.repo_service.artefacts],
        )
        



        # Montagem da linha (input + botão)
        self.controls = [
            ft.Row([self.repo_input, self.btn_select_repo]),
            ft.Row([self.artefact_type, self.artefacts])
        ]

        
    def on_type_change(self, e):
            self.repo_service.select_artefact_type( self.page, self.artefact_type.value)

    def on_select_repo(self, e):
        """Chama o serviço pra selecionar pasta."""
        self.repo_service.select_repo(self.page, callback=self.update_repo_input)

    def update_repo_input(self, path: str):
        """Atualiza o campo com o caminho escolhido."""
        self.repo_input.value = path
        self.repo_input.update()

 
