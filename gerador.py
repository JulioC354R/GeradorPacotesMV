import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import subprocess
import shutil


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

def run_commands(repo_dir: str, window: str, type: str):
    sucess = False #Padrão False
    os.chdir(repo_dir)
        # colar old aqui
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
            sucess = True
        text_output.insert(tk.END, line)
        text_output.see(tk.END)
        text_output.update()  # força atualização imediata do Tkinter

    process.wait()  # espera o processo terminar
  

    if sucess:
        make_zip(repo_dir, window, type)
        text_output.insert(tk.END, "\n[Processo finalizado]\n")
        btn_process.config(state="normal")
    else:   
        messagebox.showerror("Erro", f"Ocorreu um erro! Pacote não gerado!!")
        btn_process.config(state="normal")

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
    threading.Thread(target=run_commands, args=(repo_dir, window, type), daemon=True).start()


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
            text_output.insert(tk.END, "O arquivo " +  window_dir + file_extension + " está presente! Criando Pacote....")
            text_output.see(tk.END)
            text_output.update()  # força atualização imediata do Tkinter
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

        text_output.insert(tk.END, "Criando pacote do dbservice...")
        text_output.see(tk.END)
        text_output.update()  # força atualização imediata do Tkinter
        zipFile  = os.path.normpath(os.path.join("C:\\", "MV_HTML5","pacotes_gerados", 'soul-'+ os.path.basename(repo_dir)+ '-'+ type+'-'+ window_dir))
        shutil.make_archive(zipFile,'zip', file_path)
        messagebox.showinfo("Pacote gerado em: ", zipFile + '.zip')



# --- Interface ---
root = tk.Tk()
root.title("Gerador de pacote HTML5")

# Frame para entrada do repositório
frame_repo = tk.Frame(root)
frame_repo.pack(pady=5, fill="x")

tk.Label(frame_repo, text="Selecione a pasta do repositório:").pack(anchor="w")

frame_entry = tk.Frame(frame_repo)
frame_entry.pack(fill="x")

entry_repo_dir = tk.Entry(frame_entry, width=78)
entry_repo_dir.pack(side="left")

# Botão com ícone unicode (📂)
btn_repo = tk.Button(frame_entry, text="📂", font=("Arial", 12) ,command=select_repo)
btn_repo.pack(side="left")

# Label do tipo
tk.Label(root, text="Selecione o tipo:").pack(anchor="w")
tipos = ["forms", "reports", 'libs']
combo_type = ttk.Combobox(root, values=tipos, state="readonly")
combo_type.pack(fill="x", padx=5)
combo_type.bind("<<ComboboxSelected>>", load_windows)

# Label e combobox dos pacotes
tk.Label(root, text="Selecione o pacote:").pack(anchor="w")
combobox_windows = ttk.Combobox(root, width=80, state="readonly")
combobox_windows.pack(fill="x", padx=5)

# Botão processar
btn_process = tk.Button(root, text="Processar", command=process)
btn_process.pack(pady=10)

# Saída de texto
text_output = tk.Text(root, width=80, height=30)
text_output.pack(pady=5)

#variaveis globais:

root.mainloop()
