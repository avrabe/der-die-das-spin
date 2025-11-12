#!/usr/bin/env python3
"""
Wiktionary Parser for German Nouns
Extracts comprehensive data for Der Die Das educational games
"""

import re
import json
import xml.etree.ElementTree as ET
import bz2
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict
from pathlib import Path
import sqlite3

@dataclass
class GermanNoun:
    """Represents a German noun with all relevant grammatical information"""
    word: str
    article: str  # der, die, das
    plural: Optional[str] = None
    plural_article: str = "die"  # always die for plural

    # Declensions
    gen_singular: Optional[str] = None
    dat_singular: Optional[str] = None
    akk_singular: Optional[str] = None
    gen_plural: Optional[str] = None
    dat_plural: Optional[str] = None
    akk_plural: Optional[str] = None

    # Additional info
    syllables: Optional[str] = None
    syllable_count: int = 1
    category: Optional[str] = None
    is_compound: bool = False
    compound_parts: Optional[List[str]] = None
    synonyms: Optional[List[str]] = None
    antonyms: Optional[List[str]] = None
    example_sentences: Optional[List[str]] = None
    difficulty: int = 3  # 1-5, will be calculated based on frequency
    frequency_rank: Optional[int] = None

class WiktionaryParser:
    """Parse German Wiktionary XML dump"""

    def __init__(self):
        self.namespace = '{http://www.mediawiki.org/xml/export-0.10/}'
        self.nouns = []
        self.stats = {
            'total_pages': 0,
            'german_nouns': 0,
            'with_plural': 0,
            'with_declension': 0,
            'with_examples': 0,
            'skipped': 0
        }

        # Age-inappropriate keywords to filter out
        self.exclude_keywords = {
            'sex', 'sexu', 'porno', 'abtreibung', 'drog', 'waffe',
            'krieg', 'gewalt', 'tot', 'mord', 'atom', 'nuklear',
            'philosophie', 'metaph', 'epistem', 'ontolog'
        }

        # Child-friendly categories
        self.category_patterns = {
            'Tier': r'\b(tier|hund|katz|vogel|fisch|pferd|schwein|kuh|schaf|ziege|huhn|maus|hase|bär|löwe|elefant|affe)\b',
            'Pflanze': r'\b(pflanz|baum|blum|ros|tulp|gras|strauch|kraut)\b',
            'Essen': r'\b(essen|brot|käse|wurst|obst|gemüse|apfel|birn|kartoffel|reis|nudel|kuchen|keks)\b',
            'Möbel': r'\b(möbel|stuhl|tisch|bett|schrank|regal|sofa|sessel)\b',
            'Schule': r'\b(schul|lehrer|schüler|heft|buch|stift|tafel|klasse|pause|unterricht)\b',
            'Familie': r'\b(familie|mutter|vater|kind|bruder|schwester|oma|opa|tante|onkel|cousin)\b',
            'Körper': r'\b(körper|kopf|arm|bein|hand|fuß|auge|ohr|nase|mund|haar|zahn)\b',
            'Kleidung': r'\b(kleid|hose|hemd|jacke|schuh|socke|mütze|schal|rock|pullover)\b',
            'Haus': r'\b(haus|zimmer|küch|bad|wohn|schlaf|tür|fenster|wand|dach)\b',
            'Natur': r'\b(natur|berg|fluss|see|meer|wald|wiese|himmel|sonne|mond|stern|regen|schnee)\b',
            'Farbe': r'\b(farb|rot|blau|grün|gelb|schwarz|weiß|braun|grau|orange|rosa|lila)\b',
            'Fahrzeug': r'\b(auto|fahrrad|bus|zug|schiff|flugzeug|motorrad|lkw)\b',
            'Werkzeug': r'\b(werkzeug|hammer|säge|schrauben|zange|schere)\b',
            'Zeit': r'\b(zeit|tag|woche|monat|jahr|stunde|minute|sekunde|morgen|mittag|abend|nacht)\b',
            'Zahl': r'\b(zahl|eins|zwei|drei|vier|fünf|sechs|sieben|acht|neun|zehn|hundert|tausend)\b'
        }

    def is_age_appropriate(self, word: str, text: str) -> bool:
        """Check if word is appropriate for 4th graders"""
        word_lower = word.lower()
        text_lower = text.lower()

        # Check for inappropriate keywords
        for keyword in self.exclude_keywords:
            if keyword in word_lower or keyword in text_lower[:500]:
                return False

        # Too long words are usually too complex
        if len(word) > 20:
            return False

        # Allow simple compounds but reject overly complex ones
        if '-' in word and word.count('-') > 2:
            return False

        return True

    def extract_article(self, text: str) -> Optional[str]:
        """Extract article (der/die/das) from Wiktionary text"""
        # Look for genus markers
        patterns = [
            r'\{\{Genus\|([mfn])\}\}',
            r'\|Genus=([mfn])',
            r'\{\{([mfn])\}\}',
            r'===.*?\{\{([mfn])\}\}.*?===',
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                genus = match.group(1)
                return {'m': 'der', 'f': 'die', 'n': 'das'}.get(genus)

        return None

    def extract_declension_table(self, text: str) -> Dict[str, str]:
        """Extract declension information from template"""
        declension = {}

        # Common Wiktionary templates
        patterns = {
            'nom_sg': r'\|Nominativ Singular\s*=\s*([^\|\n]+)',
            'nom_pl': r'\|Nominativ Plural\s*=\s*([^\|\n]+)',
            'gen_sg': r'\|Genitiv Singular\s*=\s*([^\|\n]+)',
            'gen_pl': r'\|Genitiv Plural\s*=\s*([^\|\n]+)',
            'dat_sg': r'\|Dativ Singular\s*=\s*([^\|\n]+)',
            'dat_pl': r'\|Dativ Plural\s*=\s*([^\|\n]+)',
            'akk_sg': r'\|Akkusativ Singular\s*=\s*([^\|\n]+)',
            'akk_pl': r'\|Akkusativ Plural\s*=\s*([^\|\n]+)',
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                # Clean up wikitext
                value = re.sub(r'\{\{.*?\}\}', '', value)
                value = re.sub(r'\[\[([^\|\]]+\|)?([^\]]+)\]\]', r'\2', value)
                value = value.strip()
                if value and value != '—' and value != '-':
                    declension[key] = value

        return declension

    def extract_syllables(self, text: str) -> tuple[Optional[str], int]:
        """Extract syllable information"""
        # Look for syllable breaks
        pattern = r'\{\{Worttrennung\}\}\s*:([^\n]+)'
        match = re.search(pattern, text)

        if match:
            syllables = match.group(1).strip()
            # Clean up
            syllables = re.sub(r'<[^>]+>', '', syllables)
            syllables = syllables.split(',')[0]  # Take first variant
            syllable_count = syllables.count('·') + 1 if '·' in syllables else 1
            return syllables.replace('·', '-'), syllable_count

        return None, 1

    def detect_category(self, word: str, text: str) -> Optional[str]:
        """Detect semantic category of the word"""
        word_lower = word.lower()
        text_sample = text[:1000].lower()

        for category, pattern in self.category_patterns.items():
            if re.search(pattern, word_lower) or re.search(pattern, text_sample):
                return category

        return None

    def extract_examples(self, text: str, max_examples: int = 3) -> List[str]:
        """Extract example sentences"""
        examples = []

        # Look for example section
        pattern = r'\{\{Beispiele\}\}(.*?)(?=\n\n|\{\{|\Z)'
        match = re.search(pattern, text, re.DOTALL)

        if match:
            example_text = match.group(1)
            # Extract numbered examples
            example_pattern = r':\[[\d\]]\s*([^:\[\n]+)'
            for example_match in re.finditer(example_pattern, example_text):
                example = example_match.group(1).strip()
                # Clean up wikitext
                example = re.sub(r'\{\{.*?\}\}', '', example)
                example = re.sub(r'\[\[([^\|\]]+\|)?([^\]]+)\]\]', r'\2', example)
                example = re.sub(r"''", '', example)
                if example and len(example) > 10 and len(example) < 150:
                    examples.append(example)
                    if len(examples) >= max_examples:
                        break

        return examples

    def is_compound(self, word: str) -> tuple[bool, Optional[List[str]]]:
        """Check if word is a compound and extract parts"""
        # Simple heuristic: German compounds are typically written together
        # Look for capital letters in the middle
        if len(word) > 6:
            # Find potential split points (capital letters after lowercase)
            capitals = [i for i, c in enumerate(word[1:], 1) if c.isupper()]
            if capitals:
                # Try to split at first capital
                parts = [word[:capitals[0]], word[capitals[0]:]]
                return True, parts

        return False, None

    def parse_page(self, page_text: str, title: str) -> Optional[GermanNoun]:
        """Parse a single Wiktionary page"""
        # Check if this is a German noun entry
        if '{{Wortart|Substantiv|Deutsch}}' not in page_text:
            return None

        # Check age-appropriateness
        if not self.is_age_appropriate(title, page_text):
            self.stats['skipped'] += 1
            return None

        # Extract article
        article = self.extract_article(page_text)
        if not article:
            return None

        # Extract declension table
        declension = self.extract_declension_table(page_text)

        # Extract syllables
        syllables, syllable_count = self.extract_syllables(page_text)

        # Detect category
        category = self.detect_category(title, page_text)

        # Extract examples
        examples = self.extract_examples(page_text)

        # Check if compound
        is_comp, comp_parts = self.is_compound(title)

        noun = GermanNoun(
            word=title,
            article=article,
            plural=declension.get('nom_pl'),
            gen_singular=declension.get('gen_sg'),
            dat_singular=declension.get('dat_sg'),
            akk_singular=declension.get('akk_sg'),
            gen_plural=declension.get('gen_pl'),
            dat_plural=declension.get('dat_pl'),
            akk_plural=declension.get('akk_pl'),
            syllables=syllables,
            syllable_count=syllable_count,
            category=category,
            is_compound=is_comp,
            compound_parts=comp_parts,
            example_sentences=examples if examples else None
        )

        # Update stats
        self.stats['german_nouns'] += 1
        if noun.plural:
            self.stats['with_plural'] += 1
        if declension:
            self.stats['with_declension'] += 1
        if examples:
            self.stats['with_examples'] += 1

        return noun

    def parse_xml_dump(self, xml_path: str, limit: int = None):
        """Parse Wiktionary XML dump"""
        print(f"Parsing {xml_path}...")

        # Handle bz2 compressed files
        if xml_path.endswith('.bz2'):
            file_obj = bz2.open(xml_path, 'rt', encoding='utf-8')
        else:
            file_obj = open(xml_path, 'r', encoding='utf-8')

        try:
            # Use iterparse for memory efficiency
            context = ET.iterparse(file_obj, events=('start', 'end'))
            context = iter(context)
            event, root = next(context)

            current_title = None
            current_text = None

            for event, elem in context:
                if event == 'end':
                    tag = elem.tag.replace(self.namespace, '')

                    if tag == 'title':
                        current_title = elem.text
                    elif tag == 'text':
                        current_text = elem.text
                    elif tag == 'page':
                        self.stats['total_pages'] += 1

                        if current_title and current_text:
                            noun = self.parse_page(current_text, current_title)
                            if noun:
                                self.nouns.append(noun)

                        # Progress update
                        if self.stats['total_pages'] % 1000 == 0:
                            print(f"Processed {self.stats['total_pages']} pages, found {self.stats['german_nouns']} nouns...")

                        # Limit for testing
                        if limit and self.stats['german_nouns'] >= limit:
                            break

                        current_title = None
                        current_text = None

                        # Clear element to save memory
                        elem.clear()
                        root.clear()

        finally:
            file_obj.close()

        print(f"\nParsing complete!")
        print(f"Statistics:")
        for key, value in self.stats.items():
            print(f"  {key}: {value}")

    def save_to_json(self, output_path: str):
        """Save parsed nouns to JSON file"""
        print(f"\nSaving to {output_path}...")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump([asdict(noun) for noun in self.nouns], f, ensure_ascii=False, indent=2)
        print(f"Saved {len(self.nouns)} nouns to JSON")

    def save_to_sqlite(self, db_path: str):
        """Save parsed nouns to SQLite database"""
        print(f"\nSaving to SQLite database {db_path}...")

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create table with extended schema
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
                difficulty INTEGER DEFAULT 3,
                frequency_rank INTEGER
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS example_sentences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word_id INTEGER,
                sentence TEXT NOT NULL,
                FOREIGN KEY (word_id) REFERENCES words(id)
            )
        ''')

        # Insert nouns
        for noun in self.nouns:
            cursor.execute('''
                INSERT OR REPLACE INTO words
                (word, article, plural, gen_singular, dat_singular, akk_singular,
                 gen_plural, dat_plural, akk_plural, syllables, syllable_count,
                 category, is_compound, compound_parts, difficulty)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                noun.word, noun.article, noun.plural,
                noun.gen_singular, noun.dat_singular, noun.akk_singular,
                noun.gen_plural, noun.dat_plural, noun.akk_plural,
                noun.syllables, noun.syllable_count,
                noun.category, noun.is_compound,
                json.dumps(noun.compound_parts) if noun.compound_parts else None,
                noun.difficulty
            ))

            word_id = cursor.lastrowid

            # Insert example sentences
            if noun.example_sentences:
                for sentence in noun.example_sentences:
                    cursor.execute('''
                        INSERT INTO example_sentences (word_id, sentence)
                        VALUES (?, ?)
                    ''', (word_id, sentence))

        conn.commit()
        conn.close()
        print(f"Saved {len(self.nouns)} nouns to SQLite database")

def main():
    parser = WiktionaryParser()

    # For testing, you can use a sample file or limit the parsing
    import sys

    if len(sys.argv) < 2:
        print("Usage: python wiktionary_parser.py <xml_dump_path> [output_db_path] [--limit N]")
        print("\nExample:")
        print("  python wiktionary_parser.py dewiktionary-latest-pages-articles.xml.bz2 words.db --limit 1000")
        sys.exit(1)

    xml_path = sys.argv[1]
    output_db = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else 'words.db'

    # Check for limit
    limit = None
    if '--limit' in sys.argv:
        limit_idx = sys.argv.index('--limit')
        if limit_idx + 1 < len(sys.argv):
            limit = int(sys.argv[limit_idx + 1])

    # Parse
    parser.parse_xml_dump(xml_path, limit=limit)

    # Save
    parser.save_to_sqlite(output_db)
    parser.save_to_json(output_db.replace('.db', '.json'))

if __name__ == '__main__':
    main()
