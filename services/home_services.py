import os
import flet as ft
from services.utils import Utils
class HomeService:
    """Controla a lógica de seleção e armazenamento do repositório."""

    def __init__(self):
        self.repo_path = None  # guarda o caminho da pasta
        self.artefacts_list:list[str] = []
        self.artefact_type: str = ''

    def select_repo(self, page: ft.Page, callback=None):
        """Abre o seletor de pastas e guarda o caminho escolhido."""

        def on_result(res: ft.FilePickerResultEvent):
            if res.path:
                self.repo_path = res.path
                if callback:
                    callback(self.repo_path)  # atualiza a UI se necessário

        picker = ft.FilePicker(on_result=on_result)
        page.overlay.append(picker)
        page.update()
        picker.get_directory_path()
    
    def select_artefact_type(self, page: ft.Page,str:str):
        self.artefact_type = str
        base_path = os.path.normpath(os.path.join(
            self.repo_path,
            self.artefact_type, "src", "main", "java", 'br', "com", "mv", "soul",
            os.path.basename(self.repo_path),
            self.artefact_type
        ))
        if not os.path.exists(base_path):
           Utils.show_error(page, 'Esse caminho não é válido!\nSelecione a base do repositório')
        self.artefacts_list = [f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))]
