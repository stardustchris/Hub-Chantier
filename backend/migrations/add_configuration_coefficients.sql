-- Migration: Ajout des coefficients financiers a configuration_entreprise
-- Les coefficients etaient hardcodes dans calcul_financier.py, maintenant configurables par l'admin.

ALTER TABLE configuration_entreprise
    ADD COLUMN IF NOT EXISTS coeff_frais_generaux NUMERIC(5, 2) NOT NULL DEFAULT 19.00,
    ADD COLUMN IF NOT EXISTS coeff_charges_patronales NUMERIC(5, 2) NOT NULL DEFAULT 1.45,
    ADD COLUMN IF NOT EXISTS coeff_heures_sup NUMERIC(5, 2) NOT NULL DEFAULT 1.25,
    ADD COLUMN IF NOT EXISTS coeff_heures_sup_2 NUMERIC(5, 2) NOT NULL DEFAULT 1.50;

-- Contraintes de validation
ALTER TABLE configuration_entreprise
    ADD CONSTRAINT check_config_coeff_fg_range
        CHECK (coeff_frais_generaux >= 0 AND coeff_frais_generaux <= 100),
    ADD CONSTRAINT check_config_coeff_cp_min
        CHECK (coeff_charges_patronales >= 1),
    ADD CONSTRAINT check_config_coeff_hs_min
        CHECK (coeff_heures_sup >= 1),
    ADD CONSTRAINT check_config_coeff_hs2_min
        CHECK (coeff_heures_sup_2 >= 1);

-- Mettre a jour la ligne existante (2026) avec les valeurs par defaut
UPDATE configuration_entreprise
SET coeff_frais_generaux = 19.00,
    coeff_charges_patronales = 1.45,
    coeff_heures_sup = 1.25,
    coeff_heures_sup_2 = 1.50
WHERE annee = 2026;
