-- =============================================================================
-- SCHEMA SQL - MODULE LOGISTIQUE (CDC Section 11 - LOG-01 a LOG-18)
-- =============================================================================
-- Hub Chantier - Greg Constructions
-- Date: 2026-01-24
--
-- Fonctionnalites couvertes:
-- LOG-01: Referentiel materiel (Admin uniquement)
-- LOG-02: Fiche ressource (nom, code, photo, couleur, plage horaire)
-- LOG-03 a LOG-06: Planning par ressource, navigation, axe horaire, blocs colores
-- LOG-07 a LOG-09: Demande de reservation, selection chantier/creneau
-- LOG-10: Option validation N+1 par ressource
-- LOG-11, LOG-12: Workflow validation et statuts
-- LOG-13 a LOG-15: Notifications (infrastructure separee)
-- LOG-16: Motif de refus
-- LOG-17: Detection conflits
-- LOG-18: Historique par ressource
--
-- Types de ressources (Greg Constructions):
-- - levage: Grue mobile, Manitou, Nacelle (N+1 requis)
-- - terrassement: Mini-pelle, Pelleteuse (N+1 requis)
-- - vehicule: Camion benne, Fourgon (Validation optionnelle)
-- - outillage: Betonniere, Vibrateur (Validation optionnelle)
-- - equipement: Echafaudage, Etais, Banches (N+1 requis)
-- =============================================================================

-- -----------------------------------------------------------------------------
-- TABLE: ressources
-- Referentiel du materiel de l'entreprise (LOG-01, LOG-02)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ressources (
    -- Identifiant
    id SERIAL PRIMARY KEY,

    -- Identification (LOG-02)
    code VARCHAR(20) NOT NULL UNIQUE,
    nom VARCHAR(255) NOT NULL,
    description TEXT,

    -- Type de ressource
    -- Valeurs: 'levage', 'terrassement', 'vehicule', 'outillage', 'equipement'
    type_ressource VARCHAR(50) NOT NULL,

    -- Identification visuelle (LOG-02)
    photo_url VARCHAR(500),
    couleur VARCHAR(7) NOT NULL DEFAULT '#3498DB',

    -- Plage horaire par defaut (LOG-05) - Format HH:MM
    plage_horaire_debut VARCHAR(5) NOT NULL DEFAULT '08:00',
    plage_horaire_fin VARCHAR(5) NOT NULL DEFAULT '18:00',

    -- Option validation N+1 (LOG-10)
    -- TRUE = demande doit etre validee par chef/conducteur
    -- FALSE = reservation directe
    validation_requise BOOLEAN NOT NULL DEFAULT TRUE,

    -- Statut
    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Soft delete (RGPD compliant)
    deleted_at TIMESTAMP
);

-- Index pour recherches frequentes
CREATE UNIQUE INDEX IF NOT EXISTS ix_ressources_code ON ressources(code);
CREATE INDEX IF NOT EXISTS ix_ressources_type ON ressources(type_ressource);
CREATE INDEX IF NOT EXISTS ix_ressources_active ON ressources(is_active, deleted_at);

-- Commentaire sur la table
COMMENT ON TABLE ressources IS 'Referentiel materiel de l''entreprise (LOG-01, LOG-02)';
COMMENT ON COLUMN ressources.type_ressource IS 'Type: levage, terrassement, vehicule, outillage, equipement';
COMMENT ON COLUMN ressources.validation_requise IS 'LOG-10: Si TRUE, demande doit etre validee par N+1';


-- -----------------------------------------------------------------------------
-- TABLE: reservations
-- Reservations de ressources par chantier (LOG-07 a LOG-12, LOG-16 a LOG-18)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reservations (
    -- Identifiant
    id SERIAL PRIMARY KEY,

    -- Relations obligatoires
    ressource_id INTEGER NOT NULL REFERENCES ressources(id) ON DELETE CASCADE,
    chantier_id INTEGER NOT NULL REFERENCES chantiers(id) ON DELETE CASCADE,
    demandeur_id INTEGER NOT NULL REFERENCES users(id) ON DELETE SET NULL,

    -- Valideur (NULL si pas encore traite ou validation non requise)
    valideur_id INTEGER REFERENCES users(id) ON DELETE SET NULL,

    -- Creneau de reservation (LOG-09)
    date_debut DATE NOT NULL,
    date_fin DATE NOT NULL,
    heure_debut VARCHAR(5) NOT NULL,  -- Format HH:MM
    heure_fin VARCHAR(5) NOT NULL,    -- Format HH:MM

    -- Statut de la reservation (LOG-11, LOG-12)
    -- Valeurs: 'en_attente' (jaune), 'validee' (vert), 'refusee' (rouge), 'annulee'
    statut VARCHAR(20) NOT NULL DEFAULT 'en_attente',

    -- Motif de refus (LOG-16) - rempli si statut = 'refusee'
    motif_refus TEXT,

    -- Note/commentaire du demandeur
    note TEXT,

    -- Horodatages des actions
    validated_at TIMESTAMP,
    refused_at TIMESTAMP,
    cancelled_at TIMESTAMP,

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Contrainte de coherence: date_fin >= date_debut
    CONSTRAINT ck_reservation_dates CHECK (date_fin >= date_debut)
);

