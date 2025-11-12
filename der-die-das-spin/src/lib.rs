use anyhow::Result;
use serde::{Deserialize, Serialize};
use spin_sdk::{
    http::{IntoResponse, Request, Response, Router},
    http_component,
    key_value::Store,
    sqlite::{Connection, Value},
};

mod sentences;
mod kid_id;

// Helper for returning the query results as JSON
#[derive(Serialize, Deserialize, Debug, Clone)]
struct DerDieDas {
    nominativ_singular: String,
    genus: String,
}

#[derive(Serialize, Deserialize, Debug, Clone)]
struct GameSession {
    session_id: String,
    player1_id: String,
    player2_id: Option<String>,
    player1_score: i32,
    player2_score: i32,
    current_word_index: i32,
    game_mode: String,
    created_at: i64,
}

#[derive(Serialize, Deserialize)]
struct CreateSessionRequest {
    player_name: String,
    game_mode: String,
}

#[derive(Serialize, Deserialize)]
struct JoinSessionRequest {
    session_id: String,
    player_name: String,
}

/// Main HTTP handler using Spin SDK's Router
#[http_component]
fn handle_request(req: Request) -> Result<impl IntoResponse> {
    let mut router = Router::new();

    router.get("/api/entry.json", get_random_entry);
    router.get("/api/sentence/:word", get_example_sentence);
    router.get("/api/syllable-quiz", get_syllable_quiz);
    router.get("/api/category-quiz", get_category_quiz);
    router.post("/api/session/create", create_session);
    router.post("/api/session/join", join_session);
    router.get("/api/session/:id", get_session);
    router.post("/api/session/:id/answer", submit_answer);

    Ok(router.handle(req))
}

/// Get a random German noun entry
fn get_random_entry(_req: Request, _params: spin_sdk::http::Params) -> Result<impl IntoResponse> {
    let connection = Connection::open_default()?;

    // Try new 'words' table first, fall back to legacy 'derdiedas' table
    let rowset = connection.execute(
        "SELECT word as nominativ_singular,
                CASE article
                    WHEN 'der' THEN 'm'
                    WHEN 'die' THEN 'f'
                    WHEN 'das' THEN 'n'
                    ELSE 'm'
                END as genus
         FROM words
         ORDER BY RANDOM()
         LIMIT 1",
        &[],
    );

    let entries: Vec<DerDieDas> = match rowset {
        Ok(rs) => rs.rows()
            .map(|row| DerDieDas {
                nominativ_singular: row.get::<&str>("nominativ_singular").unwrap().to_owned(),
                genus: row.get::<&str>("genus").unwrap().to_owned(),
            })
            .collect(),
        Err(_) => {
            // Fall back to legacy table
            let rowset_legacy = connection.execute(
                "SELECT nominativ_singular, genus FROM derdiedas ORDER BY RANDOM() LIMIT 1",
                &[],
            )?;

            rowset_legacy.rows()
                .map(|row| DerDieDas {
                    nominativ_singular: row.get::<&str>("nominativ_singular").unwrap().to_owned(),
                    genus: row.get::<&str>("genus").unwrap().to_owned(),
                })
                .collect()
        }
    };

    Ok(Response::builder()
        .status(200)
        .header("content-type", "application/json")
        .body(serde_json::to_string(&entries)?)
        .build())
}

