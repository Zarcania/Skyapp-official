-- Add DRAFT status to search_status enum if missing
ALTER TYPE search_status ADD VALUE IF NOT EXISTS 'DRAFT';
