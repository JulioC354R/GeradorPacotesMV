import flet as ft

from services.home_services import Artefact

class ProcessPage(ft.Column):
    def __init__(self, page: ft.Page, artefacts_to_process: list[Artefact]):
        super().__init__()
        self.page = page
        self.artefacts = artefacts_to_process
        self.count = 1
        
        # Área de logs - IMPORTANTE: REMOVA read_only=True
        self.log_area = ft.TextField(
            label="Logs (Digite aqui ou use o botão para adicionar)",
            multiline=True,
            expand=True,
            # Não defina min_lines ou max_lines para permitir expansão total
        )

        self.controls = [
            ft.Row([
                ft.ElevatedButton("Voltar para Home", on_click=self.go_back),
                ft.ElevatedButton("Adicionar log de teste", on_click=self.add_sample_log)
            ]),
            # O Container com expand=True garante que o TextField ocupe o espaço
            ft.Container(content=self.log_area, expand=True) 
        ]
        
        # A própria coluna deve expandir
        self.expand = True

    def go_back(self, e):
        from ui.home import HomePage
        self.page.controls.clear()
        self.page.add(HomePage(self.page))

    def add_log(self, message: str):
        """
        Adiciona uma linha de log, força a rolagem para o final, 
        e garante que o cursor fique na última linha.
        """
        # 1. Atualiza o valor do texto
        if self.log_area.value:
            self.log_area.value += "\n" + message
        else:
            self.log_area.value = message

        end_of_text = len(self.log_area.value)
        self.log_area.selection_end = end_of_text
        self.log_area.selection_start = end_of_text # Garante que não haja seleção
        self.log_area.focus() 


    def add_sample_log(self, e):
        """Exemplo de log."""
        self.count += 1
        self.add_log(f"Log de teste adicionado! {self.artefacts}")

    

