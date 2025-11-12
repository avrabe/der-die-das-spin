#!/usr/bin/env python3
"""
Database Enrichment Script
Adds syllables, categories, compound detection, difficulty, and frequency to existing words
"""

import sqlite3
import sys
import re
from pathlib import Path

# Category keywords (German)
CATEGORIES = {
    'Tier': ['hund', 'katz', 'vogel', 'fisch', 'pferd', 'kuh', 'schaf', 'ziege',
             'schwein', 'huhn', 'ente', 'gans', 'maus', 'ratte', 'kaninchen', 'hase',
             'löwe', 'tiger', 'bär', 'wolf', 'fuchs', 'eichhörnchen', 'reh', 'hirsch',
             'elefant', 'affe', 'schlange', 'frosch', 'schildkröte', 'fliege', 'biene',
             'schmetterling', 'käfer', 'spinne', 'ameise', 'tier'],

    'Essen': ['brot', 'butter', 'käse', 'milch', 'ei', 'fleisch', 'wurst', 'fisch',
              'apfel', 'birne', 'banane', 'orange', 'kirsch', 'erdbeer', 'traube',
              'kartoffel', 'tomat', 'gurke', 'salat', 'zwiebel', 'karotte', 'kohl',
              'reis', 'nudel', 'suppe', 'kuchen', 'torte', 'schokolade', 'bonbon',
              'saft', 'wasser', 'tee', 'kaffee', 'essen', 'nahrung', 'lebensmittel'],

    'Familie': ['mutter', 'vater', 'eltern', 'kind', 'sohn', 'tochter', 'bruder',
                'schwester', 'oma', 'opa', 'großmutter', 'großvater', 'tante', 'onkel',
                'cousin', 'baby', 'familie', 'verwandt'],

    'Schule': ['schule', 'lehrer', 'schüler', 'klasse', 'unterricht', 'pause', 'heft',
               'buch', 'stift', 'bleistift', 'füller', 'radiergummi', 'lineal', 'tafel',
               'kreide', 'ranzen', 'rucksack', 'prüfung', 'hausaufgabe', 'zeugnis'],

    'Körper': ['kopf', 'haar', 'auge', 'nase', 'mund', 'ohr', 'zahn', 'hals', 'arm',
               'hand', 'finger', 'bein', 'fuß', 'zeh', 'bauch', 'rücken', 'herz',
               'körper', 'gesicht'],

    'Haus': ['haus', 'wohnung', 'zimmer', 'küche', 'bad', 'schlafzimmer', 'wohnzimmer',
             'tür', 'fenster', 'wand', 'boden', 'decke', 'treppe', 'dach', 'garten',
             'tisch', 'stuhl', 'bett', 'schrank', 'sofa', 'lampe', 'möbel'],

    'Natur': ['baum', 'blume', 'gras', 'wald', 'berg', 'fluss', 'see', 'meer', 'strand',
              'sonne', 'mond', 'stern', 'himmel', 'wolke', 'regen', 'schnee', 'wind',
              'wetter', 'natur', 'pflanze', 'stein', 'sand', 'erde'],

    'Kleidung': ['kleid', 'hose', 'hemd', 'pullover', 'jacke', 'mantel', 'mütze', 'hut',
                 'schuhe', 'socken', 'strumpf', 'kleidung'],

    'Fahrzeug': ['auto', 'wagen', 'bus', 'zug', 'fahrrad', 'motorrad', 'schiff', 'boot',
                 'flugzeug', 'fahrzeug'],

    'Zeit': ['tag', 'nacht', 'morgen', 'mittag', 'abend', 'woche', 'monat', 'jahr',
             'stunde', 'minute', 'sekunde', 'uhr', 'zeit'],

    'Farbe': ['rot', 'blau', 'grün', 'gelb', 'schwarz', 'weiß', 'braun', 'grau',
              'orange', 'rosa', 'lila', 'farbe'],
}

def count_syllables(word):
    """
    Count syllables in a German word using vowel-based heuristic
    """
    if not word:
        return 1

    word = word.lower()

    # German diphthongs count as one syllable
    diphthongs = ['ei', 'ai', 'au', 'eu', 'äu', 'ie', 'oi', 'ui']
    for diphthong in diphthongs:
        word = word.replace(diphthong, 'X')

    # Count vowels
    vowels = 'aeiouäöüy'
    syllable_count = sum(1 for char in word if char in vowels)

    # Minimum 1 syllable
    return max(1, syllable_count)

def create_syllable_breaks(word):
    """
    Create basic syllable breaks for German words
    Just use the original word for now - proper syllabification is complex
    """
    syllable_count = count_syllables(word)

    if syllable_count == 1:
        return word

    # For now, just return the word
    # TODO: Implement proper German syllabification rules
    return word

