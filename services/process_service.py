# services/process_service.py
import time
from services.home_services import Artefact

class ProcessService:
    def __init__(self):
        # Campos similares aos do HomeService
        self.repo_path: str | None = None
        self.artefact_type: str = ""
        self.artefacts_list: list[Artefact] = []
        self.selected_artefacts: list[Artefact] = []

        # Callback para logs (deve ser setado pela UI)
        self.add_log_callback = None

    def set_log_callback(self, log_callback):
        """Define a função que será usada para adicionar logs na UI."""
        self.add_log_callback = log_callback

    def add_log(self, message: str):
        """Envia log para a UI se a função estiver definida."""
        if self.add_log_callback:
            self.add_log_callback(message)
        else:
            print(message)  # fallback no console

    def start_processing(self):
        """Exemplo de processamento de artefatos."""
        self.add_log("Iniciando processamento...")
        if not self.selected_artefacts:
            self.add_log("Nenhum artefato selecionado!")
            return

        for i, art in enumerate(self.selected_artefacts, start=1):
            self.add_log(f"Processando artefato {i}/{len(self.selected_artefacts)}: {art.name}")
            # Simula algum processamento demorado
            time.sleep(0.5)
            self.add_log(f"Artefato {art.name} processado com sucesso!")

        self.add_log("Processamento finalizado.")
