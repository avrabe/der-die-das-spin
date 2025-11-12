# Cleanup and Implementation Roadmap

## Problem Analysis

### Duplication Found

**TWO PARSERS doing the same job:**
1. **Rust Parser** (Original - WORKING)
   - Location: `dewiktionary/`, `dewiktionary-importer-cli/`
   - Status: ✅ Works - extracted 33,280 words
   - Limitation: Only extracts basic data (word + genus)
   - Output: `derdiedas` table (old schema)

2. **Python Parser** (Added later - BROKEN)
   - Location: `tools/wiktionary_parser.py`, `tools/build_database.py`
   - Status: ❌ Broken - extracted 0 words
   - Purpose: Extract extended data (plurals, syllables, categories, compounds)
   - Output: `words` table (new schema)
   - Added in: commit 748e425 "educational framework for 4th graders"

**TWO DATABASE SCHEMAS:**
- Old: `derdiedas` table - genus only (m/f/n)
- New: `words` table - full grammar (plurals, syllables, categories, etc.)
- Current code supports BOTH with fallback logic (lib.rs:124-157)

**ROOT CAUSE:**
When expanding from 4 basic game modes to 10 advanced game modes, someone added a Python parser to extract extended grammatical data rather than enhancing the existing working Rust parser.

---

## Current Status

### ✅ Working Features (Deployed)
1. **Übungs-Modus** (Practice Mode) - Learn at your own pace
2. **Zeit-Challenge** (Timed Challenge) - Configurable by time/points/questions
3. **Multiplayer Erstellen** (Create Multiplayer) - Kid-friendly session IDs
4. **Multiplayer Beitreten** (Join Multiplayer)
5. **LLM Sentence Generation** - Fixed timeout issue (1 sentence per request)
6. **Database**: 33,280 German nouns working in production

### 📋 Designed But Not Implemented
10 additional game modes documented in GAME_DESIGN.md:
1. Classic Artikel-Duell (enhanced with difficulty)
2. Plural-Battle 🔢
3. Zusammensetz-Rennen 🧩
4. Wortfamilien-Sprint 👨‍👩‍👧‍👦
5. Artikel-Änderungs-Quiz 📝
6. Gegenteil-Duell ↔️
7. Kategorie-Blitz ⚡
8. Reime-Schlacht 🎵
9. Silben-Puzzle 🧩
10. Satzbau-Express 🚂

---

## Cleanup Plan

### Phase 1: Parser Consolidation

**DECISION: Enhance Rust parser, remove Python parser**

Why Rust?
- Already working (33,280 words extracted)
- Native performance
- Single language for entire project
- Better long-term maintenance

**Files to KEEP:**
- `dewiktionary/` - Core parser library ✅
- `dewiktionary-diesel/` - Database ORM ✅
- `dewiktionary-importer-cli/` - CLI tool ✅
- `tools/create_sample_db.py` - Useful for testing ✅

**Files to REMOVE:**
- `tools/wiktionary_parser.py` - Broken Python parser ❌
- `tools/build_database.py` - Wrapper for broken parser ❌

**Files to UPDATE:**
- `DATABASE_SETUP.md` - Update with Rust parser instructions
- `lib.rs` - Simplify to single schema (migrate derdiedas→words)
- `IMPROVEMENTS.md` - Update implementation status

### Phase 2: Database Schema Unification

**Migrate from dual schema to single extended schema:**

```sql
-- Target unified schema
CREATE TABLE words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT NOT NULL UNIQUE,
    article TEXT NOT NULL,           -- der/die/das
    plural TEXT,                     -- plural form
    gen_singular TEXT,               -- genitive
    dat_singular TEXT,               -- dative
    akk_singular TEXT,               -- accusative
    gen_plural TEXT,
    dat_plural TEXT,
    akk_plural TEXT,
    syllables TEXT,                  -- "Hund" or "Schmet-ter-ling"
    syllable_count INTEGER DEFAULT 1,
    category TEXT,                   -- Tier, Essen, Familie
    is_compound BOOLEAN DEFAULT 0,
    compound_parts TEXT,             -- JSON: ["Fahr", "Rad"]
    difficulty INTEGER DEFAULT 1,    -- 1-5 scale
    frequency_rank INTEGER
);

-- Legacy compatibility view
CREATE VIEW derdiedas AS
SELECT
    word as nominativ_singular,
    CASE article
        WHEN 'der' THEN 'm'
        WHEN 'die' THEN 'f'
        WHEN 'das' THEN 'n'
    END as genus
FROM words;
```

---

## Implementation Roadmap

### Week 1: Parser Enhancement & Database Generation

**Tasks:**
1. Enhance `dewiktionary/src/parser.rs` to extract:
   - ✅ nominativ_singular (already done)
   - ✅ genus (already done)
   - 🆕 plural forms
   - 🆕 syllable breaks
   - 🆕 syllable count
   - 🆕 semantic category
   - 🆕 compound detection
   - 🆕 compound parts
   - 🆕 difficulty level
   - 🆕 frequency rank
   - 🆕 declension tables (gen/dat/akk)