def detect_category(word):
    """
    Detect semantic category based on keyword matching
    """
    word_lower = word.lower()

    for category, keywords in CATEGORIES.items():
        if any(keyword in word_lower for keyword in keywords):
            return category

    return None

def is_compound_word(word):
    """
    Detect if word is likely a compound
    """
    # German compounds are often long
    if len(word) > 12:
        return True

    # Contains capital letters mid-word (except for certain patterns)
    if len(word) > 1:
        for i, char in enumerate(word[1:], start=1):
            if char.isupper():
                return True

    return False

def split_compound(word):
    """
    Attempt to split compound words
    Returns JSON-like string of parts or None
    """
    if not is_compound_word(word):
        return None

    # Very basic splitting - look for capital letters
    parts = []
    current = word[0]

    for char in word[1:]:
        if char.isupper():
            parts.append(current)
            current = char
        else:
            current += char

    if current:
        parts.append(current)

    if len(parts) > 1:
        import json
        return json.dumps(parts)

    return None

def calculate_difficulty(word, syllable_count):
    """
    Calculate difficulty level (1-5) based on word characteristics
    """
    # Factors: length, syllable count
    length_score = min(5, len(word) / 4)
    syllable_score = min(5, syllable_count)

    # Average the scores
    difficulty = int((length_score + syllable_score) / 2)

    # Clamp to 1-5
    return max(1, min(5, difficulty))

def estimate_frequency(word):
    """
    Estimate frequency rank (lower = more frequent)
    Based on word length - shorter words tend to be more common
    """
    # Simple heuristic: length * 100
    # Short common words: 300-600
    # Medium words: 700-1200
    # Long rare words: 1300+
    return len(word) * 100

def enrich_database(db_path, verbose=True):
    """
    Enrich database with computed fields
    """
    if verbose:
        print(f"📊 Enriching database: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if columns exist, add if needed
    cursor.execute("PRAGMA table_info(derdiedas)")
    columns = [col[1] for col in cursor.fetchall()]

    new_columns = [
        ('syllables', 'TEXT'),
        ('syllable_count', 'INTEGER DEFAULT 1'),
        ('category', 'TEXT'),
        ('is_compound', 'BOOLEAN DEFAULT 0'),
        ('compound_parts', 'TEXT'),
        ('difficulty', 'INTEGER DEFAULT 1'),
        ('frequency_rank', 'INTEGER'),
    ]

    for col_name, col_type in new_columns:
        if col_name not in columns:
            if verbose:
                print(f"  ➕ Adding column: {col_name}")
            cursor.execute(f"ALTER TABLE derdiedas ADD COLUMN {col_name} {col_type}")

    conn.commit()

    # Get all words
    cursor.execute("SELECT nominativ_singular FROM derdiedas")
    words = cursor.fetchall()

    total = len(words)
    if verbose:
        print(f"  🔄 Processing {total:,} words...")

    stats = {
        'total': total,
        'categorized': 0,
        'compounds': 0,
    }

    # Process each word
    for i, (word,) in enumerate(words, 1):
        if verbose and i % 5000 == 0:
            print(f"    Progress: {i:,}/{total:,} ({i*100//total}%)")

        syllable_count = count_syllables(word)
        syllables = create_syllable_breaks(word)
        category = detect_category(word)
        is_comp = is_compound_word(word)
        comp_parts = split_compound(word) if is_comp else None
        difficulty = calculate_difficulty(word, syllable_count)
        frequency = estimate_frequency(word)

        if category:
            stats['categorized'] += 1
        if is_comp:
            stats['compounds'] += 1

        cursor.execute("""
            UPDATE derdiedas
            SET syllables = ?,
                syllable_count = ?,
                category = ?,
                is_compound = ?,
                compound_parts = ?,
                difficulty = ?,
                frequency_rank = ?
            WHERE nominativ_singular = ?
        """, (syllables, syllable_count, category, is_comp,
              comp_parts, difficulty, frequency, word))

    conn.commit()
    conn.close()

    if verbose:
        print(f"\n✅ Enrichment complete!")
        print(f"  📊 Statistics:")
        print(f"    Total words: {stats['total']:,}")
        print(f"    Categorized: {stats['categorized']:,} ({stats['categorized']*100//stats['total']}%)")
        print(f"    Compounds: {stats['compounds']:,} ({stats['compounds']*100//stats['total']}%)")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 enrich_database.py <database_path>")
        print("Example: python3 enrich_database.py sample_words.db")
        sys.exit(1)

    db_path = Path(sys.argv[1])

    if not db_path.exists():
        print(f"❌ Error: Database not found: {db_path}")
        sys.exit(1)

    try:
        enrich_database(str(db_path))
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