/// Get an example sentence for a given word
fn get_example_sentence(_req: Request, params: spin_sdk::http::Params) -> Result<impl IntoResponse> {
    #[derive(Serialize)]
    struct SentenceResponse {
        word: String,
        sentence: String,
        cached: bool,
    }

    let word = params.get("word")
        .ok_or_else(|| anyhow::anyhow!("Missing word parameter"))?;

    // First, look up the genus for this word from the database
    let connection = Connection::open_default()?;

    // Try new 'words' table first
    let genus = match connection.execute(
        "SELECT CASE article
                    WHEN 'der' THEN 'm'
                    WHEN 'die' THEN 'f'
                    WHEN 'das' THEN 'n'
                    ELSE 'm'
                END as genus
         FROM words WHERE word = ? LIMIT 1",
        &[Value::Text(word.to_string())],
    ) {
        Ok(rs) => {
            let rows: Vec<_> = rs.rows().collect();
            rows.first()
                .and_then(|row| row.get::<&str>("genus"))
                .map(|s| s.to_owned())
                .unwrap_or_else(|| "m".to_string())
        },
        Err(_) => {
            // Fall back to legacy table
            match connection.execute(
                "SELECT genus FROM derdiedas WHERE nominativ_singular = ? LIMIT 1",
                &[Value::Text(word.to_string())],
            ) {
                Ok(rs) => {
                    let rows: Vec<_> = rs.rows().collect();
                    rows.first()
                        .and_then(|row| row.get::<&str>("genus"))
                        .map(|s| s.to_owned())
                        .unwrap_or_else(|| "m".to_string())
                },
                Err(_) => "m".to_string()
            }
        }
    };

    // Try to get from cache first
    let cache_key = format!("sentence:{}", word.to_lowercase());
    let store = Store::open_default()?;

    let (sentence, cached) = if let Ok(Some(data)) = store.get(&cache_key) {
        // Got from cache
        let cached_sentences: Vec<String> = serde_json::from_slice(&data)?;
        // Return a random one from the cache
        let idx = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)?
            .as_secs() as usize % cached_sentences.len();
        (cached_sentences[idx].clone(), true)
    } else {
        // Generate ONE new sentence using LLM (generating 5 causes timeout)
        // Each request will add to the cache, building up over time
        let new_sentence = sentences::generate_sentences(word, &genus, 1);
        let sentence_text = new_sentence[0].sentence.clone();

        // Get existing cache or create new
        let mut cached_sentences: Vec<String> = if let Ok(Some(data)) = store.get(&cache_key) {
            serde_json::from_slice(&data).unwrap_or_default()
        } else {
            Vec::new()
        };

        // Add new sentence if not already cached (max 5 variations)
        if !cached_sentences.contains(&sentence_text) && cached_sentences.len() < 5 {
            cached_sentences.push(sentence_text.clone());
            let cache_data = serde_json::to_vec(&cached_sentences)?;
            store.set(&cache_key, &cache_data)?;
        }

        (sentence_text, false)
    };

    let response = SentenceResponse {
        word: word.to_string(),
        sentence,
        cached,
    };

    Ok(Response::builder()
        .status(200)
        .header("content-type", "application/json")
        .body(serde_json::to_string(&response)?)
        .build())
}

/// Create a new game session
fn create_session(req: Request, _params: spin_sdk::http::Params) -> Result<impl IntoResponse> {
    let body: CreateSessionRequest = serde_json::from_slice(req.body())?;

    // Use kid-friendly short ID instead of UUID
    let session_id = kid_id::generate_default();
    let player1_id = uuid::Uuid::new_v4().to_string();

    let connection = Connection::open_default()?;

    // Create sessions table if it doesn't exist
    connection.execute(
        "CREATE TABLE IF NOT EXISTS game_sessions (
            session_id TEXT PRIMARY KEY,
            player1_id TEXT NOT NULL,
            player2_id TEXT,
            player1_score INTEGER DEFAULT 0,
            player2_score INTEGER DEFAULT 0,
            current_word_index INTEGER DEFAULT 0,
            game_mode TEXT NOT NULL,
            created_at INTEGER NOT NULL
        )",
        &[],
    )?;

    let now = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)?
        .as_secs() as i64;

    connection.execute(
        "INSERT INTO game_sessions (session_id, player1_id, game_mode, created_at) VALUES (?, ?, ?, ?)",
        &[
            Value::Text(session_id.clone()),
            Value::Text(player1_id.clone()),
            Value::Text(body.game_mode.clone()),
            Value::Integer(now),
        ],
    )?;

    let session = GameSession {
        session_id: session_id.clone(),
        player1_id: player1_id.clone(),
        player2_id: None,
        player1_score: 0,
        player2_score: 0,
        current_word_index: 0,
        game_mode: body.game_mode,
        created_at: now,
    };

    Ok(Response::builder()
        .status(200)
        .header("content-type", "application/json")
        .body(serde_json::to_string(&session)?)
        .build())
}

