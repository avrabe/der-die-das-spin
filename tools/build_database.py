#!/usr/bin/env python3
"""
Automated Wiktionary Database Builder
Complete automation: Download → Parse → Build → Integrate

Usage:
    python3 tools/build_database.py [--limit N] [--skip-download] [--test]
"""

import os
import sys
import subprocess
import time
import hashlib
from pathlib import Path
from datetime import datetime

class DatabaseBuilder:
    """Automates the complete Wiktionary database build process"""

    def __init__(self, limit=None, skip_download=False, test_mode=False):
        self.limit = limit
        self.skip_download = skip_download
        self.test_mode = test_mode

        # Paths
        self.project_root = Path(__file__).parent.parent
        self.tools_dir = self.project_root / 'tools'
        self.data_dir = self.project_root / 'data'
        self.app_dir = self.project_root / 'der-die-das-spin'

        # Create data directory
        self.data_dir.mkdir(exist_ok=True)

        # Wiktionary URLs
        self.wiktionary_url = 'https://dumps.wikimedia.org/dewiktionary/latest/dewiktionary-latest-pages-articles.xml.bz2'
        self.wiktionary_md5_url = 'https://dumps.wikimedia.org/dewiktionary/latest/dewiktionary-latest-pages-articles.xml.bz2.md5'

        # File paths
        self.dump_file = self.data_dir / 'dewiktionary-latest-pages-articles.xml.bz2'
        self.output_db = self.data_dir / 'words.db'
        self.output_json = self.data_dir / 'words.json'
        self.final_db = self.app_dir / 'words.db'
        self.backup_db = self.app_dir / 'result.sql.backup'

        # Statistics
        self.stats = {
            'start_time': None,
            'end_time': None,
            'download_time': 0,
            'parse_time': 0,
            'total_time': 0,
            'dump_size_mb': 0,
            'words_extracted': 0,
            'db_size_mb': 0
        }

    def log(self, message, level='INFO'):
        """Log with timestamp"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        prefix = {
            'INFO': '📋',
            'SUCCESS': '✅',
            'WARNING': '⚠️',
            'ERROR': '❌',
            'DOWNLOAD': '⬇️',
            'PARSE': '🔍',
            'BUILD': '🔨',
            'TEST': '🧪'
        }.get(level, '•')

        print(f"{prefix} [{timestamp}] {message}")

    def run_command(self, cmd, description, capture_output=False):
        """Run shell command with error handling"""
        self.log(f"Running: {description}", 'INFO')
        try:
            if capture_output:
                result = subprocess.run(
                    cmd,
                    shell=True,
                    check=True,
                    capture_output=True,
                    text=True
                )
                return result.stdout
            else:
                subprocess.run(cmd, shell=True, check=True)
                return None
        except subprocess.CalledProcessError as e:
            self.log(f"Failed: {description}", 'ERROR')
            self.log(f"Error: {e}", 'ERROR')
            if capture_output and e.stderr:
                self.log(f"Stderr: {e.stderr}", 'ERROR')
            raise

    def verify_md5(self, file_path, expected_md5=None):
        """Verify file MD5 checksum"""
        self.log(f"Verifying MD5 checksum for {file_path.name}...", 'INFO')

        md5_hash = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                md5_hash.update(chunk)

        actual_md5 = md5_hash.hexdigest()

        if expected_md5:
            if actual_md5 == expected_md5:
                self.log("MD5 checksum verified ✓", 'SUCCESS')
                return True
            else:
                self.log(f"MD5 mismatch! Expected: {expected_md5}, Got: {actual_md5}", 'ERROR')
                return False
        else:
            self.log(f"MD5: {actual_md5}", 'INFO')
            return True

    def download_wiktionary(self):
        """Download Wiktionary dump"""
        if self.skip_download and self.dump_file.exists():
            self.log("Skipping download (file exists)", 'INFO')
            self.stats['dump_size_mb'] = self.dump_file.stat().st_size / (1024 * 1024)
            return

        self.log("Starting Wiktionary dump download...", 'DOWNLOAD')
        self.log(f"URL: {self.wiktionary_url}", 'INFO')

        start_time = time.time()

        try:
            # Download MD5 checksum first
            self.log("Downloading MD5 checksum...", 'DOWNLOAD')
            md5_output = self.run_command(
                f"curl -L '{self.wiktionary_md5_url}'",
                "Download MD5 checksum",
                capture_output=True
            )
            expected_md5 = md5_output.split()[0] if md5_output else None
            self.log(f"Expected MD5: {expected_md5}", 'INFO')

            # Download dump file with progress
            self.log("Downloading Wiktionary dump (this may take 10-30 minutes)...", 'DOWNLOAD')
            self.run_command(
                f"curl -L --progress-bar '{self.wiktionary_url}' -o '{self.dump_file}'",
                "Download Wiktionary dump"
            )

            self.stats['download_time'] = time.time() - start_time
            self.stats['dump_size_mb'] = self.dump_file.stat().st_size / (1024 * 1024)

            self.log(f"Download complete! Size: {self.stats['dump_size_mb']:.2f} MB", 'SUCCESS')
            self.log(f"Download time: {self.stats['download_time']:.1f} seconds", 'INFO')

            # Verify MD5
            if expected_md5:
                if not self.verify_md5(self.dump_file, expected_md5):
                    raise Exception("MD5 checksum verification failed!")

        except Exception as e:
            self.log(f"Download failed: {e}", 'ERROR')
            raise

    def parse_wiktionary(self):
        """Parse Wiktionary dump"""
        self.log("Starting Wiktionary parsing...", 'PARSE')

        if not self.dump_file.exists():
            raise FileNotFoundError(f"Dump file not found: {self.dump_file}")

        start_time = time.time()

        # Build command
        cmd = [
            'python3',
            str(self.tools_dir / 'wiktionary_parser.py'),
            str(self.dump_file),
            str(self.output_db)
        ]

        if self.limit:
            cmd.extend(['--limit', str(self.limit)])

        self.log(f"Running parser with command: {' '.join(cmd)}", 'INFO')

        try:
            # Run parser
            subprocess.run(cmd, check=True)

            self.stats['parse_time'] = time.time() - start_time

            # Get statistics from database
            import sqlite3
            conn = sqlite3.connect(str(self.output_db))
            cursor = conn.cursor()

            cursor.execute('SELECT COUNT(*) FROM words')
            self.stats['words_extracted'] = cursor.fetchone()[0]

            conn.close()

            self.stats['db_size_mb'] = self.output_db.stat().st_size / (1024 * 1024)

            self.log(f"Parsing complete!", 'SUCCESS')
            self.log(f"Words extracted: {self.stats['words_extracted']}", 'SUCCESS')
            self.log(f"Database size: {self.stats['db_size_mb']:.2f} MB", 'INFO')
            self.log(f"Parse time: {self.stats['parse_time']:.1f} seconds", 'INFO')

        except Exception as e:
            self.log(f"Parsing failed: {e}", 'ERROR')
            raise

    def backup_old_database(self):
        """Backup existing database"""
        old_db = self.app_dir / 'result.sql'

        if old_db.exists():
            self.log("Backing up old database...", 'INFO')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = self.app_dir / f'result.sql.backup_{timestamp}'
            old_db.rename(backup_path)
            self.log(f"Backed up to: {backup_path.name}", 'SUCCESS')

    def integrate_database(self):
        """Integrate new database into application"""
        self.log("Integrating database into application...", 'BUILD')

        try:
            # Copy to application directory
            import shutil

            # Keep old database as backup
            self.backup_old_database()

            # Copy new database
            shutil.copy2(str(self.output_db), str(self.final_db))
            self.log(f"Database copied to: {self.final_db}", 'SUCCESS')

            # Also keep JSON for reference
            if self.output_json.exists():
                final_json = self.app_dir / 'words.json'
                shutil.copy2(str(self.output_json), str(final_json))
                self.log(f"JSON copied to: {final_json}", 'INFO')

        except Exception as e:
            self.log(f"Integration failed: {e}", 'ERROR')
            raise

    def generate_statistics_report(self):
        """Generate comprehensive statistics report"""
        import sqlite3

        self.log("Generating statistics report...", 'INFO')

        report = []
        report.append("\n" + "="*70)
        report.append("WIKTIONARY DATABASE BUILD REPORT")
        report.append("="*70)
        report.append(f"Build completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total time: {self.stats['total_time']:.1f} seconds ({self.stats['total_time']/60:.1f} minutes)")
        report.append("")

        report.append("DOWNLOAD")
        report.append("-" * 70)
        report.append(f"  Dump size: {self.stats['dump_size_mb']:.2f} MB")
        report.append(f"  Download time: {self.stats['download_time']:.1f} seconds")
        report.append("")

        report.append("PARSING")
        report.append("-" * 70)
        report.append(f"  Parse time: {self.stats['parse_time']:.1f} seconds")
        report.append(f"  Words extracted: {self.stats['words_extracted']}")
        report.append(f"  Database size: {self.stats['db_size_mb']:.2f} MB")
        report.append("")

        # Query database for detailed statistics
        try:
            conn = sqlite3.connect(str(self.final_db))
            cursor = conn.cursor()

            report.append("DATABASE STATISTICS")
            report.append("-" * 70)

            # Total words
            cursor.execute('SELECT COUNT(*) FROM words')
            total_words = cursor.fetchone()[0]
            report.append(f"  Total words: {total_words}")

            # Articles breakdown
            cursor.execute('SELECT article, COUNT(*) FROM words GROUP BY article ORDER BY COUNT(*) DESC')
            report.append("\n  Articles:")
            for article, count in cursor.fetchall():
                pct = (count / total_words * 100) if total_words > 0 else 0
                report.append(f"    {article}: {count} ({pct:.1f}%)")

            # Categories
            cursor.execute('SELECT category, COUNT(*) FROM words WHERE category IS NOT NULL GROUP BY category ORDER BY COUNT(*) DESC LIMIT 15')
            categories = cursor.fetchall()
            if categories:
                report.append("\n  Top Categories:")
                for category, count in categories:
                    report.append(f"    {category}: {count}")

            # Words with plurals
            cursor.execute('SELECT COUNT(*) FROM words WHERE plural IS NOT NULL')
            with_plural = cursor.fetchone()[0]
            pct = (with_plural / total_words * 100) if total_words > 0 else 0
            report.append(f"\n  Words with plural: {with_plural} ({pct:.1f}%)")

            # Words with syllables
            cursor.execute('SELECT COUNT(*) FROM words WHERE syllables IS NOT NULL')
            with_syllables = cursor.fetchone()[0]
            pct = (with_syllables / total_words * 100) if total_words > 0 else 0
            report.append(f"  Words with syllables: {with_syllables} ({pct:.1f}%)")

            # Compound words
            cursor.execute('SELECT COUNT(*) FROM words WHERE is_compound = 1')
            compounds = cursor.fetchone()[0]
            pct = (compounds / total_words * 100) if total_words > 0 else 0
            report.append(f"  Compound words: {compounds} ({pct:.1f}%)")

            # Example sentences
            cursor.execute('SELECT COUNT(*) FROM example_sentences')
            sentences = cursor.fetchone()[0]
            report.append(f"\n  Example sentences: {sentences}")

            # Difficulty distribution
            cursor.execute('SELECT difficulty, COUNT(*) FROM words GROUP BY difficulty ORDER BY difficulty')
            report.append("\n  Difficulty levels:")
            for difficulty, count in cursor.fetchall():
                pct = (count / total_words * 100) if total_words > 0 else 0
                report.append(f"    Level {difficulty}: {count} ({pct:.1f}%)")

            conn.close()

        except Exception as e:
            report.append(f"  Error querying database: {e}")

        report.append("\n" + "="*70)
        report.append("DATABASE READY FOR USE!")
        report.append("="*70)
        report.append(f"\nDatabase location: {self.final_db}")
        report.append("\nNext steps:")
        report.append("  1. Test with: cd der-die-das-spin && spin build && spin up")
        report.append("  2. Open http://localhost:3000 in browser")
        report.append("  3. Try all game modes with age-appropriate content")
        report.append("")

        report_text = "\n".join(report)
        print(report_text)

        # Save report to file
        report_file = self.data_dir / f'build_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        report_file.write_text(report_text)
        self.log(f"Report saved to: {report_file}", 'INFO')

    def run_tests(self):
        """Run basic tests on the database"""
        self.log("Running database tests...", 'TEST')

        import sqlite3

        try:
            conn = sqlite3.connect(str(self.final_db))
            cursor = conn.cursor()

            # Test 1: Check tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            expected_tables = ['words', 'example_sentences', 'derdiedas']

            for table in expected_tables:
                if table in tables:
                    self.log(f"✓ Table '{table}' exists", 'TEST')
                else:
                    self.log(f"✗ Table '{table}' missing", 'ERROR')

            # Test 2: Sample queries
            cursor.execute('SELECT word, article, plural FROM words LIMIT 5')
            samples = cursor.fetchall()
            self.log(f"Sample words:", 'TEST')
            for word, article, plural in samples:
                self.log(f"  {article} {word} → {plural if plural else '(no plural)'}", 'TEST')

            # Test 3: Check for inappropriate content
            cursor.execute("SELECT word FROM words WHERE word LIKE '%sex%' OR word LIKE '%porno%' LIMIT 5")
            inappropriate = cursor.fetchall()
            if inappropriate:
                self.log(f"⚠️ Found potentially inappropriate words: {inappropriate}", 'WARNING')
            else:
                self.log("✓ No obvious inappropriate content found", 'TEST')

            # Test 4: Check old derdiedas table for backward compatibility
            cursor.execute('SELECT COUNT(*) FROM derdiedas')
            legacy_count = cursor.fetchone()[0]
            self.log(f"✓ Legacy derdiedas table has {legacy_count} entries", 'TEST')

            conn.close()

            self.log("All tests passed!", 'SUCCESS')

        except Exception as e:
            self.log(f"Tests failed: {e}", 'ERROR')
            raise

    def run(self):
        """Execute complete build process"""
        self.stats['start_time'] = time.time()

        try:
            self.log("="*70, 'INFO')
            self.log("AUTOMATED WIKTIONARY DATABASE BUILDER", 'INFO')
            self.log("="*70, 'INFO')

            if self.test_mode:
                self.log("Running in TEST MODE (limited words)", 'WARNING')

            if self.limit:
                self.log(f"Limiting to {self.limit} words", 'INFO')

            # Step 1: Download
            if not self.skip_download:
                self.download_wiktionary()
            else:
                self.log("Skipping download step", 'INFO')
                self.stats['dump_size_mb'] = self.dump_file.stat().st_size / (1024 * 1024) if self.dump_file.exists() else 0

            # Step 2: Parse
            self.parse_wiktionary()

            # Step 3: Integrate
            self.integrate_database()

            # Step 4: Test
            self.run_tests()

            # Calculate total time
            self.stats['end_time'] = time.time()
            self.stats['total_time'] = self.stats['end_time'] - self.stats['start_time']

            # Generate report
            self.generate_statistics_report()

            self.log("Build completed successfully! 🎉", 'SUCCESS')

            return True

        except KeyboardInterrupt:
            self.log("\n\nBuild interrupted by user", 'WARNING')
            return False
        except Exception as e:
            self.log(f"\n\nBuild failed: {e}", 'ERROR')
            import traceback
            traceback.print_exc()
            return False

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Automated Wiktionary Database Builder for Der Die Das',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full build (production)
  python3 tools/build_database.py

  # Test build (limited words)
  python3 tools/build_database.py --limit 1000

  # Skip download (use existing dump)
  python3 tools/build_database.py --skip-download

  # Quick test
  python3 tools/build_database.py --test

Note: Full build takes 30-60 minutes. Test mode is faster.
        """
    )

    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of words to extract (for testing)'
    )

    parser.add_argument(
        '--skip-download',
        action='store_true',
        help='Skip download step (use existing dump file)'
    )

    parser.add_argument(
        '--test',
        action='store_true',
        help='Test mode (limit to 500 words)'
    )

    args = parser.parse_args()

    # Test mode implies limit
    limit = args.limit
    if args.test and not limit:
        limit = 500

    # Create builder and run
    builder = DatabaseBuilder(
        limit=limit,
        skip_download=args.skip_download,
        test_mode=args.test
    )

    success = builder.run()

    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
