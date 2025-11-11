-- Add all German case columns to support comprehensive grammar learning
ALTER TABLE derdiedas ADD COLUMN nominativ_plural TEXT;
ALTER TABLE derdiedas ADD COLUMN genitiv_singular TEXT;
ALTER TABLE derdiedas ADD COLUMN genitiv_plural TEXT;
ALTER TABLE derdiedas ADD COLUMN dativ_singular TEXT;
ALTER TABLE derdiedas ADD COLUMN dativ_plural TEXT;
ALTER TABLE derdiedas ADD COLUMN akkusativ_singular TEXT;
ALTER TABLE derdiedas ADD COLUMN akkusativ_plural TEXT;
