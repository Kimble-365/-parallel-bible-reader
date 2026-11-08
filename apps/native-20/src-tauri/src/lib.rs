use serde::Serialize;
use std::io::Write;
use tauri::Manager;
use tauri_plugin_clipboard_manager::ClipboardExt;
use tauri_plugin_opener::OpenerExt;

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
struct RuntimeInfo {
    version: &'static str,
    os: &'static str,
    arch: &'static str,
    native: bool,
}

#[tauri::command]
fn runtime_info() -> RuntimeInfo {
    RuntimeInfo {
        version: env!("CARGO_PKG_VERSION"),
        os: std::env::consts::OS,
        arch: std::env::consts::ARCH,
        native: true,
    }
}

#[tauri::command]
fn copy_text(app: tauri::AppHandle, text: String) -> Result<(), String> {
    if text.len() > 2_000_000 {
        return Err("Text is too large for clipboard export.".into());
    }
    app.clipboard().write_text(text).map_err(|e| e.to_string())
}

fn web_url(input: &str) -> Result<url::Url, String> {
    let u = url::Url::parse(input).map_err(|_| "Invalid web link.")?;
    if !matches!(u.scheme(), "http" | "https")
        || u.host_str().is_none()
        || !u.username().is_empty()
        || u.password().is_some()
    {
        return Err("Only ordinary HTTP(S) links can open outside the reader.".into());
    }
    Ok(u)
}

#[tauri::command]
fn open_external(app: tauri::AppHandle, url: String) -> Result<(), String> {
    let u = web_url(&url)?;
    app.opener()
        .open_url(u.as_str(), None::<&str>)
        .map_err(|e| e.to_string())
}

fn safe_name(name: &str) -> Result<String, String> {
    if name.is_empty()
        || name.len() > 120
        || name.starts_with('.')
        || name
            .chars()
            .any(|c| !(c.is_ascii_alphanumeric() || "._-".contains(c)))
    {
        return Err("Use a plain export file name without folders.".into());
    }
    Ok(name.into())
}

#[tauri::command]
fn save_export(app: tauri::AppHandle, name: String, bytes: Vec<u8>) -> Result<String, String> {
    let name = safe_name(&name)?;
    if bytes.len() > 25 * 1024 * 1024 {
        return Err("Export exceeds the 25 MiB file limit.".into());
    }
    let folder = app
        .path()
        .app_data_dir()
        .map_err(|e| e.to_string())?
        .join("exports");
    std::fs::create_dir_all(&folder).map_err(|e| e.to_string())?;
    // Never overwrite a previous export or accept a caller-supplied folder.
    for n in 0..1000 {
        let filename = if n == 0 {
            name.clone()
        } else {
            format!("{n}-{name}")
        };
        let path = folder.join(filename);
        match std::fs::OpenOptions::new()
            .write(true)
            .create_new(true)
            .open(&path)
        {
            Ok(mut file) => {
                if let Err(e) = file.write_all(&bytes) {
                    let _ = std::fs::remove_file(&path);
                    return Err(e.to_string());
                }
                return Ok(path.to_string_lossy().into_owned());
            }
            Err(e) if e.kind() == std::io::ErrorKind::AlreadyExists => continue,
            Err(e) => return Err(e.to_string()),
        }
    }
    Err("Too many exports with this name. Choose another name.".into())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_clipboard_manager::init())
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![
            runtime_info,
            copy_text,
            open_external,
            save_export
        ])
        .run(tauri::generate_context!())
        .expect("Could not start Parallel Bible Reader 2.0");
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn links_cannot_execute_local_files_or_credentials() {
        for link in [
            "file:///etc/passwd",
            "javascript:alert(1)",
            "https://user:pass@example.org",
            "shell:cmd",
        ] {
            assert!(web_url(link).is_err());
        }
        assert!(web_url("https://ebible.org/hebsg/").is_ok());
    }
    #[test]
    fn exports_cannot_escape_their_folder() {
        for name in [
            "",
            "..",
            "../notes.json",
            "C:\\notes.txt",
            "/tmp/x",
            ".secret",
        ] {
            assert!(safe_name(name).is_err());
        }
        assert!(safe_name("wlc-israeli-complete.txt").is_ok());
    }
}
