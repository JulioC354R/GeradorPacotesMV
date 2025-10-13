import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import subprocess
import shutil


# ------ Variaveis Globais ----------

command_succeeded = False

# ------ Funções ------------------

def select_repo():
    repo = filedialog.askdirectory()
    entry_repo_dir.delete(0, tk.END)
    entry_repo_dir.insert(0, repo)



def load_windows(event:None):
    window_type = combo_type.get()
    repo_dir = entry_repo_dir.get()
    entry_repo_dir.delete(0, tk.END)
    entry_repo_dir.insert(0, repo_dir)
    forms_path = os.path.normpath(os.path.join(
        repo_dir,
        window_type, "src", "main", "java", 'br', "com", "mv", "soul",
        os.path.basename(repo_dir),
        window_type
    ))

    if not os.path.exists(forms_path):
        messagebox.showerror("Erro", f"Caminho não encontrado:\n{forms_path}")
        lista_pacotes = []
        combobox_windows['values'] = lista_pacotes
        return

    lista_pacotes = [f for f in os.listdir(forms_path) if os.path.isdir(os.path.join(forms_path, f))]
    if window_type == 'libs':
        dbservices_path = os.path.normpath(os.path.join(
        repo_dir,
        window_type, "src", "main", "java", 'br', "com", "mv", "soul",
        os.path.basename(repo_dir),
        'dbservices'
        ))
        if os.path.exists(dbservices_path):
            lista_pacotes.append('dbservices')
    
    combobox_windows['values'] = lista_pacotes
    if lista_pacotes:
        combobox_windows.current(0)
    else:
        combobox_windows.set('')


def process():
    btn_process.config(state="disabled")
    repo_dir = entry_repo_dir.get()
    window = combobox_windows.get()
    type = combo_type.get()
    

    if not repo_dir:
        messagebox.showerror("Erro", "Selecione o caminho do repositório!")
        return
    if not window:
        messagebox.showerror("Erro", "Selecione um pacote!")
        return
    if not type:
        messagebox.showerror("Erro", "Selecione o Tipo")
        return

    text_output.delete("1.0", tk.END)
    
    if force_maven_update_var.get():
        write_log("\n[Aguardando conclusão do Maven...]\n")
        
        # -------- Executa comandos ---------
        os.chdir(repo_dir)
        process = subprocess.Popen(
            ["mvn", "clean", "install", "-U"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell= True,
            text=True,
            bufsize=1
        )

        # Lê linha por linha enquanto o processo está rodando
        for line in process.stdout:
            if line == "[INFO] BUILD SUCCESS\n":
                command_succeeded = True
            write_log(line)

        process.wait()  # espera o processo terminar


        if command_succeeded:
            make_zip(repo_dir, window, type)
            write_log("\n[Processo finalizado]\n")
        else:   
            messagebox.showerror("Erro", f"Ocorreu um erro! Pacote não gerado!!")
    else:
        make_zip(repo_dir, window, type)
        write_log("\n[Processo finalizado]\n")
    btn_process.config(state="normal")




def make_zip(repo_dir: str, window_dir: str, type: str):
    if window_dir != 'dbservices':

        file_path = os.path.normpath(os.path.join(
        repo_dir,
        type, "target", "classes", "br", "com", "mv", "soul",
        os.path.basename(repo_dir),
        type,
        window_dir
    ))
        file_extension= ''

        if (type == 'forms'):
            file_extension = 'Task.class'
        elif (type == 'reports'):
            file_extension = 'Scriptlet.class'
        elif (type == 'libs'):
            file_extension = 'Services.class'


        #verificando se o o arquivo .class foi gerado
        file  = os.path.normpath(os.path.join(
            file_path,
            window_dir + file_extension

        ))
        if (os.path.exists(file)):
            write_log("O arquivo " +  window_dir + file_extension + " está presente! Criando Pacote....")
            zipFile  = os.path.normpath(os.path.join("C:\\", "MV_HTML5","pacotes_gerados", 'soul-'+ os.path.basename(repo_dir)+ '-'+ type+'-'+ window_dir))
            shutil.make_archive(zipFile,'zip', file_path)
            messagebox.showinfo("Pacote gerado em: ", zipFile + '.zip')

        else:
            messagebox.showerror("ERRO", "Arquivo .class não foi encontrado")
    else:
        file_path = os.path.normpath(os.path.join(
        repo_dir,
        type, "target", "classes", "br", "com", "mv", "soul",
        os.path.basename(repo_dir),
        window_dir
        ))

        write_log("Criando pacote do dbservice...")
        zipFile  = os.path.normpath(os.path.join("C:\\", "MV_HTML5","pacotes_gerados", 'soul-'+ os.path.basename(repo_dir)+ '-'+ type+'-'+ window_dir))
        shutil.make_archive(zipFile,'zip', file_path)
        messagebox.showinfo("Pacote gerado em: ", zipFile + '.zip')

def write_log(txt: str):
    text_output.insert(tk.END, txt)
    text_output.see(tk.END)
    text_output.update() # força atualização imediata do Tkinter


# --- Interface ---
root = tk.Tk()
# --- Detecta o caminho correto mesmo no executável ---
if getattr(sys, 'frozen', False):
    # Caminho quando o app está empacotado pelo PyInstaller
    base_path = sys._MEIPASS
else:
    # Caminho normal durante o desenvolvimento
    base_path = os.path.dirname(__file__)

icon_path = os.path.join(base_path, "icone.ico")

# Aplica o ícone (sem depender do arquivo local no runtime)
root.iconbitmap(icon_path)
root.title("Gerador de pacote HTML5")
root.geometry("650x600") # Tamanho inicial da janela

# Configura o grid para expandir com a janela
root.columnconfigure(0, weight=1)
root.rowconfigure(3, weight=2) # A linha do Text de saída vai expandir

# --- Widgets ---

# Frame principal para melhor organização
main_frame = tk.Frame(root, padx=10, pady=10)
main_frame.grid(row=0, column=0, sticky="nsew")
main_frame.columnconfigure(1, weight=1) # Permite que a coluna do Entry expanda

# 1. SELEÇÃO DO REPOSITÓRIO (Linha 0)
label_repo = tk.Label(main_frame, text="Selecione a pasta do repositório:")
label_repo.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 2))

