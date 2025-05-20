// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

async fn main() -> std::io::Result<()> {
  println!("Servidor corriendo en http://localhost:8080");

  HttpServer::new(|| {
    App::new()
        .service(getSeasons)
        .service(getEvents)
        .service(getCompetitions)
        .service(getLinks)
        .service(verTabla)
  })
      .bind(("127.0.0.1", 8080))?
      .run()
      .await
}
