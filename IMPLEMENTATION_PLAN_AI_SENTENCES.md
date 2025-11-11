# 🤖 Implementation Plan: AI-Powered Example Sentences

**Feature**: Generate contextual German sentences using Spin's Serverless AI without revealing der/die/das

---

## 🎯 Goal

Add an interactive "🦫 Beispiel Satz" (Example Sentence) button that:
1. Generates a kid-friendly German sentence using the current word
2. Uses declined forms (dem, den, am) but NEVER reveals der/die/das
3. Optionally mentions capybaras for extra fun!
4. Caches sentences for performance
5. Fits the existing Roblox/Capybara theme

---

## 📋 Technical Approach

### Phase 1: Backend - AI Integration (2-3 hours)

#### Step 1.1: Check Spin AI Support

**Note**: Based on research, Spin's Serverless AI is available in Spin CLI v1.5+ but may require specific runtime support. Spin SDK 5.1.1 may not have direct LLM bindings in Rust yet.

**Action Required**: Verify current Spin version and LLM module availability

```bash
# Check Spin CLI version
spin --version

# Check if AI plugin is available
spin plugins list
```

**Decision Point**:
- **If Spin LLM available**: Use built-in Serverless AI (Priority A)
- **If NOT available**: Use HTTP outbound to external AI API (Priority B)

#### Step 1.2A: Implementation with Spin Serverless AI (Preferred)

```rust
// der-die-das-spin/src/lib.rs

use spin_sdk::llm::{infer_with_options, InferencingModel, InferencingParams};

fn generate_example_sentence(word: &str, genus: &str) -> Result<String, Error> {
    let prompt = format!(
        "Create a simple German sentence for a child learning German. \
        Use the word '{}' in a context that shows how it's used. \
        Important rules:
        1. Use ONLY declined forms like 'dem {}', 'den {}', 'am {}', 'beim {}'
        2. NEVER use 'der {}', 'die {}', or 'das {}' at the start
        3. Keep it under 12 words
        4. Use simple vocabulary for children
        5. If possible, mention a capybara (Capybara) to make it fun!
        6. Just return the sentence, nothing else.

        Example good sentences:
        - 'Ein Capybara sitzt neben dem Tisch.'
        - 'Ich sehe einen Vogel am Himmel.'
        - 'Das Kind spielt mit der Katze.'

        Now create a sentence with '{}':",
        word, word, word, word, word, word, word, word, word
    );

    let response = infer_with_options(
        InferencingModel::Llama2Chat,
        &prompt,
        InferencingParams {
            max_tokens: 50,
            repeat_penalty: 1.2,
            repeat_penalty_last_n_token_count: 64,
            temperature: 0.7,  // Balanced creativity
            top_k: 40,
            top_p: 0.9,
        },
    )?;

    // Clean up response
    let sentence = response.text.trim().to_string();

    // Validate: ensure no nominative articles at start
    if sentence.starts_with("Der ") || sentence.starts_with("Die ") || sentence.starts_with("Das ") {
        return Err(anyhow::anyhow!("AI revealed the article!"));
    }

    Ok(sentence)
}
```

**Update spin.toml**:
```toml
[component.der-die-das-api]
source = "target/wasm32-wasip1/release/der_die_das.wasm"
allowed_outbound_hosts = []
sqlite_databases = ["default"]
ai_models = ["llama2-chat"]  # ← Add this line
```

#### Step 1.2B: Implementation with External AI API (Fallback)

```rust
// If Spin LLM not available, use OpenAI or other API

use spin_sdk::http;

async fn generate_example_sentence_external(word: &str, genus: &str) -> Result<String, Error> {
    let api_key = spin_sdk::variables::get("openai_api_key")?;

    let request_body = serde_json::json!({
        "model": "gpt-3.5-turbo",
        "messages": [{
            "role": "system",
            "content": "You are a German teacher for children. Create simple example sentences."
        }, {
            "role": "user",
            "content": format!(
                "Create a simple German sentence using '{}'. Use declined forms (dem, den, am) but never der/die/das at the start. Max 12 words. Mention a capybara if possible!",
                word
            )
        }],
        "max_tokens": 50,
        "temperature": 0.7
    });

    let response = http::send(
        http::Request::builder()
            .method("POST")
            .uri("https://api.openai.com/v1/chat/completions")
            .header("Authorization", format!("Bearer {}", api_key))
            .header("Content-Type", "application/json")
            .body(serde_json::to_vec(&request_body)?)?
    ).await?;

    if !response.status().is_success() {
        return Err(anyhow::anyhow!("API request failed"));
    }

    let result: serde_json::Value = serde_json::from_slice(response.body())?;
    let sentence = result["choices"][0]["message"]["content"]
        .as_str()
        .ok_or_else(|| anyhow::anyhow!("No response"))?
        .trim()
        .to_string();

    Ok(sentence)
}
```

