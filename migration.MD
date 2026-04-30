# Plano de Migração: Flet (Python) → Tauri + React + shadcn/ui + Tailwind CSS

## Stack Alvo

| Camada    | Atual (Flet)         | Alvo                    |
|-----------|----------------------|-------------------------|
| Frontend  | Flet (Python GUI)    | React + shadcn/ui       |
| Estilo    | Flet nativo          | Tailwind CSS            |
| Backend   | Python sync          | Tauri (Rust) — async    |
| IPC       | N/A (monolito)       | Tauri Commands          |
| Build     | PyInstaller (.exe)   | Tauri Bundler (.exe/.msi) |

---

## 1. Mapeamento de Componentes de UI

| Flet (atual)                          | React + shadcn/ui (alvo)                           |
|---------------------------------------|----------------------------------------------------|
| `ft.TextField` (repo_input)           | `<Input>` + botão de seleção de pasta              |
| `ft.IconButton` (btn_select_repo)     | `<Button variant="outline">` + `<FolderOpen />`    |
| `ft.Dropdown` (artefact_type)         | `<Select>` de shadcn                               |
| `ft.Dropdown` editável (artefacts)    | `<Command>` + `<Popover>` (combobox searchable)    |
| `ft.Chip` (selected_container)        | `<Badge variant="secondary">` + `<X />`            |
| `ft.ElevatedButton` (btn_process)     | `<Button>` (verde, com `<Play />`)                 |
| `ft.ElevatedButton` (btn_clear)       | `<Button variant="destructive">`                   |
| `ft.TextField` (jira / cervello / client) | `<Input maxLength={20} />`                     |
| `ft.TextField` (pasta_pai) — NOVO        | `<Input>` torre (FINAN, CONTR, etc.)          |
| `ft.TextField` (modulo) — NOVO           | `<Input>` módulo (fcct, fncp, etc.)           |
| `ft.AlertDialog` (erro/sucesso)       | `<AlertDialog>` de shadcn                          |
| `ft.ProgressBar` + `ft.Text`         | `<Progress>` + `<p>` dentro de `<Dialog>`         |
| `ft.ListView` (log)                   | `<div>` com scroll + `<pre>` ou lista              |
| `ft.ResponsiveRow` + `columns`        | Tailwind grid (`grid grid-cols-2 sm:grid-cols-4`)  |
| `page.run_thread(process_task)`       | `invoke("process_artefacts")` + streaming de evento |
| `ft.FilePicker`                       | `@tauri-apps/plugin-dialog` — `open()`            |

## 2. Regras de Negócio (Python → Rust/Tauri Commands)

### 2.1 `select_repo` → Tauri Dialog Plugin

Usar o plugin `@tauri-apps/plugin-dialog`:

```rust
// Rust — Tauri command
#[tauri::command]
fn select_repo(app: tauri::AppHandle) -> Result<String, String> {
    let path = tauri_plugin_dialog::FileDialog::new()
        .pick_folder()?
        .ok_or("Nenhuma pasta selecionada")?;
    Ok(path.to_string_lossy().to_string())
}
```

```tsx
// React
import { open } from "@tauri-apps/plugin-dialog";
const folder = await open({ directory: true });
```

### 2.2 `select_artefact_type` → Tauri Command

Lógica que monta o caminho `{repo}/{type}/src/main/java/br/com/mv/soul/{module}/{type}` (com `module` vindo do campo de tela, não mais do nome da pasta do repositório) e lista diretórios.

```rust
#[tauri::command]
fn list_artefacts(
    repo_path: &str,
    artefact_type: &str,
    module: &str,                          // ← NOVO: recebido do input em tela
) -> Result<Vec<Artefact>, String> {
    // monta o path: {repo}/{type}/src/main/java/br/com/mv/soul/{module}/{type}
    // retorna Vec<Artefact>
}
```

### 2.3 `process_artefact` → Tauri Command com Event Stream

A lógica principal de processamento (copiar `build_path`, `verify_major`, zipar) pode rodar em uma thread Rust separada e emitir eventos de progresso para o frontend via `app_handle.emit("log", line)` e `app_handle.emit("progress", value)`.

```rust
#[tauri::command]
async fn process_artefacts(
    app: AppHandle,
    artefacts: Vec<Artefact>,
    jira: Option<String>,
    cervello: Option<String>,
    client: Option<String>,
    pasta_pai: String,                     // ← NOVO: torre (FINAN, CONTR, etc.)
    module: String,                        // ← NOVO: módulo (fcct, fncp, etc.)
) -> Result<bool, String> {
    // usa std::fs, zip crate, e emite eventos
}
```

### 2.4 `mvn_clean_install` → `std::process::Command`

```rust
use std::process::Command;

let mut child = Command::new("cmd")
    .args(["/c", "mvn", "clean", "install", "-U"])
    .stdout(std::process::Stdio::piped())
    .spawn()
    .map_err(|e| e.to_string())?;
```

### 2.5 `zip_packages` → `zip` crate

Usar `zip` crate ou `std::fs` + `flate2` para criar os zips.

### 2.6 `verify_major` → `zip` crate + leitura de bytes

