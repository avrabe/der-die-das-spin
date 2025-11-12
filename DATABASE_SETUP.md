# Database Setup Guide - Automated Wiktionary Build

## Complete Automated Process

This guide explains how to build a production-ready database from Wiktionary using the automated build script.

## Quick Start

### Option 1: Test Build (Recommended First! ⚡)

```bash
cd /home/user/der-die-das-spin

# Quick test with 500 words (~10 minutes)
python3 tools/build_database.py --test
```

### Option 2: Production Build (Full Database)

```bash
cd /home/user/der-die-das-spin

# Full build (~30-60 minutes)
python3 tools/build_database.py
```

### Option 3: Use Sample Database (Immediate)

```bash
cd /home/user/der-die-das-spin/der-die-das-spin
cp ../sample_words.db words.db
```

## What the Build Script Does

The `build_database.py` script automates everything:

1. **Downloads** Wiktionary XML dump (~500 MB)
2. **Verifies** MD5 checksum
3. **Parses** XML with age-appropriate filtering
4. **Extracts** complete grammatical information
5. **Creates** SQLite database with extended schema
6. **Backs up** old database automatically
7. **Integrates** into Spin application
8. **Tests** database integrity
9. **Generates** comprehensive statistics report

## Build Options

```bash
# Quick test (500 words, ~10 min)
python3 tools/build_database.py --test

# Custom limit (e.g., 2000 words, ~25 min)
python3 tools/build_database.py --limit 2000

# Skip download if you already have the dump
python3 tools/build_database.py --skip-download

# Full production build
python3 tools/build_database.py

# Get help
python3 tools/build_database.py --help
```

## Expected Output

```
📋 [2025-11-12 12:00:00] AUTOMATED WIKTIONARY DATABASE BUILDER
⬇️  [2025-11-12 12:00:05] Starting Wiktionary dump download...
⬇️  [2025-11-12 12:00:10] Downloading MD5 checksum...
⬇️  [2025-11-12 12:00:15] Downloading Wiktionary dump (this may take 10-30 minutes)...
✅ [2025-11-12 12:08:23] Download complete! Size: 485.23 MB
✅ [2025-11-12 12:08:45] MD5 checksum verified ✓
🔍 [2025-11-12 12:08:50] Starting Wiktionary parsing...
✅ [2025-11-12 12:32:15] Parsing complete!
✅ [2025-11-12 12:32:15] Words extracted: 1847
📋 [2025-11-12 12:32:15] Database size: 5.23 MB
🔨 [2025-11-12 12:32:20] Integrating database into application...
✅ [2025-11-12 12:32:25] Database copied to: words.db
🧪 [2025-11-12 12:32:30] Running database tests...
🧪 [2025-11-12 12:32:35] ✓ Table 'words' exists
🧪 [2025-11-12 12:32:35] ✓ Table 'example_sentences' exists
🧪 [2025-11-12 12:32:35] ✓ Table 'derdiedas' exists
✅ [2025-11-12 12:32:40] All tests passed!

===========================================================================
DATABASE STATISTICS
---------------------------------------------------------------------------
  Total words: 1,847

  Articles:
    die: 897 (48.6%)
    der: 658 (35.6%)
    das: 292 (15.8%)

  Top Categories:
    Tier: 156
    Essen: 124
    Natur: 98
    Familie: 87
    Schule: 76

  Words with plural: 1,756 (95.1%)
  Words with syllables: 1,498 (81.1%)
  Compound words: 234 (12.7%)

  Example sentences: 892

  Difficulty levels:
    Level 1: 743 (40.2%)
    Level 2: 521 (28.2%)
    Level 3: 583 (31.6%)

===========================================================================
DATABASE READY FOR USE!
===========================================================================

Database location: der-die-das-spin/words.db

Next steps:
  1. Test with: cd der-die-das-spin && spin build && spin up
  2. Open http://localhost:3000 in browser
  3. Try all game modes with age-appropriate content

✅ Build completed successfully! 🎉
```

## Time Estimates

