# Der Die Das - Game Design for 4th Graders (NRW)

## Current Status
- Database: 33,279 words (many too advanced for 4th graders)
- Current game: Simple article guessing (Der/Die/Das)
- Focus: Multiplayer as primary mode

## Target Audience: 4th Grade (9-10 years old) in NRW
- Official Grundwortschatz NRW: 533 core words
- 145 concrete nouns with visual support
- Schools add 200-300 additional words
- Expected knowledge: Basic grammar, articles, word families, compounds, plurals

## New Game Modes (All Multiplayer-Focused)

### 1. **Classic Artikel-Duell** (Current Game Enhanced)
**What:** Two players race to identify correct articles
**Skills:** Gender recognition, vocabulary
**Improvements Needed:**
- Filter to age-appropriate words
- Add difficulty levels (easy/medium/hard based on word frequency)
- Visual hints (optional): Show category (animal, object, person)
- Streak bonuses

### 2. **Plural-Battle** 🔢
**What:** Players guess the correct plural form
**Skills:** Plural formation rules, irregular plurals
**Example:** Hund → ? (die Hunde)
**Database needs:** Add plural_form column
**Multiplayer:** First to answer correctly gets point

### 3. **Zusammensetz-Rennen** (Compound Word Race) 🧩
**What:** Given two words, combine them correctly with/without Fugen-S
**Skills:** Compound word formation
**Example:** Hund + Hütte → ? (Hundehütte)
**Database needs:** Store compound words and their components
**Multiplayer:** Fastest correct combination wins

### 4. **Wortfamilien-Sprint** (Word Family Sprint) 👨‍👩‍👧‍👦
**What:** Given a root word, find related words in the same family
**Skills:** Word relationships, morphology
**Example:** lauf → laufen, Lauf, Läufer, gelaufen
**Database needs:** Word family groupings
**Multiplayer:** Who finds more family members in 30 seconds

### 5. **Artikel-Änderungs-Quiz** (Article Declension Quiz) 📝
**What:** Change article based on case
**Skills:** Declension, grammatical cases
**Example:** "der Hund" → "mit ___ Hund" → "mit dem Hund"
**Database needs:** Add declension patterns
**Multiplayer:** Fastest correct declension wins

### 6. **Gegenteil-Duell** (Opposite Duel) ↔️
**What:** Find the opposite (antonym)
**Skills:** Vocabulary breadth, semantic relationships
**Example:** groß → ? (klein)
**Database needs:** Antonym pairs
**Multiplayer:** Race to find opposite

### 7. **Kategorie-Blitz** (Category Lightning) ⚡
**What:** Sort words into categories as fast as possible
**Skills:** Semantic classification, vocabulary
**Example:** Categories: Tiere, Möbel, Essen
**Multiplayer:** Who sorts 20 words faster

### 8. **Reime-Schlacht** (Rhyme Battle) 🎵
**What:** Find words that rhyme
**Skills:** Phonological awareness, vocabulary
**Example:** Haus → ? (Maus, Klaus, raus)
**Database needs:** Rhyme groups or phonetic endings
**Multiplayer:** First with 3 correct rhymes wins round

### 9. **Silben-Puzzle** (Syllable Puzzle) 🧩
**What:** Break words into syllables correctly
**Skills:** Syllabification, phonological awareness
**Example:** Schmet-ter-ling (3 syllables)
**Database needs:** Syllable count and breaks
**Multiplayer:** Most correct syllable breaks in 60 seconds

### 10. **Satzbau-Express** (Sentence Building Express) 🚂
**What:** Arrange shuffled words to form correct sentences
**Skills:** Syntax, word order
**Example:** [Hund, der, bellt, laut] → Der Hund bellt laut
**Database needs:** Template sentences
**Multiplayer:** First to build 5 correct sentences

## Database Schema Extensions