**Update spin.toml** (for external API):
```toml
[variables]
openai_api_key = { required = false, secret = true }

[component.der-die-das-api]
source = "target/wasm32-wasip1/release/der_die_das.wasm"
allowed_outbound_hosts = ["https://api.openai.com"]
sqlite_databases = ["default"]
variables = ["openai_api_key"]
```

#### Step 1.3: Add REST API Endpoint

```rust
// Add to router in lib.rs

use spin_sdk::http::{Router, Request, Response};

fn handle_request(req: Request) -> anyhow::Result<Response> {
    let mut router = Router::new();

    // Existing routes...
    router.get("/api/entry.json", api::handle_entry);
    router.post("/api/session/create", api::handle_session_create);

    // New route for example sentences
    router.get("/api/sentence/:word", api::handle_generate_sentence);

    router.handle(req)
}

// In your api module
pub fn handle_generate_sentence(req: Request, params: Params) -> anyhow::Result<Response> {
    let word = params.get("word").ok_or_else(|| anyhow::anyhow!("Missing word"))?;

    // Check cache first (see Phase 2)
    // If not in cache, generate with AI
    // Store in cache
    // Return response

    let sentence = generate_example_sentence(word, "")?;

    let response = serde_json::json!({
        "word": word,
        "sentence": sentence,
        "cached": false
    });

    Ok(http::Response::builder()
        .status(200)
        .header("Content-Type", "application/json")
        .body(serde_json::to_vec(&response)?)?)
}
```

---

### Phase 2: Backend - Caching (1-2 hours)

#### Step 2.1: Add Key-Value Storage

```rust
use spin_sdk::key_value::Store;
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Debug)]
struct CachedSentence {
    word: String,
    sentences: Vec<String>,  // Store multiple variations
    created_at: i64,
}

fn get_cached_sentence(word: &str) -> Result<Option<String>, Error> {
    let store = Store::open_default()?;
    let key = format!("sentence:{}", word.to_lowercase());

    if let Ok(Some(data)) = store.get(&key) {
        let cached: CachedSentence = serde_json::from_slice(&data)?;

        // Check if cache is still valid (7 days)
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)?
            .as_secs() as i64;

        if now - cached.created_at < 604800 {  // 7 days
            // Return random sentence from cache
            let idx = (now % cached.sentences.len() as i64) as usize;
            return Ok(Some(cached.sentences[idx].clone()));
        }
    }

    Ok(None)
}

fn cache_sentence(word: &str, sentence: String) -> Result<(), Error> {
    let store = Store::open_default()?;
    let key = format!("sentence:{}", word.to_lowercase());

    let mut cached = if let Ok(Some(data)) = store.get(&key) {
        serde_json::from_slice(&data)?
    } else {
        CachedSentence {
            word: word.to_string(),
            sentences: vec![],
            created_at: std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)?
                .as_secs() as i64,
        }
    };

    // Add new sentence if not already present
    if !cached.sentences.contains(&sentence) && cached.sentences.len() < 5 {
        cached.sentences.push(sentence);
    }

    store.set(&key, &serde_json::to_vec(&cached)?)?;
    Ok(())
}
```

**Update spin.toml**:
```toml
[component.der-die-das-api]
source = "target/wasm32-wasip1/release/der_die_das.wasm"
allowed_outbound_hosts = []
sqlite_databases = ["default"]
ai_models = ["llama2-chat"]
key_value_stores = ["default"]  # ← Add this line
```

#### Step 2.2: Update API Handler with Caching

