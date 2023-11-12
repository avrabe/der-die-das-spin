use crate::schema::derdiedas;
use diesel::prelude::*;

#[derive(Queryable, Selectable)]
#[diesel(table_name = derdiedas)]
#[diesel(check_for_backend(diesel::sqlite::Sqlite))]
pub struct DerDieDas {
    pub nominativ_singular: String,
    pub genus: String,
}

#[derive(Insertable)]
#[diesel(table_name = derdiedas)]
pub struct NewEntry<'a> {
    pub nominativ_singular: &'a str,
    pub genus: &'a str,
}
