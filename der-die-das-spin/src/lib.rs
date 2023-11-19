use serde::Serialize;
use spin_sdk::sqlite::Connection;

use {
    bindings::wasi::http::incoming_handler,
    futures::SinkExt,
    spin_sdk::{
        http::{Fields, IncomingRequest, Method, OutgoingResponse, ResponseOutparam},
        http_component,
    },
};

mod bindings {
    wit_bindgen::generate!({
        path: "../spin-fileserver/examples/wit",
        world: "delegate",
        with: {
            "wasi:http/types@0.2.0-rc-2023-10-18": spin_sdk::wit::wasi::http::types,
            "wasi:io/streams@0.2.0-rc-2023-10-18": spin_sdk::wit::wasi::io::streams,
            "wasi:io/poll@0.2.0-rc-2023-10-18": spin_sdk::wit::wasi::io,
        }
    });
}

async fn h() -> Option<Vec<u8>> {
    let connection = Connection::open_default().unwrap();

    let rowset = connection
        .execute(
            "SELECT nominativ_singular, genus FROM derdiedas
                   ORDER BY RANDOM() LIMIT 1",
            &[],
        )
        .expect("msg");

    let todos: Vec<_> = rowset
        .rows()
        .map(|row| DerDieDas {
            nominativ_singular: row.get::<&str>("nominativ_singular").unwrap().to_owned(),
            genus: row.get::<&str>("genus").unwrap().to_owned(),
        })
        .collect();

    Some(serde_json::to_vec(&todos).unwrap())
}

// Helper for returning the query results as JSON
#[derive(Serialize)]
struct DerDieDas {
    nominativ_singular: String,
    genus: String,
}

#[http_component]
async fn handle_request(request: IncomingRequest, response_out: ResponseOutparam) {
    match (request.method(), request.path_with_query().as_deref()) {
        (Method::Get, Some("/entry.json")) => {
            let response = OutgoingResponse::new(
                200,
                &Fields::new(&[("content-type".to_string(), b"application/json".to_vec())]),
            );

            let mut body = response.take_body();

            response_out.set(response);
            let b = h().await.unwrap();

            if let Err(e) = body.send(b).await {
                eprintln!("Error sending payload: {e}");
            }
        }

        (Method::Get, _) => {
            // Delegate to spin-fileserver component
            incoming_handler::handle(request, response_out.into_inner())
        }

        _ => {
            response_out.set(OutgoingResponse::new(405, &Fields::new(&[])));
        }
    }
}
