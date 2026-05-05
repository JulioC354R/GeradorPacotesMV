use std::io::Write;
use std::path::Path;
use std::process::Command;
use std::sync::mpsc;
use std::thread;
use tauri::{AppHandle, Emitter};
use walkdir::WalkDir;
use zip::ZipArchive;
use time::OffsetDateTime;

use crate::models::artefact::Artefact;

fn today_ddmmmyyyy() -> String {
    let now = OffsetDateTime::now_local().unwrap_or_else(|_| OffsetDateTime::now_utc());
    format!("{:02}{:02}{:04}", now.day(), now.month() as u8, now.year())
}

fn get_major_version_from_bytes(b: &[u8]) -> u16 {
    u16::from_be_bytes([b[6], b[7]])
}

fn major_to_java(major: u16) -> &'static str {
    match major {
        45 => "Java 1.1",   46 => "Java 1.2",   47 => "Java 1.3",
        48 => "Java 1.4",   49 => "Java 5",     50 => "Java 6",
        51 => "Java 7",     52 => "Java 8",     53 => "Java 9",
        54 => "Java 10",    55 => "Java 11",    56 => "Java 12",
        57 => "Java 13",    58 => "Java 14",    59 => "Java 15",
        60 => "Java 16",    61 => "Java 17",    62 => "Java 18",
        63 => "Java 19",    64 => "Java 20",    65 => "Java 21",
        66 => "Java 22",    _ => "Unknown",
    }
}

fn build_readme_content(
    modules_info: &[(&str, &str)],
    pasta_pai: &str,
    process_log: &[String],
    major_classes: &std::collections::BTreeMap<String, String>,
    major_jars: &std::collections::BTreeMap<String, Vec<(String, String)>>,
) -> String {
    let sep = "========================================";
    let sub = "----------------------------------------";
    let mut out = String::new();

    out.push_str(&format!("{}\n", sep));
    out.push_str("RELATÓRIO DE GERAÇÃO DE PACOTE\n");
    out.push_str(&format!("{}\n\n", sep));
    out.push_str(&format!("TORRE: {}\n\n", pasta_pai));
    out.push_str("Módulos:\n");
    for (m, v) in modules_info {
        out.push_str(&format!("  - {} (versão {})\n", m, v));
    }
    out.push('\n');

    out.push_str(&format!("{}\n", sep));
    out.push_str("MAJOR VERSIONS - CLASSES\n");
    out.push_str(&format!("{}\n", sub));

    if major_classes.is_empty() {
        out.push_str("  (nenhum .class encontrado)\n");
    } else {
        for (name, major) in major_classes {
            let java_ver = major.parse::<u16>().ok().map(major_to_java).unwrap_or("-");
            out.push_str(&format!("  {:<50} {} ({})\n", name, major, java_ver));
        }
    }
    out.push('\n');

    out.push_str(&format!("{}\n", sep));
    out.push_str("MAJOR VERSIONS - JARs\n");
    out.push_str(&format!("{}\n", sub));

    if major_jars.is_empty() {
        out.push_str("  (nenhum .jar encontrado)\n");
    } else {
        for (jar_name, classes) in major_jars {
            out.push_str(&format!("  {}:\n", jar_name));
            for (cls, major) in classes {
                let java_ver = major.parse::<u16>().ok().map(major_to_java).unwrap_or("-");
                out.push_str(&format!("    {:<46} {} ({})\n", cls, major, java_ver));
            }
        }
    }
    out.push('\n');

    out.push_str(&format!("{}\n", sep));
    out.push_str("LOG DE PROCESSAMENTO\n");
    out.push_str(&format!("{}\n", sub));
    for line in process_log {
        out.push_str(&format!("  {}\n", line));
    }
    out.push('\n');

    out
}