2. Update database schema in `dewiktionary-diesel/`
3. Regenerate database with extended data
4. Test locally with sample data
5. Deploy to Fermyon Cloud
6. Remove Python parser files
7. Update documentation

**Success Criteria:**
- Single working Rust parser
- Database with 30,000+ words with extended data
- All existing game modes still work
- Ready for new game mode implementation

### Week 2: First Game Mode - Silben-Puzzle 🧩

**Why first:** Uses syllables data, simple UI, educational value

**Frontend (static/index.html + script.js):**
```javascript
// Game screen showing word with syllable gaps
// Player drags syllable pieces to correct positions
// Example: [Schmet] [ter] [ling]
```

**Backend (lib.rs):**
```rust
// New endpoint: GET /api/syllable/:word
// Returns: {"word": "Schmetterling", "syllables": ["Schmet", "ter", "ling"]}
```

**Multiplayer:**
- Race mode: Who solves 10 words faster
- Score based on speed and accuracy

### Week 3: Second Game Mode - Kategorie-Blitz ⚡

**Why second:** Uses category data, builds vocabulary

**Frontend:**
```javascript
// Show word, present 3-4 category options
// Example: "Hund" → Tier, Essen, Möbel?
// Timed challenge: categorize 20 words
```

**Backend:**
```rust
// New endpoint: GET /api/category-quiz
// Returns random words with categories
```

**Multiplayer:**
- Who categorizes more words correctly in 60 seconds

### Week 4: Third Game Mode - Plural-Battle 🔢

**Why third:** Uses plural data, critical grammar skill

**Frontend:**
```javascript
// Show singular word
// Player types or selects plural form
// Example: "Hund" → ?
// Options: die Hunde, die Hunds, die Hunden
```

**Backend:**
```rust
// New endpoint: GET /api/plural/:word
// Returns: {"singular": "Hund", "plural": "Hunde", "article": "die"}
```

**Multiplayer:**
- First to answer correctly wins point
- 10 rounds per game

### Week 5-8: Next 4 Game Modes

4. **Zusammensetz-Rennen 🧩** - Compound word formation
5. **Artikel-Änderungs-Quiz 📝** - Declension practice
6. **Classic Enhanced** - Difficulty levels + streaks
7. **Gegenteil-Duell ↔️** - Antonyms (needs antonym table)

### Week 9-12: Final 3 Game Modes

8. **Wortfamilien-Sprint 👨‍👩‍👧‍👦** - Word families (needs algorithm)
9. **Reime-Schlacht 🎵** - Rhymes (needs phonetic data)
10. **Satzbau-Express 🚂** - Sentence building (needs templates)

---

## Technical Details

### Rust Parser Enhancements Needed

**Current Wiktionary XML Structure:**
```xml
<page>
  <title>Hund</title>
  <text>
    {{Deutsch Substantiv Übersicht
    |Genus=m
    |Nominativ Singular=Hund
    |Nominativ Plural=Hunde
    |Genitiv Singular=Hundes
    |Genitiv Plural=Hunde
    |Dativ Singular=Hund
    |Dativ Plural=Hunden
    |Akkusativ Singular=Hund
    |Akkusativ Plural=Hunde
    }}

    {{Worttrennung}}
    :Hund

    {{Beispiele}}
    :[1] Der [[Hund]] bellt.

    [[Kategorie:Tier]]
  </text>
</page>
```

**Parser Strategy:**
1. Use nom combinators to parse template syntax
2. Extract key-value pairs from templates
3. Parse categories from bottom of page
4. Compute compound detection (hyphen or length heuristic)
5. Estimate difficulty from word length + frequency

### Database Migration Strategy

**Step 1: Create words table with extended schema**
**Step 2: Migrate existing 33,280 words from derdiedas**
**Step 3: Run enhanced parser to fill missing columns**
**Step 4: Create compatibility view for old code**
**Step 5: Update lib.rs to use words table primarily**

---

## Success Metrics

### Phase 1 (Cleanup) Success:
- ✅ Single Rust parser working
- ✅ No Python parser files
- ✅ Single database schema
- ✅ All existing features still work
- ✅ 30,000+ words with extended data

### Phase 2 (First 3 Modes) Success:
- ✅ 3 new game modes working
- ✅ Multiplayer support for new modes
- ✅ Positive feedback from 4th graders
- ✅ No performance regressions

### Phase 3 (All 10 Modes) Success:
- ✅ All 10 game modes implemented
- ✅ Full curriculum coverage
- ✅ 50+ active users (kids + teachers)
- ✅ Average session time > 10 minutes

---

## Questions for Discussion

1. **Timeline:** Is 12-week roadmap realistic? Should we prioritize differently?
2. **Parser:** Should we enhance Rust parser or fix Python parser instead?
3. **Testing:** How can we get feedback from actual 4th graders?
4. **Deployment:** Should we stage new modes on separate URL first?
5. **Database:** Keep both schemas during transition or migrate all at once?

---

## Next Immediate Steps

1. ✅ Document findings (this file)
2. Review and approve roadmap
3. Start Week 1: Parser enhancement
4. Create GitHub issues for each phase
5. Set up testing environment

---

Generated: 2025-11-12
Status: Proposal - Awaiting Approval
