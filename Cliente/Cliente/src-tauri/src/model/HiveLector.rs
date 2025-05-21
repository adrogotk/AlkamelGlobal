use odbc_api::{Environment, Connection, Cursor};

pub fn obtenerTablas() -> Result<Vec<String>, Box<dyn std::error::Error>> {
    let environment = Environment::new()?;
    let conn = environment.connect("DSN_HIVE", "", "")?;
    let catalog: &str = "";
    let schema: &str = "";
    let table: &str = "";
    let tableType: &str = "TABLE";
    let mut cursor = conn.tables(catalog, schema, table, tableType)?;

    let mut nombres = Vec::new();
    let mut buffer = vec![0u8; 512];

    let mut buffer = vec![0u8; 512];

    while let Some(mut row) = cursor.next_row()? {
        if row.get_text(2, &mut buffer)? {
            // Convertimos buffer hasta el primer byte nulo (si hay)
            if let Some(pos) = buffer.iter().position(|&b| b == 0) {
                let name = std::str::from_utf8(&buffer[..pos])?;
                nombres.push(name.to_string());
            } else {
                let name = std::str::from_utf8(&buffer)?;
                nombres.push(name.to_string());
            }
        }
    }
    

    Ok(nombres)
}