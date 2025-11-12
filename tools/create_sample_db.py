#!/usr/bin/env python3
"""
Create a sample database with age-appropriate German words for 4th graders
Based on Grundwortschatz NRW and common words
"""

import sqlite3
import json

# Sample words appropriate for 4th graders in NRW
SAMPLE_WORDS = [
    # Animals (Tiere)
    {'word': 'Hund', 'article': 'der', 'plural': 'Hunde', 'category': 'Tier', 'syllables': 'Hund', 'syllable_count': 1, 'difficulty': 1},
    {'word': 'Katze', 'article': 'die', 'plural': 'Katzen', 'category': 'Tier', 'syllables': 'Kat-ze', 'syllable_count': 2, 'difficulty': 1},
    {'word': 'Vogel', 'article': 'der', 'plural': 'Vögel', 'category': 'Tier', 'syllables': 'Vo-gel', 'syllable_count': 2, 'difficulty': 1},
    {'word': 'Fisch', 'article': 'der', 'plural': 'Fische', 'category': 'Tier', 'syllables': 'Fisch', 'syllable_count': 1, 'difficulty': 1},
    {'word': 'Pferd', 'article': 'das', 'plural': 'Pferde', 'category': 'Tier', 'syllables': 'Pferd', 'syllable_count': 1, 'difficulty': 1},
    {'word': 'Maus', 'article': 'die', 'plural': 'Mäuse', 'category': 'Tier', 'syllables': 'Maus', 'syllable_count': 1, 'difficulty': 1},
    {'word': 'Hase', 'article': 'der', 'plural': 'Hasen', 'category': 'Tier', 'syllables': 'Ha-se', 'syllable_count': 2, 'difficulty': 1},
    {'word': 'Schmetterling', 'article': 'der', 'plural': 'Schmetterlinge', 'category': 'Tier', 'syllables': 'Schmet-ter-ling', 'syllable_count': 3, 'difficulty': 2},
    {'word': 'Biene', 'article': 'die', 'plural': 'Bienen', 'category': 'Tier', 'syllables': 'Bie-ne', 'syllable_count': 2, 'difficulty': 1},
    {'word': 'Kuh', 'article': 'die', 'plural': 'Kühe', 'category': 'Tier', 'syllables': 'Kuh', 'syllable_count': 1, 'difficulty': 1},

    # Food (Essen)
    {'word': 'Brot', 'article': 'das', 'plural': 'Brote', 'category': 'Essen', 'syllables': 'Brot', 'syllable_count': 1, 'difficulty': 1},
    {'word': 'Apfel', 'article': 'der', 'plural': 'Äpfel', 'category': 'Essen', 'syllables': 'Ap-fel', 'syllable_count': 2, 'difficulty': 1},
    {'word': 'Kuchen', 'article': 'der', 'plural': 'Kuchen', 'category': 'Essen', 'syllables': 'Ku-chen', 'syllable_count': 2, 'difficulty': 1},
    {'word': 'Milch', 'article': 'die', 'plural': 'Milch', 'category': 'Essen', 'syllables': 'Milch', 'syllable_count': 1, 'difficulty': 1},
    {'word': 'Käse', 'article': 'der', 'plural': 'Käse', 'category': 'Essen', 'syllables': 'Kä-se', 'syllable_count': 2, 'difficulty': 1},
    {'word': 'Banane', 'article': 'die', 'plural': 'Bananen', 'category': 'Essen', 'syllables': 'Ba-na-ne', 'syllable_count': 3, 'difficulty': 1},
    {'word': 'Kartoffel', 'article': 'die', 'plural': 'Kartoffeln', 'category': 'Essen', 'syllables': 'Kar-tof-fel', 'syllable_count': 3, 'difficulty': 2},
    {'word': 'Tomate', 'article': 'die', 'plural': 'Tomaten', 'category': 'Essen', 'syllables': 'To-ma-te', 'syllable_count': 3, 'difficulty': 1},

    # Family (Familie)
    {'word': 'Mutter', 'article': 'die', 'plural': 'Mütter', 'category': 'Familie', 'syllables': 'Mut-ter', 'syllable_count': 2, 'difficulty': 1},
    {'word': 'Vater', 'article': 'der', 'plural': 'Väter', 'category': 'Familie', 'syllables': 'Va-ter', 'syllable_count': 2, 'difficulty': 1},
    {'word': 'Kind', 'article': 'das', 'plural': 'Kinder', 'category': 'Familie', 'syllables': 'Kind', 'syllable_count': 1, 'difficulty': 1},
    {'word': 'Bruder', 'article': 'der', 'plural': 'Brüder', 'category': 'Familie', 'syllables': 'Bru-der', 'syllable_count': 2, 'difficulty': 1},
    {'word': 'Schwester', 'article': 'die', 'plural': 'Schwestern', 'category': 'Familie', 'syllables': 'Schwes-ter', 'syllable_count': 2, 'difficulty': 1},
    {'word': 'Oma', 'article': 'die', 'plural': 'Omas', 'category': 'Familie', 'syllables': 'O-ma', 'syllable_count': 2, 'difficulty': 1},
    {'word': 'Opa', 'article': 'der', 'plural': 'Opas', 'category': 'Familie', 'syllables': 'O-pa', 'syllable_count': 2, 'difficulty': 1},

    # School (Schule)
    {'word': 'Schule', 'article': 'die', 'plural': 'Schulen', 'category': 'Schule', 'syllables': 'Schu-le', 'syllable_count': 2, 'difficulty': 1},
    {'word': 'Lehrer', 'article': 'der', 'plural': 'Lehrer', 'category': 'Schule', 'syllables': 'Leh-rer', 'syllable_count': 2, 'difficulty': 1},
    {'word': 'Buch', 'article': 'das', 'plural': 'Bücher', 'category': 'Schule', 'syllables': 'Buch', 'syllable_count': 1, 'difficulty': 1},
    {'word': 'Heft', 'article': 'das', 'plural': 'Hefte', 'category': 'Schule', 'syllables': 'Heft', 'syllable_count': 1, 'difficulty': 1},
    {'word': 'Stift', 'article': 'der', 'plural': 'Stifte', 'category': 'Schule', 'syllables': 'Stift', 'syllable_count': 1, 'difficulty': 1},
    {'word': 'Tafel', 'article': 'die', 'plural': 'Tafeln', 'category': 'Schule', 'syllables': 'Ta-fel', 'syllable_count': 2, 'difficulty': 1},
    {'word': 'Klasse', 'article': 'die', 'plural': 'Klassen', 'category': 'Schule', 'syllables': 'Klas-se', 'syllable_count': 2, 'difficulty': 1},

    # Body (Körper)
    {'word': 'Kopf', 'article': 'der', 'plural': 'Köpfe', 'category': 'Körper', 'syllables': 'Kopf', 'syllable_count': 1, 'difficulty': 1},
    {'word': 'Hand', 'article': 'die', 'plural': 'Hände', 'category': 'Körper', 'syllables': 'Hand', 'syllable_count': 1, 'difficulty': 1},
    {'word': 'Fuß', 'article': 'der', 'plural': 'Füße', 'category': 'Körper', 'syllables': 'Fuß', 'syllable_count': 1, 'difficulty': 1},
    {'word': 'Auge', 'article': 'das', 'plural': 'Augen', 'category': 'Körper', 'syllables': 'Au-ge', 'syllable_count': 2, 'difficulty': 1},
    {'word': 'Ohr', 'article': 'das', 'plural': 'Ohren', 'category': 'Körper', 'syllables': 'Ohr', 'syllable_count': 1, 'difficulty': 1},
    {'word': 'Nase', 'article': 'die', 'plural': 'Nasen', 'category': 'Körper', 'syllables': 'Na-se', 'syllable_count': 2, 'difficulty': 1},
    {'word': 'Mund', 'article': 'der', 'plural': 'Münder', 'category': 'Körper', 'syllables': 'Mund', 'syllable_count': 1, 'difficulty': 1},

    # Clothing (Kleidung)
    {'word': 'Hose', 'article': 'die', 'plural': 'Hosen', 'category': 'Kleidung', 'syllables': 'Ho-se', 'syllable_count': 2, 'difficulty': 1},
    {'word': 'Hemd', 'article': 'das', 'plural': 'Hemden', 'category': 'Kleidung', 'syllables': 'Hemd', 'syllable_count': 1, 'difficulty': 1},
    {'word': 'Schuh', 'article': 'der', 'plural': 'Schuhe', 'category': 'Kleidung', 'syllables': 'Schuh', 'syllable_count': 1, 'difficulty': 1},
    {'word': 'Jacke', 'article': 'die', 'plural': 'Jacken', 'category': 'Kleidung', 'syllables': 'Ja-cke', 'syllable_count': 2, 'difficulty': 1},
    {'word': 'Mütze', 'article': 'die', 'plural': 'Mützen', 'category': 'Kleidung', 'syllables': 'Müt-ze', 'syllable_count': 2, 'difficulty': 1},

    # House (Haus)
    {'word': 'Haus', 'article': 'das', 'plural': 'Häuser', 'category': 'Haus', 'syllables': 'Haus', 'syllable_count': 1, 'difficulty': 1},
    {'word': 'Zimmer', 'article': 'das', 'plural': 'Zimmer', 'category': 'Haus', 'syllables': 'Zim-mer', 'syllable_count': 2, 'difficulty': 1},
    {'word': 'Tür', 'article': 'die', 'plural': 'Türen', 'category': 'Haus', 'syllables': 'Tür', 'syllable_count': 1, 'difficulty': 1},
    {'word': 'Fenster', 'article': 'das', 'plural': 'Fenster', 'category': 'Haus', 'syllables': 'Fens-ter', 'syllable_count': 2, 'difficulty': 1},
    {'word': 'Bett', 'article': 'das', 'plural': 'Betten', 'category': 'Haus', 'syllables': 'Bett', 'syllable_count': 1, 'difficulty': 1},
    {'word': 'Tisch', 'article': 'der', 'plural': 'Tische', 'category': 'Haus', 'syllables': 'Tisch', 'syllable_count': 1, 'difficulty': 1},
    {'word': 'Stuhl', 'article': 'der', 'plural': 'Stühle', 'category': 'Haus', 'syllables': 'Stuhl', 'syllable_count': 1, 'difficulty': 1},

    # Nature (Natur)
    {'word': 'Baum', 'article': 'der', 'plural': 'Bäume', 'category': 'Natur', 'syllables': 'Baum', 'syllable_count': 1, 'difficulty': 1},
    {'word': 'Blume', 'article': 'die', 'plural': 'Blumen', 'category': 'Natur', 'syllables': 'Blu-me', 'syllable_count': 2, 'difficulty': 1},
    {'word': 'Sonne', 'article': 'die', 'plural': 'Sonnen', 'category': 'Natur', 'syllables': 'Son-ne', 'syllable_count': 2, 'difficulty': 1},
    {'word': 'Mond', 'article': 'der', 'plural': 'Monde', 'category': 'Natur', 'syllables': 'Mond', 'syllable_count': 1, 'difficulty': 1},
    {'word': 'Stern', 'article': 'der', 'plural': 'Sterne', 'category': 'Natur', 'syllables': 'Stern', 'syllable_count': 1, 'difficulty': 1},
    {'word': 'Berg', 'article': 'der', 'plural': 'Berge', 'category': 'Natur', 'syllables': 'Berg', 'syllable_count': 1, 'difficulty': 1},
    {'word': 'Fluss', 'article': 'der', 'plural': 'Flüsse', 'category': 'Natur', 'syllables': 'Fluss', 'syllable_count': 1, 'difficulty': 1},

    # Vehicles (Fahrzeuge)
    {'word': 'Auto', 'article': 'das', 'plural': 'Autos', 'category': 'Fahrzeug', 'syllables': 'Au-to', 'syllable_count': 2, 'difficulty': 1},
    {'word': 'Fahrrad', 'article': 'das', 'plural': 'Fahrräder', 'category': 'Fahrzeug', 'syllables': 'Fahr-rad', 'syllable_count': 2, 'difficulty': 1, 'is_compound': True, 'compound_parts': ['Fahr', 'Rad']},
    {'word': 'Bus', 'article': 'der', 'plural': 'Busse', 'category': 'Fahrzeug', 'syllables': 'Bus', 'syllable_count': 1, 'difficulty': 1},
    {'word': 'Zug', 'article': 'der', 'plural': 'Züge', 'category': 'Fahrzeug', 'syllables': 'Zug', 'syllable_count': 1, 'difficulty': 1},

    # Colors (Farben)
    {'word': 'Farbe', 'article': 'die', 'plural': 'Farben', 'category': 'Farbe', 'syllables': 'Far-be', 'syllable_count': 2, 'difficulty': 1},

    # Time (Zeit)
    {'word': 'Tag', 'article': 'der', 'plural': 'Tage', 'category': 'Zeit', 'syllables': 'Tag', 'syllable_count': 1, 'difficulty': 1},
    {'word': 'Nacht', 'article': 'die', 'plural': 'Nächte', 'category': 'Zeit', 'syllables': 'Nacht', 'syllable_count': 1, 'difficulty': 1},
    {'word': 'Woche', 'article': 'die', 'plural': 'Wochen', 'category': 'Zeit', 'syllables': 'Wo-che', 'syllable_count': 2, 'difficulty': 1},
    {'word': 'Jahr', 'article': 'das', 'plural': 'Jahre', 'category': 'Zeit', 'syllables': 'Jahr', 'syllable_count': 1, 'difficulty': 1},
]

