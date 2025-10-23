import os
import flet as ft
class HomeService:
    """Controla a lógica de seleção e armazenamento do repositório."""

    def __init__(self):
        self.repo_path = None  # guarda o caminho da pasta
        self.artefacts:list[str] = []
        self.artefact_type: str = ''

    def show_error(self, page: ft.Page, message: str):
        # Criar o diálogo de erro
        
        dlg_error = ft.AlertDialog(
            modal=True,
            title=ft.Text("Erro!"),
            content=ft.Text(message),
            actions=[
                ft.TextButton("OK", on_click=lambda e: page.close(dlg_error)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=lambda e: print("Erro fechado!"),
        )
        page.open(dlg_error)





    def select_repo(self, page: ft.Page, callback=None):
        """Abre o seletor de pastas e guarda o caminho escolhido."""

        def on_result(res: ft.FilePickerResultEvent):
            if res.path:
                self.repo_path = res.path
                print(f"[RepoService] Repositório selecionado: {self.repo_path}")
                if callback:
                    callback(self.repo_path)  # atualiza a UI se necessário
            else:
                print("[RepoService] Nenhuma pasta selecionada.")

        picker = ft.FilePicker(on_result=on_result)
        page.overlay.append(picker)
        page.update()
        picker.get_directory_path()
    
    def select_artefact_type(self, page: ft.Page,str:str):
        self.artefact_type = str
        print('tipo: ', self.artefact_type)
        base_path = os.path.normpath(os.path.join(
            self.repo_path,
            self.artefact_type, "src", "main", "java", 'br', "com", "mv", "soul",
            os.path.basename(self.repo_path),
            self.artefact_type
        ))
        print(base_path)
        if not os.path.exists(base_path):
            print('erro')
            self.show_error(page, 'Esse caminho não é válido!\nSelecione a base do repositório')

        return ['OREcConv', 'MConRec', 'TelaExemplo','OPag']