```rust
pub fn handle_generate_sentence(req: Request, params: Params) -> anyhow::Result<Response> {
    let word = params.get("word").ok_or_else(|| anyhow::anyhow!("Missing word"))?;

    // Try cache first
    let (sentence, from_cache) = if let Some(cached) = get_cached_sentence(word)? {
        (cached, true)
    } else {
        // Generate new sentence
        let new_sentence = generate_example_sentence(word, "")?;

        // Cache it
        cache_sentence(word, new_sentence.clone())?;

        (new_sentence, false)
    };

    let response = serde_json::json!({
        "word": word,
        "sentence": sentence,
        "cached": from_cache
    });

    Ok(http::Response::builder()
        .status(200)
        .header("Content-Type", "application/json")
        .body(serde_json::to_vec(&response)?)?)
}
```

---

### Phase 3: Frontend - UI Integration (2-3 hours)

#### Step 3.1: Add HTML Button

```html
<!-- In der-die-das-spin/static/index.html -->

<div class="word-display">
    <div class="article-container">
        <span id="genus" class="genus" hidden></span>
        <span id="nominativ_singular" class="word"></span>
    </div>

    <!-- Add sentence display area -->
    <div id="exampleSentenceContainer" class="sentence-container hidden">
        <div class="capybara-speech-bubble">
            <span class="speech-header">🦫 Capybara sagt:</span>
            <p id="exampleSentence" class="sentence-text"></p>
            <div class="speech-bubble-tail"></div>
        </div>
    </div>

    <!-- Add example button -->
    <button id="exampleButton" class="btn-example" onclick="showExampleSentence()">
        🦫 Beispiel Satz
    </button>
</div>
```

#### Step 3.2: Add CSS Styling

```css
/* In der-die-das-spin/static/style.css */

.btn-example {
    background: linear-gradient(145deg, #6BCF7F, #4CAF50);
    color: white;
    border: 4px solid #2E7D32;
    padding: 12px 24px;
    font-size: 18px;
    font-family: 'Comic Sans MS', cursive;
    border-radius: 15px;
    cursor: pointer;
    box-shadow: 0 6px 0 #1B5E20, 0 8px 15px rgba(0, 0, 0, 0.3);
    transition: all 0.2s;
    margin: 15px 5px;
}

.btn-example:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 0 #1B5E20, 0 10px 20px rgba(0, 0, 0, 0.4);
}

.btn-example:active {
    transform: translateY(3px);
    box-shadow: 0 3px 0 #1B5E20, 0 4px 8px rgba(0, 0, 0, 0.3);
}

.btn-example:disabled {
    background: #ccc;
    border-color: #999;
    box-shadow: 0 4px 0 #888;
    cursor: not-allowed;
}

.sentence-container {
    margin: 20px auto;
    max-width: 500px;
}

.sentence-container.hidden {
    display: none;
}

.capybara-speech-bubble {
    background: linear-gradient(145deg, #FFF9E6, #FFFACD);
    border: 4px solid #8B4513;
    border-radius: 20px;
    padding: 20px;
    position: relative;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    animation: bounceIn 0.5s ease-out;
}

.speech-header {
    font-size: 16px;
    font-weight: bold;
    color: #8B4513;
    font-family: 'Comic Sans MS', cursive;
    display: block;
    margin-bottom: 10px;
}

.sentence-text {
    font-size: 20px;
    color: #333;
    line-height: 1.6;
    font-family: 'Comic Sans MS', cursive;
    margin: 0;
}

.speech-bubble-tail {
    position: absolute;
    bottom: -15px;
    left: 50px;
    width: 0;
    height: 0;
    border-left: 15px solid transparent;
    border-right: 15px solid transparent;
    border-top: 15px solid #8B4513;
}

.speech-bubble-tail::after {
    content: '';
    position: absolute;
    bottom: 2px;
    left: -12px;
    width: 0;
    height: 0;
    border-left: 12px solid transparent;
    border-right: 12px solid transparent;
    border-top: 12px solid #FFF9E6;
}

@keyframes bounceIn {
    0% {
        opacity: 0;
        transform: scale(0.3);
    }
    50% {
        transform: scale(1.05);
    }
    70% {
        transform: scale(0.9);
    }
    100% {
        opacity: 1;
        transform: scale(1);
    }
}

.loading-capybara {
    text-align: center;
    padding: 20px;
    font-size: 48px;
    animation: wiggle 1s ease-in-out infinite;
}

@keyframes wiggle {
    0%, 100% { transform: rotate(-5deg); }
    50% { transform: rotate(5deg); }
}
```

