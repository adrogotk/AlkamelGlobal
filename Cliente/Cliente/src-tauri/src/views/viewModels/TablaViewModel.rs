use odbc_api::{Environment, Connection, Cursor, ResultSetMetadata, buffers::TextRowSet};
use actix_web::{web, App, HttpServer, Responder, get};

#[get("/tabla/{nombre}")]
async fn verTabla(nombre: web::Path<String>) -> impl Responder {
    match obtenerDatosTabla(&nombre) {
        Ok(html) => actix_web::HttpResponse::Ok()
            .content_type("text/html; charset=utf-8")
            .body(html),
        Err(e) => actix_web::HttpResponse::InternalServerError().body(format!("Error: {}", e)),
    }
}

fn obtenerDatosTabla(tabla: &str) -> Result<String, Box<dyn std::error::Error>> {
    let env = Environment::new()?;
    let conn = env.connect("DSN_HIVE", "", "")?;
    let query = format!("SELECT * FROM `{}`", tabla);
    let mut html = String::from("<table border=\"1\"><tr>");

    if let Some(mut odbc_cursor) = conn.execute(&query, ())? {
        let cols = odbc_cursor.num_result_cols()? as usize;
        html.push_str("<tr>");
        for i in 1..=cols {
            html.push_str(&format!("<th>Col{}</th>", i));
        }
        html.push_str("</tr>");

        const MAX_ROWS_PER_BATCH: usize = 100;
        const MAX_BYTES_PER_CELL: usize = 1024;
        let mut buffers = TextRowSet::for_cursor(MAX_ROWS_PER_BATCH, &mut odbc_cursor, Some(MAX_BYTES_PER_CELL))?;
        let mut row_set_cursor = odbc_cursor.bind_buffer(&mut buffers)?;

        while let Some(batch) = row_set_cursor.fetch()? {
            for row_idx in 0..batch.num_rows() {
                html.push_str("<tr>");
                for col_idx in 0..cols {
                    let val_bytes = batch.at(row_idx, col_idx).unwrap_or(b"NULL");
                    let val_str = String::from_utf8_lossy(val_bytes).into_owned();
                    html.push_str(&format!("<td>{}</td>", val_str));
                }
                html.push_str("</tr>");
            }
        }
    } else {
        html.push_str("<tr><td colspan=\"100%\">No data returned or query did not produce results.</td></tr>");
    }

    html.push_str("</table>");
    Ok(html)
}