| Words | Download  | Parse     | Total      |
|-------|-----------|-----------|------------|
| 500   | 5-10 min  | 2-3 min   | ~10 min    |
| 1000  | 5-10 min  | 5-8 min   | ~15 min    |
| 2000  | 5-10 min  | 10-15 min | ~25 min    |
| Full  | 5-10 min  | 20-45 min | 30-60 min  |

*Note: Download is one-time. Use `--skip-download` for subsequent builds.*

## Files Created

```
der-die-das-spin/
├── data/                                    # Build directory
│   ├── dewiktionary-latest-pages-articles.xml.bz2
│   ├── words.db                            # Parsed database
│   ├── words.json                          # JSON export
│   └── build_report_20251112_120000.txt   # Statistics
│
├── der-die-das-spin/
│   ├── words.db                            # ✨ Production database
│   ├── words.json                          # Reference
│   └── result.sql.backup_20251112          # Old DB backup
```

## Database Schema

The new database has an extended schema:

```sql
-- Main words table
CREATE TABLE words (
    id INTEGER PRIMARY KEY,
    word TEXT NOT NULL,              -- "Hund"
    article TEXT NOT NULL,            -- "der", "die", "das"
    plural TEXT,                      -- "Hunde"
    syllables TEXT,                   -- "Hund" or "Schmet-ter-ling"
    syllable_count INTEGER,           -- 1 or 3
    category TEXT,                    -- "Tier", "Essen", "Familie", etc.
    is_compound BOOLEAN,              -- true for "Fahrrad"
    compound_parts TEXT,              -- JSON: ["Fahr", "Rad"]
    difficulty INTEGER,               -- 1-5 scale
    -- Declension columns
    gen_singular TEXT,                -- Genitive singular
    dat_singular TEXT,                -- Dative singular
    akk_singular TEXT,                -- Accusative singular
    gen_plural TEXT,                  -- Genitive plural
    dat_plural TEXT,                  -- Dative plural
    akk_plural TEXT                   -- Accusative plural
);

-- Example sentences
CREATE TABLE example_sentences (
    id INTEGER PRIMARY KEY,
    word_id INTEGER,
    sentence TEXT NOT NULL,
    difficulty INTEGER,
    FOREIGN KEY (word_id) REFERENCES words(id)
);

-- Legacy table (backward compatible)
CREATE TABLE derdiedas (
    nominativ_singular TEXT PRIMARY KEY,
    genus TEXT NOT NULL              -- "m", "f", "n"
);
```

## Age-Appropriate Filtering

The parser automatically filters out:

❌ **Excluded Content:**
- Violence, weapons, war terms
- Sexual content
- Drugs, alcohol
- Adult-only topics
- Complex scientific/philosophical terms
- Words longer than 20 characters
- Overly complex compounds

✅ **Included Content:**
- Animals (Tiere)
- Food (Essen)
- Family (Familie)
- School (Schule)
- Body parts (Körper)
- Clothing (Kleidung)
- House/Furniture (Haus/Möbel)
- Nature (Natur)
- Vehicles (Fahrzeuge)
- Colors (Farben)
- Time (Zeit)
- Common everyday objects

## Testing Your Database

### 1. Quick SQLite Check

```bash
sqlite3 der-die-das-spin/words.db

-- Total words
SELECT COUNT(*) FROM words;

-- Sample words
SELECT word, article, plural, category
FROM words
LIMIT 10;

-- Category breakdown
SELECT category, COUNT(*) as count
FROM words
WHERE category IS NOT NULL
GROUP BY category
ORDER BY count DESC;

-- Check for inappropriate content
SELECT word FROM words
WHERE word LIKE '%sex%' OR word LIKE '%gewalt%'
LIMIT 10;

.quit
```

### 2. Test Application

```bash
cd der-die-das-spin

# Build and run
spin build && spin up

# In another terminal, test API
curl http://localhost:3000/api/entry.json

# Open in browser
open http://localhost:3000
```

### 3. Test Game Modes

- ✅ Practice Mode - unlimited play
- ✅ Timed Challenge - configurable end conditions
- ✅ Multiplayer - create and join sessions
- ✅ Example sentences - from database

## Troubleshooting

### Download Fails

