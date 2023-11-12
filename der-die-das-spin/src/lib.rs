use anyhow::Result;
use serde::Serialize;
use spin_sdk::{
    http::{Request, IntoResponse},
    http_component,
    sqlite::Connection,
};

#[http_component]
fn handle_request(_req: Request) -> Result<impl IntoResponse> {
    let connection = Connection::open_default()?;

    let rowset = connection.execute(
        "SELECT nominativ_singular, genus FROM derdiedas
                   ORDER BY RANDOM() LIMIT 1",
        &[]
    )?;

    let todos: Vec<_> = rowset.rows().map(|row|
        DerDieDas {
            nominativ_singular: row.get::<&str>("nominativ_singular").unwrap().to_owned(),
            genus: row.get::<&str>("genus").unwrap().to_owned(),
        }
    ).collect();

    let body = Some(serde_json::to_vec(&todos)?);
    let response = http::Response::builder().status(200).body(body)?;
    Ok(response)
}

// Helper for returning the query results as JSON
#[derive(Serialize)]
struct DerDieDas {
    nominativ_singular: String,
    genus: String,
}