mod commands;
mod models;

use commands::{repo::{list_artefacts, get_repo_info}, process::process_artefacts};

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_shell::init())
        .invoke_handler(tauri::generate_handler![
            list_artefacts,
            get_repo_info,
            process_artefacts
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