#### Step 3.3: Add JavaScript Logic

```javascript
// In der-die-das-spin/static/script.js

async function showExampleSentence() {
    const word = gameState.currentWord?.nominativ_singular;
    if (!word) {
        showError('Kein Wort ausgewählt!');
        return;
    }

    const container = document.getElementById('exampleSentenceContainer');
    const sentenceEl = document.getElementById('exampleSentence');
    const button = document.getElementById('exampleButton');

    // Disable button and show loading
    button.disabled = true;
    button.textContent = '🦫 Denkt nach...';
    sentenceEl.innerHTML = '<div class="loading-capybara">🦫</div>';
    container.classList.remove('hidden');

    try {
        const response = await fetch(`/api/sentence/${encodeURIComponent(word)}`);

        if (!response.ok) {
            throw new Error('Fehler beim Laden des Satzes');
        }

        const data = await response.json();

        // Animate text reveal
        sentenceEl.textContent = data.sentence;

        // Show cache indicator (optional, for debugging)
        if (data.cached) {
            console.log('Sentence from cache ✓');
        }

        // Re-enable button with new text
        button.textContent = '🦫 Noch ein Beispiel';
        button.disabled = false;

    } catch (error) {
        console.error('Error loading sentence:', error);
        sentenceEl.textContent = 'Ups! Der Capybara konnte keinen Satz finden. 😞';
        button.textContent = '🦫 Nochmal versuchen';
        button.disabled = false;
    }
}

// Hide sentence when moving to next word
function loadJSON() {
    // ... existing code ...

    // Hide example sentence
    document.getElementById('exampleSentenceContainer').classList.add('hidden');
    document.getElementById('exampleButton').textContent = '🦫 Beispiel Satz';

    // ... rest of existing code ...
}
```

---

### Phase 4: Testing & Quality Assurance (1-2 hours)

#### Step 4.1: Manual Testing Checklist

- [ ] Test with 20+ different German nouns
- [ ] Verify NO nominative articles (der/die/das) at sentence start
- [ ] Check sentence quality and kid-friendliness
- [ ] Test caching (click twice, verify second is faster)
- [ ] Test error handling (network errors, AI failures)
- [ ] Verify button states (enabled/disabled/loading)
- [ ] Test on mobile devices
- [ ] Test in all 4 game modes
- [ ] Check with long words (Donaudampfschifffahrtsgesellschaft)
- [ ] Verify capybara mentions appear occasionally

#### Step 4.2: Automated Tests

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_prompt_generation() {
        let prompt = create_prompt("Tisch", "m");
        assert!(prompt.contains("Tisch"));
        assert!(prompt.contains("dem Tisch"));
    }

    #[test]
    fn test_article_detection() {
        assert!(starts_with_article("Der Tisch ist groß."));
        assert!(starts_with_article("Die Katze schläft."));
        assert!(starts_with_article("Das Haus ist alt."));
        assert!(!starts_with_article("Ein Capybara sitzt am Tisch."));
    }

    #[test]
    fn test_cache_key_generation() {
        let key = cache_key("Tisch");
        assert_eq!(key, "sentence:tisch");
    }
}
```

#### Step 4.3: Performance Testing

```bash
# Test cache performance
curl http://localhost:3000/api/sentence/Tisch  # ~500-2000ms (AI)
curl http://localhost:3000/api/sentence/Tisch  # <50ms (cached)

# Test with Apache Bench
ab -n 100 -c 10 http://localhost:3000/api/sentence/Tisch
```

---

### Phase 5: Documentation & Release (30 mins)

#### Step 5.1: Update Documentation

**Add to CAPYBARA_THEME.md**:
```markdown
### 🤖 AI Example Sentences

- **🦫 Beispiel Satz Button** - Generate contextual sentences
- **Smart AI** - Never reveals der/die/das
- **Kid-Friendly** - Simple, fun sentences
- **Capybara Mentions** - Sometimes capybaras appear in sentences!
- **Fast Caching** - Instant responses for popular words
```

**Add to QUICKSTART.md**:
```markdown
### 🤖 Example Sentences (NEW!)

