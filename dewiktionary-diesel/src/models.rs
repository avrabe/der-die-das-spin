use crate::schema::derdiedas;
use diesel::prelude::*;

#[derive(Queryable, Selectable)]
#[diesel(table_name = derdiedas)]
#[diesel(check_for_backend(diesel::sqlite::Sqlite))]
pub struct DerDieDas {
    pub nominativ_singular: String,
    pub genus: String,
    pub nominativ_plural: Option<String>,
    pub genitiv_singular: Option<String>,
    pub genitiv_plural: Option<String>,
    pub dativ_singular: Option<String>,
    pub dativ_plural: Option<String>,
    pub akkusativ_singular: Option<String>,
    pub akkusativ_plural: Option<String>,
}

#[derive(Insertable)]
#[diesel(table_name = derdiedas)]
pub struct NewEntry<'a> {
    pub nominativ_singular: &'a str,
    pub genus: &'a str,
    pub nominativ_plural: Option<&'a str>,
    pub genitiv_singular: Option<&'a str>,
    pub genitiv_plural: Option<&'a str>,
    pub dativ_singular: Option<&'a str>,
    pub dativ_plural: Option<&'a str>,
    pub akkusativ_singular: Option<&'a str>,
    pub akkusativ_plural: Option<&'a str>,
}