#[tauri::command]
pub async fn process_artefacts(
    app: AppHandle,
    artefacts: Vec<Artefact>,
    codigo: Option<String>,
    pasta_pai: String,
) -> Result<bool, String> {
    let destiny_path = Path::new("C:\\MV_HTML5\\pacotes_gerados");
    let temp_path = destiny_path.join("tmp");

    let mut process_log: Vec<String> = Vec::new();
    let mut errors: Vec<String> = Vec::new();

    process_log.push("Iniciando processamento...".to_string());
    let _ = app.emit("log-line", "Iniciando processamento...");

    let _ = app.emit("status", "Preparando diretório temporário...");
    process_log.push(format!("Diretório de destino: {}", destiny_path.display()));

    if temp_path.exists() {
        if let Err(e) = std::fs::remove_dir_all(&temp_path) {
            let msg = format!("ERRO ao limpar diretório temporário: {}", e);
            process_log.push(msg.clone());
            let _ = app.emit("log-line", &msg);
            errors.push(e.to_string());
        }
    }
    if let Err(e) = std::fs::create_dir_all(&temp_path) {
        let msg = format!("ERRO ao criar diretório temporário: {}", e);
        process_log.push(msg.clone());
        let _ = app.emit("log-line", &msg);
        errors.push(e.to_string());
        return Err(format!("Falha ao preparar diretório temporário: {}", e));
    }
    process_log.push(format!("Diretório temporário criado em: {}", temp_path.display()));

    let total = artefacts.len();
    process_log.push(format!("Total de artefato(s) a processar: {}", total));

    let mut all_major_classes: std::collections::BTreeMap<String, String> = std::collections::BTreeMap::new();
    let mut all_major_jars: std::collections::BTreeMap<String, Vec<(String, String)>> = std::collections::BTreeMap::new();

    let first = match artefacts.first() {
        Some(f) => f,
        None => return Err("Nenhum artefato selecionado".to_string()),
    };
    let version = &first.version;

    let pasta_pai_upper = pasta_pai.to_uppercase();
    let codigo_part = codigo.as_deref().filter(|c| !c.is_empty());
    let today_str = today_ddmmmyyyy();

    let mut pack_name = format!("SOULMV_{}_{}", pasta_pai_upper, version);
    if let Some(ref c) = codigo_part {
        pack_name.push_str(&format!("_{}", c));
    }
    pack_name.push_str(&format!("_{}", today_str));

    pack_name = pack_name
        .chars()
        .filter(|c| !matches!(c, '<' | '>' | ':' | '"' | '/' | '\\' | '|' | '?' | '*' | '\0'..='\u{1f}'))
        .collect::<String>()
        .replace(' ', "");

    process_log.push(format!("Nome do pacote: {}.zip", pack_name));

    let mut by_module: std::collections::BTreeMap<String, Vec<Artefact>> = std::collections::BTreeMap::new();
    for a in artefacts {
        by_module.entry(a.module.clone()).or_default().push(a);
    }

    process_log.push(format!("Módulos identificados: {}", by_module.keys().cloned().collect::<Vec<_>>().join(", ")));

    for (module, module_artefacts) in &by_module {
        let repo_path_str = module_artefacts.first().map(|a| &*a.repo_path).unwrap_or("");
        process_log.push(format!("[{}] Iniciando processamento do módulo...", module));

        for (i, artefact) in module_artefacts.iter().enumerate() {
            let status = format!("[{}] Processando {} ({}/{})...", module, artefact.name, i + 1, module_artefacts.len());
            process_log.push(status.clone());
            let _ = app.emit("status", &status);
            let _ = app.emit("log-line", &status);
            let _ = app.emit("progress", ((i + 1) as f64 / total as f64) * 100.0);

            let build_path = Path::new(&artefact.build_path);

            process_log.push(format!("[{}] Verificando build de {} em {}", module, artefact.name, build_path.display()));

            if !build_path.exists() {
                let msg = format!("[{}] AVISO: Caminho de build não encontrado para {}", module, artefact.name);
                process_log.push(msg.clone());
                let _ = app.emit("log-line", &msg);
                errors.push(format!("Build path não existe: {}", build_path.display()));
                continue;
            }

            let has_class = WalkDir::new(build_path)
                .into_iter()
                .filter_map(|e| e.ok())
                .any(|e| e.path().extension().is_some_and(|ext| ext == "class"));

            if !has_class {
                let msg = format!("[{}] Nenhum .class encontrado, executando mvn clean install -U em {}...", module, repo_path_str);
                process_log.push(msg.clone());
                let _ = app.emit("log-line", &msg);
                let _ = app.emit("status", &msg);
                let mvn_ok = run_mvn(&app, repo_path_str).await;
                if !mvn_ok {
                    let msg = format!("[{}] ERRO: mvn clean install falhou para {}", module, artefact.name);
                    process_log.push(msg.clone());
                    let _ = app.emit("log-line", &msg);
                    errors.push(msg);
                    continue;
                }
                process_log.push(format!("[{}] mvn clean install concluído com sucesso para {}", module, artefact.name));
            } else {
                process_log.push(format!("[{}] Build já compilado, copiando artefato {}", module, artefact.name));
            }

            let artefact_dest = temp_path
                .join(&pack_name)
                .join(&pasta_pai_upper)
                .join(module)
                .join(&artefact.artefact_type)
                .join(&artefact.name);

            if build_path.exists() {
                match copy_dir_recursively(build_path, &artefact_dest) {
                    Ok(_) => {
                        let msg = format!("[{}] Copiado: {} para {}", module, artefact.name, artefact_dest.display());
                        process_log.push(msg.clone());
                        let _ = app.emit("log-line", &msg);
                    }
                    Err(e) => {
                        let msg = format!("[{}] ERRO ao copiar {}: {}", module, artefact.name, e);
                        process_log.push(msg.clone());
                        let _ = app.emit("log-line", &msg);
                        errors.push(format!("Falha ao copiar {}: {}", artefact.name, e));
                        continue;
                    }
                }
            }

            process_log.push(format!("[{}] Verificando major versions de {}...", module, artefact.name));
            if let Err(e) = collect_major_versions(&artefact_dest, &mut all_major_classes, &mut all_major_jars) {
                let msg = format!("[{}] ERRO ao verificar major versions de {}: {}", module, artefact.name, e);
                process_log.push(msg.clone());
                let _ = app.emit("log-line", &msg);
                errors.push(format!("Falha ao verificar major versions de {}: {}", artefact.name, e));
            }
        }
    }

    process_log.push(format!("Total de classes com major version verificadas: {}", all_major_classes.len()));
    process_log.push(format!("Total de JARs com major version verificadas: {}", all_major_jars.len()));

    let modules_info: Vec<(&str, &str)> = by_module.keys().map(|m| {
        let v = by_module[m].first().map(|a| &*a.version).unwrap_or("?");
        (m.as_str(), v)
    }).collect();

    if !errors.is_empty() {
        process_log.push("".to_string());
        process_log.push("========================================".to_string());
        process_log.push("ERROS ENCONTRADOS DURANTE O PROCESSAMENTO".to_string());
        process_log.push("========================================".to_string());
        for err in &errors {
            process_log.push(format!("  - {}", err));
        }
        process_log.push("".to_string());
    }

    let readme_content = build_readme_content(
        &modules_info,
        &pasta_pai_upper,
        &process_log,
        &all_major_classes,
        &all_major_jars,
    );

    let _ = app.emit("status", "Gerando readme.txt...");
    process_log.push("Gerando readme.txt...".to_string());
    let readme_path = temp_path.join(&pack_name).join("readme.txt");
    if let Some(parent) = readme_path.parent() {
        if let Err(e) = std::fs::create_dir_all(parent) {
            let msg = format!("ERRO ao criar diretório do readme: {}", e);
            process_log.push(msg.clone());
            let _ = app.emit("log-line", &msg);
            errors.push(e.to_string());
        }
    }
    if let Err(e) = std::fs::write(&readme_path, &readme_content) {
        let msg = format!("ERRO ao escrever readme.txt: {}", e);
        let _ = app.emit("log-line", &msg);
        errors.push(e.to_string());
    } else {
        process_log.push("readme.txt gerado com sucesso".to_string());
    }

    let _ = app.emit("status", "Compactando pacotes...");
    process_log.push("Compactando pacote zip...".to_string());
    if let Err(e) = zip_packages(&temp_path, destiny_path) {
        let msg = format!("ERRO ao compactar pacote: {}", e);
        process_log.push(msg.clone());
        let _ = app.emit("log-line", &msg);
        errors.push(e.to_string());
    } else {
        process_log.push(format!("Pacote salvo em: {}", destiny_path.join(format!("{}.zip", pack_name)).display()));
    }

    if temp_path.exists() {
        if let Err(e) = std::fs::remove_dir_all(&temp_path) {
            let msg = format!("ERRO ao limpar diretório temporário: {}", e);
            let _ = app.emit("log-line", &msg);
            errors.push(e.to_string());
        } else {
            process_log.push("Diretório temporário removido com sucesso".to_string());
        }
    }

    let _ = Command::new("explorer").arg(destiny_path).spawn();

    let _ = app.emit("progress", 100.0);

    if !errors.is_empty() {
        let _ = app.emit("status", "Processamento concluído com erros!");
        process_log.push("Processamento concluído com erros! Verifique o readme.txt para mais detalhes.".to_string());
        return Err(format!("Processamento concluído com {} erro(s). Verifique o readme.txt no pacote gerado.", errors.len()));
    }

    let _ = app.emit("status", "Processamento concluído com sucesso!");
    process_log.push("Processamento concluído com sucesso!".to_string());

    Ok(true)
}

