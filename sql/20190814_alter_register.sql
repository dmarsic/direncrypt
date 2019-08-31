ALTER TABLE register ADD COLUMN is_link BOOLEAN NULL CHECK (is_link IN (0,1));
ALTER TABLE register ADD COLUMN target TEXT;
