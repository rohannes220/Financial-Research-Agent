ALTER TABLE filing_chunks ADD COLUMN IF NOT EXISTS section VARCHAR(64) DEFAULT 'other';
CREATE INDEX IF NOT EXISTS ix_filing_chunks_section ON filing_chunks(section);
