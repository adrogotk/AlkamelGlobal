#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use actix_files::NamedFile;
use actix_web::{App, HttpServer, Result, get, web};
mod controller;
mod model;
mod views;

use controller::TablasController::{
  getSeasons,
  getEvents,
  getCompetitions,
  getLinks,
};
use views::viewModels::TablaViewModel::verTabla;


use tauri::{Builder};
fn main() {
  tauri::Builder::default()
      .invoke_handler(tauri::generate_handler![
            getSeasons,
            getEvents,
            getCompetitions,
            getLinks,
            verTabla,
        ])
      .run(tauri::generate_context!())
      .expect("error while running tauri application");
}