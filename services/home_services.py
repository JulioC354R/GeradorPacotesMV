from dataclasses import dataclass
import os
import flet as ft
from services.utils import Utils

@dataclass
class Artefact:
    name: str
    module:str
    path: str



class HomeService:
    """Camada de lógica de negócio da HomePage."""

    def __init__(self):
        self.repo_path: str | None = None
        self.artefact_type: str = ""
        self.artefacts_list: list[Artefact] = []
        self.selected_artefacts: list[Artefact] = []
        

    # -------------------------------------------------
    # SELEÇÃO DE PASTA
    # -------------------------------------------------
    def select_repo(self, page: ft.Page, callback=None):
        """Abre o seletor de pastas e guarda o caminho escolhido."""
        def on_result(res: ft.FilePickerResultEvent):
            if res.path:
                self.repo_path = res.path
                if callback:
                    callback(self.repo_path)

        picker = ft.FilePicker(on_result=on_result)
        page.overlay.append(picker)
        page.update()
        picker.get_directory_path()

    # -------------------------------------------------
    # CARREGAMENTO DE ARTEFATOS
    # -------------------------------------------------
    def select_artefact_type(self, page: ft.Page, artefact_type: str):
        """Define o tipo e busca os artefatos do diretório correspondente."""
        self.artefact_type = artefact_type
        if not self.repo_path:
            Utils.show_message(page, "Selecione um repositório primeiro!")
            return

        base_path = os.path.normpath(os.path.join(
            self.repo_path,
            artefact_type.lower(), "src", "main", "java", "br", "com", "mv", "soul",
            os.path.basename(self.repo_path),
            artefact_type.lower()
        ))

        if not os.path.exists(base_path):
            Utils.show_message(page, "Esse caminho não é válido!\nSelecione a base do repositório.")
            self.artefacts_list = []
            return

        # Aqui criamos objetos Artefact ao invés de strings
        self.artefacts_list = [
            Artefact(name=f, path=os.path.join(base_path, f), module= artefact_type.lower())
            for f in os.listdir(base_path)
            if os.path.isdir(os.path.join(base_path, f))
        ]

    # -------------------------------------------------
    # MANIPULAÇÃO DE ARTEFATOS SELECIONADOS
    # -------------------------------------------------
    def add_artefact(self, artefact: Artefact):
        """Adiciona um artefato à lista se ainda não estiver presente."""
        if artefact not in self.selected_artefacts:
            self.selected_artefacts.append(artefact)

    def remove_artefact(self, artefact: Artefact):
        """Remove um artefato da lista."""
        if artefact in self.selected_artefacts:
            self.selected_artefacts.remove(artefact)
