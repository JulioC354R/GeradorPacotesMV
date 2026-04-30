# Gerador de Pacotes HTML5 — Soul MV

Aplicação desktop em **Tauri + React + Rust** para automatizar a geração de pacotes a partir de artefatos Java do repositório **HTML Soul** (MV Sistemas).

---

## Funcionalidades

- Seleção visual de repositório local via seletor de pastas
- Leitura automática do `pom.xml` para extrair **módulo** e **versão**
- Listagem dinâmica de artefatos Java organizados por tipo (Forms, Reports, Libs)
- Seleção múltipla de artefatos de **diferentes repositórios/módulos**
- Execução de `mvn clean install -U` para recompilar artefatos desatualizados
- Geração de pacotes `.zip` em `C:\MV_HTML5\pacotes_gerados`
- Verificação de *major version* de arquivos `.class` e `.jar`
- `readme.txt` dentro de cada zip com versões, major versions e log de processamento
- Interface responsiva com barra de progresso e logs em tempo real

---

## Estrutura do pacote gerado

```
{nome_do_zip}.zip
├── readme.txt
└── {PASTA_PRINCIPAL}/
    └── {modulo}/
        ├── forms/
        │   └── {artefato}/
        ├── reports/
        │   └── {artefato}/
        └── libs/
            └── {artefato}/
```

## Nome do arquivo zip

```
SOULMV_{TORRE}_{VERSAO}_{CODIGO}_{DDMMYYYY}.zip
```

Exemplo: `SOULMV_FINAN_2025.10.1-RC3-SNAPSHOT_JIRA-123_30042026.zip`

---

## Tecnologias

| Camada    | Tecnologia                          |
|-----------|-------------------------------------|
| Frontend  | React 19 + TypeScript + Tailwind v4 |
| UI Kit    | shadcn/ui                          |
| Backend   | Rust + Tauri 2                      |
| Ícones    | Lucide React                       |
| Empacotamento | Tauri Bundler (MSI / NSIS)     |

---

## Como desenvolver

```bash
# Instalar dependências
npm install

# Rodar em modo dev
npm run tauri dev

# Build para produção
npm run tauri build
```

O executável será gerado em `src-tauri/target/release/bundle/`.

---

## Estrutura do projeto

```
GeradorPacoteHtml5/
├── src/                          # Frontend React
│   ├── App.tsx                   # Componente principal
│   ├── main.tsx                  # Entry point
│   ├── index.css                 # Estilos globais + Tailwind
│   ├── components/
│   │   ├── ui/                   # shadcn/ui components
│   │   ├── RepoSelector.tsx
│   │   ├── FolderInfo.tsx
│   │   ├── ArtefactSelector.tsx
│   │   ├── SelectedList.tsx
│   │   ├── CodeInputs.tsx
│   │   └── ProcessDialog.tsx
│   ├── hooks/
│   └── types/
├── src-tauri/                    # Backend Rust
│   ├── src/
│   │   ├── main.rs
│   │   ├── lib.rs
│   │   ├── commands/
│   │   │   ├── repo.rs           # get_repo_info, list_artefacts
│   │   │   └── process.rs        # process_artefacts
│   │   └── models/
│   │       └── artefact.rs
│   ├── icons/
│   ├── Cargo.toml
│   └── tauri.conf.json
├── package.json
├── vite.config.ts
└── pom.xml                       # Exemplo de POM para referência
```

---

## Contribuição

Projeto mantido pela equipe de desenvolvimento.
Sugestões e melhorias via _pull request_ ou _issue_.
