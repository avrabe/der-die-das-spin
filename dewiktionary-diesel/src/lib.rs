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

pub fn create_entry(conn: &mut SqliteConnection, nominativ_singular: &str, genus: &str) {
    let new_post = NewEntry {
        nominativ_singular,
        genus,
    };

    diesel::insert_into(derdiedas::table)
        .values(&new_post)
        .execute(conn)
        .expect("Error saving new entry");
}
