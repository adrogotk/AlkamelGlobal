use odbc_api::{Environment, Connection, Cursor, ResultSetMetadata, buffers::TextRowSet};
use actix_web::{web, App, HttpServer, Responder, get};
use crate::model::HiveLector::obtenerDatosTabla;

// Llama al modelo para obtener el HTML necesario con los datos necesarios para mostrar
// la tabla correspondiente al link de la competición del evento de la temporada escogido
#[tauri::command]
pub fn verTabla(nombre: String) -> Result<String, String> {
    obtenerDatosTabla(&nombre).map_err(|e| e.to_string())
}


