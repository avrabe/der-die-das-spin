# 🚀 Spin SDK Features Research

Research on additional Spin features to enhance the Der Die Das Capybara Game!

---

## 🤖 1. Serverless AI / LLM Integration

### Overview
Spin provides built-in support for AI inferencing through the **Serverless AI API**, available since Spin v1.5+.

### Supported Models
- **llama2-chat** - For conversational AI and text generation
- **codellama-instruct** - For code generation and instructions
- **all-minilm-l6-v2** - For generating embeddings

### Rust API Example

```rust
use spin_sdk::llm;

// Basic inference
let response = llm::infer(
    llm::InferencingModel::Llama2Chat,
    "Create a German sentence using the word 'Tisch' without using der/die/das",
)?;

// Advanced inference with parameters
let response = llm::infer_with_options(
    llm::InferencingModel::Llama2Chat,
    &prompt,
    llm::InferencingParams {
        max_tokens: 100,
        repeat_penalty: 1.1,
        repeat_penalty_last_n_token_count: 64,
        temperature: 0.7,  // Lower for more deterministic
        top_k: 40,
        top_p: 0.9,
    },
)?;
```

### Configuration in spin.toml

```toml
[[trigger.http]]
route = "/api/..."
component = "der-die-das-api"

[component.der-die-das-api]
source = "target/wasm32-wasip1/release/der_die_das.wasm"
# Enable AI models
ai_models = ["llama2-chat"]
```

### 🦫 Use Case: Example Sentence Generation

**Feature**: Generate example sentences for words without revealing the article!

**Example Flow**:
1. User sees word: "Tisch"
2. Click "🦫 Beispiel Satz" button
3. AI generates: "Ich sitze am Tisch und lerne Deutsch."
4. User must still guess der/die/das
5. Sentence provides context without giving away the answer!

**Benefits**:
- **Educational**: Provides context for how words are used
- **Engaging**: Makes learning more interactive
- **Smart**: AI adapts to different words dynamically
- **No spoilers**: Sentences use declined forms (dem Tisch, den Tisch) not nominative

---

## 💾 2. Key-Value Storage

### Overview
Spin provides built-in key-value storage using SQLite, available by default since Spin v0.9.0.

### Rust API Example

```rust
use spin_sdk::key_value::{Store, Error};

// Open default store
let store = Store::open_default()?;

// Store data
store.set("sentence:Tisch", b"Ich sitze am Tisch.")?;

// Retrieve data
let sentence = store.get("sentence:Tisch")?;

// Delete data
store.delete("sentence:Tisch")?;

// Check if exists
let exists = store.exists("sentence:Tisch")?;
```

### Typed Storage (with Serde)

```rust
use spin_sdk::key_value::Store;
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
struct CachedSentence {
    word: String,
    sentence: String,
    genus: String,
    created_at: i64,
}

let store = Store::open_default()?;

// Store typed data (automatically serialized to JSON)
store.set_json("cache:Tisch", &cached_sentence)?;

// Retrieve typed data
let cached: CachedSentence = store.get_json("cache:Tisch")?;
```

### Configuration in spin.toml

```toml
[component.der-die-das-api]
source = "target/wasm32-wasip1/release/der_die_das.wasm"
# Enable key-value storage
key_value_stores = ["default"]
```

### 🦫 Use Cases

**1. Cache AI-Generated Sentences**
- Store AI responses to avoid regenerating for same words
- Faster response times
- Reduce AI inference costs

**2. User Progress Tracking**
- Store user scores and achievements
- Track which words they've practiced
- Remember game statistics

**3. Session Data**
- Cache multiplayer session info
- Store temporary game state
- Quick lookups without database queries

---

## 🌐 3. HTTP Outbound Requests

### Overview
Make HTTP requests to external APIs (OpenAI, DeepL, etc.) for enhanced functionality.

### Rust API Example

```rust
use spin_sdk::http;

// Simple GET request
let response = http::send(
    http::Request::builder()
        .method("GET")
        .uri("https://api.openai.com/v1/chat/completions")
        .header("Authorization", "Bearer YOUR_TOKEN")
        .body(request_body)?
).await?;

// Check response
if response.status().is_success() {
    let body = response.body();
    // Process response
}
```

