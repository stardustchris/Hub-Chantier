-- Migration: Ajout colonnes version pour lock optimiste
ALTER TABLE budgets ADD COLUMN IF NOT EXISTS version INTEGER NOT NULL DEFAULT 1;
ALTER TABLE situations_travaux ADD COLUMN IF NOT EXISTS version INTEGER NOT NULL DEFAULT 1;