```rust
fn get_major_version(class_bytes: &[u8]) -> u16 {
    u16::from_be_bytes([class_bytes[6], class_bytes[7]])
}
```

### 2.7 `check_build` → `glob` crate ou `std::fs::read_dir`

## 3. NOVO Padrão de Estrutura de Pastas (padroniza.pdf)

O PDF `padroniza.pdf` define um novo padrão para a **estrutura de saída dos pacotes**. Antes de zipar, os artefatos agora devem ser organizados em:

```
{NOME_DEMANDA}_{TORRE}_{VERSAO}/        ← pasta pai (ex: CNPJ_FINAN_2025.009.XX)
└── {TORRE}/                              ← torre em MAIÚSCULO (ex: FINAN, CONTR)
    ├── forms/                            ← só se houver conteúdo (plural, minúsculo)
    │   └── {scripts}
    ├── libs/                             ← só se houver conteúdo
    │   └── {scripts}
    └── reports/                          ← só se houver conteúdo
        └── {scripts}
```

### 3.1 Mudanças no fluxo atual

| Aspecto                | Antes (atual)                                        | Depois (novo padrão)                                          |
|------------------------|------------------------------------------------------|---------------------------------------------------------------|
| Nome do módulo         | Extraído do nome da pasta do repositório (`basename`) | Digitado em campo próprio na tela (`fcct`, `fncp`, etc.)      |
| Pasta pai do pacote    | Nome do artefato + códigos                            | Nome da demanda + torre + versão (entrada em tela)            |
| Pasta da torre         | Inexistente                                          | Criada dentro da pasta pai, nome em MAIÚSCULO                 |
| Subpastas (forms/libs) | Artefatos copiados diretamente                       | Cria pastas `forms/`, `libs/`, `reports/` apenas com conteúdo |
| Caminho de busca (src) | `{repo}/{type}/.../soul/{basename}/{type}`           | `{repo}/{type}/.../soul/{modulo_digitado}/{type}`             |

### 3.2 Novos campos de entrada na UI

Além dos campos existentes (Jira, Cervello, Cliente), adicionar:

| Campo       | Label                | Exemplo        | Validação                          |
|-------------|----------------------|----------------|------------------------------------|
| `pasta_pai` | "Pasta Principal"    | `FINAN`        | Apenas letras maiúsculas e números |
| `modulo`    | "Módulo"             | `fcct`         | Apenas letras minúsculas           |

### 3.3 Impacto no caminho de busca dos artefatos (source)

O caminho atual:
```
{repo}/{type}/src/main/java/br/com/mv/soul/{basename(repo)}/{type}/
```

Passa a ser:
```
{repo}/{type}/src/main/java/br/com/mv/soul/{modulo_digitado}/{type}/
```

### 3.4 Impacto na estrutura de saída (zip)

**Antes:**
```
temp/
└── soul-{module}-{type}_{jira}_{cervello}_{client}.zip
    └── {artefact_name}/
         ├── target/classes/...
         └── libs/*.jar
```

**Depois (novo padrão):**
```
temp/
└── {pasta_pai}_{jira}_{cervello}_{client}.zip
    └── {PASTA_PAI}/
         ├── forms/
         │   └── {artefato}/target/classes/...
         ├── reports/
         │   └── {artefato}/target/classes/...
         └── libs/
             └── {artefato}/target/classes/...
```

### 3.5 Novas validações

1. `pasta_pai` é obrigatório e deve conter apenas letras maiúsculas, números e `_`
2. `modulo` é obrigatório e deve conter apenas letras minúsculas
3. A pasta `forms/`, `libs/` ou `reports/` só deve ser criada no zip se houver ao menos um artefato daquele tipo selecionado
4. O nome da pasta pai (ex: `FINAN`) deve estar em MAIÚSCULO conforme o padrão

## 4. Estrutura de Diretórios (Tauri + React)

```
GeradorPacoteHtml5/
├── src/                          # Frontend React
│   ├── App.tsx                   # Layout raiz
│   ├── main.tsx                  # Entry point
│   ├── components/
│   │   ├── RepoSelector.tsx      # Input + botão de selecionar pasta
│   │   ├── FolderInfo.tsx        # NOVO: Inputs de pasta pai (FINAN) e módulo (fcct)
│   │   ├── ArtefactSelector.tsx  # Select de tipo + Combobox de artefatos
│   │   ├── SelectedList.tsx      # Grid de Badges com delete
│   │   ├── CodeInputs.tsx        # Jira / Cervello / Cliente inputs
│   │   ├── ProcessDialog.tsx     # Dialog de progresso com barra + log
│   │   └── ui/                   # shadcn/ui components
│   │       ├── button.tsx
│   │       ├── input.tsx
│   │       ├── select.tsx
│   │       ├── command.tsx
│   │       ├── badge.tsx
│   │       ├── dialog.tsx
│   │       ├── alert-dialog.tsx
│   │       └── progress.tsx
│   ├── hooks/
│   │   └── useArtefacts.ts      # Estado global ou custom hook
│   ├── lib/
│   │   └── utils.ts              # Utilitários (cn, etc.)
│   └── types/
│       └── artefact.ts           # Interface Artefact
├── src-tauri/                    # Backend Rust
│   ├── src/
│   │   ├── main.rs               # Config Tauri + comandos
│   │   ├── commands/
│   │   │   ├── mod.rs
│   │   │   ├── repo.rs           # list_artefacts, select_repo
│   │   │   ├── process.rs        # process_artefacts, mvn_clean_install
│   │   │   └── verify.rs         # verify_major, check_build
│   │   └── models/
│   │       └── artefact.rs       # Struct Artefact + serde
│   ├── Cargo.toml
│   └── tauri.conf.json
├── package.json
├── tailwind.config.ts
├── tsconfig.json
└── vite.config.ts
```

