import flet as ft
from services.home_services import HomeService
from services.utils import Utils

class HomePage(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.home_service = HomeService()
        self.utils = Utils()

        
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

          # Botão de processar
        self.btn_process = ft.ElevatedButton(
            text="Processar",
            icon=ft.Icons.PLAY_ARROW,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.GREEN_600,
            ),
            on_click=self.on_process_click,
        )


        # Montagem dos componentes
        self.controls = [
            ft.Column(
                [
                    ft.Row([self.repo_input, self.btn_select_repo]),
                    ft.Row([self.artefact_type, self.artefacts]),
                    ft.Text("Artefatos selecionados:"),
                    self.selected_container,
                ],
                expand=True,  # ocupa o espaço vertical restante
            ),
            ft.Container(
                content=self.btn_process,
                alignment=ft.alignment.center_right,
                padding=ft.padding.only(top=10, bottom=10),
            ),
        ]
        self.expand = True
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

    def on_process_click(self, e):
        """Abre a janela de logs e inicia o processamento."""

        # Validações
        if not self.repo_input.value:
            Utils.show_message(self.page,"Selecione um repositório.")
            return

        if not self.artefact_type.value:
            Utils.show_message(self.page,"Selecione um tipo de artefato.")
            return

        if not self.home_service.selected_artefacts:
            Utils.show_message(self.page,"Selecione ao menos um artefato.")
            return

        # Se passou todas as validações, abre a tela de logs
        # Cria uma barra de progresso e adiciona na UI
        self.progress_bar = ft.ProgressBar(width=400, value=0)
        self.progress_text = ft.Text("Iniciando processamento...", size=14)
        self.page.overlay.append(
            ft.AlertDialog(
                modal=True,
                title=ft.Text("Processando artefatos"),
                content=ft.Column(
                    [self.progress_text, self.progress_bar],
                    tight=True,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                ),
            )
        )

        dialog = self.page.overlay[-1]
        dialog.open = True
        self.page.update()


        # Inicia o processamento em background
        def process_task():
            mvn_sucess = True
            total = len(self.home_service.selected_artefacts)

            # Cria campo de log dentro do diálogo
            log_field = ft.ListView(
            expand=True,
            auto_scroll=True,   # faz o scroll automático pro final
            height=200,
            spacing=3,
            padding=ft.padding.all(8),
            )
            # adiciona a primeira linha de log
            log_field.controls.append(ft.Text("Iniciando processamento..."))
            dialog.content.controls.append(log_field)
            dialog.update()
            self.page.update()

            def append_log(line: str):
                # remove quebra de linha e adiciona como novo Text
                log_field.controls.append(ft.Text(line.strip()))
                # evita crescimento infinito (opcional)
                if len(log_field.controls) > 1000:
                    log_field.controls.pop(0)
                log_field.update()

            for i, artefact in enumerate(self.home_service.selected_artefacts, start=1):
                self.progress_text.value = f"Processando {artefact.name} ({i}/{total})..."
                self.progress_bar.value = i / total +1
                self.page.update()

                if not self.home_service.check_build(artefact.build_path, artefact.type): # Se não tiver arquivo de build, rodar mvn clean install
                    self.progress_text.value = f"Executando mvn clean install..."
                    self.page.update()
                    mvn_sucess = self.home_service.mvn_clean_install(on_log=append_log)
                    if not mvn_sucess:
                        break

                self.home_service.process_artefact(artefact)

            # Finaliza

            self.progress_text.value = "Processamento concluído!"
            self.progress_bar.value = 1.0



            self.page.update()
            import time
            time.sleep(1)
            dialog.open = False
            self.page.update()

            Utils.show_message(
                self.page,
                "Processamento concluído!" if mvn_sucess else "GERAÇÃO FALHOU!",
                "",
            )

        # Roda em thread para não travar a UI
        self.page.run_thread(process_task)
