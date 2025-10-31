from dataclasses import dataclass
import os
from pathlib import Path
import subprocess
import flet as ft
from services.utils import Utils
import shutil

@dataclass
class Artefact:
    name: str
    type:str
    path: str
    build_path: str



class HomeService:
    """Camada de lógica de negócio da HomePage."""

    def __init__(self):
        self.destiny_path = 'C:\\MV_HTML5\\pacotes_gerados'
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
            Artefact(
                name=f,
                type=artefact_type.lower(),
                path=os.path.join(base_path, f),
                build_path=os.path.normpath(
                    os.path.join(
                        self.repo_path,
                        artefact_type.lower(),
                        "target",
                        "classes",
                        "br",
                        "com",
                        "mv",
                        "soul",
                        os.path.basename(self.repo_path),
                        artefact_type.lower(),
                        f.lower()
                    )
                )
                
            )
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


    

    def process_artefact(self, artefact: Artefact, jira: str | None, cervello: str | None, client: str | None):
        pack_name ='soul-'+ os.path.basename(self.repo_path) + '-'+ artefact.type.lower()
        if jira:
            pack_name+= '_' + jira
        if cervello:
            pack_name += '_' + cervello
        if client:
            pack_name += '_' + client 

        dest_dir = os.path.join(self.destiny_path, 'tmp', pack_name,  artefact.name)
        shutil.copytree(artefact.build_path, dest_dir, dirs_exist_ok=True)
        self.zip_packages()
        
    def zip_packages(self):
        dirs = os.listdir(os.path.join(self.destiny_path, 'tmp'))
        for item in dirs:
            item_path = os.path.join(self.destiny_path, 'tmp', item)
            zip_path = os.path.join(self.destiny_path, item)
            shutil.make_archive(zip_path,'zip', item_path)

    def clear_temp(self):    
        shutil.rmtree(os.path.join(self.destiny_path, 'tmp'))



    def check_build(self, build_path: str, type_str: str):
        path = Path(build_path)
        has_class = any(path.rglob("*.class"))
        return has_class

    def mvn_clean_install(self, on_log=None):
        os.chdir(self.repo_path)
        command_succeeded = False

        process = subprocess.Popen(
            ["cmd", "/c","mvn", "clean", "install", "-U"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        for line in process.stdout:
            if on_log:
                on_log(line)  # envia o log para o callback
            if "[INFO] BUILD SUCCESS" in line:
                command_succeeded = True

        process.wait()
        return command_succeeded
                
