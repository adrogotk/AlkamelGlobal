use odbc_api::{Environment, Connection};

fn obtener_tablas() -> Result<Vec<String>, Box<dyn std::error::Error>> {
    let environment = Environment::new()?;
    let conn = environment.connect("DSN_HIVE", "", "")?;
    let cursor = conn.tables(None, None, None, Some("TABLE"))?;

    let mut nombres = Vec::new();
    if let Some(mut cursor) = cursor {
        while let Some(row) = cursor.fetch()? {
            let name = row.get_string(2)?;
            nombres.push(name.to_string());
        }
    }

    Ok(nombres)
}