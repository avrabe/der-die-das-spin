use diesel::prelude::*;
use diesel::sqlite::SqliteConnection;
use schema::derdiedas;

pub mod models;
pub mod schema;

pub fn establish_connection(database_url: &str) -> SqliteConnection {
    SqliteConnection::establish(database_url)
        .unwrap_or_else(|_| panic!("Error connecting to {}", database_url))
}

use crate::models::NewEntry;

#[allow(clippy::too_many_arguments)]
pub fn create_entry(
    conn: &mut SqliteConnection,
    nominativ_singular: &str,
    genus: &str,
    nominativ_plural: Option<&str>,
    genitiv_singular: Option<&str>,
    genitiv_plural: Option<&str>,
    dativ_singular: Option<&str>,
    dativ_plural: Option<&str>,
    akkusativ_singular: Option<&str>,
    akkusativ_plural: Option<&str>,
) {
    let new_post = NewEntry {
        nominativ_singular,
        genus,
        nominativ_plural,
        genitiv_singular,
        genitiv_plural,
        dativ_singular,
        dativ_plural,
        akkusativ_singular,
        akkusativ_plural,
    };

    diesel::insert_into(derdiedas::table)
        .values(&new_post)
        .execute(conn)
        .expect("Error saving new entry");
}
