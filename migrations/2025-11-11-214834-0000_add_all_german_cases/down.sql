-- Revert schema changes - remove additional case columns
-- Note: SQLite doesn't support DROP COLUMN in older versions
-- This requires recreating the table

CREATE TABLE derdiedas_backup (
  nominativ_singular TEXT NOT NULL PRIMARY KEY,
  genus TEXT NOT NULL
);

INSERT INTO derdiedas_backup (nominativ_singular, genus)
SELECT nominativ_singular, genus FROM derdiedas;

DROP TABLE derdiedas;

ALTER TABLE derdiedas_backup RENAME TO derdiedas;