# Example sentences
EXAMPLE_SENTENCES = {
    'Hund': [
        'Der Hund bellt laut.',
        'Mein Hund heißt Max.',
        'Der kleine Hund spielt im Garten.'
    ],
    'Katze': [
        'Die Katze schläft auf dem Sofa.',
        'Unsere Katze jagt Mäuse.',
        'Die schwarze Katze miaut.'
    ],
    'Apfel': [
        'Der Apfel ist rot und saftig.',
        'Ich esse gerne einen Apfel.',
        'Der grüne Apfel schmeckt sauer.'
    ],
    'Schule': [
        'Die Schule beginnt um 8 Uhr.',
        'Ich gehe gerne zur Schule.',
        'Unsere Schule hat einen großen Spielplatz.'
    ],
    'Mutter': [
        'Meine Mutter kocht sehr gut.',
        'Die Mutter liest eine Geschichte vor.',
        'Mama, ich liebe dich!'
    ],
}

def create_database(db_path: str):
    """Create SQLite database with sample words"""
    print(f"Creating database at {db_path}...")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tables with new schema
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT NOT NULL UNIQUE,
            article TEXT NOT NULL,
            plural TEXT,
            gen_singular TEXT,
            dat_singular TEXT,
            akk_singular TEXT,
            gen_plural TEXT,
            dat_plural TEXT,
            akk_plural TEXT,
            syllables TEXT,
            syllable_count INTEGER DEFAULT 1,
            category TEXT,
            is_compound BOOLEAN DEFAULT 0,
            compound_parts TEXT,
            difficulty INTEGER DEFAULT 1,
            frequency_rank INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS example_sentences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word_id INTEGER,
            sentence TEXT NOT NULL,
            difficulty INTEGER DEFAULT 1,
            FOREIGN KEY (word_id) REFERENCES words(id)
        )
    ''')

    # Also keep old table for backward compatibility
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS derdiedas (
            nominativ_singular TEXT PRIMARY KEY,
            genus TEXT NOT NULL
        )
    ''')

    # Insert sample words
    for word_data in SAMPLE_WORDS:
        # Insert into new words table
        cursor.execute('''
            INSERT OR REPLACE INTO words
            (word, article, plural, syllables, syllable_count, category,
             is_compound, compound_parts, difficulty)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            word_data['word'],
            word_data['article'],
            word_data.get('plural'),
            word_data.get('syllables'),
            word_data.get('syllable_count', 1),
            word_data.get('category'),
            word_data.get('is_compound', False),
            json.dumps(word_data.get('compound_parts')) if word_data.get('compound_parts') else None,
            word_data.get('difficulty', 1)
        ))

        word_id = cursor.lastrowid

        # Insert example sentences if available
        if word_data['word'] in EXAMPLE_SENTENCES:
            for sentence in EXAMPLE_SENTENCES[word_data['word']]:
                cursor.execute('''
                    INSERT INTO example_sentences (word_id, sentence)
                    VALUES (?, ?)
                ''', (word_id, sentence))

        # Also insert into old table for backward compatibility
        genus_map = {'der': 'm', 'die': 'f', 'das': 'n'}
        cursor.execute('''
            INSERT OR REPLACE INTO derdiedas (nominativ_singular, genus)
            VALUES (?, ?)
        ''', (word_data['word'], genus_map[word_data['article']]))

    conn.commit()

    # Print statistics
    cursor.execute('SELECT COUNT(*) FROM words')
    word_count = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM example_sentences')
    sentence_count = cursor.fetchone()[0]

    cursor.execute('SELECT category, COUNT(*) FROM words GROUP BY category')
    categories = cursor.fetchall()

    print(f"\n✅ Database created successfully!")
    print(f"   Total words: {word_count}")
    print(f"   Example sentences: {sentence_count}")
    print(f"\n   Words by category:")
    for category, count in categories:
        print(f"     {category}: {count}")

    conn.close()

if __name__ == '__main__':
    import sys
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'sample_words.db'
    create_database(db_path)
    print(f"\nDatabase saved to: {db_path}")
    print("\nNext steps:")
    print("1. Copy to der-die-das-spin directory")
    print("2. Update spin.toml to use this database")
    print("3. Test with 'spin build && spin up'")
