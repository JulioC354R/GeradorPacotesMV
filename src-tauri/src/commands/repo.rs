use std::path::Path;
use crate::models::artefact::{Artefact, RepoInfo};

fn find_subdirs(path: &Path) -> Vec<String> {
    let mut dirs = Vec::new();
    if let Ok(entries) = std::fs::read_dir(path) {
        for entry in entries.flatten() {
            if entry.path().is_dir() {
                if let Some(name) = entry.file_name().to_str() {
                    dirs.push(name.to_string());
                }
            }
        }
    }
    dirs
}

fn extract_tag_content(xml: &str, tag: &str) -> Option<String> {
    let open = format!("<{}>", tag);
    let close = format!("</{}>", tag);
    if let Some(start) = xml.find(&open) {
        let content_start = start + open.len();
        if let Some(end) = xml[content_start..].find(&close) {
            return Some(xml[content_start..content_start + end].trim().to_string());
        }
    }
    None
}

fn read_repo_info(repo_path: &str) -> Result<RepoInfo, String> {
    let pom_path = Path::new(repo_path).join("pom.xml");
    let xml = std::fs::read_to_string(&pom_path)
        .map_err(|_| format!("pom.xml não encontrado em {}", pom_path.display()))?;

    let url = extract_tag_content(&xml, "url")
        .ok_or("Tag <url> não encontrada no pom.xml")?;
    let module = url
        .trim_end_matches('/')
        .rsplit('/')
        .next()
        .ok_or("URL inválida no pom.xml")?
        .to_string();

    let version = extract_tag_content(&xml, "version")
        .ok_or("Tag <version> não encontrada no pom.xml")?;

    Ok(RepoInfo { module, version })
}

#[tauri::command]
pub fn get_repo_info(repo_path: &str) -> Result<RepoInfo, String> {
    read_repo_info(repo_path)
}

#[tauri::command]
pub fn list_artefacts(
    repo_path: &str,
    artefact_type: &str,
) -> Result<Vec<Artefact>, String> {
    let info = read_repo_info(repo_path)?;
    let module = &info.module;
    let version = &info.version;
    let artefact_type_lower = artefact_type.to_lowercase();

    let base_path = Path::new(repo_path)
        .join(&artefact_type_lower)
        .join("src")
        .join("main")
        .join("java")
        .join("br")
        .join("com")
        .join("mv")
        .join("soul")
        .join(module)
        .join(&artefact_type_lower);

    if !base_path.exists() {
        return Err(format!(
            "Caminho não encontrado: {}",
            base_path.display()
        ));
    }

    let repo_basename = Path::new(repo_path)
        .file_name()
        .and_then(|n| n.to_str())
        .unwrap_or("");

    let mut artefacts: Vec<Artefact> = find_subdirs(&base_path)
        .into_iter()
        .map(|name| {
            let build_path = Path::new(repo_path)
                .join(&artefact_type_lower)
                .join("target")
                .join("classes")
                .join("br")
                .join("com")
                .join("mv")
                .join("soul")
                .join(repo_basename)
                .join(&artefact_type_lower)
                .join(&name.to_lowercase())
                .to_string_lossy()
                .to_string();

            Artefact {
                name: name.clone(),
                artefact_type: artefact_type_lower.clone(),
                path: base_path.join(&name).to_string_lossy().to_string(),
                module: module.clone(),
                version: version.clone(),
                repo_path: repo_path.to_string(),
                build_path,
            }
        })
        .collect();

    if artefact_type_lower == "libs" {
        if let Some(parent) = base_path.parent() {
            if let Some(parent_path) = parent.to_str() {
                let extra = find_subdirs(Path::new(parent_path))
                    .into_iter()
                    .map(|name| {
                        let build_path = Path::new(repo_path)
                            .join(&artefact_type_lower)
                            .join("target")
                            .join("classes")
                            .join("br")
                            .join("com")
                            .join("mv")
                            .join("soul")
                            .join(repo_basename)
                            .join(&name.to_lowercase())
                            .to_string_lossy()
                            .to_string();

                        Artefact {
                            name: name.clone(),
                            artefact_type: artefact_type_lower.clone(),
                            path: Path::new(parent_path)
                                .join(&name)
                                .to_string_lossy()
                                .to_string(),
                            module: module.clone(),
                            version: version.clone(),
                            repo_path: repo_path.to_string(),
                            build_path,
                        }
                    })
                    .collect::<Vec<_>>();
                artefacts.extend(extra);
            }
        }
    }

    Ok(artefacts)
}
