import os
import subprocess
import flet as ft
from services.home_services import Artefact, HomeService
import time
import threading
from pathlib import Path
from services.utils import Utils

class ProcessPage(ft.Column):
    def __init__(self, page: ft.Page, home_service: HomeService):
        super().__init__()
        self.page = page
        self._active = True  # Página está ativa
        self.home_service = home_service

        self.log_area = ft.TextField(
            label="Logs",
            multiline=True,
            expand=True,
            text_size=12,
            autofocus=True
        )

        self.controls = [
            ft.Container(content=self.log_area, expand=True)
        ]

        self.expand = True

        self.page.add(self)
        self.page.update()

        # Inicia o processo automaticamente em thread
        threading.Thread(target=self.start_long_process, args=(None,), daemon=True).start()
    def add_log(self, message: str):
        if not self._active:  # não atualiza se a página não estiver ativa
            return
        if self.log_area.value:
            self.log_area.value += "\n" + message
        else:
            self.log_area.value = message
        self.log_area.focus()
        self.log_area.update()
        

        

    def start_long_process(self, e):
        self.add_log("Iniciando processo em background...")
        self.long_running_task()

    def long_running_task(self):
        try:
            for i, artefact in enumerate(self.home_service.selected_artefacts):
                if not self._active:
                    break
                self.page.run_thread(self.add_log, f"Processando item {i+1}: {str(artefact)}")
                has_class = self.check_build(type_str= artefact.module, artefact_str=artefact.name)
                if has_class:
                    success = self.mvn_clean_install()
                    if not success:
                        Utils.show_message(self.page, 'OCORREU UM ERRO DURANTE O MVN CLEAN INSTALL')
                    
                
            
            if self._active:
                self.page.run_thread(self.add_log, "Processo finalizado!")

            from ui.home import HomePage
            self.page.clean()
            home = HomePage(self.page)
            self.page.add(home)
            time.sleep(0.5)

            
            Utils.show_message(self.page, 'Processo concluído com sucesso', 'Mensagem')
            # Fecha a janela da aplicação

            
            

        except Exception as ex:
            if self._active:
                self.page.run_thread(self.add_log, f"ERRO no processo: {ex}")
        

    def check_build(self, type_str: str, artefact_str: str):
        print(artefact_str)
        print(self.home_service.repo_path)
        print()
        file_path = os.path.normpath(os.path.join(
            self.home_service.repo_path,
            type_str, "target", "classes", "br", "com", "mv", "soul",
            os.path.basename(self.home_service.repo_path),
            type_str,
            artefact_str
        ))
        print(file_path)
        path = Path(file_path)
        has_class = any(path.rglob("*.class"))
        print(has_class)
        return has_class

    def mvn_clean_install(self):
        os.chdir(self.home_service.repo_path)
        command_succeeded = False
        commands = ['mvn clean install -U']
        for command in commands:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=True,
                text=True,
                bufsize=1
            )

        # Lê o log sem travar a UI
        for line in process.stdout:
            # Usa after() para atualizar o log de forma segura na thread principal
            self.page.run_thread(self.add_log, line)
            if "[INFO] BUILD SUCCESS" in line:
                command_succeeded = True

        process.wait()

        return command_succeeded
                

    

        
        
