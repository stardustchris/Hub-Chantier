-- Migration: DEV-15, DEV-18, DEV-21 - Workflow complet, Historique, Import DPGF
-- Date: 2026-02-15
-- Description:
--   DEV-15: Suivi statut devis (workflow complet avec guards et domain events)
--   DEV-18: Historique modifications (avant/apres dans details JSON)
--   DEV-21: Import DPGF automatique (Excel/CSV)
--
-- Note: Pas de changement de schema necessaire pour ces features.
-- Les donnees enrichies (transitions statut, changements avant/apres)
-- sont stockees dans la colonne `details` (TEXT/JSON) existante de journal_devis.
-- Cette migration ajoute des index supplementaires pour la performance.

-- ─────────────────────────────────────────────────────────────────────────────
-- DEV-15: Index pour le filtrage par action dans le journal
-- ─────────────────────────────────────────────────────────────────────────────

-- Index composite pour filtrer les transitions de statut d'un devis
CREATE INDEX IF NOT EXISTS ix_journal_devis_devis_action
    ON journal_devis (devis_id, action);

-- ─────────────────────────────────────────────────────────────────────────────
-- DEV-18: Index pour la recherche d'historique par date et auteur
-- ─────────────────────────────────────────────────────────────────────────────

-- Index pour les recherches d'historique par plage de dates
CREATE INDEX IF NOT EXISTS ix_journal_devis_created_at
    ON journal_devis (created_at DESC);

-- ─────────────────────────────────────────────────────────────────────────────
-- DEV-21: Aucun changement schema - Import DPGF utilise les tables existantes
-- (lots_devis, lignes_devis, journal_devis)
-- L'action "import_dpgf" est enregistree dans le journal existant.
-- ─────────────────────────────────────────────────────────────────────────────

-- ─────────────────────────────────────────────────────────────────────────────
-- Commentaires documentation
-- ─────────────────────────────────────────────────────────────────────────────

COMMENT ON INDEX ix_journal_devis_devis_action IS
    'DEV-15: Filtrage rapide des entrees journal par type d''action';

COMMENT ON INDEX ix_journal_devis_created_at IS
    'DEV-18: Recherche d''historique par plage de dates';
