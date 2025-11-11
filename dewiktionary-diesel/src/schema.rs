// @generated automatically by Diesel CLI.

diesel::table! {
    derdiedas (nominativ_singular) {
        nominativ_singular -> Text,
        genus -> Text,
        nominativ_plural -> Nullable<Text>,
        genitiv_singular -> Nullable<Text>,
        genitiv_plural -> Nullable<Text>,
        dativ_singular -> Nullable<Text>,
        dativ_plural -> Nullable<Text>,
        akkusativ_singular -> Nullable<Text>,
        akkusativ_plural -> Nullable<Text>,
    }
}
