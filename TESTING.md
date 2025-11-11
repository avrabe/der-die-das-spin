# Testing Guide for Der Die Das Spin Application

## Build and Run Locally

### Prerequisites
```bash
# Install Spin (if not already installed)
curl -fsSL https://developer.fermyon.com/downloads/install.sh | bash

# Add wasm32-wasip1 target
rustup target add wasm32-wasip1
```

### Build the Application
```bash
cd der-die-das-spin
cargo build --target wasm32-wasip1 --release
spin build
```

### Run the Application
```bash
spin up
# Application will start on http://localhost:3000
```

---

## API Testing with curl

### 1. Get Random Word Entry
Test the basic word retrieval endpoint:

```bash
curl -v http://localhost:3000/api/entry.json
```

**Expected Response:**
```json
[
  {
    "nominativ_singular": "Tisch",
    "genus": "m"
  }
]
```

---

### 2. Create Multiplayer Session

Create a new game session:

```bash
curl -X POST http://localhost:3000/api/session/create \
  -H "Content-Type: application/json" \
  -d '{
    "player_name": "Alice",
    "game_mode": "multiplayer"
  }'
```

**Expected Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "player1_id": "123e4567-e89b-12d3-a456-426614174000",
  "player2_id": null,
  "player1_score": 0,
  "player2_score": 0,
  "current_word_index": 0,
  "game_mode": "multiplayer",
  "created_at": 1699123456
}
```

**Save the session_id for next tests!**

---

### 3. Get Session Details

Retrieve session information (replace `<SESSION_ID>` with actual ID from step 2):

```bash
SESSION_ID="550e8400-e29b-41d4-a716-446655440000"
curl http://localhost:3000/api/session/$SESSION_ID
```

**Expected Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "player1_id": "123e4567-e89b-12d3-a456-426614174000",
  "player2_id": null,
  "player1_score": 0,
  "player2_score": 0,
  "current_word_index": 0,
  "game_mode": "multiplayer",
  "created_at": 1699123456
}
```

---

### 4. Join Existing Session

Join a session as player 2:

```bash
curl -X POST http://localhost:3000/api/session/join \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "player_name": "Bob"
  }'
```

**Expected Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "player1_id": "123e4567-e89b-12d3-a456-426614174000",
  "player2_id": "789e0123-e45b-67c8-d901-234567890123",
  "player1_score": 0,
  "player2_score": 0,
  "current_word_index": 0,
  "game_mode": "multiplayer",
  "created_at": 1699123456
}
```

---

### 5. Submit Answer

Submit a correct/incorrect answer (replace IDs with actual values):

```bash
# Player 1 submits correct answer
curl -X POST http://localhost:3000/api/session/$SESSION_ID/answer \
  -H "Content-Type: application/json" \
  -d '{
    "player_id": "123e4567-e89b-12d3-a456-426614174000",
    "correct": true
  }'
```

**Expected Response:**
```json
{
  "success": true
}
```

Now check the session to see updated score:

```bash
curl http://localhost:3000/api/session/$SESSION_ID
```

**Expected Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "player1_id": "123e4567-e89b-12d3-a456-426614174000",
  "player2_id": "789e0123-e45b-67c8-d901-234567890123",
  "player1_score": 1,  // ← Score increased!
  "player2_score": 0,
  "current_word_index": 0,
  "game_mode": "multiplayer",
  "created_at": 1699123456
}
```

---

### 6. Test Static Files

Access the frontend:

```bash
# Homepage
curl http://localhost:3000/

# Static assets
curl http://localhost:3000/style.css
curl http://localhost:3000/script.js
curl http://localhost:3000/favicon-16x16.png
```

---

## Complete Testing Workflow

### Full Multiplayer Game Simulation