## 4. Dependências (Rust — Cargo.toml)

```toml
[dependencies]
tauri = { version = "2", features = ["devtools"] }
tauri-plugin-dialog = "2"
tauri-plugin-shell = "2"
serde = { version = "1", features = ["derive"] }
serde_json = "1"
zip = "2"
walkdir = "2"
glob = "0.3"
tokio = { version = "1", features = ["full"] }
```

## 5. Dependências (Frontend — package.json)

```json
{
  "dependencies": {
    "react": "^19",
    "react-dom": "^19",
    "lucide-react": "^0.400",
    "@tauri-apps/api": "^2",
    "@tauri-apps/plugin-dialog": "^2",
    "@tauri-apps/plugin-shell": "^2",
    "class-variance-authority": "^0.7",
    "clsx": "^2",
    "tailwind-merge": "^2"
  },
  "devDependencies": {
    "typescript": "^5",
    "tailwindcss": "^4",
    "vite": "^6",
    "@vitejs/plugin-react": "^4"
  }
}
```

## 6. Ordem de Implementação Sugerida

| Fase | Tarefa                                             | Esforço |
|------|----------------------------------------------------|---------|
| 1    | Scaffold do projeto Tauri + React + Tailwind       | 1h      |
| 2    | Configurar shadcn/ui + componentes base            | 1h      |
| 3    | Componente `RepoSelector` + integração dialog      | 2h      |
| 4    | Componente `FolderInfo` (pasta pai + módulo)       | 1h      |
| 5    | Componente `ArtefactSelector` (Select + Combobox)  | 3h      |
| 6    | Componente `SelectedList` (Badges)                 | 1h      |
| 7    | Componente `CodeInputs` + validação (regex)        | 1h      |
| 8    | Tauri Command `list_artefacts` (Rust) — c/ módulo  | 3h      |
| 9    | Tauri Command `process_artefacts` + eventos        | 5h      |
| 10   | Tauri Command `mvn_clean_install` + stdout stream  | 3h      |
| 11   | Tauri Command `verify_major` (class + jar) + JSON  | 3h      |
| 12   | Tauri Command `zip_packages` — novo padrão pastas  | 3h      |
| 13   | Componente `ProcessDialog` com progresso + log     | 3h      |
| 14   | Fluxo de erro completo + AlertDialog               | 2h      |
| 15   | Limpeza de temp, abertura de pasta ao final        | 1h      |
| 16   | Testes e ajustes finais                            | 2h      |
|      | **Total estimado**                                 | **34h** |

## 7. Observações Técnicas Importantes

1. **Streaming de log**: Tauri 2 suporta eventos emitidos do backend para o frontend. Usar `app.app_handle().emit("log-line", line)` para enviar cada linha do Maven em tempo real. No React, usar `listen("log-line", callback)` do `@tauri-apps/api/event`.

2. **File picker**: Não é possível usar `<input type="file">` web padrão no Tauri — obrigatório usar `@tauri-apps/plugin-dialog` com `open({ directory: true })`.

3. **Caminhos Windows**: Rust lida bem com `PathBuf` e `\\`. Manter a constante `C:\\MV_HTML5\\pacotes_gerados` como configurável (`tauri.conf.json` ou env).

4. **Regex de validação**: A regex `[\/\\\:\*\?\"\<\>\|]` é facilmente replicada no frontend (`input.replace(...)`).

5. **Async vs Sync**: Comandos Tauri que fazem I/O pesado (Maven, zip, cópia de arquivos) devem ser `async` e executados em `tokio::task::spawn_blocking` para não travar o event loop.

6. **Zip**: A crate `zip` é pure Rust e funciona bem para criar arquivos `.zip`. Alternativa: usar `std::fs` + `flate2` + `tar` se precisar de `.tar.gz`.

7. **Build path**: O caminho de build dos artefatos (`target/classes/...`) deve ser montado no backend Rust, mesma lógica do `home_services.py` atual.

8. **Novo padrão de pastas (padroniza.pdf)**: O módulo agora é digitado em tela (não extraído do nome da pasta do repositório). A estrutura de saída do zip deve seguir: `{PASTA_PAI}/{TORRE}/{forms|libs|reports}/`. A pasta pai (ex: `FINAN`) e o módulo (ex: `fcct`) são campos obrigatórios na UI. As subpastas `forms/`, `libs/`, `reports/` só devem ser criadas se houver artefatos selecionados daquele tipo.
