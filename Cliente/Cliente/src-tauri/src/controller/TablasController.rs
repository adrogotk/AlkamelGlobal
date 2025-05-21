use actix_web::{web, App, HttpServer, Responder, get};
use serde::Serialize;
use std::collections::HashSet;
use std::env;

#[derive(Serialize)]
struct TablasResponse {
    seasons: Vec<String>,
    events: Vec<String>,
    competitions: Vec<String>,
    links: Vec<String>,
}

#[get("/api/seasons")]
async fn getSeasons() -> impl Responder {
    match obtener_tablas() {
        Ok(tablas) => {
            let mut seasons = HashSet::new();
            for partes in tablas {
                if partes.len() >= 4 {
                    let season_parts: Vec<&str> = partes[2].split('_').collect();
                    if season_parts.len() >= 2 {
                        seasons.insert(season_parts[1].to_string());
                    }
                }
            }
            let mut seasons: Vec<String> = seasons.into_iter().collect();
            seasons.sort();
            web::Json(seasons)
        }
        Err(e) => web::Json(vec![format!("Error: {e}")]),
    }
}

#[get("/api/events")]
async fn getEvents(query: web::Query<std::collections::HashMap<String, String>>) -> impl Responder {
    let Some(season) = query.get("season") else {
        return web::Json(vec!["season requerida".to_string()]);
    };

    match obtener_tablas() {
        Ok(tablas) => {
            let mut events = HashSet::new();
            for partes in tablas {
                if partes.len() >= 4 {
                    let season_parts: Vec<&str> = partes[2].split('_').collect();
                    if season_parts.len() >= 2 && season_parts[1] == season {
                        events.insert(partes[3].to_string());
                    }
                }
            }
            let mut events: Vec<String> = events.into_iter().collect();
            events.sort();
            web::Json(events)
        }
        Err(e) => web::Json(vec![format!("Error: {e}")]),
    }
}

#[get("/api/competitions")]
async fn getCompetitions(query: web::Query<std::collections::HashMap<String, String>>) -> impl Responder {
    let (Some(season), Some(event)) = (query.get("season"), query.get("event")) else {
        return web::Json(vec!["season y event requeridos".to_string()]);
    };

    match obtener_tablas() {
        Ok(tablas) => {
            let mut comps = HashSet::new();
            for partes in tablas {
                if partes.len() >= 4 {
                    let season_parts: Vec<&str> = partes[2].split('_').collect();
                    if season_parts.len() >= 2 && season_parts[1] == season && partes[3] == event {
                        comps.insert(partes[1].to_string());
                    }
                }
            }
            let mut comps: Vec<String> = comps.into_iter().collect();
            comps.sort();
            web::Json(comps)
        }
        Err(e) => web::Json(vec![format!("Error: {e}")]),
    }
}

#[get("/api/links")]
async fn getLinks(query: web::Query<std::collections::HashMap<String, String>>) -> impl Responder {
    let (Some(season), Some(event), Some(competition)) =
        (query.get("season"), query.get("event"), query.get("competition"))
    else {
        return web::Json(vec!["season, event y competition requeridos".to_string()]);
    };

    match obtener_tablas() {
        Ok(tablas) => {
            let mut links = HashSet::new();
            for partes in tablas {
                if partes.len() >= 4 {
                    let season_parts: Vec<&str> = partes[2].split('_').collect();
                    if season_parts.len() >= 2 && season_parts[1] == season && partes[3] == event && partes[1] == competition {
                        links.insert(partes[0].to_string());
                    }
                }
            }
            let mut links: Vec<String> = links.into_iter().collect();
            links.sort();
            web::Json(links)
        }
        Err(e) => web::Json(vec![format!("Error: {e}")]),
    }
}