fn collect_major_versions(
    repo_path: &Path,
    result_classes: &mut std::collections::BTreeMap<String, String>,
    result_jars: &mut std::collections::BTreeMap<String, Vec<(String, String)>>,
) -> Result<(), String> {
    for entry in WalkDir::new(repo_path).into_iter().filter_map(|e| e.ok()) {
        if entry.path().extension().is_some_and(|ext| ext == "class") {
            let data = std::fs::read(entry.path()).map_err(|e| e.to_string())?;
            let major = get_major_version_from_bytes(&data);
            result_classes.insert(
                entry.file_name().to_string_lossy().to_string(),
                major.to_string(),
            );
        }
    }

    for entry in WalkDir::new(repo_path)
        .into_iter()
        .filter_map(|e| e.ok())
        .filter(|e| e.path().extension().is_some_and(|ext| ext == "jar"))
    {
        let jar_name = entry.file_name().to_string_lossy().to_string();
        let jar_path = entry.path().to_path_buf();

        let mut classes: Vec<(String, String)> = Vec::new();
        if let Ok(file) = std::fs::File::open(&jar_path) {
            if let Ok(mut archive) = ZipArchive::new(file) {
                for i in 0..archive.len() {
                    if let Ok(mut file_in_zip) = archive.by_index(i) {
                        if file_in_zip.name().ends_with(".class") {
                            let mut data = Vec::new();
                            if std::io::Read::read_to_end(&mut file_in_zip, &mut data).is_ok() {
                                if data.len() >= 8 {
                                    let major = get_major_version_from_bytes(&data);
                                    classes.push((file_in_zip.name().to_string(), major.to_string()));
                                }
                            }
                        }
                    }
                }
            }
        }
        result_jars.insert(jar_name, classes);
    }

    Ok(())
}