entry_repo_dir = tk.Entry(main_frame)
entry_repo_dir.grid(row=1, column=0, columnspan=2, sticky="ew")

btn_repo = tk.Button(main_frame, text="📂", font=("Arial", 12), command=select_repo)
btn_repo.grid(row=1, column=2, sticky="w", padx=(5, 0))


# 2. SELEÇÃO DE TIPO E PACOTE (Lado a Lado na Linha 2)
# Frame para agrupar os combos
frame_combos = tk.Frame(main_frame)
frame_combos.grid(row=2, column=0, columnspan=3, sticky='ew', pady=10)
frame_combos.columnconfigure(0, weight=1) # Coluna do Tipo
frame_combos.columnconfigure(1, weight=2) # Coluna do Pacote (maior)

# -- Tipo --
label_type = tk.Label(frame_combos, text="Selecione o tipo:")
label_type.grid(row=0, column=0, sticky='w')

tipos = ["forms", "reports", 'libs']
combo_type = ttk.Combobox(frame_combos, values=tipos, state="readonly")
combo_type.grid(row=1, column=0, sticky='ew', padx=(0, 10))
combo_type.bind("<<ComboboxSelected>>", load_windows)

# -- Pacote --
label_package = tk.Label(frame_combos, text="Selecione o pacote:")
label_package.grid(row=0, column=1, sticky='w')

combobox_windows = ttk.Combobox(frame_combos, state="readonly")
combobox_windows.grid(row=1, column=1, sticky='ew')


# 3. CHECKBOX (Linha 3)
# Variável booleana para o Checkbox
force_maven_update_var = tk.BooleanVar(value=True) # Inicia marcado como padrão

check_maven = ttk.Checkbutton(
    main_frame,
    text="Force Update Maven",
    variable=force_maven_update_var
)
check_maven.grid(row=3, column=0, columnspan=2, sticky='w', pady=5)


# 4. BOTÃO PROCESSAR (Linha 4)
btn_process = tk.Button(main_frame, text="Processar", command=process)
btn_process.grid(row=4, column=0, columnspan=3, pady=10)


# 5. ÁREA DE TEXTO (Saída) (Linha 5)
text_output = tk.Text(main_frame, height=15) # A altura agora é mais flexível
text_output.grid(row=5, column=0, columnspan=3, sticky="nsew")

# Adiciona uma scrollbar à área de texto
scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=text_output.yview)
scrollbar.grid(row=5, column=3, sticky='ns')
text_output['yscrollcommand'] = scrollbar.set


# Configura o grid do frame principal para expandir
main_frame.rowconfigure(5, weight=1)
main_frame.columnconfigure(1, weight=1)

# --- Loop Principal ---
root.mainloop()