/// Join an existing game session
fn join_session(req: Request, _params: spin_sdk::http::Params) -> Result<impl IntoResponse> {
    let body: JoinSessionRequest = serde_json::from_slice(req.body())?;
    let player2_id = uuid::Uuid::new_v4().to_string();

    let connection = Connection::open_default()?;

    connection.execute(
        "UPDATE game_sessions SET player2_id = ? WHERE session_id = ?",
        &[
            Value::Text(player2_id.clone()),
            Value::Text(body.session_id.clone()),
        ],
    )?;

    let rowset = connection.execute(
        "SELECT * FROM game_sessions WHERE session_id = ?",
        &[Value::Text(body.session_id.clone())],
    )?;

    let rows: Vec<_> = rowset.rows().collect();

    if let Some(row) = rows.first() {
        let session = GameSession {
            session_id: row.get::<&str>("session_id").unwrap().to_owned(),
            player1_id: row.get::<&str>("player1_id").unwrap().to_owned(),
            player2_id: Some(player2_id.clone()),
            player1_score: row.get::<i32>("player1_score").unwrap_or(0),
            player2_score: row.get::<i32>("player2_score").unwrap_or(0),
            current_word_index: row.get::<i32>("current_word_index").unwrap_or(0),
            game_mode: row.get::<&str>("game_mode").unwrap().to_owned(),
            created_at: row.get::<i64>("created_at").unwrap_or(0),
        };

        Ok(Response::builder()
            .status(200)
            .header("content-type", "application/json")
            .body(serde_json::to_string(&session)?)
            .build())
    } else {
        Ok(Response::builder()
            .status(404)
            .body("Session not found".to_string())
            .build())
    }
}

/// Get session details
fn get_session(_req: Request, params: spin_sdk::http::Params) -> Result<impl IntoResponse> {
    let session_id = params.get("id").ok_or(anyhow::anyhow!("Missing session ID"))?;

    let connection = Connection::open_default()?;
    let rowset = connection.execute(
        "SELECT * FROM game_sessions WHERE session_id = ?",
        &[Value::Text(session_id.to_string())],
    )?;

    let rows: Vec<_> = rowset.rows().collect();

    if let Some(row) = rows.first() {
        let player2_id = row.get::<&str>("player2_id").map(|s| s.to_owned());

        let session = GameSession {
            session_id: row.get::<&str>("session_id").unwrap().to_owned(),
            player1_id: row.get::<&str>("player1_id").unwrap().to_owned(),
            player2_id,
            player1_score: row.get::<i32>("player1_score").unwrap_or(0),
            player2_score: row.get::<i32>("player2_score").unwrap_or(0),
            current_word_index: row.get::<i32>("current_word_index").unwrap_or(0),
            game_mode: row.get::<&str>("game_mode").unwrap().to_owned(),
            created_at: row.get::<i64>("created_at").unwrap_or(0),
        };

        Ok(Response::builder()
            .status(200)
            .header("content-type", "application/json")
            .body(serde_json::to_string(&session)?)
            .build())
    } else {
        Ok(Response::builder()
            .status(404)
            .body("Session not found".to_string())
            .build())
    }
}

