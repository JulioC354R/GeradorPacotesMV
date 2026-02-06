from dataclasses import dataclass
import os
from pathlib import Path
import re
import subprocess
import flet as ft
from services.utils import Utils
import shutil
from queue import Queue
from zipfile import ZipFile
import json


@dataclass
class Artefact:
    name: str
    type: str
    path: str
    module: str
    build_path: str


class HomeService:
    """Camada de lógica de negócio da HomePage."""

    def __init__(self):
        self.destiny_path = "C:\\MV_HTML5\\pacotes_gerados"
        self.repo_path: str | None = None
        self.artefact_type: str = ""
        self.artefacts_list: list[Artefact] = []
        self.selected_artefacts: list[Artefact] = []
        self.temp_path = os.path.join(self.destiny_path, "tmp")

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

        base_path = os.path.normpath(
            os.path.join(
                self.repo_path,
                artefact_type.lower(),
                "src",
                "main",
                "java",
                "br",
                "com",
                "mv",
                "soul",
                os.path.basename(self.repo_path),
                artefact_type.lower(),
            )
        )

        if not os.path.exists(base_path):
            Utils.show_message(
                page, "Esse caminho não é válido!\nSelecione a base do repositório."
            )
            self.artefacts_list = []
            return

        # Aqui criamos objetos Artefact ao invés de strings
        self.artefacts_list = [
            Artefact(
                name=f,
                type=artefact_type.lower(),
                path=os.path.join(base_path, f),
                module=os.path.basename(self.repo_path),
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
                        f.lower(),
                    )
                ),
            )
            for f in os.listdir(base_path)
            if os.path.isdir(os.path.join(base_path, f))
        ]

        if artefact_type.lower() == "libs":
            parent_folder = os.path.dirname(base_path)
            libs_on_parent_folder = [
                Artefact(
                    name=f,
                    type=artefact_type.lower(),
                    path=os.path.join(parent_folder, f),
                    module=os.path.basename(self.repo_path),
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
                            f.lower(),
                        )
                    ),
                )
                for f in os.listdir(parent_folder)
                if os.path.isdir(os.path.join(parent_folder, f))
            ]

            for item in libs_on_parent_folder:
                self.artefacts_list.append(item)

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

    def process_artefact(
        self,
        artefact: Artefact,
        jira: str | None,
        cervello: str | None,
        client: str | None,
    ):
        pack_name = "soul-" + artefact.module + "-" + artefact.type.lower()
        if jira:
            pack_name += "_" + jira
        if cervello:
            pack_name += "_" + cervello
        if client:
            pack_name += "_" + client

        pack_name = re.sub(r'[<>:"/\\|?*\x00-\x1F]', "", pack_name).replace(" ", "")

        dest_dir = os.path.join(self.temp_path, pack_name, artefact.name)
        shutil.copytree(artefact.build_path, dest_dir, dirs_exist_ok=True)
        self.verify_major(pack_name)
        self.zip_packages()

    def zip_packages(self):
        for item in os.listdir(self.temp_path):
            item_path = os.path.join(self.temp_path, item)
            if not os.path.isdir(item_path):  # <-- ignora JSON e outros arquivos
                continue

            zip_path = os.path.join(self.destiny_path, item)
            shutil.make_archive(zip_path, "zip", item_path)

    def clear_temp(self):
        path = self.temp_path
        if os.path.exists(path):
            shutil.rmtree(path)

    def check_build(self, build_path: str):
        path = Path(build_path)
        has_class = any(path.rglob("*.class"))
        return has_class

    def mvn_clean_install(self, on_log=None):
        os.chdir(self.repo_path)
        command_succeeded = False

        process = subprocess.Popen(
            ["cmd", "/c", "mvn", "clean", "install", "-U"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        for line in process.stdout:
            if on_log:
                on_log(line)  # envia o log para o callback
            if "[INFO] BUILD SUCCESS" in line:
                command_succeeded = True

        process.wait()
        return command_succeeded

    def open_destiny_path(self):
        subprocess.Popen(
            ["explorer.exe", r"C:\MV_HTML5\pacotes_gerados"],
            stdout=subprocess.PIPE,
            bufsize=1,
        )

    def verify_major(self, path):

        def get_major_version_from_class_bytes(b: bytes) -> int:
            """Extrai o major version a partir dos bytes de um .class"""
            return int.from_bytes(b[6:8], byteorder="big")  # 7º e 8º byte

        repo_path = Path(os.path.join(self.temp_path, path)).resolve()

        # filas
        dirs_queue = Queue()
        class_files_queue = Queue()
        jar_files_queue = Queue()

        # resultados
        result_classes = {}
        result_jars = {}

        # 1️⃣ percorre apenas o primeiro nível para target/classes e jars
        for first_level in repo_path.iterdir():
            if not first_level.is_dir():
                continue

            # pastas target/classes
            target_classes = first_level  # / "target" / "classes"
            if target_classes.exists() and target_classes.is_dir():
                dirs_queue.put(target_classes)

            # arquivos .jar no primeiro nível e recursivamente
            for jar_file in first_level.rglob("*.jar"):
                if jar_file.is_file():
                    jar_files_queue.put(jar_file.resolve())

        print("✅ Terminou primeiro nível")
        print("Pastas para BFS:", list(dirs_queue.queue))
        print("JARs encontrados:", list(jar_files_queue.queue))

        # 2️⃣ BFS para .class
        while not dirs_queue.empty():
            current_dir = dirs_queue.get()
            for item in current_dir.iterdir():
                if item.is_dir():
                    dirs_queue.put(item)
                elif item.is_file() and item.suffix == ".class":
                    class_files_queue.put(item.resolve())

        print("✅ BFS completo para .class")
        print("Total de .class encontrados:", class_files_queue.qsize())

        # 3️⃣ processa os .class encontrados
        while not class_files_queue.empty():
            class_file = class_files_queue.get()
            try:
                major = get_major_version_from_class_bytes(class_file.read_bytes())
                result_classes[class_file.name] = major
            except Exception:
                result_classes[class_file.name] = "ERROR"

        print("✅ Verificou .class")
        print("Total de .class processados:", len(result_classes))

        # 4️⃣ processa os .jar encontrados
        while not jar_files_queue.empty():
            jar_file = jar_files_queue.get()
            jar_entry = {"path": str(jar_file), "classes": {}}
            try:
                with ZipFile(jar_file, "r") as zipf:
                    for file in zipf.namelist():
                        if file.endswith(".class"):
                            data = zipf.read(file)
                            try:
                                jar_entry["classes"][file] = (
                                    get_major_version_from_class_bytes(data)
                                )
                            except Exception:
                                jar_entry["classes"][file] = "ERROR"
                result_jars[jar_file.name] = jar_entry
            except Exception:
                result_jars[jar_file.name] = {"path": str(jar_file), "classes": "ERROR"}

        print("✅ Verificou .jar")
        print("Total de JARs processados:", len(result_jars))

        # 5️⃣ salva os JSONs

        output_classes = Path(repo_path) / "major_versions_classes.json"
        with output_classes.open("w", encoding="utf-8") as f:
            json.dump(result_classes, f, indent=2)

        output_jars = Path(repo_path) / "major_versions_jars.json"
        with output_jars.open("w", encoding="utf-8") as f:
            json.dump(result_jars, f, indent=2)

        print(f"📄 JSON de classes: {output_classes} | total: {len(result_classes)}")
        print(f"📄 JSON de jars: {output_jars} | total: {len(result_jars)}")
