use odbc_api::{Environment, Connection, Cursor, ResultSetMetadata, buffers::TextRowSet};
use actix_web::{web, App, HttpServer, Responder, get};
use crate::model::HiveLector::obtenerDatosTabla;

#[tauri::command]
pub fn verTabla(nombre: String) -> Result<String, String> {
    obtenerDatosTabla(&nombre).map_err(|e| e.to_string())
}