Click "🦫 Beispiel Satz" to see how the word is used in context!
- Learn through examples
- AI-generated sentences
- No spoilers - der/die/das is hidden!
```

**Add to README.md**:
```markdown
### 🤖 NEW: AI-Powered Example Sentences
- Click "🦫 Beispiel Satz" for contextual examples
- Powered by Spin Serverless AI
- Smart caching for fast responses
- Kid-friendly content
```

#### Step 5.2: Update CHANGELOG.md

```markdown
## [0.2.0] - 2025-11-XX

### Added
- 🤖 **AI-Powered Example Sentences**
  - New "🦫 Beispiel Satz" button on word display
  - Generates contextual German sentences using Spin Serverless AI
  - Smart caching with Key-Value storage
  - Never reveals der/die/das articles
  - Kid-friendly content with occasional capybara mentions
  - Animated speech bubble display
  - Loading states and error handling

### Technical
- Integrated Spin Serverless AI (Llama2-chat model)
- Added Key-Value storage for sentence caching
- New API endpoint: GET /api/sentence/:word
- Prompt engineering for educational content
- Cache TTL: 7 days, up to 5 variations per word
```

---

## 🚀 Deployment Checklist

### Pre-deployment
- [ ] All tests pass
- [ ] Manual QA complete
- [ ] Documentation updated
- [ ] Performance benchmarks met
- [ ] Error handling verified

### Deployment Steps
```bash
# 1. Build
cargo build --target wasm32-wasip1 --release
cd der-die-das-spin && spin build

# 2. Test locally
spin up
# Manual testing...

# 3. Commit changes
git add .
git commit -m "feat: Add AI-powered example sentence generation 🤖🦫"

# 4. Push and deploy
git push origin feature/ai-sentences
# Create PR and merge
# Tag release: v0.2.0
```

### Post-deployment
- [ ] Monitor AI response times
- [ ] Check cache hit rates
- [ ] Gather user feedback
- [ ] Monitor error rates
- [ ] Track feature usage

---

## 📊 Success Metrics

### Week 1
- Feature completion: 100%
- Cache hit rate: >60%
- AI response time (p95): <3s
- Error rate: <1%

### Week 2-4
- User adoption: >40% click "Beispiel Satz"
- Average sentences per session: >3
- User feedback score: >4/5
- Cache hit rate: >75%

---

## 🐛 Known Limitations & Future Improvements

### Current Limitations
1. **AI Model**: Llama2-chat may not always produce perfect German
2. **Response Time**: First request takes 500ms-2s (acceptable for educational use)
3. **Offline Mode**: Requires AI model to be loaded
4. **Content Filtering**: Limited validation of AI output

### Future Enhancements (v0.3.0+)
- [ ] Multiple AI models (fallback to better model if available)
- [ ] Pre-generated sentence database for most common words
- [ ] User feedback on sentence quality
- [ ] Sentence difficulty levels
- [ ] Text-to-speech for pronunciation
- [ ] Translation toggle (German ↔ English)
- [ ] Save favorite sentences

---

## 💰 Cost Analysis

### Local Development
- **Cost**: $0 (runs locally in Spin)
- **Resources**: ~50MB RAM for AI model

### Fermyon Cloud
- **Cost**: Included in free tier
- **Limitations**: Check Fermyon Cloud quotas

### External AI (if needed)
- **OpenAI GPT-3.5**: ~$0.002 per request
- **Estimated monthly**: 10,000 requests = $20
- **With caching**: 75% cache hit = $5/month

---

## 🦫 Final Notes

This feature will make the Der Die Das game significantly more educational while keeping it fun! Kids will love seeing capybaras in the example sentences, and the contextual learning will help them understand how articles work in real German sentences.

**Remember**: The goal is education through fun, so prioritize:
1. **Quality** - Sentences must be correct and helpful
2. **Safety** - Kid-friendly content only
3. **Performance** - Fast responses with caching
4. **Fun** - Capybaras and playful language!

**Ready to build?** Let's make German learning even more fun with AI! 🤖🦫✨