```bash
#!/bin/bash
set -e

echo "=== Testing Der Die Das Multiplayer Game ==="

# 1. Create session
echo -e "\n1. Creating game session..."
SESSION_RESPONSE=$(curl -s -X POST http://localhost:3000/api/session/create \
  -H "Content-Type: application/json" \
  -d '{"player_name": "Alice", "game_mode": "multiplayer"}')
echo $SESSION_RESPONSE | jq .

SESSION_ID=$(echo $SESSION_RESPONSE | jq -r .session_id)
PLAYER1_ID=$(echo $SESSION_RESPONSE | jq -r .player1_id)
echo "Session ID: $SESSION_ID"
echo "Player 1 ID: $PLAYER1_ID"

# 2. Join session
echo -e "\n2. Player 2 joining session..."
JOIN_RESPONSE=$(curl -s -X POST http://localhost:3000/api/session/join \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"$SESSION_ID\", \"player_name\": \"Bob\"}")
echo $JOIN_RESPONSE | jq .

PLAYER2_ID=$(echo $JOIN_RESPONSE | jq -r .player2_id)
echo "Player 2 ID: $PLAYER2_ID"

# 3. Get some words
echo -e "\n3. Getting random words..."
for i in {1..3}; do
  echo "Word $i:"
  curl -s http://localhost:3000/api/entry.json | jq .
done

# 4. Simulate gameplay - Player 1 gets 3 correct
echo -e "\n4. Player 1 answering correctly (3 times)..."
for i in {1..3}; do
  curl -s -X POST http://localhost:3000/api/session/$SESSION_ID/answer \
    -H "Content-Type: application/json" \
    -d "{\"player_id\": \"$PLAYER1_ID\", \"correct\": true}" | jq .
done

# 5. Simulate gameplay - Player 2 gets 2 correct
echo -e "\n5. Player 2 answering correctly (2 times)..."
for i in {1..2}; do
  curl -s -X POST http://localhost:3000/api/session/$SESSION_ID/answer \
    -H "Content-Type: application/json" \
    -d "{\"player_id\": \"$PLAYER2_ID\", \"correct\": true}" | jq .
done

# 6. Check final scores
echo -e "\n6. Final scores:"
curl -s http://localhost:3000/api/session/$SESSION_ID | jq .

echo -e "\n=== Test Complete ==="
```

Save this as `test_multiplayer.sh`, make it executable with `chmod +x test_multiplayer.sh`, and run it!

---

## Browser Testing

1. Open http://localhost:3000 in your browser
2. Test each game mode:
   - **Practice Mode**: Unlimited time, learn at your own pace
   - **Timed Challenge**: 2-minute countdown timer
   - **Create Multiplayer**: Creates a session and shows session ID
   - **Join Multiplayer**: Enter a session ID to join

### Multiplayer Testing (2 browsers)

1. **Browser 1**: Create a multiplayer game, copy the session ID
2. **Browser 2**: Join using the session ID
3. Both browsers should now show opponent scores updating in real-time
4. Play a few rounds and verify:
   - Scores update correctly
   - Both players can see each other's scores
   - Game ends properly

---

## Database Inspection

Check the SQLite database directly:

```bash
cd der-die-das-spin
sqlite3 .spin/sqlite_db.db

-- View all tables
.tables

-- Check word entries
SELECT nominativ_singular, genus FROM derdiedas LIMIT 10;

-- Check game sessions
SELECT session_id, player1_score, player2_score, game_mode
FROM game_sessions;

-- Exit
.quit
```

---

## Performance Testing

### Load Test with Apache Bench

```bash
# Test word retrieval endpoint
ab -n 1000 -c 10 http://localhost:3000/api/entry.json

# Test session creation
ab -n 100 -c 5 -p create_session.json -T application/json \
  http://localhost:3000/api/session/create
```

Where `create_session.json` contains:
```json
{"player_name": "TestUser", "game_mode": "multiplayer"}
```

---

## Troubleshooting

### No words showing up?
Make sure you've imported data from Wiktionary:
```bash
cd ..
cargo build -p dewiktionary-importer-cli --release
DATABASE_URL=der-die-das-spin/.spin/sqlite_db.db \
  ./target/release/dewiktionary-importer-cli \
  -f dewiktionary-latest-pages-articles-multistream.xml.bz2
```

### Session not found?
Sessions are stored in SQLite. Check if the table exists:
```bash
sqlite3 der-die-das-spin/.spin/sqlite_db.db "SELECT name FROM sqlite_master WHERE type='table';"
```

### Port already in use?
Change the port in `spin.toml` or stop the conflicting service.

---

## Expected Behavior Summary

✅ **API Endpoints Working**
- `/api/entry.json` returns random German nouns with genus
- `/api/session/create` creates new multiplayer sessions
- `/api/session/join` allows joining existing sessions
- `/api/session/:id` retrieves session details
- `/api/session/:id/answer` submits answers and updates scores

✅ **Frontend Features Working**
- Mode selection screen with 4 options
- Practice mode with unlimited time
- Timed challenge with 2-minute countdown
- Multiplayer with session sharing
- Real-time score updates
- Responsive design on mobile and desktop

✅ **Database Features Working**
- Supports all 8 German cases (Nominativ, Genitiv, Dativ, Akkusativ × singular/plural)
- Session persistence
- Score tracking

---

## CI/CD Verification

The GitHub Actions workflow will:
1. ✅ Install Rust toolchain with wasm32-wasip1 target
2. ✅ Build all crates (dewiktionary, dewiktionary-diesel, dewiktionary-importer-cli)
3. ✅ Build the WASM module
4. ✅ Run Spin build
5. ✅ Run cargo tests
6. ✅ Check dependencies with cargo-deny
7. ✅ Generate code coverage reports

Check the CI results at:
https://github.com/avrabe/der-die-das-spin/actions
