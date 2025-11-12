#!/usr/bin/env python3
"""
Upload enriched database to Fermyon Cloud in batches
"""

import sqlite3
import subprocess
import sys

def execute_cloud_sql(sql):
    """Execute SQL statement on cloud database"""
    result = subprocess.run(
        ['spin', 'cloud', 'sqlite', 'execute', '--app', 'der-die-das', '--label', 'default', sql],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"Error executing SQL: {result.stderr}")
        return False
    return True

def upload_database(db_path):
    """Upload database to cloud in batches"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get table schema
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='derdiedas'")
    create_table_sql = cursor.fetchone()[0]

    print("Creating table...")
    if not execute_cloud_sql(create_table_sql):
        return False

    # Get all rows
    cursor.execute("SELECT * FROM derdiedas")
    rows = cursor.fetchall()

    # Get column names
    cursor.execute("PRAGMA table_info(derdiedas)")
    columns = [row[1] for row in cursor.fetchall()]

    print(f"Uploading {len(rows)} rows in batches of 100...")

    batch_size = 100
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i+batch_size]
        values = []
        for row in batch:
            # Escape quotes in strings
            escaped_row = []
            for val in row:
                if val is None:
                    escaped_row.append('NULL')
                elif isinstance(val, str):
                    escaped_row.append(f"'{val.replace(chr(39), chr(39)+chr(39))}'")
                else:
                    escaped_row.append(str(val))
            values.append(f"({','.join(escaped_row)})")

        insert_sql = f"INSERT INTO derdiedas ({','.join(columns)}) VALUES {','.join(values)}"

        if not execute_cloud_sql(insert_sql):
            print(f"Failed at batch {i//batch_size + 1}")
            return False

        print(f"  Uploaded batch {i//batch_size + 1}/{(len(rows)-1)//batch_size + 1}")

    conn.close()
    print("✅ Database upload complete!")
    return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 upload_cloud_db.py <database_path>")
        sys.exit(1)

    db_path = sys.argv[1]
    if not upload_database(db_path):
        sys.exit(1)