### Configuration in spin.toml

```toml
[component.der-die-das-api]
source = "target/wasm32-wasip1/release/der_die_das.wasm"
# Allow outbound HTTP to specific hosts
allowed_outbound_hosts = [
    "https://api.openai.com",
    "https://api.deepl.com"
]

# Or allow all (not recommended for production)
# allowed_outbound_hosts = ["https://*:*"]
```

### 🦫 Use Cases

**1. External AI Services**
- OpenAI GPT for better sentence generation
- Google Translate API for translations
- DeepL for high-quality translations

**2. Dictionary APIs**
- Wiktionary API for additional word data
- Duden API for definitions
- Collins German Dictionary API

**3. Analytics & Monitoring**
- Send telemetry to external services
- Error reporting to Sentry
- Usage analytics

---

## 📊 4. Application Variables

### Overview
Configure application behavior without rebuilding, using environment variables.

### Rust API Example

```rust
use spin_sdk::variables;

// Get variable
let api_key = variables::get("openai_api_key")?;
let max_cache_age = variables::get("max_cache_age_seconds")?;
```

### Configuration in spin.toml

```toml
[variables]
openai_api_key = { required = true, secret = true }
max_cache_age_seconds = { default = "86400" }
ai_temperature = { default = "0.7" }
enable_sentence_generation = { default = "true" }

[component.der-die-das-api]
source = "target/wasm32-wasip1/release/der_die_das.wasm"
variables = [
    "openai_api_key",
    "max_cache_age_seconds",
    "ai_temperature",
    "enable_sentence_generation"
]
```

### Runtime Configuration

```bash
# Set variables when running
spin up --variable openai_api_key="sk-..." --variable ai_temperature="0.8"

# Or use environment variables
export SPIN_VARIABLE_OPENAI_API_KEY="sk-..."
spin up
```

### 🦫 Use Cases

**1. Feature Flags**
- Enable/disable sentence generation
- Toggle different AI models
- A/B testing features

**2. Configuration**
- AI temperature settings
- Cache durations
- Rate limits

**3. Secrets Management**
- API keys for external services
- Database credentials
- Authentication tokens

---

## 🗄️ 5. Redis Support

### Overview
Use Redis for advanced caching, pub/sub, and distributed storage.

### Rust API Example

```rust
use spin_sdk::redis;

// Set value
redis::set(&address, &key, &value)?;

// Get value
let value = redis::get(&address, &key)?;

// Publish message
redis::publish(&address, &channel, &message)?;

// Increment counter
redis::incr(&address, &key)?;
```

### Configuration in spin.toml

```toml
[component.der-die-das-api]
source = "target/wasm32-wasip1/release/der_die_das.wasm"
# Allow Redis connections
redis_databases = ["redis://localhost:6379"]
```

### 🦫 Use Cases

**1. Distributed Caching**
- Share AI responses across multiple Spin instances
- Session data in cloud deployments

**2. Pub/Sub for Multiplayer**
- Real-time score updates
- Chat between players
- Game events

**3. Leaderboards**
- Global high scores using Redis sorted sets
- Daily/weekly challenges

---

## 🎯 6. SQLite Database (Already Using!)

### What We're Already Using
- ✅ Storing German nouns with all 8 cases
- ✅ Multiplayer session management
- ✅ Score tracking

### Additional Possibilities

**1. User Accounts**
```sql
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    username TEXT NOT NULL,
    created_at INTEGER,
    total_score INTEGER DEFAULT 0,
    games_played INTEGER DEFAULT 0
);
```

**2. Word Statistics**
```sql
CREATE TABLE word_stats (
    word TEXT PRIMARY KEY,
    times_shown INTEGER DEFAULT 0,
    times_correct INTEGER DEFAULT 0,
    difficulty_rating REAL DEFAULT 0.5
);
```

