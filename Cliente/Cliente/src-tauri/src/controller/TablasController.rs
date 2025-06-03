use std::collections::HashSet;
use crate::model::HiveLector::obtenerTablas;

// Obtiene todas las temporadas que aparecen en los nombres de las tablas de Hive
#[tauri::command]
pub fn getSeasons() -> Result<Vec<String>, String> {
    let tablas = obtenerTablas().map_err(|e| format!("Error: {e}"))?;
    let mut seasons = HashSet::new();

    for tabla in tablas {
        let partes: Vec<&str> = tabla.split("_barra_").collect();
        if partes.len() >= 4 {
            seasons.insert(partes[2].to_string());
        }
    }

    let mut seasons: Vec<String> = seasons.into_iter().collect();
    seasons.sort();
    Ok(seasons)
}

// Obtiene todos los eventos de una temporada que aparecen en los nombres de las tablas de Hive
#[tauri::command]
pub fn getEvents(season: String) -> Result<Vec<String>, String> {
    let tablas = obtenerTablas().map_err(|e| format!("Error: {e}"))?;
    let mut events = HashSet::new();

    for tabla in tablas {
        let partes: Vec<&str> = tabla.split("_barra_").collect();
        if partes.len() >= 4 {
            if partes[2]== season {
                events.insert(partes[3].to_string());
            }
        }
    }

    let mut events: Vec<String> = events.into_iter().collect();
    events.sort();
    Ok(events)
}

// Obtiene todas las competiciones de un evento de una temporada
// que aparecen en los nombres de las tablas de Hive
#[tauri::command]
pub fn getCompetitions(season: String, event: String) -> Result<Vec<String>, String> {
    let tablas = obtenerTablas().map_err(|e| format!("Error: {e}"))?;
    let mut competitions = HashSet::new();

    for tabla in tablas {
        let partes: Vec<&str> = tabla.split("_barra_").collect();
        if partes.len() >= 4 {
            if partes[2] == season && partes[3] == event {
                competitions.insert(partes[1].to_string());
            }
        }
    }

    let mut comps: Vec<String> = competitions.into_iter().collect();
    comps.sort();
    Ok(comps)
}

// Obtiene todos los links de una competición de un evento de una temporada
// que aparecen en los nombres de las tablas de Hive
#[tauri::command]
pub fn getLinks(season: String, event: String, competition: String) -> Result<Vec<String>, String> {
    let tablas = obtenerTablas().map_err(|e| format!("Error: {e}"))?;
    let mut links = HashSet::new();

    for tabla in tablas {
        let partes: Vec<&str> = tabla.split("_barra_").collect();
        if partes.len() >= 4 {
            if  partes[2] == season
                && partes[3] == event
                && partes[1] == competition
            {
                links.insert(partes[0].to_string().replace("_"," "));
            }
        }
    }

    let mut links: Vec<String> = links.into_iter().collect();
    links.sort();
    Ok(links)
}
