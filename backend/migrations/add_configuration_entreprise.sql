CREATE TABLE IF NOT EXISTS configuration_entreprise (
    id SERIAL PRIMARY KEY,
    couts_fixes_annuels NUMERIC(12, 2) NOT NULL DEFAULT 600000.00,
    annee INTEGER NOT NULL DEFAULT 2026,
    notes TEXT,
    updated_at TIMESTAMP,
    updated_by INTEGER,
    UNIQUE(annee)
);

INSERT INTO configuration_entreprise (couts_fixes_annuels, annee, notes)
VALUES (600000.00, 2026, 'Valeur initiale - frais generaux hors salaires')
ON CONFLICT (annee) DO NOTHING;
