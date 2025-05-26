use odbc_api::{Environment, Connection, Cursor, ResultSetMetadata};
use odbc_api::buffers::TextRowSet;

const CONNECTION_STRING: &str="Driver={Cloudera ODBC Driver for Apache Hive};Host=localhost;Port=10000;Schema=AlkamelCsvs;UID=hive;PWD=hive;";
const TABLE_TYPE: &str="TABLE";
const EMPTY_TABLE: &str="<tr><td colspan=\"100%\">No data returned or query did not produce results.</td></tr>";
const MAX_ROWS_PER_BATCH: usize = 100;
const MAX_BYTES_PER_CELL: usize = 1024;
pub fn obtenerTablas() -> Result<Vec<String>, Box<dyn std::error::Error>> {
    let env = odbc_api::Environment::new()?;
    let conn = env.connect_with_connection_string(CONNECTION_STRING)?;
    let catalog: &str = "";
    let schema: &str = "";
    let table: &str = "%";
    let mut cursor = conn.tables(catalog, schema, table, TABLE_TYPE)?;

    let mut nombres = Vec::new();

    let mut buffer = vec![0u8; 512];

    while let Some(mut row) = cursor.next_row()? {
        if row.get_text(3, &mut buffer)? {
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
pub fn obtenerDatosTabla(tabla: &str) -> Result<String, Box<dyn std::error::Error>> {
    let env = odbc_api::Environment::new()?;
    let conn = env.connect_with_connection_string(CONNECTION_STRING)?;
    let query = format!("SELECT * FROM `{}`", tabla);
    let mut html = String::from("<table id='datos' border=\"1\">");

    if let Some(mut cursor) = conn.execute(&query, ())? {
        // Obtener nombres reales de columnas
        let cols = cursor.num_result_cols()? as usize;
        let mut columnNames = Vec::with_capacity(cols);
        for i in 1..=cols as u16 {
            columnNames.push(cursor.col_name(i));
        }

        // Cabecera HTML
        html.push_str("<tr>");
        for i in 1..=cols {
            let colNameHive = cursor.col_name(i.try_into()?)?;
            let colName=colNameHive.replace(tabla,"").replace(".", "");
            html.push_str(&format!("<th>{}</th>", colName));
        }
        html.push_str("</tr>");

        // Cargar datos en buffer
        let mut buffers = TextRowSet::for_cursor(MAX_ROWS_PER_BATCH, &mut cursor, Some(MAX_BYTES_PER_CELL))?;
        let mut rowSetCursor = cursor.bind_buffer(&mut buffers)?;

        while let Some(batch) = rowSetCursor.fetch()? {
            let numRows = batch.num_rows();
            let numCols = batch.num_cols();
            for rowIdx in 0..numRows {
                html.push_str("<tr>");
                for colIdx in 0..numCols {
                    let valStr = match batch.at(colIdx, rowIdx) {
                        Some(bytes) => String::from_utf8_lossy(bytes).into_owned(),
                        None => "NULL".to_string(),
                    };
                    let celdas=valStr.split(";");
                    for celdaHive in celdas{
                        let celda=celdaHive.replace("_", " ");
                        html.push_str(&format!("<td>{}</td>", celda));
                    }
                }
                html.push_str("</tr>");
            }
        }
    } else {
        html.push_str(EMPTY_TABLE);
    }

    html.push_str("</table>");
    Ok(html)
}