```bash
# Check connection
ping dumps.wikimedia.org

# Manual download
wget https://dumps.wikimedia.org/dewiktionary/latest/dewiktionary-latest-pages-articles.xml.bz2 \
  -O data/dewiktionary-latest-pages-articles.xml.bz2

# Then skip download
python3 tools/build_database.py --skip-download
```

### Parsing is Slow

This is normal! Full parsing takes 20-45 minutes.

**Solutions:**
- Use `--test` for quick 500-word build
- Use `--limit 2000` for medium build
- Use sample database for immediate testing
- Be patient - it's worth it!

### Database Not Found

```bash
# Check if files exist
ls -lh data/words.db
ls -lh der-die-das-spin/words.db

# If missing, rebuild
python3 tools/build_database.py --skip-download
```

### Too Few Words

```bash
# Check statistics
cat data/build_report_*.txt

# Adjust filters in tools/wiktionary_parser.py:
# - self.exclude_keywords (line 62)
# - self.category_patterns (line 74)
# - is_age_appropriate() (line 93)

# Rebuild
python3 tools/build_database.py --skip-download
```

## Updating Database

To get fresh Wiktionary content:

```bash
# Remove old dump
rm data/dewiktionary-latest-pages-articles.xml.bz2

# Run fresh build (downloads latest)
python3 tools/build_database.py

# Old database automatically backed up
ls -la der-die-das-spin/result.sql.backup_*
```

## Backend Integration

The backend automatically supports both old and new schemas:

```rust
// src/lib.rs automatically:
// 1. Tries new 'words' table first
// 2. Falls back to legacy 'derdiedas' table
// 3. Converts between formats
// No configuration needed!
```

## Performance Tips

### Faster Builds

```bash
# Use existing dump
python3 tools/build_database.py --skip-download

# Limit words for testing
python3 tools/build_database.py --limit 1000

# Use sample for development
cp sample_words.db der-die-das-spin/words.db
```

### Memory Usage

- Full parse uses ~500 MB RAM
- Test mode uses ~100 MB RAM
- No swap needed

### Disk Space

- Download: ~500 MB
- Database: ~5-8 MB (full), ~1 MB (test)
- Total needed: ~2 GB free space

## Statistics Example

Sample statistics from a full build:

```
DATABASE STATISTICS
---------------------------------------------------------------------------
  Total words: 1,847

  Articles:
    die: 897 (48.6%)  # Feminine
    der: 658 (35.6%)  # Masculine
    das: 292 (15.8%)  # Neuter

  Top Categories:
    Tier: 156        # Animals
    Essen: 124       # Food
    Natur: 98        # Nature
    Familie: 87      # Family
    Schule: 76       # School
    Haus: 65         # House
    Körper: 54       # Body
    Kleidung: 48     # Clothing
    Fahrzeug: 42     # Vehicles
    Zeit: 38         # Time

  Words with plural: 1,756 (95.1%)
  Words with syllables: 1,498 (81.1%)
  Compound words: 234 (12.7%)

  Example sentences: 892

  Difficulty levels:
    Level 1: 743 (40.2%)  # Easy
    Level 2: 521 (28.2%)  # Medium
    Level 3: 583 (31.6%)  # Hard
```

## Next Steps

After successful build:

1. **Test Locally**
   ```bash
   cd der-die-das-spin
   spin build && spin up
   ```

2. **Review Build Report**
   ```bash
   cat data/build_report_*.txt
   ```

3. **Query Database**
   ```bash
   sqlite3 der-die-das-spin/words.db
   ```

4. **Implement New Games**
   - See `GAME_DESIGN.md` for 10 game modes
   - Use extended schema fields
   - Start with Plural-Battle

5. **Deploy**
   - Test thoroughly
   - Commit changes
   - Deploy to production

## Additional Resources

- `GAME_DESIGN.md` - 10 new game mode designs
- `IMPROVEMENTS.md` - Complete feature documentation
- `tools/wiktionary_parser.py` - Parser implementation
- `tools/create_sample_db.py` - Sample database creator

## Success Checklist

✅ Build script runs without errors
✅ Database file created (words.db)
✅ Statistics show expected word count
✅ No inappropriate words found
✅ All tests pass
✅ Application starts successfully
✅ Words display in game

**You're ready to go! Start playing and learning! 🦫🇩🇪**
