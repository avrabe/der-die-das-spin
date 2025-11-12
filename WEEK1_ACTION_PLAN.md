# Week 1 Action Plan: Database Enhancement

## Current Situation

**DISCOVERY:** The Rust parser and database schema ALREADY support all declension forms!
- Parser extracts: nominativ/genitiv/dativ/akkusativ (singular + plural)
- Schema has columns for all these fields
- **BUT:** All 33,280 words have NULL values in these columns
- **ROOT CAUSE:** Mediawiki XML parser is broken (Issue #31)

## What's Actually Missing

Comparing to desired `words` schema:
- ✅ HAS: nominativ_singular, genus, all declension columns (but NULL)
- ❌ MISSING: syllables, syllable_count, category, is_compound, compound_parts, difficulty, frequency_rank

## Revised Strategy (Practical Approach)

Instead of fixing the broken XML parser, **enrich the existing 33,280 words** with computed/heuristic data:

### Step 1: Extend Schema (SQL Migration)
```sql
ALTER TABLE derdiedas ADD COLUMN syllables TEXT;
ALTER TABLE derdiedas ADD COLUMN syllable_count INTEGER DEFAULT 1;
ALTER TABLE derdiedas ADD COLUMN category TEXT;
ALTER TABLE derdiedas ADD COLUMN is_compound BOOLEAN DEFAULT 0;
ALTER TABLE derdiedas ADD COLUMN compound_parts TEXT;
ALTER TABLE derdiedas ADD COLUMN difficulty INTEGER DEFAULT 1;
ALTER TABLE derdiedas ADD COLUMN frequency_rank INTEGER;
```

### Step 2: Compute Missing Data (Python/Rust Script)

**Syllable Detection** (heuristic):
```python
def count_syllables(word):
    # German vowels indicate syllables
    vowels = 'aeiouäöüAEIOUÄÖÜ'
    diphthongs = ['ei', 'au', 'eu', 'äu', 'ie']

    # Remove diphthongs first
    for d in diphthongs:
        word = word.replace(d, 'X')

    # Count remaining vowels
    return sum(1 for char in word if char in vowels)
```

**Category Detection** (keyword matching):
```python
ANIMAL_KEYWORDS = ['hund', 'katze', 'vogel', 'fisch', 'tier', ...]
FOOD_KEYWORDS = ['brot', 'käse', 'obst', 'gemüse', ...]
FAMILY_KEYWORDS = ['mutter', 'vater', 'kind', 'bruder', ...]

def detect_category(word):
    word_lower = word.lower()
    if any(kw in word_lower for kw in ANIMAL_KEYWORDS):
        return 'Tier'
    elif any(kw in word_lower for kw in FOOD_KEYWORDS):
        return 'Essen'
    # ... etc
    return None  # unclassified
```

**Compound Detection** (simple):
```python
def detect_compound(word):
    # German compounds are often long
    if len(word) > 12:
        return True
    # Or contain capital letters mid-word (Roblox-style)
    if any(c.isupper() for c in word[1:]):
        return True
    return False
```

**Difficulty Calculation** (heuristic):
```python
def calculate_difficulty(word, syllables):
    # Base on length and syllable count
    length_score = len(word) / 4  # 1-5 scale
    syllable_score = syllables    # 1-5 scale
    return min(5, int((length_score + syllable_score) / 2))
```

**Frequency Rank** (external list or default):
```python
# Could use: https://github.com/hermitdave/FrequencyWords/tree/master/content/2018/de
# Or just estimate based on word length (shorter = more common)
def estimate_frequency(word):
    return len(word) * 100  # Lower = more frequent
```

### Step 3: Apply to Database

Create `tools/enrich_database.py`:
```python
import sqlite3

def enrich_database(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all words
    cursor.execute("SELECT nominativ_singular FROM derdiedas")
    words = cursor.fetchall()

    for (word,) in words:
        syllables = count_syllables(word)
        category = detect_category(word)
        is_compound = detect_compound(word)
        difficulty = calculate_difficulty(word, syllables)
        frequency = estimate_frequency(word)

        cursor.execute("""
            UPDATE derdiedas
            SET syllables = ?,
                syllable_count = ?,
                category = ?,
                is_compound = ?,
                difficulty = ?,
                frequency_rank = ?
            WHERE nominativ_singular = ?
        """, (word, syllables, category, is_compound,
              difficulty, frequency, word))

    conn.commit()
    conn.close()
```

## Implementation Timeline

**Day 1 (Today):**
- ✅ Create schema migration SQL
- ✅ Write enrichment script
- ✅ Test on sample_words.db (67 words)

**Day 2:**
- Apply to full database (33,280 words)
- Verify data quality
- Create statistics report

**Day 3:**
- Upload to Fermyon Cloud
- Test in production
- Update API to use new fields

**Day 4:**
- Remove Python parser files
- Update documentation
- Start implementing first game mode (Silben-Puzzle)

## Advantages of This Approach

1. **Fast:** No XML parsing needed, works with existing data
2. **Pragmatic:** Heuristics are good enough for educational games
3. **Incremental:** Can improve algorithms later
4. **Tested:** Sample DB already works this way

## Data Quality Expectations

- **Syllables:** 80-90% accurate (good enough for learning)
- **Categories:** 30-40% classified (enough to start)
- **Compounds:** 70-80% accurate (length-based heuristic)
- **Difficulty:** Reasonable approximation
- **Frequency:** Estimated, can replace with real data later

## Next Steps After This

Once we have enriched database:
1. Implement Silben-Puzzle game (uses syllables)
2. Implement Kategorie-Blitz game (uses categories)
3. Implement Plural-Battle game (database already has genus)
4. Continue with remaining game modes

## Decision Point

**Should we:**
A. ✅ Proceed with heuristic enrichment (fast, practical)
B. Fix XML parser first (slow, perfect data)

**Recommendation:** Option A - ship working games sooner, improve data quality later.

---
Status: Ready to implement
Estimated time: 1-2 days
Risk: Low
