use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Artefact {
    pub name: String,
    #[serde(rename = "type")]
    pub artefact_type: String,
    pub path: String,
    pub module: String,
    pub version: String,
    pub repo_path: String,
    pub build_path: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RepoInfo {
    pub module: String,
    pub version: String,
}