**3. Achievements**
```sql
CREATE TABLE achievements (
    id INTEGER PRIMARY KEY,
    user_id TEXT,
    achievement_type TEXT,
    unlocked_at INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## 🚀 Implementation Priority for Der Die Das Game

### 🥇 Priority 1: AI Example Sentences (Highest Value)

**Feature**: Generate contextual example sentences using Spin's Serverless AI

**Why First?**
- Most educational value for learners
- Unique feature that differentiates our game
- Built-in Spin feature (no external dependencies)
- Kids will love seeing sentences about capybaras! 🦫

**Implementation**:
1. Add `ai_models = ["llama2-chat"]` to spin.toml
2. Create prompt template: "Create a German sentence using '{word}' in context. Use declined forms (dem, den, einem) but never use der/die/das in nominative case at the start."
3. Add "🦫 Beispiel" button to game UI
4. Stream or display AI-generated sentence
5. Keep it kid-friendly!

**Example Prompts**:
```
"Create a simple German sentence for a child using the word 'Tisch'.
Use the word in a declined form (dem Tisch, den Tisch, am Tisch)
but never reveal whether it's der/die/das.
Make it fun and mention a capybara if possible!
Keep it under 15 words."
```

**Example Outputs**:
- "Ein Capybara sitzt neben dem Tisch." ✅ (doesn't reveal der)
- "Ich stelle Blumen auf den Tisch." ✅ (doesn't reveal der)
- "Das Capybara malt am Tisch." ✅ (doesn't reveal der)

---

### 🥈 Priority 2: Key-Value Caching

**Feature**: Cache AI-generated sentences to improve speed and reduce costs

**Why Second?**
- Complements Priority 1 perfectly
- Built-in Spin feature (easy to implement)
- Improves performance significantly
- No external dependencies

**Implementation**:
1. Add `key_value_stores = ["default"]` to spin.toml
2. Cache structure: `sentence:{word}:{genus}` -> JSON
3. Check cache before calling AI
4. Set TTL or cache invalidation strategy
5. Store multiple sentences per word for variety

---

### 🥉 Priority 3: Application Variables

**Feature**: Configure AI behavior without redeploying

**Why Third?**
- Allows tweaking AI temperature, max_tokens, etc.
- Easy feature flags
- Production-ready configuration management
- No code changes needed for tuning

**Implementation**:
1. Add variables for AI parameters
2. Feature flags for new features
3. Configuration for cache TTL
4. A/B testing parameters

---

### 🎖️ Priority 4: HTTP Outbound (Optional)

**Feature**: Integrate external AI services like OpenAI GPT-4

**Why Fourth (Optional)?**
- More powerful AI than Llama2
- Better German language support
- Requires API key and costs money
- Dependency on external service
- Only needed if Llama2 isn't good enough

**When to Implement?**
- If Llama2 sentences aren't high quality
- If you want more sophisticated prompts
- If deploying to production with budget

---

### 🏅 Priority 5: Redis (Future)

**Feature**: Distributed caching and real-time multiplayer features

**Why Last?**
- Requires Redis server setup
- More complex infrastructure
- Only needed for cloud deployments at scale
- Current multiplayer works with SQLite

**When to Implement?**
- When deploying to Fermyon Cloud
- When scaling to many concurrent users
- When adding real-time chat or advanced features

---

## 📋 Implementation Checklist for Priority 1

### Phase 1: AI Sentence Generation (Week 1)

- [ ] Update `spin.toml` with `ai_models = ["llama2-chat"]`
- [ ] Create new API endpoint: `GET /api/sentence/:word`
- [ ] Implement prompt engineering for kid-friendly sentences
- [ ] Add error handling and fallbacks
- [ ] Test AI responses quality
- [ ] Ensure no article spoilers in generated sentences

### Phase 2: UI Integration (Week 1-2)

- [ ] Add "🦫 Beispiel Satz" button to word display
- [ ] Create loading animation (cute capybara thinking!)
- [ ] Display sentence in speech bubble or card
- [ ] Add capybara illustration saying the sentence
- [ ] Style button with Roblox 3D effect
- [ ] Add German subtitle explaining the feature

### Phase 3: Caching (Week 2)

- [ ] Add `key_value_stores = ["default"]` to spin.toml
- [ ] Implement cache-check before AI call
- [ ] Store sentences with metadata (word, genus, timestamp)
- [ ] Add cache invalidation (7-day TTL recommended)
- [ ] Generate 3-5 variations per word
- [ ] Rotate through cached sentences for variety

### Phase 4: Testing & Polish (Week 2-3)

- [ ] Test with 100+ different German words
- [ ] Verify no articles revealed in sentences
- [ ] Check kid-friendly language (no complex vocabulary)
- [ ] Test cache hit rates
- [ ] Measure AI response times
- [ ] User testing with kids
- [ ] Update documentation
- [ ] Add to CAPYBARA_THEME.md

---

## 🎨 UI/UX Design Ideas

### Example Sentence Display

```
┌─────────────────────────────────────────┐
│  🦫  Capybara sagt:                     │
│                                         │
│  "Ein Capybara sitzt neben dem Tisch   │
│   und isst eine Orange!"                │
│                                         │
│  ╭──────────────────────────╮          │
│  │  [🦫 Noch ein Beispiel]  │          │
│  ╰──────────────────────────╯          │
└─────────────────────────────────────────┘
```

### Button Placement Options

**Option A**: Below the word
```
┌────────────────┐
│  _____ Tisch   │
├────────────────┤
│ [🦫 Beispiel]  │
└────────────────┘
```

**Option B**: Beside article buttons
```
Der 💙   Die 💗   Das 💚   [🦫 Beispiel Satz]
```

**Option C**: Floating capybara helper
```
         🦫💭 "Möchtest du einen
              Beispiel Satz?"
              [Ja!] [Nein]