/// Submit an answer and update score
fn submit_answer(req: Request, params: spin_sdk::http::Params) -> Result<impl IntoResponse> {
    #[derive(Deserialize)]
    struct AnswerRequest {
        player_id: String,
        correct: bool,
    }

    let session_id = params.get("id").ok_or(anyhow::anyhow!("Missing session ID"))?;
    let body: AnswerRequest = serde_json::from_slice(req.body())?;

    let connection = Connection::open_default()?;

    // Get current session
    let rowset = connection.execute(
        "SELECT player1_id, player2_id FROM game_sessions WHERE session_id = ?",
        &[Value::Text(session_id.to_string())],
    )?;

    let rows: Vec<_> = rowset.rows().collect();

    if let Some(row) = rows.first() {
        let player1_id = row.get::<&str>("player1_id").unwrap().to_owned();
        let is_player1 = player1_id == body.player_id;

        if body.correct {
            let update_query = if is_player1 {
                "UPDATE game_sessions SET player1_score = player1_score + 1 WHERE session_id = ?"
            } else {
                "UPDATE game_sessions SET player2_score = player2_score + 1 WHERE session_id = ?"
            };

            connection.execute(
                update_query,
                &[Value::Text(session_id.to_string())],
            )?;
        }

        Ok(Response::builder()
            .status(200)
            .header("content-type", "application/json")
            .body(r#"{"success": true}"#.to_string())
            .build())
    } else {
        Ok(Response::builder()
            .status(404)
            .body("Session not found".to_string())
            .build())
    }
}

/// Get a syllable quiz question
fn get_syllable_quiz(_req: Request, _params: spin_sdk::http::Params) -> Result<impl IntoResponse> {
    #[derive(Serialize)]
    struct SyllableQuiz {
        word: String,
        syllable_count: i32,
        difficulty: i32,
    }

    let connection = Connection::open_default()?;

    // Get a random word with syllable data
    let rowset = connection.execute(
        "SELECT nominativ_singular, syllable_count, difficulty
         FROM derdiedas
         WHERE syllable_count IS NOT NULL AND syllable_count > 0
         ORDER BY RANDOM() LIMIT 1",
        &[],
    )?;

    let rows: Vec<_> = rowset.rows().collect();

    if let Some(row) = rows.first() {
        let quiz = SyllableQuiz {
            word: row.get::<&str>("nominativ_singular").unwrap().to_owned(),
            syllable_count: row.get::<i32>("syllable_count").unwrap_or(1),
            difficulty: row.get::<i32>("difficulty").unwrap_or(1),
        };

        Ok(Response::builder()
            .status(200)
            .header("content-type", "application/json")
            .body(serde_json::to_string(&quiz)?)
            .build())
    } else {
        Ok(Response::builder()
            .status(404)
            .body("No words with syllable data found".to_string())
            .build())
    }
}

/// Get a category quiz question
fn get_category_quiz(_req: Request, _params: spin_sdk::http::Params) -> Result<impl IntoResponse> {
    #[derive(Serialize)]
    struct CategoryQuiz {
        word: String,
        category: String,
        difficulty: i32,
        options: Vec<String>,
    }

    let connection = Connection::open_default()?;

    // Get a random word with category data
    let rowset = connection.execute(
        "SELECT nominativ_singular, category, difficulty
         FROM derdiedas
         WHERE category IS NOT NULL
         ORDER BY RANDOM() LIMIT 1",
        &[],
    )?;

    let rows: Vec<_> = rowset.rows().collect();

    if let Some(row) = rows.first() {
        let word = row.get::<&str>("nominativ_singular").unwrap().to_owned();
        let category = row.get::<&str>("category").unwrap().to_owned();
        let difficulty = row.get::<i32>("difficulty").unwrap_or(1);

        // Get 3 other random categories as distractors
        let distractor_rowset = connection.execute(
            "SELECT DISTINCT category FROM derdiedas
             WHERE category IS NOT NULL AND category != ?
             ORDER BY RANDOM() LIMIT 3",
            &[Value::Text(category.clone())],
        )?;

        let mut options: Vec<String> = distractor_rowset
            .rows()
            .map(|r| r.get::<&str>("category").unwrap().to_owned())
            .collect();

        // Add correct answer
        options.push(category.clone());

        // Shuffle options using a simple algorithm
        use std::time::SystemTime;
        let seed = SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)?
            .as_secs() as usize;

        for i in (1..options.len()).rev() {
            let j = (seed + i) % (i + 1);
            options.swap(i, j);
        }

        let quiz = CategoryQuiz {
            word,
            category,
            difficulty,
            options,
        };

        Ok(Response::builder()
            .status(200)
            .header("content-type", "application/json")
            .body(serde_json::to_string(&quiz)?)
            .build())
    } else {
        Ok(Response::builder()
            .status(404)
            .body("No words with category data found".to_string())
            .build())
    }
}