-- Index pour les recherches frequentes
-- Planning par ressource (LOG-03, LOG-18)
CREATE INDEX IF NOT EXISTS ix_reservations_ressource_id ON reservations(ressource_id);
CREATE INDEX IF NOT EXISTS ix_reservations_ressource_dates ON reservations(ressource_id, date_debut, date_fin);

-- Planning par chantier
CREATE INDEX IF NOT EXISTS ix_reservations_chantier_id ON reservations(chantier_id);
CREATE INDEX IF NOT EXISTS ix_reservations_chantier_dates ON reservations(chantier_id, date_debut);

-- Reservations par demandeur/valideur
CREATE INDEX IF NOT EXISTS ix_reservations_demandeur_id ON reservations(demandeur_id);
CREATE INDEX IF NOT EXISTS ix_reservations_valideur_id ON reservations(valideur_id);

-- Recherche par statut (pour liste des demandes en attente)
CREATE INDEX IF NOT EXISTS ix_reservations_statut ON reservations(statut);
CREATE INDEX IF NOT EXISTS ix_reservations_statut_ressource ON reservations(statut, ressource_id);

-- Index pour detection de conflits (LOG-17)
-- Requete typique: trouver les reservations qui chevauchent un creneau donne
CREATE INDEX IF NOT EXISTS ix_reservations_conflit ON reservations(
    ressource_id,
    statut,
    date_debut,
    date_fin,
    heure_debut,
    heure_fin
);

-- Commentaires
COMMENT ON TABLE reservations IS 'Reservations de ressources par chantier (LOG-07 a LOG-18)';
COMMENT ON COLUMN reservations.statut IS 'LOG-12: en_attente (jaune), validee (vert), refusee (rouge), annulee';
COMMENT ON COLUMN reservations.motif_refus IS 'LOG-16: Motif du refus (optionnel)';


