pub mod controller;
pub mod model;

pub mod views;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
const EXPECT_ERROR:&str="error while running tauri application";
// Prepara y construye la aplicación
pub fn run() {
  tauri::Builder::default()
    .setup(|app| {
      Ok(())
    })
    .run(tauri::generate_context!())
    .expect(EXPECT_ERROR);
}