```

---

## 💡 Advanced Feature Ideas

### 1. 🎯 Difficulty Adaptation
- Track which words users struggle with
- Generate easier sentences for difficult words
- Adjust AI complexity based on user age/level

### 2. 🏆 Achievements
- "Sentence Scholar" - View 10 example sentences
- "Capybara Linguist" - View 50 sentences
- "Context King" - Use hints less over time

### 3. 📚 Sentence Collections
- Save favorite sentences
- Build a personal phrasebook
- Export sentences for study

### 4. 🎮 Sentence Challenge Mode
- Show sentence, remove the word
- User must identify the missing word AND article
- Advanced gameplay for experienced learners

### 5. 🔊 Text-to-Speech (Future)
- Read sentences aloud
- Help with pronunciation
- Audio for auditory learners

---

## 📊 Expected Performance

### AI Inference Times
- **Llama2-chat**: ~500ms - 2s per sentence (depending on complexity)
- **With caching**: <50ms for cached sentences
- **Cache hit rate**: Expected 60-80% after warmup

### Resource Usage
- **Memory**: +50MB for AI model
- **Storage**: ~1KB per cached sentence
- **Network**: None (AI runs locally in Spin!)

### Cost Analysis
- **Spin Serverless AI**: Included in Fermyon Cloud free tier
- **Key-Value Storage**: Included in Spin
- **External AI (Optional)**: $0.002 per request with OpenAI

---

## 🔐 Security & Privacy

### Data Privacy
- ✅ AI runs locally in Spin (no data sent to third parties)
- ✅ No user data collected for sentence generation
- ✅ Cache is per-word, not per-user
- ✅ GDPR-friendly

### Safety for Kids
- ✅ AI prompts specify kid-friendly content
- ✅ Add content filtering if needed
- ✅ Pre-generate and review sentences for quality
- ✅ Fallback to pre-written sentences if AI produces poor output

---

## 📈 Success Metrics

### Engagement
- % of users who click "Beispiel" button
- Average sentences viewed per session
- Time spent on words with sentences vs. without

### Learning Outcomes
- Accuracy improvement with vs. without sentences
- User feedback on helpfulness
- Retention rate of users who use sentences

### Technical
- Cache hit rate
- AI response time (p50, p95, p99)
- Error rate
- User satisfaction

---

## 🎯 Next Steps

1. **Review this research** with the team
2. **Decide on Priority 1** implementation approach
3. **Test Llama2-chat** locally with Spin
4. **Create prompt templates** for German sentences
5. **Prototype UI** for sentence display
6. **Build MVP** of AI sentence feature
7. **User test** with kids learning German
8. **Iterate** based on feedback
9. **Deploy** to production
10. **Measure** success metrics

---

## 🦫 Made with Love

This research is part of the Der Die Das Capybara Game - helping kids learn German with fun AI-powered features!

**Questions?** Open an issue or discussion on GitHub!

**Ready to implement?** Start with Priority 1 and let the capybaras help kids learn! 🦫✨