-- -----------------------------------------------------------------------------
-- TABLE: historique_reservations
-- Journal des actions sur les reservations (LOG-18)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS historique_reservations (
    id SERIAL PRIMARY KEY,

    -- Reservation concernee
    reservation_id INTEGER NOT NULL REFERENCES reservations(id) ON DELETE CASCADE,

    -- Action effectuee
    -- Valeurs: 'created', 'validated', 'refused', 'cancelled', 'modified'
    action VARCHAR(50) NOT NULL,

    -- Utilisateur ayant effectue l'action
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,

    -- Details de l'action (JSON pour flexibilite)
    details JSONB,

    -- Timestamp
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Index pour l'historique
CREATE INDEX IF NOT EXISTS ix_historique_reservations_reservation_id ON historique_reservations(reservation_id);
CREATE INDEX IF NOT EXISTS ix_historique_reservations_user_id ON historique_reservations(user_id);
CREATE INDEX IF NOT EXISTS ix_historique_reservations_action ON historique_reservations(action);
CREATE INDEX IF NOT EXISTS ix_historique_reservations_created_at ON historique_reservations(created_at);

-- Commentaire
COMMENT ON TABLE historique_reservations IS 'Historique des actions sur les reservations (LOG-18)';
COMMENT ON COLUMN historique_reservations.action IS 'Actions: created, validated, refused, cancelled, modified';


-- =============================================================================
-- REQUETES UTILES
-- =============================================================================

-- Requete: Trouver les conflits de reservation (LOG-17)
-- Detecte les reservations actives qui chevauchent un creneau donne
-- Parametres: :ressource_id, :date_debut, :date_fin, :heure_debut, :heure_fin, :exclude_id
/*
SELECT r.*
FROM reservations r
WHERE r.ressource_id = :ressource_id
  AND r.statut IN ('en_attente', 'validee')
  AND r.id != COALESCE(:exclude_id, 0)
  AND NOT (
      r.date_fin < :date_debut
      OR r.date_debut > :date_fin
  )
  AND NOT (
      r.heure_fin <= :heure_debut
      OR r.heure_debut >= :heure_fin
  );
*/

-- Requete: Planning d'une ressource pour une semaine (LOG-03)
-- Parametres: :ressource_id, :semaine_debut, :semaine_fin
/*
SELECT
    r.*,
    u.nom AS demandeur_nom,
    u.prenom AS demandeur_prenom,
    c.nom AS chantier_nom,
    c.code AS chantier_code
FROM reservations r
JOIN users u ON r.demandeur_id = u.id
JOIN chantiers c ON r.chantier_id = c.id
WHERE r.ressource_id = :ressource_id
  AND r.date_debut <= :semaine_fin
  AND r.date_fin >= :semaine_debut
  AND r.statut IN ('en_attente', 'validee')
ORDER BY r.date_debut, r.heure_debut;
*/

-- Requete: Reservations en attente de validation
-- Pour un chef/conducteur responsable d'un chantier
/*
SELECT
    r.*,
    res.nom AS ressource_nom,
    res.code AS ressource_code,
    u.nom AS demandeur_nom,
    c.nom AS chantier_nom
FROM reservations r
JOIN ressources res ON r.ressource_id = res.id
JOIN users u ON r.demandeur_id = u.id
JOIN chantiers c ON r.chantier_id = c.id
WHERE r.statut = 'en_attente'
  AND res.validation_requise = TRUE
  AND c.id IN (
      -- Chantiers ou l'utilisateur est chef ou conducteur
      SELECT id FROM chantiers
      WHERE :user_id = ANY(conducteur_ids)
         OR :user_id = ANY(chef_chantier_ids)
  )
ORDER BY r.created_at;
*/

-- Requete: Historique complet d'une reservation (LOG-18)
/*
SELECT
    h.*,
    u.nom AS user_nom,
    u.prenom AS user_prenom
FROM historique_reservations h
LEFT JOIN users u ON h.user_id = u.id
WHERE h.reservation_id = :reservation_id
ORDER BY h.created_at ASC;
*/


-- =============================================================================
-- DONNEES DE REFERENCE (optionnel - pour initialisation)
-- =============================================================================

-- Exemples de ressources Greg Constructions
/*
INSERT INTO ressources (code, nom, description, type_ressource, validation_requise, couleur) VALUES
-- Engins de levage (N+1 requis)
('LEV001', 'Grue mobile 40T', 'Grue mobile Liebherr 40 tonnes', 'levage', TRUE, '#E74C3C'),
('LEV002', 'Manitou MHT', 'Chariot telescopique Manitou', 'levage', TRUE, '#E67E22'),
('LEV003', 'Nacelle 20m', 'Nacelle articulee 20 metres', 'levage', TRUE, '#F1C40F'),

-- Engins de terrassement (N+1 requis)
('TER001', 'Mini-pelle 3T', 'Mini-pelle Kubota 3 tonnes', 'terrassement', TRUE, '#27AE60'),
('TER002', 'Pelleteuse 14T', 'Pelleteuse CAT 14 tonnes', 'terrassement', TRUE, '#2ECC71'),

-- Vehicules (Validation optionnelle)
('VEH001', 'Camion benne 8T', 'Camion benne Renault 8 tonnes', 'vehicule', FALSE, '#3498DB'),
('VEH002', 'Fourgon L3H2', 'Fourgon utilitaire', 'vehicule', FALSE, '#2980B9'),

-- Gros outillage (Validation optionnelle)
('OUT001', 'Betonniere 350L', 'Betonniere electrique 350 litres', 'outillage', FALSE, '#9B59B6'),
('OUT002', 'Vibrateur beton', 'Aiguille vibrante avec convertisseur', 'outillage', FALSE, '#8E44AD'),

-- Equipements (N+1 requis)
('EQP001', 'Echafaudage 100m2', 'Lot echafaudage multidirectionnel', 'equipement', TRUE, '#1ABC9C'),
('EQP002', 'Banches 50m2', 'Lot banches coffrage voiles', 'equipement', TRUE, '#16A085'),
('EQP003', 'Etais 3m', 'Lot 50 etais telescopiques 3m', 'equipement', TRUE, '#2C3E50');
*/
