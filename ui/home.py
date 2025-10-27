import flet as ft
from services.home_services import HomeService


class HomePage(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.home_service = HomeService()
        
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

        # Campo de selecionar tipo de artefato
        self.artefact_type = ft.Dropdown(
            label="Selecione o tipo",
            options=[
                ft.dropdown.Option("Forms"),
                ft.dropdown.Option("Reports"),
                ft.dropdown.Option("Libs")
            ],
            on_change=self.on_type_change,
        )

        # Campo para pesquisar e escolher artefato
        self.artefacts = ft.Dropdown(
            label="Selecione o artefato",
            editable=True,
            enable_search=True,
            enable_filter=True,
            expand=True,
            menu_height=300,
            options=[],
            on_change=self.on_artefact_selected,
        )

        # Container onde serão mostrados os artefatos selecionados
        self.selected_container = ft.ResponsiveRow(
            alignment=ft.MainAxisAlignment.START,
            run_spacing=5,
            columns=12,
        )

        # Montagem dos componentes
        self.controls = [
            ft.Row([self.repo_input, self.btn_select_repo]),
            ft.Row([self.artefact_type, self.artefacts]),
            ft.Text("Artefatos selecionados:"),
            self.selected_container,
        ]

    # -------------------------------------------------
    # EVENTOS DE UI
    # -------------------------------------------------
    def on_select_repo(self, e):
        """Abre seletor de pasta e atualiza o campo na UI."""
        self.home_service.select_repo(self.page, callback=self.update_repo_input)

    def update_repo_input(self, path: str):
        """Atualiza o campo com o caminho escolhido."""
        self.repo_input.value = path
        self.repo_input.update()

    def on_type_change(self, e):
        """Quando muda o tipo de artefato, carrega as opções."""
        self.home_service.select_artefact_type(self.page, self.artefact_type.value)
        self.artefacts.options = [
            ft.dropdown.Option(a.name) for a in self.home_service.artefacts_list
        ]
        self.artefacts.value = None
        self.artefacts.update()


    def on_artefact_selected(self, e):
        """Quando escolhe um artefato, adiciona à lista de selecionados."""
        selected_name = self.artefacts.value
        if not selected_name:
            return

        # pega o objeto correspondente
        artefact = next(
            (a for a in self.home_service.artefacts_list if a.name == selected_name),
            None
        )
        if artefact is None:
            return

        self.home_service.add_artefact(artefact)
        self.update_selected_list()
        self.artefacts.value = None
        self.artefacts.update()

    def remove_artefact(self, artefact):
        """Remove artefato da lista."""
        self.home_service.remove_artefact(artefact)
        self.update_selected_list()

    def update_selected_list(self):
        self.selected_container.controls = [
            ft.Container(
                content=ft.Chip(
                    label=ft.Text(f"{a.name}"),
                    tooltip=a.path,
                    delete_icon=ft.Icon(ft.Icons.CLOSE),
                    on_delete=lambda e, artefact=a: self.remove_artefact(artefact),
                ),
                col={"xs": 6, "sm": 4, "md": 3, "lg": 2},
            )
            for a in self.home_service.selected_artefacts
        ]
        self.selected_container.update()