fn copy_dir_recursively(src: &Path, dst: &Path) -> Result<(), String> {
    std::fs::create_dir_all(dst).map_err(|e| e.to_string())?;
    for entry in WalkDir::new(src).into_iter().filter_map(|e| e.ok()) {
        if entry.path() == src { continue; }
        let relative = entry.path().strip_prefix(src).map_err(|e| e.to_string())?;
        let dest_path = dst.join(relative);
        if entry.path().is_dir() {
            std::fs::create_dir_all(&dest_path).map_err(|e| e.to_string())?;
        } else {
            std::fs::copy(entry.path(), &dest_path).map_err(|e| e.to_string())?;
        }
    }
    Ok(())
}

fn zip_packages(src: &Path, dest: &Path) -> Result<(), String> {
    use std::fs::File;
    use zip::write::FileOptions;
    use zip::ZipWriter;

    std::fs::create_dir_all(dest).map_err(|e| e.to_string())?;

    for entry in std::fs::read_dir(src).map_err(|e| e.to_string())? {
        let entry = entry.map_err(|e| e.to_string())?;
        let dir_path = entry.path();
        if !dir_path.is_dir() { continue; }

        let dir_name = entry.file_name();
        let zip_path = dest.join(format!("{}.zip", dir_name.to_string_lossy()));
        let file = File::create(&zip_path).map_err(|e| e.to_string())?;
        let mut zip = ZipWriter::new(file);

        for walk_entry in WalkDir::new(&dir_path).into_iter().filter_map(|e| e.ok()) {
            let path = walk_entry.path();
            let name = path
                .strip_prefix(&dir_path)
                .map_err(|e| e.to_string())?
                .to_string_lossy()
                .replace('\\', "/");

            if path.is_file() {
                zip.start_file(&name, FileOptions::<()>::default()).map_err(|e| e.to_string())?;
                let data = std::fs::read(path).map_err(|e| e.to_string())?;
                zip.write_all(&data).map_err(|e| e.to_string())?;
            } else if !name.is_empty() {
                zip.add_directory(&name, FileOptions::<()>::default()).map_err(|e| e.to_string())?;
            }
        }

        zip.finish().map_err(|e| e.to_string())?;
    }

    Ok(())
}

async fn run_mvn(app: &AppHandle, repo_path: &str) -> bool {
    let (tx, rx) = mpsc::channel();
    let repo_path_owned = repo_path.to_string();

    thread::spawn(move || {
        let child = Command::new("cmd")
            .args(["/c", "mvn", "clean", "install", "-U"])
            .current_dir(&repo_path_owned)
            .stdout(std::process::Stdio::piped())
            .stderr(std::process::Stdio::piped())
            .spawn();

        let mut child = match child {
            Ok(c) => c,
            Err(e) => {
                let _ = tx.send((false, format!("Erro ao executar mvn: {}", e)));
                return;
            }
        };

        use std::io::BufRead;
        if let Some(stdout) = child.stdout.take() {
            let reader = std::io::BufReader::new(stdout);
            for line in reader.lines().flatten() {
                let _ = tx.send((true, line));
            }
        }
        let _ = child.wait();
        let _ = tx.send((false, String::new()));
    });

    for received in rx {
        let (is_log, line) = received;
        if is_log {
            let _ = app.emit("log-line", &line);
        }
    }

    true
}