```sql
-- Extended main table
CREATE TABLE words (
    id INTEGER PRIMARY KEY,
    word TEXT NOT NULL,
    article TEXT NOT NULL, -- der/die/das
    plural TEXT, -- plural form
    syllables TEXT, -- Hund would be "Hund" (1), Schmetterling would be "Schmet-ter-ling"
    syllable_count INTEGER,
    difficulty INTEGER DEFAULT 1, -- 1-5, based on word frequency/grade level
    category TEXT, -- Tier, Pflanze, Möbel, Essen, etc.
    is_compound BOOLEAN DEFAULT 0,
    compound_parts TEXT, -- JSON array of parts
    frequency_rank INTEGER, -- 1-1000 for Grundwortschatz
    audio_path TEXT, -- path to pronunciation audio
    image_path TEXT -- path to visual representation
);

-- Word families
CREATE TABLE word_families (
    id INTEGER PRIMARY KEY,
    root_word TEXT NOT NULL,
    related_word_id INTEGER,
    relationship TEXT, -- verb_form, noun_form, adjective_form, etc.
    FOREIGN KEY (related_word_id) REFERENCES words(id)
);

-- Antonyms
CREATE TABLE antonyms (
    word1_id INTEGER,
    word2_id INTEGER,
    PRIMARY KEY (word1_id, word2_id),
    FOREIGN KEY (word1_id) REFERENCES words(id),
    FOREIGN KEY (word2_id) REFERENCES words(id)
);

-- Rhyme groups
CREATE TABLE rhyme_groups (
    id INTEGER PRIMARY KEY,
    ending TEXT NOT NULL, -- phonetic ending
    word_id INTEGER,
    FOREIGN KEY (word_id) REFERENCES words(id)
);

-- Declension patterns
CREATE TABLE declensions (
    word_id INTEGER,
    case_name TEXT, -- nominativ, genitiv, dativ, akkusativ
    article TEXT, -- der/des/dem/den, etc.
    form TEXT, -- declined form
    FOREIGN KEY (word_id) REFERENCES words(id)
);

-- Example sentences
CREATE TABLE example_sentences (
    id INTEGER PRIMARY KEY,
    word_id INTEGER,
    sentence TEXT NOT NULL,
    difficulty INTEGER DEFAULT 1,
    FOREIGN KEY (word_id) REFERENCES words(id)
);

-- Game sessions enhanced
CREATE TABLE game_sessions (
    session_id TEXT PRIMARY KEY,
    game_mode TEXT NOT NULL, -- artikel_duell, plural_battle, etc.
    player1_id TEXT NOT NULL,
    player2_id TEXT,
    player1_score INTEGER DEFAULT 0,
    player2_score INTEGER DEFAULT 0,
    current_round INTEGER DEFAULT 1,
    max_rounds INTEGER DEFAULT 10,
    difficulty INTEGER DEFAULT 1,
    status TEXT DEFAULT 'waiting', -- waiting, active, finished
    created_at INTEGER NOT NULL,
    started_at INTEGER,
    finished_at INTEGER
);

-- Round tracking
CREATE TABLE game_rounds (
    id INTEGER PRIMARY KEY,
    session_id TEXT NOT NULL,
    round_number INTEGER NOT NULL,
    word_id INTEGER NOT NULL,
    player1_answer TEXT,
    player2_answer TEXT,
    correct_answer TEXT,
    player1_correct BOOLEAN,
    player2_correct BOOLEAN,
    player1_time_ms INTEGER, -- response time in milliseconds
    player2_time_ms INTEGER,
    FOREIGN KEY (session_id) REFERENCES game_sessions(session_id),
    FOREIGN KEY (word_id) REFERENCES words(id)
);
```

## Implementation Priorities

### Phase 1: Foundation (Week 1)
1. ✅ Configurable timed mode (DONE)
2. ✅ Easter egg (DONE)
3. Download Wiktionary dump
4. Parse basic word info (article, plural, syllables)
5. Filter to age-appropriate words
6. Update database schema

### Phase 2: Enhanced Classic Mode (Week 2)
1. Add difficulty levels
2. Add category hints
3. Add streak tracking
4. Improve multiplayer synchronization

### Phase 3: New Games (Week 3-4)
1. Implement Plural-Battle
2. Implement Wortfamilien-Sprint
3. Implement Gegenteil-Duell
4. Add game selection screen

### Phase 4: Advanced Features (Week 5-6)
1. Add remaining games
2. Leaderboards
3. Achievement system
4. Progress tracking

## Wiktionary Parsing Strategy

### Download
- Use Wiktionary XML dump for German
- URL: https://dumps.wikimedia.org/dewiktionary/latest/dewiktionary-latest-pages-articles.xml.bz2

### Parsing Requirements
Extract from each German noun entry:
- Nominativ singular
- Article (der/die/das)
- Nominativ plural
- Genitiv singular/plural
- Dativ singular/plural
- Akkusativ singular/plural
- Syllable breaks
- Etymology (for compounds)
- Synonyms
- Antonyms
- Example sentences

### XML Structure (Wiktionary)
```xml
<page>
  <title>Hund</title>
  <ns>0</ns>
  <text>
    == Hund ({{Sprache|Deutsch}}) ==
    === {{Wortart|Substantiv|Deutsch}}, {{m}} ===
    {{Deutsch Substantiv Übersicht
    |Genus=m
    |Nominativ Singular=Hund
    |Nominativ Plural=Hunde
    |Genitiv Singular=Hundes
    |Genitiv Plural=Hunde
    ...
    }}
  </text>
</page>
```

## Age-Appropriate Word Filtering

### Include:
- Grundwortschatz NRW (533 words)
- Common animals, objects, food, family, school terms
- Frequency rank < 2000 in child-directed text
- No abstract philosophical/political terms
- No adult-only topics

### Exclude:
- Violence, sexuality, drugs
- Complex scientific terminology
- Rare/archaic words
- Words unlikely in child's environment

## Testing Strategy
1. Local testing with Spin framework
2. Test each game mode with 2 browsers
3. Performance testing (load times, response times)
4. Kid testing (if possible) for enjoyment
5. Curriculum alignment check

## Success Metrics
- Engagement: Average session length > 10 minutes
- Learning: Improvement in accuracy over time
- Fun: Return rate > 70%
- Educational: Alignment with NRW curriculum standards
