#[get("/tabla/{nombre}")]
async fn ver_tabla(nombre: web::Path<String>) -> impl Responder {
    match obtener_datos_tabla(&nombre) {
        Ok(html) => actix_web::HttpResponse::Ok()
            .content_type("text/html; charset=utf-8")
            .body(html),
        Err(e) => actix_web::HttpResponse::InternalServerError().body(format!("Error: {e}")),
    }
}

fn obtener_datos_tabla(tabla: &str) -> Result<String, Box<dyn std::error::Error>> {
    let env = Environment::new()?;
    let conn = env.connect("DSN_HIVE", "", "")?;
    let query = format!("SELECT * FROM `{}`", tabla);
    let mut cursor = conn.execute(&query, ())?.unwrap();

    let cols = cursor.num_result_cols()?;
    let mut html = String::from("<table border=\"1\"><tr>");

    for i in 1..=cols {
        html.push_str(&format!("<th>Col{i}</th>"));
    }
    html.push_str("</tr>");

    while let Some(row) = cursor.fetch()? {
        html.push_str("<tr>");
        for i in 0..cols {
            let val = row.get_data(i)?.unwrap_or("NULL".into());
            html.push_str(&format!("<td>{}</td>", val));
        }
        html.push_str("</tr>");
    }

    html.push_str("</table>");
    Ok(html)
}
