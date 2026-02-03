#!/usr/bin/env python3
"""
Script de seed pour peupler la base de donnees avec des donnees de demonstration.

Usage:
    cd backend
    python -m scripts.seed_demo_data

Cree:
- 8 utilisateurs avec differents roles
- 5 chantiers
- Des affectations/planning
- Des pointages
- Des taches

CONFORMITE RGPD (Art. 5, 6, 13):
    Ce script utilise UNIQUEMENT des donnees fictives et anonymisees pour la demonstration.
    AUCUNE donnee personnelle reelle n'est utilisee sans consentement prealable.
    Les noms, prenoms, adresses et telephones sont entierement FICTIFS.

    Base legale: Art. 6(1)(f) - Interet legitime (demonstration et tests internes).
    Minimisation: Art. 5(1)(c) - Seules les donnees strictement necessaires sont generees.
    Information: Art. 13 - Les personnes concernees (utilisateurs demo) sont informees.
"""

import os
import sys
from datetime import date, datetime, timedelta, time
import asyncio

# Ajouter le chemin du backend pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bcrypt
from sqlalchemy.orm import Session

from shared.infrastructure.database import SessionLocal, init_db
from shared.infrastructure.event_bus import event_bus
from modules.auth.infrastructure.persistence.user_model import UserModel
from modules.chantiers.infrastructure.persistence.chantier_model import ChantierModel
from modules.planning.infrastructure.persistence.affectation_model import AffectationModel
from modules.planning.domain.events import AffectationCreatedEvent
from modules.pointages.infrastructure.persistence.models import PointageModel
from modules.taches.infrastructure.persistence import TacheModel
from modules.formulaires.infrastructure.persistence import (
    TemplateFormulaireModel,
    ChampTemplateModel,
    FormulaireRempliModel,
    ChampRempliModel,
    PhotoFormulaireModel,
)
from modules.financier.infrastructure.persistence.models import (
    BudgetModel,
    LotBudgetaireModel,
    AchatModel,
    FournisseurModel,
    SituationTravauxModel,
    FactureClientModel,
)
from modules.logistique.infrastructure.persistence.models import (
    RessourceModel,
    ReservationModel,
)
from modules.logistique.domain.value_objects import (
    CategorieRessource,
    StatutReservation,
)
from modules.devis.infrastructure.persistence.models import (
    ArticleDevisModel,
    DevisModel,
    LotDevisModel,
    LigneDevisModel,
    JournalDevisModel,
)


def hash_password(password: str) -> str:
    """Hash un mot de passe avec bcrypt (meme methode que le module auth)."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


# =============================================================================
# DONNEES DE DEMONSTRATION
# =============================================================================

USERS_DATA = [
    # Admin - pas de taux horaire (personnel administratif)
    {
        "email": "admin@example.com",
        "password": "Admin123!",
        "nom": "ADMIN",
        "prenom": "Super",
        "role": "admin",
        "type_utilisateur": "employe",
        "telephone": "00 00 00 00 01",
        "metiers": None,
        "code_utilisateur": "ADM001",
        "couleur": "#9B59B6",
        "taux_horaire": None,
    },
    {
        "email": "dupont.admin@example.com",
        "password": "Test123!",
        "nom": "DUPONT",
        "prenom": "Marie",
        "role": "admin",
        "type_utilisateur": "employe",
        "telephone": "00 00 00 00 02",
        "metiers": ["assistante_administrative"],
        "code_utilisateur": "ADM002",
        "couleur": "#8E44AD",
        "taux_horaire": None,
    },
    # Chefs de chantier et d'équipe - 50-55 EUR/h (cout entreprise avec charges)
    {
        "email": "martin.chef@example.com",
        "password": "Test123!",
        "nom": "MARTIN",
        "prenom": "Jean",
        "role": "chef_chantier",
        "type_utilisateur": "employe",
        "telephone": "00 00 00 00 03",
        "metiers": ["chef_chantier"],
        "code_utilisateur": "CHF001",
        "couleur": "#27AE60",
        "taux_horaire": 55.00,  # Chef de chantier senior
    },
    {
        "email": "bernard.chef@example.com",
        "password": "Test123!",
        "nom": "BERNARD",
        "prenom": "Pierre",
        "role": "chef_chantier",
        "type_utilisateur": "employe",
        "telephone": "00 00 00 00 04",
        "metiers": ["chef_equipe"],
        "code_utilisateur": "CHF002",
        "couleur": "#E67E22",
        "taux_horaire": 50.00,  # Chef d'equipe
    },
    {
        "email": "thomas.chef@example.com",
        "password": "Test123!",
        "nom": "THOMAS",
        "prenom": "Luc",
        "role": "chef_chantier",
        "type_utilisateur": "employe",
        "telephone": "00 00 00 00 05",
        "metiers": ["chef_equipe"],
        "code_utilisateur": "CHF003",
        "couleur": "#16A085",
        "taux_horaire": 50.00,  # Chef d'equipe
    },
    {
        "email": "petit.chef@example.com",
        "password": "Test123!",
        "nom": "PETIT",
        "prenom": "Marc",
        "role": "chef_chantier",
        "type_utilisateur": "employe",
        "telephone": "00 00 00 00 06",
        "metiers": ["chef_equipe"],
        "code_utilisateur": "CHF004",
        "couleur": "#D35400",
        "taux_horaire": 50.00,  # Chef d'equipe
    },
    # Compagnons - Macons qualifies 38-42 EUR/h
    {
        "email": "robert.macon@example.com",
        "password": "Test123!",
        "nom": "ROBERT",
        "prenom": "Paul",
        "role": "compagnon",
        "type_utilisateur": "employe",
        "telephone": "00 00 00 00 07",
        "metiers": ["macon"],
        "code_utilisateur": "CMP001",
        "couleur": "#E74C3C",
        "taux_horaire": 42.00,  # Macon qualifie senior
    },
    {
        "email": "richard.macon@example.com",
        "password": "Test123!",
        "nom": "RICHARD",
        "prenom": "Andre",
        "role": "compagnon",
        "type_utilisateur": "employe",
        "telephone": "00 00 00 00 08",
        "metiers": ["macon_coffreur"],
        "code_utilisateur": "CMP002",
        "couleur": "#C0392B",
        "taux_horaire": 44.00,  # Coffreur specialise
    },
    {
        "email": "durand.macon@example.com",
        "password": "Test123!",
        "nom": "DURAND",
        "prenom": "Francois",
        "role": "compagnon",
        "type_utilisateur": "employe",
        "telephone": "00 00 00 00 09",
        "metiers": ["macon"],
        "code_utilisateur": "CMP003",
        "couleur": "#E84393",
        "taux_horaire": 40.00,  # Macon qualifie
    },
    {
        "email": "dubois.macon@example.com",
        "password": "Test123!",
        "nom": "DUBOIS",
        "prenom": "Michel",
        "role": "compagnon",
        "type_utilisateur": "employe",
        "telephone": "00 00 00 00 10",
        "metiers": ["macon"],
        "code_utilisateur": "CMP004",
        "couleur": "#F1C40F",
        "taux_horaire": 40.00,  # Macon qualifie
    },
    {
        "email": "moreau.macon@example.com",
        "password": "Test123!",
        "nom": "MOREAU",
        "prenom": "Alain",
        "role": "compagnon",
        "type_utilisateur": "employe",
        "telephone": "00 00 00 00 11",
        "metiers": ["macon"],
        "code_utilisateur": "CMP005",
        "couleur": "#F39C12",
        "taux_horaire": 38.00,  # Macon
    },
    {
        "email": "laurent.macon@example.com",
        "password": "Test123!",
        "nom": "LAURENT",
        "prenom": "Bruno",
        "role": "compagnon",
        "type_utilisateur": "employe",
        "telephone": "00 00 00 00 12",
        "metiers": ["macon"],
        "code_utilisateur": "CMP006",
        "couleur": "#3498DB",
        "taux_horaire": 38.00,  # Macon
    },
    {
        "email": "simon.macon@example.com",
        "password": "Test123!",
        "nom": "SIMON",
        "prenom": "David",
        "role": "compagnon",
        "type_utilisateur": "employe",
        "telephone": "00 00 00 00 13",
        "metiers": ["macon_polyvalent"],
        "code_utilisateur": "CMP007",
        "couleur": "#2980B9",
        "taux_horaire": 40.00,  # Macon polyvalent
    },
    # Compagnons - Ouvriers 28-32 EUR/h
    {
        "email": "michel.ouvrier@example.com",
        "password": "Test123!",
        "nom": "MICHEL",
        "prenom": "Eric",
        "role": "compagnon",
        "type_utilisateur": "employe",
        "telephone": "00 00 00 00 14",
        "metiers": ["ouvrier"],
        "code_utilisateur": "CMP008",
        "couleur": "#9B59B6",
        "taux_horaire": 32.00,  # Ouvrier qualifie
    },
    {
        "email": "leroy.ouvrier@example.com",
        "password": "Test123!",
        "nom": "LEROY",
        "prenom": "Olivier",
        "role": "compagnon",
        "type_utilisateur": "employe",
        "telephone": "00 00 00 00 15",
        "metiers": ["ouvrier"],
        "code_utilisateur": "CMP009",
        "couleur": "#8E44AD",
        "taux_horaire": 30.00,  # Ouvrier
    },
    {
        "email": "lefebvre.ouvrier@example.com",
        "password": "Test123!",
        "nom": "LEFEBVRE",
        "prenom": "Vincent",
        "role": "compagnon",
        "type_utilisateur": "employe",
        "telephone": "00 00 00 00 16",
        "metiers": ["ouvrier"],
        "code_utilisateur": "CMP010",
        "couleur": "#1ABC9C",
        "taux_horaire": 30.00,  # Ouvrier
    },
    {
        "email": "garnier.ouvrier@example.com",
        "password": "Test123!",
        "nom": "GARNIER",
        "prenom": "Sebastien",
        "role": "compagnon",
        "type_utilisateur": "employe",
        "telephone": "00 00 00 00 17",
        "metiers": ["ouvrier"],
        "code_utilisateur": "CMP011",
        "couleur": "#16A085",
        "taux_horaire": 28.00,  # Ouvrier debutant
    },
    {
        "email": "roux.ouvrier@example.com",
        "password": "Test123!",
        "nom": "ROUX",
        "prenom": "Laurent",
        "role": "compagnon",
        "type_utilisateur": "employe",
        "telephone": "00 00 00 00 18",
        "metiers": ["ouvrier"],
        "code_utilisateur": "CMP012",
        "couleur": "#EC407A",
        "taux_horaire": 28.00,  # Ouvrier debutant
    },
    # Grutier - specialiste 45 EUR/h
    {
        "email": "blanc.grutier@example.com",
        "password": "Test123!",
        "nom": "BLANC",
        "prenom": "Nicolas",
        "role": "compagnon",
        "type_utilisateur": "employe",
        "telephone": "00 00 00 00 19",
        "metiers": ["grutier"],
        "code_utilisateur": "CMP013",
        "couleur": "#3F51B5",
        "taux_horaire": 45.00,  # Grutier specialise
    },
]

# Chantiers speciaux (conges, formations, etc.)
# Ces chantiers sont utilises pour les affectations hors chantier
CHANTIERS_SPECIAUX = [
    {
        "code": "CONGES",
        "nom": "Conges payes",
        "adresse": "-",
        "description": "Conges payes du personnel",
        "statut": "ouvert",
        "couleur": "#4CAF50",  # Vert
        "heures_estimees": 0,
    },
    {
        "code": "MALADIE",
        "nom": "Arret maladie",
        "adresse": "-",
        "description": "Arrets maladie",
        "statut": "ouvert",
        "couleur": "#F44336",  # Rouge
        "heures_estimees": 0,
    },
    {
        "code": "FORMATION",
        "nom": "Formation",
        "adresse": "-",
        "description": "Sessions de formation",
        "statut": "ouvert",
        "couleur": "#2196F3",  # Bleu
        "heures_estimees": 0,
    },
    {
        "code": "RTT",
        "nom": "RTT",
        "adresse": "-",
        "description": "Jours de RTT",
        "statut": "ouvert",
        "couleur": "#9C27B0",  # Violet
        "heures_estimees": 0,
    },
]

CHANTIERS_DATA = [
    # =============================================================================
    # CHANTIERS AVEC SCENARIOS DE DERIVE FINANCIERE POUR TEST IA
    # =============================================================================
    # Les scénarios sont conçus pour tester l'analyse Gemini avec des cas réalistes :
    # - Chantiers SAINS (marge 8-12% cible)
    # - Chantiers en DÉRIVE LÉGÈRE (marge 5-7%)
    # - Chantiers en DÉRIVE CRITIQUE (marge < 3% ou perte)
    # =============================================================================

    # === CHANTIER A : SAIN - Démarrage normal ===
    # Budget: 850k€ | Engagé: ~12k€ (1.4%) | Marge estimée: 10.5%
    {
        "code": "2025-03-TOURNON-COMMERCIAL",
        "nom": "Bâtiment commercial Ville-I",
        "adresse": "23 Boulevard Commerce, Ville-I, 00000",
        "description": "Bâtiment commercial 1200m² - Gros œuvre complet. Démarrage récent, sous contrôle.",
        "statut": "en_cours",
        "couleur": "#27AE60",  # Vert - Sain
        "contact_nom": "SCI Commerces Alpins",
        "contact_telephone": "04 79 00 01 10",
        "heures_estimees": 5666,  # ~850k€ / 150€/h
        "date_debut": date(2025, 10, 1),
        "date_fin": date(2026, 6, 30),
    },

    # === CHANTIER B : DÉRIVE LÉGÈRE - Hausse matériaux ===
    # Budget: 750k€ | Engagé: ~95k€ (12.7%) | Réalisé: 45k€ | Marge: 6.2%
    # Problèmes: hausse prix acier +15%, retard livraison béton → heures sup
    {
        "code": "2025-07-TOUR-LOGEMENTS",
        "nom": "20 logements Ville-P",
        "adresse": "33 Boulevard Habitat, Ville-P, 00000",
        "description": "20 logements collectifs R+3. Dérive légère: hausse acier +15%, heures sup.",
        "statut": "en_cours",
        "couleur": "#F39C12",  # Orange - Dérive légère
        "contact_nom": "Promoteur Alpes Habitat",
        "contact_telephone": "04 79 00 01 17",
        "heures_estimees": 5000,  # ~750k€ / 150€/h
        "date_debut": date(2025, 7, 1),
        "date_fin": date(2026, 9, 30),
    },

    # === CHANTIER C : DÉRIVE CRITIQUE - Sous-traitant liquidé ===
    # Budget: 1.2M€ | Engagé: 520k€ (43%) | Réalisé: 380k€ (32%) | Marge: 2.1%
    # Problèmes graves: ST ferraillage liquidé (reprise régie), erreur métré +180m³,
    # pénalités retard 15k€, burn rate 95k€/mois vs 70k€ prévu
    {
        "code": "2025-11-TRIALP",
        "nom": "Reconstruction hall de tri Ville-R",
        "adresse": "Zone Industrielle, Ville-R, 00000",
        "description": "Hall de tri 2500m² + bureaux. CRITIQUE: ST liquidé, erreur métré fondations.",
        "statut": "en_cours",
        "couleur": "#E74C3C",  # Rouge - Dérive critique
        "contact_nom": "TRIALP SA",
        "contact_telephone": "04 79 00 01 19",
        "heures_estimees": 8000,  # ~1.2M€ / 150€/h
        "date_debut": date(2025, 11, 1),
        "date_fin": date(2027, 6, 30),
    },

    # === CHANTIER D : DÉPASSEMENT BUDGET - Amiante découverte ===
    # Budget initial: 450k€ → Révisé: 520k€ (avenant) | Engagé: 485k€ (93%)
    # Réalisé: 410k€ | Marge: -3.5% (PERTE)
    # Problèmes: amiante non prévue (45k€), malfaçon dalle (28k€), litige MOA
    {
        "code": "2025-02-EPIERRE-GYMNASE",
        "nom": "Extension gymnase Ville-E",
        "adresse": "34 Rue Virtuelle, Ville-E, 00000",
        "description": "Extension gymnase 800m². PERTE: amiante découverte, malfaçon dalle à reprendre.",
        "statut": "en_cours",
        "couleur": "#8E44AD",  # Violet - Problème grave
        "contact_nom": "Mairie Ville-E",
        "contact_telephone": "04 79 00 01 05",
        "heures_estimees": 3000,  # ~450k€ / 150€/h initial
        "date_debut": date(2025, 2, 1),
        "date_fin": date(2025, 12, 31),
    },

    # === CHANTIER E : TRÈS RENTABLE - Client fidèle ===
    # Budget: 380k€ | Engagé: 42k€ (11%) | Réalisé: 38k€ | Marge: 14.2%
    # Situation favorable: client fidèle, équipe expérimentée, conditions météo OK
    {
        "code": "2025-04-CHIGNIN-AGRICOLE",
        "nom": "2 bâtiments agricoles Ville-J",
        "adresse": "67 Route Agricole, Ville-J, 00000",
        "description": "2 hangars agricoles 600m². Excellent: client fidèle, équipe rodée, marge 14%.",
        "statut": "en_cours",
        "couleur": "#2ECC71",  # Vert vif - Très rentable
        "contact_nom": "GAEC Dupont Frères",
        "contact_telephone": "04 79 00 01 11",
        "heures_estimees": 2533,  # ~380k€ / 150€/h
        "date_debut": date(2025, 4, 1),
        "date_fin": date(2026, 2, 28),
    },

    # === CHANTIER F : RÉCEPTIONNÉ - Référence terminée ===
    {
        "code": "2024-10-MONTMELIAN",
        "nom": "Ensemble immobilier Ville-A",
        "adresse": "123 Rue Fictive, Ville-A, 00000",
        "description": "Immeuble bureaux + 4 logements. Terminé avec marge 9.8% (référence).",
        "statut": "receptionne",
        "couleur": "#3498DB",
        "contact_nom": "SCI Montmélian Invest",
        "contact_telephone": "04 79 00 01 01",
        "heures_estimees": 5900,  # 886k€ / 150€/h
        "date_debut": date(2024, 10, 1),
        "date_fin": date(2025, 6, 30),
    },

    # === CHANTIER G : OUVERT - En préparation ===
    {
        "code": "2026-02-BISSY-COLLEGE",
        "nom": "Restructuration collège Ville-S",
        "adresse": "55 Avenue Education, Ville-S, 00000",
        "description": "Restructuration collège (marché public). Budget prévisionnel 794k€.",
        "statut": "ouvert",
        "couleur": "#00BCD4",
        "contact_nom": "Conseil Départemental",
        "contact_telephone": "04 79 00 01 20",
        "heures_estimees": 5293,  # 794k€ / 150€/h
        "date_debut": date(2026, 2, 1),
        "date_fin": date(2027, 2, 28),
    },

    # === CHANTIER H : OUVERT - Second projet ===
    {
        "code": "2026-03-RAVOIRE-CAPITE",
        "nom": "Logements sociaux Ville-T",
        "adresse": "18 Rue Sociale, Ville-T, 00000",
        "description": "32 logements sociaux. Budget prévisionnel 717k€, marge cible 10%.",
        "statut": "ouvert",
        "couleur": "#8BC34A",
        "contact_nom": "Savoie Habitat",
        "contact_telephone": "04 79 00 01 22",
        "heures_estimees": 4780,  # 717k€ / 150€/h
        "date_debut": date(2026, 3, 1),
        "date_fin": date(2027, 3, 31),
    },
]

TACHES_DATA = [
    # === CHANTIER A : TOURNON COMMERCIAL (SAIN) ===
    # Démarrage récent, phase initiale
    {"chantier_code": "2025-03-TOURNON-COMMERCIAL", "titre": "Installation chantier", "description": "Base vie, clôtures, panneau", "statut": "termine", "heures_estimees": 80},
    {"chantier_code": "2025-03-TOURNON-COMMERCIAL", "titre": "Terrassement général", "description": "Décapage, fouilles en masse", "statut": "en_cours", "heures_estimees": 600},
    {"chantier_code": "2025-03-TOURNON-COMMERCIAL", "titre": "Fondations semelles", "description": "Semelles filantes et isolées", "statut": "a_faire", "heures_estimees": 800},
    {"chantier_code": "2025-03-TOURNON-COMMERCIAL", "titre": "Longrines et dallage", "description": "Longrines BA et dallage industriel", "statut": "a_faire", "heures_estimees": 1200},
    {"chantier_code": "2025-03-TOURNON-COMMERCIAL", "titre": "Élévation murs", "description": "Murs porteurs et façades", "statut": "a_faire", "heures_estimees": 1500},
    {"chantier_code": "2025-03-TOURNON-COMMERCIAL", "titre": "Planchers et toiture", "description": "Planchers BA, charpente métallique", "statut": "a_faire", "heures_estimees": 1200},

    # === CHANTIER B : 20 LOGEMENTS TOUR (DÉRIVE LÉGÈRE) ===
    # Avancement 15%, problèmes acier et retards
    {"chantier_code": "2025-07-TOUR-LOGEMENTS", "titre": "Terrassement VRD", "description": "Terrassement et réseaux enterrés", "statut": "termine", "heures_estimees": 600},
    {"chantier_code": "2025-07-TOUR-LOGEMENTS", "titre": "Fondations bât A", "description": "Semelles et longrines bâtiment A", "statut": "termine", "heures_estimees": 800},
    {"chantier_code": "2025-07-TOUR-LOGEMENTS", "titre": "Élévation RDC bât A", "description": "Voiles, poteaux RDC - RETARD livraison acier", "statut": "en_cours", "heures_estimees": 1000},
    {"chantier_code": "2025-07-TOUR-LOGEMENTS", "titre": "Plancher haut RDC", "description": "Plancher BA R+1 - en attente ferraillage", "statut": "a_faire", "heures_estimees": 600},
    {"chantier_code": "2025-07-TOUR-LOGEMENTS", "titre": "Fondations bât B", "description": "Semelles et longrines bâtiment B", "statut": "a_faire", "heures_estimees": 800},
    {"chantier_code": "2025-07-TOUR-LOGEMENTS", "titre": "Suite élévations", "description": "R+1 à R+3 bâtiments A et B", "statut": "a_faire", "heures_estimees": 2200},

    # === CHANTIER C : TRIALP (DÉRIVE CRITIQUE) ===
    # Avancement 32%, ST liquidé, erreur métré, pénalités
    {"chantier_code": "2025-11-TRIALP", "titre": "Démolition hall", "description": "Démolition ancien hall - terminé", "statut": "termine", "heures_estimees": 1200},
    {"chantier_code": "2025-11-TRIALP", "titre": "Terrassement", "description": "Terrassement plateforme - terminé", "statut": "termine", "heures_estimees": 800},
    {"chantier_code": "2025-11-TRIALP", "titre": "Fondations - PROBLÈME", "description": "ERREUR MÉTRÉ: +180m³ béton non prévu", "statut": "termine", "heures_estimees": 1500},
    {"chantier_code": "2025-11-TRIALP", "titre": "Ferraillage - REPRISE RÉGIE", "description": "ST liquidé, reprise en régie interne", "statut": "en_cours", "heures_estimees": 1800},
    {"chantier_code": "2025-11-TRIALP", "titre": "Structure métallique", "description": "Charpente et bardage hall", "statut": "a_faire", "heures_estimees": 2000},
    {"chantier_code": "2025-11-TRIALP", "titre": "Bureaux R+1", "description": "Construction bureaux", "statut": "a_faire", "heures_estimees": 1200},

    # === CHANTIER D : GYMNASE EPIERRE (DÉPASSEMENT/PERTE) ===
    # Avancement 90%, découverte amiante, malfaçon dalle
    {"chantier_code": "2025-02-EPIERRE-GYMNASE", "titre": "Démolition partielle", "description": "Démolition extension existante", "statut": "termine", "heures_estimees": 400},
    {"chantier_code": "2025-02-EPIERRE-GYMNASE", "titre": "Désamiantage IMPRÉVU", "description": "Découverte amiante - intervention spécialisée", "statut": "termine", "heures_estimees": 200},
    {"chantier_code": "2025-02-EPIERRE-GYMNASE", "titre": "Fondations extension", "description": "Fondations nouvelle extension", "statut": "termine", "heures_estimees": 600},
    {"chantier_code": "2025-02-EPIERRE-GYMNASE", "titre": "Dalle béton - MALFAÇON", "description": "Reprise dalle suite malfaçon (fissuration)", "statut": "termine", "heures_estimees": 800},
    {"chantier_code": "2025-02-EPIERRE-GYMNASE", "titre": "Élévation murs", "description": "Murs porteurs et pignons", "statut": "en_cours", "heures_estimees": 600},
    {"chantier_code": "2025-02-EPIERRE-GYMNASE", "titre": "Finitions GO", "description": "Acrotères, seuils, finitions", "statut": "a_faire", "heures_estimees": 300},

    # === CHANTIER E : CHIGNIN AGRICOLE (TRÈS RENTABLE) ===
    # Avancement 25%, tout se passe bien
    {"chantier_code": "2025-04-CHIGNIN-AGRICOLE", "titre": "Terrassement", "description": "Plateforme et fouilles", "statut": "termine", "heures_estimees": 300},
    {"chantier_code": "2025-04-CHIGNIN-AGRICOLE", "titre": "Fondations hangar 1", "description": "Semelles isolées sous poteaux", "statut": "termine", "heures_estimees": 350},
    {"chantier_code": "2025-04-CHIGNIN-AGRICOLE", "titre": "Dallage hangar 1", "description": "Dallage béton 15cm", "statut": "en_cours", "heures_estimees": 400},
    {"chantier_code": "2025-04-CHIGNIN-AGRICOLE", "titre": "Fondations hangar 2", "description": "Semelles isolées hangar 2", "statut": "a_faire", "heures_estimees": 350},
    {"chantier_code": "2025-04-CHIGNIN-AGRICOLE", "titre": "Dallage hangar 2", "description": "Dallage béton hangar 2", "statut": "a_faire", "heures_estimees": 400},
    {"chantier_code": "2025-04-CHIGNIN-AGRICOLE", "titre": "Murs pignons", "description": "Murs BA pour les 2 hangars", "statut": "a_faire", "heures_estimees": 500},
]


def seed_users(db: Session) -> dict:
    """Cree les utilisateurs de demo. Retourne un dict email -> user_id."""
    print("\n=== Creation des utilisateurs ===")
    user_ids = {}

    for user_data in USERS_DATA:
        taux_horaire = user_data.get("taux_horaire")

        # Verifier si l'utilisateur existe deja
        existing = db.query(UserModel).filter(UserModel.email == user_data["email"]).first()
        if existing:
            # Mettre a jour le mot de passe et le taux horaire
            existing.password_hash = hash_password(user_data["password"])
            existing.is_active = True  # S'assurer que le compte est actif
            if taux_horaire is not None:
                existing.taux_horaire = taux_horaire
            taux_info = f" - {taux_horaire} EUR/h" if taux_horaire else ""
            print(f"  [MAJ] {user_data['prenom']} {user_data['nom']} ({user_data['role']}){taux_info}")
            user_ids[user_data["email"]] = existing.id
            continue

        # Creer le nouvel utilisateur
        user = UserModel(
            email=user_data["email"],
            password_hash=hash_password(user_data["password"]),
            nom=user_data["nom"],
            prenom=user_data["prenom"],
            role=user_data["role"],
            type_utilisateur=user_data["type_utilisateur"],
            telephone=user_data.get("telephone"),
            metiers=user_data.get("metiers"),
            code_utilisateur=user_data.get("code_utilisateur"),
            couleur=user_data.get("couleur", "#3498DB"),
            taux_horaire=taux_horaire,
            is_active=True,
        )
        db.add(user)
        db.flush()  # Pour obtenir l'ID
        user_ids[user_data["email"]] = user.id
        taux_info = f" - {taux_horaire} EUR/h" if taux_horaire else ""
        print(f"  [CREE] {user_data['prenom']} {user_data['nom']} ({user_data['role']}){taux_info} - ID: {user.id}")

    db.commit()
    return user_ids


def seed_chantiers(db: Session, user_ids: dict) -> dict:
    """Cree les chantiers de demo. Retourne un dict code -> chantier_id."""
    print("\n=== Creation des chantiers ===")
    chantier_ids = {}

    # Recuperer les IDs des conducteurs et chefs
    # Note: Ces utilisateurs n'existent pas dans USERS_DATA, donc conducteur_ids et chef_ids seront vides
    conducteur_ids = [
        user_ids.get("admin@example.com"),  # Utiliser l'admin par défaut
        user_ids.get("dupont.admin@example.com"),
    ]
    chef_ids = [
        user_ids.get("martin.chef@example.com"),
        user_ids.get("bernard.chef@example.com"),
    ]

    # D'abord creer les chantiers speciaux (conges, formations, etc.)
    print("  -- Chantiers speciaux --")
    for chantier_data in CHANTIERS_SPECIAUX:
        existing = db.query(ChantierModel).filter(ChantierModel.code == chantier_data["code"]).first()
        if existing:
            print(f"  [EXISTE] {chantier_data['code']} - {chantier_data['nom']}")
            chantier_ids[chantier_data["code"]] = existing.id
            continue

        chantier = ChantierModel(
            code=chantier_data["code"],
            nom=chantier_data["nom"],
            adresse=chantier_data["adresse"],
            description=chantier_data.get("description"),
            statut=chantier_data["statut"],
            couleur=chantier_data.get("couleur", "#607D8B"),
            heures_estimees=chantier_data.get("heures_estimees", 0),
            conducteur_ids=[],
            chef_chantier_ids=[],
        )
        db.add(chantier)
        db.flush()
        chantier_ids[chantier_data["code"]] = chantier.id
        print(f"  [CREE] {chantier_data['code']} - {chantier_data['nom']} (ID: {chantier.id})")

    # Ensuite les chantiers normaux
    print("  -- Chantiers de travaux --")
    for i, chantier_data in enumerate(CHANTIERS_DATA):
        # Verifier si le chantier existe deja
        existing = db.query(ChantierModel).filter(ChantierModel.code == chantier_data["code"]).first()
        if existing:
            print(f"  [EXISTE] {chantier_data['code']} - {chantier_data['nom']}")
            chantier_ids[chantier_data["code"]] = existing.id
            continue

        # Assigner des conducteurs et chefs en rotation
        assigned_conducteurs = [conducteur_ids[i % len(conducteur_ids)]] if conducteur_ids[0] else []
        assigned_chefs = [chef_ids[i % len(chef_ids)]] if chef_ids[0] else []

        chantier = ChantierModel(
            code=chantier_data["code"],
            nom=chantier_data["nom"],
            adresse=chantier_data["adresse"],
            description=chantier_data.get("description"),
            statut=chantier_data["statut"],
            couleur=chantier_data.get("couleur", "#3498DB"),
            latitude=chantier_data.get("latitude"),
            longitude=chantier_data.get("longitude"),
            contact_nom=chantier_data.get("contact_nom"),
            contact_telephone=chantier_data.get("contact_telephone"),
            maitre_ouvrage=chantier_data.get("contact_nom"),  # Utiliser contact_nom comme maître d'ouvrage
            heures_estimees=chantier_data.get("heures_estimees"),
            date_debut=chantier_data.get("date_debut"),
            date_fin=chantier_data.get("date_fin"),
            conducteur_ids=assigned_conducteurs,
            chef_chantier_ids=assigned_chefs,
        )
        db.add(chantier)
        db.flush()
        chantier_ids[chantier_data["code"]] = chantier.id
        print(f"  [CREE] {chantier_data['code']} - {chantier_data['nom']} (ID: {chantier.id})")

    db.commit()
    return chantier_ids


def seed_affectations(db: Session, user_ids: dict, chantier_ids: dict):
    """Cree des affectations de planning pour la semaine en cours."""
    print("\n=== Creation des affectations (planning) ===")

    # Obtenir le lundi de cette semaine
    today = date.today()
    monday = today - timedelta(days=today.weekday())

    # Affectations pour les chantiers en cours - Distribution réaliste des compagnons
    affectations_data = [
        # TRIALP (DÉRIVE CRITIQUE) - 6 compagnons + grutier
        ("robert.macon@example.com", "2025-11-TRIALP"),
        ("richard.macon@example.com", "2025-11-TRIALP"),
        ("durand.macon@example.com", "2025-11-TRIALP"),
        ("dubois.macon@example.com", "2025-11-TRIALP"),
        ("moreau.macon@example.com", "2025-11-TRIALP"),
        ("laurent.macon@example.com", "2025-11-TRIALP"),
        ("blanc.grutier@example.com", "2025-11-TRIALP"),

        # 20 logements Tour (DÉRIVE LÉGÈRE) - 4 compagnons
        ("simon.macon@example.com", "2025-07-TOUR-LOGEMENTS"),
        ("michel.ouvrier@example.com", "2025-07-TOUR-LOGEMENTS"),
        ("leroy.ouvrier@example.com", "2025-07-TOUR-LOGEMENTS"),
        ("lefebvre.ouvrier@example.com", "2025-07-TOUR-LOGEMENTS"),

        # Tournon Commercial (SAIN) - 2 compagnons (démarrage)
        ("garnier.ouvrier@example.com", "2025-03-TOURNON-COMMERCIAL"),
        ("roux.ouvrier@example.com", "2025-03-TOURNON-COMMERCIAL"),

        # Chignin Agricole (TRÈS RENTABLE) - équipe réduite efficace
        # (pas d'affectation cette semaine - chantier bien avancé)

        # Gymnase Epierre (PERTE) - finitions
        # (équipe réduite, quasi terminé)

        # Chefs de chantier assignés
        ("martin.chef@example.com", "2025-11-TRIALP"),  # Chef sur TRIALP (critique)
        ("bernard.chef@example.com", "2025-07-TOUR-LOGEMENTS"),  # Chef sur Tour
        ("thomas.chef@example.com", "2025-03-TOURNON-COMMERCIAL"),  # Chef sur Tournon
        ("petit.chef@example.com", "2025-04-CHIGNIN-AGRICOLE"),  # Chef sur Chignin
    ]

    # Admin qui cree les affectations
    admin_id = user_ids.get("admin@example.com") or 1

    created_count = 0

    for email, chantier_code in affectations_data:
        user_id = user_ids.get(email)
        chantier_id = chantier_ids.get(chantier_code)

        if not user_id or not chantier_id:
            continue

        # Creer des affectations du lundi au vendredi
        for day_offset in range(5):  # Lundi a vendredi
            affectation_date = monday + timedelta(days=day_offset)

            # Verifier si existe deja
            existing = db.query(AffectationModel).filter(
                AffectationModel.utilisateur_id == user_id,
                AffectationModel.date == affectation_date
            ).first()

            if existing:
                continue

            affectation = AffectationModel(
                utilisateur_id=user_id,
                chantier_id=chantier_id,
                date=affectation_date,
                heure_debut="07:30",
                heure_fin="16:30",
                type_affectation="unique",
                created_by=admin_id,
            )
            db.add(affectation)
            created_count += 1

    db.commit()
    print(f"  [CREE] {created_count} affectations pour la semaine du {monday}")
    print(f"  [INFO] Les pointages seront créés automatiquement par FDH-10 lors de la première utilisation")


def seed_taches(db: Session, chantier_ids: dict):
    """Cree des taches pour les chantiers."""
    print("\n=== Creation des taches ===")

    created_count = 0
    for i, tache_data in enumerate(TACHES_DATA):
        chantier_id = chantier_ids.get(tache_data["chantier_code"])
        if not chantier_id:
            continue

        # Verifier si existe deja (par titre et chantier)
        existing = db.query(TacheModel).filter(
            TacheModel.chantier_id == chantier_id,
            TacheModel.titre == tache_data["titre"]
        ).first()

        if existing:
            print(f"  [EXISTE] {tache_data['titre']}")
            continue

        tache = TacheModel(
            chantier_id=chantier_id,
            titre=tache_data["titre"],
            description=tache_data.get("description"),
            statut=tache_data["statut"],
            ordre=i + 1,
            heures_estimees=tache_data.get("heures_estimees"),
            heures_realisees=0,
            quantite_realisee=0,
        )
        db.add(tache)
        created_count += 1

    db.commit()
    print(f"  [CREE] {created_count} taches")


def seed_pointages_valides(db: Session, user_ids: dict, chantier_ids: dict):
    """Cree des pointages VALIDES historiques pour generer le cout MO.

    Les heures sont calibrees pour obtenir les marges cibles :
    - Marge BTP = (Prix Vente - Cout Revient) / Prix Vente
    - Cout Revient = Achats realises + Cout MO

    Configuration des couts MO par chantier :
    - TOURNON : ~19,750 EUR (395h x 50 EUR/h moyen)
    - TOUR : ~72,500 EUR (1,812h x 40 EUR/h moyen)
    - TRIALP : ~32,760 EUR (780h x 42 EUR/h moyen)
    - GYMNASE : ~39,650 EUR (965h x 41 EUR/h moyen)
    - CHIGNIN : ~15,400 EUR (385h x 40 EUR/h moyen)
    """
    print("\n=== Creation des pointages valides (cout MO) ===")
    admin_id = user_ids.get("admin@example.com") or 1

    # Configuration des pointages par chantier
    # Les heures sont distribuees sur plusieurs semaines passees
    # pour simuler l'historique du chantier
    POINTAGES_CONFIG = [
        # TOURNON (sain) - 395h total, marge 10%
        # Demarrage recent, peu d'heures, 2 ouvriers + 1 chef partiel
        {
            "chantier_code": "2025-03-TOURNON-COMMERCIAL",
            "semaines": 4,  # 4 semaines de travail
            "equipe": [
                ("garnier.ouvrier@example.com", 35),  # 35h/sem ouvrier 1
                ("roux.ouvrier@example.com", 35),     # 35h/sem ouvrier 2
                ("thomas.chef@example.com", 20),      # 20h/sem chef (partiel)
            ],
        },
        # TOUR-LOGEMENTS (derive legere) - 1,812h total, marge 6%
        # Chantier bien avance, 6 personnes sur 8 semaines
        {
            "chantier_code": "2025-07-TOUR-LOGEMENTS",
            "semaines": 8,
            "equipe": [
                ("simon.macon@example.com", 38),
                ("michel.ouvrier@example.com", 38),
                ("leroy.ouvrier@example.com", 38),
                ("lefebvre.ouvrier@example.com", 38),
                ("dubois.macon@example.com", 35),
                ("bernard.chef@example.com", 25),
            ],
        },
        # TRIALP (derive critique) - 780h total, marge 2%
        # Equipe surchargee pendant 4 semaines intensives (problemes ST)
        {
            "chantier_code": "2025-11-TRIALP",
            "semaines": 4,
            "equipe": [
                ("robert.macon@example.com", 42),     # Heures sup
                ("richard.macon@example.com", 42),
                ("durand.macon@example.com", 38),
                ("moreau.macon@example.com", 38),
                ("martin.chef@example.com", 25),
            ],
        },
        # GYMNASE (perte) - 965h total, marge -4%
        # Chantier ancien, beaucoup d'heures sur 6 semaines
        {
            "chantier_code": "2025-02-EPIERRE-GYMNASE",
            "semaines": 6,
            "equipe": [
                ("laurent.macon@example.com", 40),
                ("dubois.macon@example.com", 40),
                ("garnier.ouvrier@example.com", 38),
                ("petit.chef@example.com", 22),
            ],
        },
        # CHIGNIN (rentable) - 385h total, marge 14%
        # Equipe efficace sur 3 semaines
        {
            "chantier_code": "2025-04-CHIGNIN-AGRICOLE",
            "semaines": 3,
            "equipe": [
                ("moreau.macon@example.com", 40),
                ("laurent.macon@example.com", 40),
                ("roux.ouvrier@example.com", 35),
                ("petit.chef@example.com", 15),
            ],
        },
    ]

    created_count = 0
    total_cout_mo = 0

    for config in POINTAGES_CONFIG:
        chantier_code = config["chantier_code"]
        chantier_id = chantier_ids.get(chantier_code)

        if not chantier_id:
            print(f"  [SKIP] {chantier_code} - chantier non trouve")
            continue

        cout_chantier = 0
        heures_chantier = 0

        # Calculer la date de debut (semaines avant aujourd'hui)
        today = date.today()
        start_date = today - timedelta(weeks=config["semaines"])

        for email, heures_semaine in config["equipe"]:
            user_id = user_ids.get(email)
            if not user_id:
                continue

            # Recuperer le taux horaire de l'utilisateur
            user = db.query(UserModel).filter(UserModel.id == user_id).first()
            taux = float(user.taux_horaire) if user and user.taux_horaire else 35.0

            # Creer un pointage par semaine
            for week in range(config["semaines"]):
                week_start = start_date + timedelta(weeks=week)

                # Un pointage par jour de travail (5 jours)
                heures_par_jour = heures_semaine / 5
                for day in range(5):
                    pointage_date = week_start + timedelta(days=day)

                    # Verifier si existe deja
                    existing = db.query(PointageModel).filter(
                        PointageModel.utilisateur_id == user_id,
                        PointageModel.chantier_id == chantier_id,
                        PointageModel.date_pointage == pointage_date,
                    ).first()

                    if existing:
                        # Mettre a jour le statut a valide si necessaire
                        if existing.statut != "valide":
                            existing.statut = "valide"
                            existing.validateur_id = admin_id
                            existing.validation_date = datetime.now()
                        continue

                    # Convertir heures en minutes
                    heures_normales_min = int(heures_par_jour * 60)
                    heures_sup_min = 0
                    if heures_par_jour > 8:
                        heures_normales_min = 8 * 60
                        heures_sup_min = int((heures_par_jour - 8) * 60)

                    pointage = PointageModel(
                        utilisateur_id=user_id,
                        chantier_id=chantier_id,
                        date_pointage=pointage_date,
                        heures_normales_minutes=heures_normales_min,
                        heures_supplementaires_minutes=heures_sup_min,
                        statut="valide",
                        validateur_id=admin_id,
                        validation_date=datetime.now(),
                        created_by=admin_id,
                    )
                    db.add(pointage)
                    created_count += 1

                    # Calculer le cout
                    heures_total = (heures_normales_min + heures_sup_min) / 60
                    cout_chantier += heures_total * taux
                    heures_chantier += heures_total

        total_cout_mo += cout_chantier
        chantier_nom = chantier_code.split("-")[-1]
        print(f"  [CREE] {chantier_nom}: {heures_chantier:,.0f}h -> {cout_chantier:,.0f} EUR")

    db.commit()
    print(f"\n  [TOTAL] {created_count} pointages valides")
    print(f"  [TOTAL] Cout MO: {total_cout_mo:,.0f} EUR")


TEMPLATES_FORMULAIRES_DATA = [
    {
        "nom": "Rapport journalier de chantier",
        "categorie": "intervention",
        "description": "Rapport quotidien a remplir par le chef de chantier en fin de journee",
        "champs": [
            {"nom": "date_intervention", "label": "Date", "type_champ": "date", "obligatoire": True, "ordre": 1},
            {"nom": "meteo", "label": "Conditions meteo", "type_champ": "select", "obligatoire": True, "ordre": 2, "options": ["Beau temps", "Nuageux", "Pluie legere", "Pluie forte", "Neige", "Gel"]},
            {"nom": "nb_ouvriers", "label": "Nombre d'ouvriers presents", "type_champ": "nombre", "obligatoire": True, "ordre": 3, "min_value": 0, "max_value": 50},
            {"nom": "travaux_realises", "label": "Travaux realises", "type_champ": "texte_long", "obligatoire": True, "ordre": 4, "placeholder": "Decrire les travaux effectues..."},
            {"nom": "materiaux_utilises", "label": "Materiaux utilises", "type_champ": "texte_long", "obligatoire": False, "ordre": 5},
            {"nom": "problemes", "label": "Problemes rencontres", "type_champ": "texte_long", "obligatoire": False, "ordre": 6},
            {"nom": "photo_avancement", "label": "Photo d'avancement", "type_champ": "photo", "obligatoire": False, "ordre": 7},
            {"nom": "signature_chef", "label": "Signature du chef de chantier", "type_champ": "signature", "obligatoire": True, "ordre": 8},
        ],
    },
    {
        "nom": "Fiche de reception travaux",
        "categorie": "reception",
        "description": "Formulaire de reception des travaux avec le client",
        "champs": [
            {"nom": "date_reception", "label": "Date de reception", "type_champ": "date", "obligatoire": True, "ordre": 1},
            {"nom": "lot_concerne", "label": "Lot concerne", "type_champ": "select", "obligatoire": True, "ordre": 2, "options": ["Gros oeuvre", "Charpente", "Couverture", "Electricite", "Plomberie", "Peinture", "Menuiserie", "Autre"]},
            {"nom": "conformite", "label": "Travaux conformes au cahier des charges", "type_champ": "radio", "obligatoire": True, "ordre": 3, "options": ["Oui", "Non", "Avec reserves"]},
            {"nom": "reserves", "label": "Liste des reserves", "type_champ": "texte_long", "obligatoire": False, "ordre": 4, "placeholder": "Detailler les reserves eventuelles..."},
            {"nom": "delai_levee", "label": "Delai de levee des reserves (jours)", "type_champ": "nombre", "obligatoire": False, "ordre": 5, "min_value": 1, "max_value": 90},
            {"nom": "photo_reception", "label": "Photos de reception", "type_champ": "photo", "obligatoire": False, "ordre": 6},
            {"nom": "signature_client", "label": "Signature du client", "type_champ": "signature", "obligatoire": True, "ordre": 7},
            {"nom": "signature_conducteur", "label": "Signature du conducteur", "type_champ": "signature", "obligatoire": True, "ordre": 8},
        ],
    },
    {
        "nom": "Inspection securite hebdomadaire",
        "categorie": "securite",
        "description": "Check-list securite a realiser chaque semaine sur le chantier",
        "champs": [
            {"nom": "date_inspection", "label": "Date d'inspection", "type_champ": "date", "obligatoire": True, "ordre": 1},
            {"nom": "epi_portes", "label": "EPI portes par tous", "type_champ": "radio", "obligatoire": True, "ordre": 2, "options": ["Oui", "Non"]},
            {"nom": "balisage_ok", "label": "Balisage et signalisation en place", "type_champ": "radio", "obligatoire": True, "ordre": 3, "options": ["Oui", "Non", "Partiel"]},
            {"nom": "echafaudages_ok", "label": "Echafaudages conformes", "type_champ": "radio", "obligatoire": True, "ordre": 4, "options": ["Oui", "Non", "N/A"]},
            {"nom": "proprete_chantier", "label": "Proprete du chantier", "type_champ": "select", "obligatoire": True, "ordre": 5, "options": ["Tres bien", "Bien", "Acceptable", "A ameliorer", "Non conforme"]},
            {"nom": "anomalies", "label": "Anomalies constatees", "type_champ": "texte_long", "obligatoire": False, "ordre": 6},
            {"nom": "actions_correctives", "label": "Actions correctives", "type_champ": "texte_long", "obligatoire": False, "ordre": 7},
            {"nom": "photo_anomalie", "label": "Photo anomalie", "type_champ": "photo", "obligatoire": False, "ordre": 8},
            {"nom": "signature_inspecteur", "label": "Signature de l'inspecteur", "type_champ": "signature", "obligatoire": True, "ordre": 9},
        ],
    },
    {
        "nom": "Declaration d'incident",
        "categorie": "incident",
        "description": "Formulaire de declaration d'incident ou accident sur chantier",
        "champs": [
            {"nom": "date_incident", "label": "Date de l'incident", "type_champ": "date", "obligatoire": True, "ordre": 1},
            {"nom": "heure_incident", "label": "Heure de l'incident", "type_champ": "heure", "obligatoire": True, "ordre": 2},
            {"nom": "type_incident", "label": "Type d'incident", "type_champ": "select", "obligatoire": True, "ordre": 3, "options": ["Accident corporel", "Presqu'accident", "Dommage materiel", "Incident environnemental", "Autre"]},
            {"nom": "gravite", "label": "Gravite", "type_champ": "select", "obligatoire": True, "ordre": 4, "options": ["Mineur", "Modere", "Grave", "Tres grave"]},
            {"nom": "personnes_impliquees", "label": "Personnes impliquees", "type_champ": "texte_long", "obligatoire": True, "ordre": 5},
            {"nom": "description_faits", "label": "Description des faits", "type_champ": "texte_long", "obligatoire": True, "ordre": 6, "placeholder": "Decrire precisement les circonstances..."},
            {"nom": "mesures_prises", "label": "Mesures prises immediatement", "type_champ": "texte_long", "obligatoire": True, "ordre": 7},
            {"nom": "temoins", "label": "Temoins", "type_champ": "texte", "obligatoire": False, "ordre": 8},
            {"nom": "photo_incident", "label": "Photos", "type_champ": "photo", "obligatoire": False, "ordre": 9},
            {"nom": "signature_declarant", "label": "Signature du declarant", "type_champ": "signature", "obligatoire": True, "ordre": 10},
        ],
    },
    {
        "nom": "Bon de livraison materiaux",
        "categorie": "approvisionnement",
        "description": "Formulaire de reception de livraison de materiaux",
        "champs": [
            {"nom": "date_livraison", "label": "Date de livraison", "type_champ": "date", "obligatoire": True, "ordre": 1},
            {"nom": "fournisseur", "label": "Fournisseur", "type_champ": "texte", "obligatoire": True, "ordre": 2},
            {"nom": "bon_numero", "label": "Numero du bon de livraison", "type_champ": "texte", "obligatoire": True, "ordre": 3},
            {"nom": "materiaux", "label": "Materiaux livres", "type_champ": "texte_long", "obligatoire": True, "ordre": 4, "placeholder": "Lister les materiaux et quantites..."},
            {"nom": "conforme_commande", "label": "Conforme a la commande", "type_champ": "radio", "obligatoire": True, "ordre": 5, "options": ["Oui", "Non", "Partiel"]},
            {"nom": "etat_materiaux", "label": "Etat des materiaux", "type_champ": "select", "obligatoire": True, "ordre": 6, "options": ["Bon etat", "Dommages mineurs", "Dommages importants"]},
            {"nom": "remarques", "label": "Remarques", "type_champ": "texte_long", "obligatoire": False, "ordre": 7},
            {"nom": "photo_livraison", "label": "Photo de la livraison", "type_champ": "photo", "obligatoire": False, "ordre": 8},
            {"nom": "signature_recepteur", "label": "Signature du receptionnaire", "type_champ": "signature", "obligatoire": True, "ordre": 9},
        ],
    },
    {
        "nom": "Controle beton - eprouvettes",
        "categorie": "gros_oeuvre",
        "description": "Fiche de suivi des eprouvettes beton pour controle qualite",
        "champs": [
            {"nom": "date_coulage", "label": "Date de coulage", "type_champ": "date", "obligatoire": True, "ordre": 1},
            {"nom": "type_beton", "label": "Type de beton", "type_champ": "select", "obligatoire": True, "ordre": 2, "options": ["C25/30", "C30/37", "C35/45", "C40/50", "Autre"]},
            {"nom": "volume_coule", "label": "Volume coule (m3)", "type_champ": "nombre", "obligatoire": True, "ordre": 3, "min_value": 0},
            {"nom": "localisation_ouvrage", "label": "Localisation de l'ouvrage", "type_champ": "texte", "obligatoire": True, "ordre": 4, "placeholder": "Ex: Dalle RDC, Poteau B3..."},
            {"nom": "nb_eprouvettes", "label": "Nombre d'eprouvettes", "type_champ": "nombre", "obligatoire": True, "ordre": 5, "min_value": 1, "max_value": 20},
            {"nom": "temperature_exterieure", "label": "Temperature exterieure (C)", "type_champ": "nombre", "obligatoire": False, "ordre": 6, "min_value": -10, "max_value": 45},
            {"nom": "observations", "label": "Observations", "type_champ": "texte_long", "obligatoire": False, "ordre": 7},
            {"nom": "photo_coulage", "label": "Photo du coulage", "type_champ": "photo", "obligatoire": False, "ordre": 8},
        ],
    },
]


def seed_templates_formulaires(db: Session, user_ids: dict) -> dict:
    """Cree les templates de formulaire. Retourne un dict nom -> template_id."""
    print("\n=== Creation des templates de formulaire ===")
    template_ids = {}
    admin_id = user_ids.get("admin@example.com") or 1

    for tpl_data in TEMPLATES_FORMULAIRES_DATA:
        existing = db.query(TemplateFormulaireModel).filter(
            TemplateFormulaireModel.nom == tpl_data["nom"]
        ).first()

        if existing:
            print(f"  [EXISTE] {tpl_data['nom']}")
            template_ids[tpl_data["nom"]] = existing.id
            continue

        template = TemplateFormulaireModel(
            nom=tpl_data["nom"],
            description=tpl_data.get("description"),
            categorie=tpl_data["categorie"],
            is_active=True,
            version=1,
            created_by=admin_id,
        )
        db.add(template)
        db.flush()

        # Creer les champs du template
        for champ_data in tpl_data.get("champs", []):
            champ = ChampTemplateModel(
                template_id=template.id,
                nom=champ_data["nom"],
                label=champ_data["label"],
                type_champ=champ_data["type_champ"],
                obligatoire=champ_data.get("obligatoire", False),
                ordre=champ_data.get("ordre", 0),
                placeholder=champ_data.get("placeholder"),
                options=champ_data.get("options"),
                valeur_defaut=champ_data.get("valeur_defaut"),
                validation_regex=champ_data.get("validation_regex"),
                min_value=champ_data.get("min_value"),
                max_value=champ_data.get("max_value"),
            )
            db.add(champ)

        template_ids[tpl_data["nom"]] = template.id
        print(f"  [CREE] {tpl_data['nom']} ({tpl_data['categorie']}, {len(tpl_data.get('champs', []))} champs) - ID: {template.id}")

    db.commit()
    return template_ids


def seed_formulaires_remplis(db: Session, user_ids: dict, chantier_ids: dict, template_ids: dict):
    """Cree des formulaires remplis de demonstration."""
    print("\n=== Creation des formulaires remplis ===")

    today = date.today()
    created_count = 0

    # Formulaires a creer : (template_nom, chantier_code, user_email, statut, jours_avant, champs_values)
    # Note: Les formulaires de demo sont optionnels - les codes chantiers fictifs A001, A002, etc. n'existent pas
    # Cette section peut être commentée ou les codes remplacés par des chantiers réels
    formulaires_data = [
        # Rapports journaliers (codes chantiers fictifs - à adapter)
        {
            "template": "Rapport journalier de chantier",
            "chantier": "2025-11-TRIALP",  # Chantier réel existant
            "user": "bernard.chef@example.com",
            "statut": "valide",
            "jours_avant": 3,
            "champs": [
                {"nom": "date_intervention", "type_champ": "date", "valeur": str(today - timedelta(days=3))},
                {"nom": "meteo", "type_champ": "select", "valeur": "Beau temps"},
                {"nom": "nb_ouvriers", "type_champ": "nombre", "valeur": 8},
                {"nom": "travaux_realises", "type_champ": "texte_long", "valeur": "Coulage dalle RDC batiment B. Ferraillage escalier central."},
                {"nom": "materiaux_utilises", "type_champ": "texte_long", "valeur": "12m3 beton C30/37, 2T acier HA"},
                {"nom": "problemes", "type_champ": "texte_long", "valeur": ""},
            ],
            "photos": [
                {"url": "https://picsum.photos/seed/dalle-rdc/800/600", "nom_fichier": "coulage_dalle_rdc_bat_b.jpg", "champ_nom": "photo_avancement"},
                {"url": "https://picsum.photos/seed/ferraillage/800/600", "nom_fichier": "ferraillage_escalier_central.jpg", "champ_nom": "photo_avancement"},
                {"url": "https://picsum.photos/seed/beton-c30/800/600", "nom_fichier": "livraison_beton_c30.jpg", "champ_nom": "photo_avancement"},
            ],
        },
        {
            "template": "Rapport journalier de chantier",
            "chantier": "2025-11-TRIALP",
            "user": "bernard.chef@example.com",
            "statut": "soumis",
            "jours_avant": 1,
            "champs": [
                {"nom": "date_intervention", "type_champ": "date", "valeur": str(today - timedelta(days=1))},
                {"nom": "meteo", "type_champ": "select", "valeur": "Nuageux"},
                {"nom": "nb_ouvriers", "type_champ": "nombre", "valeur": 6},
                {"nom": "travaux_realises", "type_champ": "texte_long", "valeur": "Elevation murs 1er etage. Pose coffrage poteau P4."},
                {"nom": "materiaux_utilises", "type_champ": "texte_long", "valeur": "800 parpaings, 50 sacs ciment"},
                {"nom": "problemes", "type_champ": "texte_long", "valeur": "Retard livraison aciers prevu demain"},
            ],
            "photos": [
                {"url": "https://picsum.photos/seed/murs-1er/800/600", "nom_fichier": "elevation_murs_1er_etage.jpg", "champ_nom": "photo_avancement"},
                {"url": "https://picsum.photos/seed/coffrage-p4/800/600", "nom_fichier": "coffrage_poteau_p4.jpg", "champ_nom": "photo_avancement"},
            ],
        },
        # Rapport sur autre chantier
        {
            "template": "Rapport journalier de chantier",
            "chantier": "2025-07-TOUR-LOGEMENTS",
            "user": "martin.chef@example.com",
            "statut": "valide",
            "jours_avant": 2,
            "champs": [
                {"nom": "date_intervention", "type_champ": "date", "valeur": str(today - timedelta(days=2))},
                {"nom": "meteo", "type_champ": "select", "valeur": "Pluie legere"},
                {"nom": "nb_ouvriers", "type_champ": "nombre", "valeur": 12},
                {"nom": "travaux_realises", "type_champ": "texte_long", "valeur": "Montage structure metallique zone A. Soudure portiques."},
                {"nom": "materiaux_utilises", "type_champ": "texte_long", "valeur": "IPE 300, HEA 200, boulons HR"},
                {"nom": "problemes", "type_champ": "texte_long", "valeur": "Arret 2h pour pluie"},
            ],
            "photos": [
                {"url": "https://picsum.photos/seed/structure-metal/800/600", "nom_fichier": "montage_structure_metallique_zone_a.jpg", "champ_nom": "photo_avancement"},
                {"url": "https://picsum.photos/seed/soudure-portique/800/600", "nom_fichier": "soudure_portiques.jpg", "champ_nom": "photo_avancement"},
                {"url": "https://picsum.photos/seed/ipe300/800/600", "nom_fichier": "materiaux_ipe300_hea200.jpg", "champ_nom": "photo_avancement"},
                {"url": "https://picsum.photos/seed/pluie-chantier/800/600", "nom_fichier": "arret_pluie_zone_a.jpg", "champ_nom": "photo_avancement"},
            ],
        },
        # Inspection securite
        {
            "template": "Inspection securite hebdomadaire",
            "chantier": "2025-11-TRIALP",
            "user": "admin@example.com",
            "statut": "valide",
            "jours_avant": 5,
            "champs": [
                {"nom": "date_inspection", "type_champ": "date", "valeur": str(today - timedelta(days=5))},
                {"nom": "epi_portes", "type_champ": "radio", "valeur": "Oui"},
                {"nom": "balisage_ok", "type_champ": "radio", "valeur": "Oui"},
                {"nom": "echafaudages_ok", "type_champ": "radio", "valeur": "Oui"},
                {"nom": "proprete_chantier", "type_champ": "select", "valeur": "Bien"},
                {"nom": "anomalies", "type_champ": "texte_long", "valeur": ""},
                {"nom": "actions_correctives", "type_champ": "texte_long", "valeur": ""},
            ],
        },
        {
            "template": "Inspection securite hebdomadaire",
            "chantier": "2025-07-TOUR-LOGEMENTS",
            "user": "dupont.admin@example.com",
            "statut": "soumis",
            "jours_avant": 2,
            "champs": [
                {"nom": "date_inspection", "type_champ": "date", "valeur": str(today - timedelta(days=2))},
                {"nom": "epi_portes", "type_champ": "radio", "valeur": "Non"},
                {"nom": "balisage_ok", "type_champ": "radio", "valeur": "Partiel"},
                {"nom": "echafaudages_ok", "type_champ": "radio", "valeur": "Oui"},
                {"nom": "proprete_chantier", "type_champ": "select", "valeur": "A ameliorer"},
                {"nom": "anomalies", "type_champ": "texte_long", "valeur": "2 ouvriers sans casque zone B. Garde-corps manquant escalier provisoire."},
                {"nom": "actions_correctives", "type_champ": "texte_long", "valeur": "Rappel consignes EPI. Pose garde-corps prevue demain matin."},
            ],
        },
        # Declaration incident
        {
            "template": "Declaration d'incident",
            "chantier": "2025-06-RAVOIRE-LOGEMENTS",
            "user": "thomas.chef@example.com",
            "statut": "valide",
            "jours_avant": 10,
            "champs": [
                {"nom": "date_incident", "type_champ": "date", "valeur": str(today - timedelta(days=10))},
                {"nom": "heure_incident", "type_champ": "heure", "valeur": "14:30"},
                {"nom": "type_incident", "type_champ": "select", "valeur": "Dommage materiel"},
                {"nom": "gravite", "type_champ": "select", "valeur": "Mineur"},
                {"nom": "personnes_impliquees", "type_champ": "texte_long", "valeur": "Aucune blessure"},
                {"nom": "description_faits", "type_champ": "texte_long", "valeur": "Chute d'une palette de parpaings lors du dechargement. Palette mal arrimee."},
                {"nom": "mesures_prises", "type_champ": "texte_long", "valeur": "Zone securisee. Nettoyage debris. Rappel procedure dechargement."},
                {"nom": "temoins", "type_champ": "texte", "valeur": "Temoin A, Temoin B"},
            ],
            "photos": [
                {"url": "https://picsum.photos/seed/palette-chute/800/600", "nom_fichier": "chute_palette_parpaings.jpg", "champ_nom": "photo_incident"},
                {"url": "https://picsum.photos/seed/zone-securisee/800/600", "nom_fichier": "zone_securisee_apres_incident.jpg", "champ_nom": "photo_incident"},
            ],
        },
        # Bon de livraison
        {
            "template": "Bon de livraison materiaux",
            "chantier": "2025-11-TRIALP",
            "user": "bernard.chef@example.com",
            "statut": "valide",
            "jours_avant": 4,
            "champs": [
                {"nom": "date_livraison", "type_champ": "date", "valeur": str(today - timedelta(days=4))},
                {"nom": "fournisseur", "type_champ": "texte", "valeur": "Fournisseur Demo"},
                {"nom": "bon_numero", "type_champ": "texte", "valeur": "BL-2026-00847"},
                {"nom": "materiaux", "type_champ": "texte_long", "valeur": "500 parpaings 20x20x50, 30 sacs ciment CEM II, 2 palettes agglos"},
                {"nom": "conforme_commande", "type_champ": "radio", "valeur": "Oui"},
                {"nom": "etat_materiaux", "type_champ": "select", "valeur": "Bon etat"},
                {"nom": "remarques", "type_champ": "texte_long", "valeur": ""},
            ],
        },
        {
            "template": "Bon de livraison materiaux",
            "chantier": "2025-07-TOUR-LOGEMENTS",
            "user": "martin.chef@example.com",
            "statut": "soumis",
            "jours_avant": 1,
            "champs": [
                {"nom": "date_livraison", "type_champ": "date", "valeur": str(today - timedelta(days=1))},
                {"nom": "fournisseur", "type_champ": "texte", "valeur": "Fournisseur Demo 2"},
                {"nom": "bon_numero", "type_champ": "texte", "valeur": "AMD-2026-12453"},
                {"nom": "materiaux", "type_champ": "texte_long", "valeur": "6 IPE 300 x 6m, 4 HEA 200 x 4m, kit boulonnerie HR"},
                {"nom": "conforme_commande", "type_champ": "radio", "valeur": "Partiel"},
                {"nom": "etat_materiaux", "type_champ": "select", "valeur": "Dommages mineurs"},
                {"nom": "remarques", "type_champ": "texte_long", "valeur": "1 IPE 300 avec traces de rouille. A signaler au fournisseur."},
            ],
        },
        # Controle beton
        {
            "template": "Controle beton - eprouvettes",
            "chantier": "2025-11-TRIALP",
            "user": "bernard.chef@example.com",
            "statut": "valide",
            "jours_avant": 7,
            "champs": [
                {"nom": "date_coulage", "type_champ": "date", "valeur": str(today - timedelta(days=7))},
                {"nom": "type_beton", "type_champ": "select", "valeur": "C30/37"},
                {"nom": "volume_coule", "type_champ": "nombre", "valeur": 12},
                {"nom": "localisation_ouvrage", "type_champ": "texte", "valeur": "Dalle RDC batiment B"},
                {"nom": "nb_eprouvettes", "type_champ": "nombre", "valeur": 6},
                {"nom": "temperature_exterieure", "type_champ": "nombre", "valeur": 8},
                {"nom": "observations", "type_champ": "texte_long", "valeur": "Coulage par temps frais. Bache de protection posee."},
            ],
        },
        # Brouillon en cours
        {
            "template": "Rapport journalier de chantier",
            "chantier": "2025-06-RAVOIRE-LOGEMENTS",
            "user": "thomas.chef@example.com",
            "statut": "brouillon",
            "jours_avant": 0,
            "champs": [
                {"nom": "date_intervention", "type_champ": "date", "valeur": str(today)},
                {"nom": "meteo", "type_champ": "select", "valeur": "Beau temps"},
                {"nom": "nb_ouvriers", "type_champ": "nombre", "valeur": 4},
                {"nom": "travaux_realises", "type_champ": "texte_long", "valeur": ""},
            ],
        },
    ]

    for form_data in formulaires_data:
        template_id = template_ids.get(form_data["template"])
        chantier_id = chantier_ids.get(form_data["chantier"])
        user_id = user_ids.get(form_data["user"])

        if not template_id or not chantier_id or not user_id:
            continue

        # Verifier si un formulaire similaire existe deja
        jours_avant = form_data["jours_avant"]
        form_date = today - timedelta(days=jours_avant)
        existing = db.query(FormulaireRempliModel).filter(
            FormulaireRempliModel.template_id == template_id,
            FormulaireRempliModel.chantier_id == chantier_id,
            FormulaireRempliModel.user_id == user_id,
            FormulaireRempliModel.created_at >= datetime(form_date.year, form_date.month, form_date.day),
            FormulaireRempliModel.created_at < datetime(form_date.year, form_date.month, form_date.day) + timedelta(days=1),
        ).first()

        if existing:
            continue

        statut = form_data["statut"]
        soumis_at = datetime.now() - timedelta(days=jours_avant) if statut in ("soumis", "valide") else None
        valide_by = user_ids.get("admin@example.com") if statut == "valide" else None
        valide_at = datetime.now() - timedelta(days=max(0, jours_avant - 1)) if statut == "valide" else None

        formulaire = FormulaireRempliModel(
            template_id=template_id,
            chantier_id=chantier_id,
            user_id=user_id,
            statut=statut,
            soumis_at=soumis_at,
            valide_by=valide_by,
            valide_at=valide_at,
            # Coordonnées fictives génériques
            localisation_latitude=45.0000,
            localisation_longitude=5.0000,
            version=1,
            created_at=datetime.now() - timedelta(days=jours_avant),
            updated_at=datetime.now() - timedelta(days=jours_avant),
        )
        db.add(formulaire)
        db.flush()

        # Ajouter les champs remplis
        for champ_data in form_data.get("champs", []):
            champ = ChampRempliModel(
                formulaire_id=formulaire.id,
                nom=champ_data["nom"],
                type_champ=champ_data["type_champ"],
                valeur=champ_data["valeur"],
                timestamp=datetime.now() - timedelta(days=jours_avant),
            )
            db.add(champ)

        # Ajouter les photos
        for photo_data in form_data.get("photos", []):
            photo = PhotoFormulaireModel(
                formulaire_id=formulaire.id,
                url=photo_data["url"],
                nom_fichier=photo_data["nom_fichier"],
                champ_nom=photo_data["champ_nom"],
                timestamp=datetime.now() - timedelta(days=jours_avant),
                latitude=formulaire.localisation_latitude,
                longitude=formulaire.localisation_longitude,
            )
            db.add(photo)

        created_count += 1

    db.commit()
    print(f"  [CREE] {created_count} formulaires remplis")


# =============================================================================
# DONNEES FINANCIERES
# =============================================================================

FOURNISSEURS_DATA = [
    {
        "raison_sociale": "Négoce Matériaux Pro",
        "type": "negoce_materiaux",
        "siret": "12345678901234",
        "contact_principal": "Jean Dupont",
        "telephone": "04 00 00 00 01",
        "email": "contact@negoce-pro.fr",
        "conditions_paiement": "30 jours fin de mois",
    },
    {
        "raison_sociale": "Location Matériel BTP",
        "type": "loueur",
        "siret": "23456789012345",
        "contact_principal": "Marie Martin",
        "telephone": "04 00 00 00 02",
        "email": "contact@location-btp.fr",
        "conditions_paiement": "Comptant",
    },
    {
        "raison_sociale": "Sous-Traitance Élec Plus",
        "type": "sous_traitant",
        "siret": "34567890123456",
        "contact_principal": "Pierre Bernard",
        "telephone": "04 00 00 00 03",
        "email": "contact@elec-plus.fr",
        "conditions_paiement": "45 jours fin de mois",
    },
    {
        "raison_sociale": "Plomberie Services",
        "type": "sous_traitant",
        "siret": "45678901234567",
        "contact_principal": "Luc Dubois",
        "telephone": "04 00 00 00 04",
        "email": "contact@plomberie-services.fr",
        "conditions_paiement": "30 jours",
    },
    {
        "raison_sociale": "Services Généraux BTP",
        "type": "service",
        "siret": "56789012345678",
        "contact_principal": "Sophie Roux",
        "telephone": "04 00 00 00 05",
        "email": "contact@services-btp.fr",
        "conditions_paiement": "Comptant",
    },
]


def seed_fournisseurs(db: Session, user_ids: dict) -> dict:
    """Cree les fournisseurs de demo. Retourne un dict raison_sociale -> fournisseur_id."""
    print("\n=== Creation des fournisseurs ===")
    fournisseur_ids = {}
    admin_id = user_ids.get("admin@example.com") or 1

    for fournisseur_data in FOURNISSEURS_DATA:
        existing = db.query(FournisseurModel).filter(
            FournisseurModel.raison_sociale == fournisseur_data["raison_sociale"]
        ).first()

        if existing:
            print(f"  [EXISTE] {fournisseur_data['raison_sociale']}")
            fournisseur_ids[fournisseur_data["raison_sociale"]] = existing.id
            continue

        fournisseur = FournisseurModel(
            raison_sociale=fournisseur_data["raison_sociale"],
            type=fournisseur_data["type"],
            siret=fournisseur_data.get("siret"),
            contact_principal=fournisseur_data.get("contact_principal"),
            telephone=fournisseur_data.get("telephone"),
            email=fournisseur_data.get("email"),
            conditions_paiement=fournisseur_data.get("conditions_paiement"),
            actif=True,
            created_by=admin_id,
        )
        db.add(fournisseur)
        db.flush()
        fournisseur_ids[fournisseur_data["raison_sociale"]] = fournisseur.id
        print(f"  [CREE] {fournisseur_data['raison_sociale']} (ID: {fournisseur.id})")

    db.commit()
    return fournisseur_ids


def seed_budgets_financiers(db: Session, user_ids: dict, chantier_ids: dict) -> dict:
    """
    Cree les budgets pour les chantiers avec scénarios de dérive financière.
    Retourne un dict chantier_code -> budget_id.

    SCÉNARIOS FINANCIERS (marges réalistes gros œuvre BTP):
    - A: SAIN - démarrage, marge cible 10.5%
    - B: DÉRIVE LÉGÈRE - marge 6.2% (hausse acier)
    - C: DÉRIVE CRITIQUE - marge 2.1% (ST liquidé)
    - D: PERTE - marge -3.5% (amiante + malfaçon)
    - E: TRÈS RENTABLE - marge 14.2% (client fidèle)
    """
    print("\n=== Creation des budgets financiers avec scénarios de dérive ===")
    budget_ids = {}
    admin_id = user_ids.get("admin@example.com") or 1

    # Structure: (code, montant_initial, montant_avenants, seuil_alerte, notes)
    # Les avenants reflètent les problèmes rencontrés
    chantiers_avec_budget = [
        # A: TOURNON - SAIN (démarrage récent)
        ("2025-03-TOURNON-COMMERCIAL", 850000.00, 0, 110.0),

        # B: TOUR LOGEMENTS - DÉRIVE LÉGÈRE (hausse acier +15%)
        ("2025-07-TOUR-LOGEMENTS", 750000.00, 0, 115.0),  # Alerte relevée car tension

        # C: TRIALP - DÉRIVE CRITIQUE (ST liquidé, erreur métré)
        ("2025-11-TRIALP", 1200000.00, 0, 120.0),  # Seuil relevé par prudence

        # D: GYMNASE - PERTE (amiante 45k + malfaçon 28k = avenant 70k)
        ("2025-02-EPIERRE-GYMNASE", 450000.00, 70000.00, 105.0),  # Avenant accepté

        # E: CHIGNIN - TRÈS RENTABLE (client fidèle)
        ("2025-04-CHIGNIN-AGRICOLE", 380000.00, 0, 110.0),
    ]

    for chantier_code, montant_initial, avenants, seuil in chantiers_avec_budget:
        chantier_id = chantier_ids.get(chantier_code)
        if not chantier_id:
            continue

        # Verifier si budget existe
        existing = db.query(BudgetModel).filter(
            BudgetModel.chantier_id == chantier_id
        ).first()

        if existing:
            print(f"  [EXISTE] Budget pour {chantier_code}")
            budget_ids[chantier_code] = existing.id
            continue

        budget = BudgetModel(
            chantier_id=chantier_id,
            montant_initial_ht=montant_initial,
            montant_avenants_ht=avenants,
            retenue_garantie_pct=5.0,
            seuil_alerte_pct=seuil,
            seuil_validation_achat=5000.0,
            created_by=admin_id,
        )
        db.add(budget)
        db.flush()
        budget_ids[chantier_code] = budget.id

        total = montant_initial + avenants
        avenant_str = f" + {avenants:,.0f}€ avenant" if avenants > 0 else ""
        print(f"  [CREE] Budget {chantier_code}: {montant_initial:,.0f}€{avenant_str} = {total:,.0f}€ HT")

    db.commit()
    return budget_ids


def seed_lots_budgetaires(db: Session, user_ids: dict, budget_ids: dict) -> dict:
    """
    Cree les lots budgetaires avec prix réalistes gros œuvre 2025-2026.
    Retourne un dict (chantier_code, code_lot) -> lot_id.

    PRIX DE RÉFÉRENCE MARCHÉ FRANÇAIS:
    - Béton C25/30 livré: 145 €/m³
    - Béton C30/37 livré: 165 €/m³
    - Coffrage traditionnel: 50-80 €/m²
    - Ferraillage (pose incluse): 2.50-3.50 €/kg
    - Terrassement: 15-35 €/m³
    - Main d'œuvre maçon: 45 €/h
    """
    print("\n=== Creation des lots budgetaires (prix marché 2025-2026) ===")
    lot_ids = {}
    admin_id = user_ids.get("admin@example.com") or 1

    # Structure: chantier_code -> [(code_lot, libelle, quantite, prix_unitaire)]
    # Prix unitaires = déboursé + marge cible selon scénario
    lots_data = {
        # === TRIALP (DÉRIVE CRITIQUE) - Budget 1.2M€ ===
        # Marge initiale 10% mais érodée par problèmes
        "2025-11-TRIALP": [
            ("TERRASSEMENT", "Terrassement général 850m³", 850, 28.00),  # 23.8k€
            ("FONDATIONS", "Fondations BA 420m³ - ERREUR MÉTRÉ", 420, 450.00),  # 189k€
            ("FONDATIONS-SUPPL", "Supplément fondations +180m³", 180, 480.00),  # 86.4k€ IMPRÉVU
            ("DALLE-BA", "Dalle BA 1200m² ép.20cm", 1200, 95.00),  # 114k€
            ("VOILES-BA", "Voiles BA 680m²", 680, 185.00),  # 125.8k€
            ("FERRAILLAGE", "Ferraillage complet 85T - REPRISE RÉGIE", 85000, 3.20),  # 272k€
            ("STRUCTURE-METAL", "Charpente métallique hall", 1, 180000.00),  # 180k€
            ("BUREAUX", "GO bureaux R+1 250m²", 250, 420.00),  # 105k€
            ("PENALITES", "Pénalités retard client", 1, 15000.00),  # 15k€ PERTE
        ],
        # === TOUR LOGEMENTS (DÉRIVE LÉGÈRE) - Budget 750k€ ===
        # Hausse acier +15% non anticipée
        "2025-07-TOUR-LOGEMENTS": [
            ("TERRASSEMENT", "Terrassement VRD 620m³", 620, 32.00),  # 19.8k€
            ("FONDATIONS", "Semelles filantes 280m³", 280, 165.00),  # 46.2k€
            ("DALLE-RDC", "Dalle RDC 850m² ép.18cm", 850, 88.00),  # 74.8k€
            ("VOILES", "Voiles porteurs 520m²", 520, 175.00),  # 91k€
            ("PLANCHERS", "Planchers BA étages 780m²", 780, 125.00),  # 97.5k€
            ("FERRAILLAGE", "Ferraillage 62T - HAUSSE +15%", 62000, 3.45),  # 213.9k€ (vs 3.00 prévu)
            ("ESCALIERS", "Escaliers BA 8 volées", 8, 4500.00),  # 36k€
            ("ACROTERES", "Acrotères périphériques", 180, 85.00),  # 15.3k€
            ("HEURES-SUP", "Heures supplémentaires retard", 120, 58.00),  # 6.96k€ IMPRÉVU
        ],
        # === GYMNASE EPIERRE (PERTE) - Budget 450k€ + 70k€ avenant ===
        # Amiante + malfaçon dalle
        "2025-02-EPIERRE-GYMNASE": [
            ("DEMOLITION", "Démolition extension 200m²", 200, 65.00),  # 13k€
            ("DESAMIANTAGE", "Désamiantage IMPRÉVU", 1, 45000.00),  # 45k€ IMPRÉVU
            ("TERRASSEMENT", "Terrassement fouilles", 380, 28.00),  # 10.6k€
            ("FONDATIONS", "Fondations semelles", 95, 175.00),  # 16.6k€
            ("DALLE", "Dalle 800m² ép.15cm", 800, 82.00),  # 65.6k€
            ("DALLE-REPRISE", "Reprise dalle malfaçon", 400, 70.00),  # 28k€ IMPRÉVU
            ("ELEVATION", "Murs porteurs 420m²", 420, 165.00),  # 69.3k€
            ("POTEAUX", "Poteaux BA 24 unités", 24, 1200.00),  # 28.8k€
            ("POUTRES", "Poutres BA 180ml", 180, 320.00),  # 57.6k€
            ("ACROTERES", "Acrotères et finitions", 120, 95.00),  # 11.4k€
        ],
        # === TOURNON COMMERCIAL (SAIN) - Budget 850k€ ===
        # Démarrage récent, tout sous contrôle
        "2025-03-TOURNON-COMMERCIAL": [
            ("INSTALLATION", "Installation chantier", 1, 8500.00),  # 8.5k€
            ("TERRASSEMENT", "Terrassement plateforme 950m³", 950, 26.00),  # 24.7k€
            ("FONDATIONS", "Fondations 340m³", 340, 168.00),  # 57.1k€
            ("DALLAGE", "Dallage industriel 1400m²", 1400, 78.00),  # 109.2k€
            ("LONGRINES", "Longrines BA 280ml", 280, 145.00),  # 40.6k€
            ("POTEAUX", "Poteaux préfa 85 unités", 85, 1650.00),  # 140.3k€
            ("ELEVATION", "Murs façade et refends", 650, 155.00),  # 100.8k€
            ("PLANCHERS", "Planchers étage 420m²", 420, 135.00),  # 56.7k€
            ("CHARPENTE", "Charpente métallique", 1, 185000.00),  # 185k€
            ("FINITIONS", "Acrotères, seuils", 1, 45000.00),  # 45k€
        ],
        # === CHIGNIN AGRICOLE (TRÈS RENTABLE) - Budget 380k€ ===
        # Client fidèle, conditions favorables, marge 14%
        "2025-04-CHIGNIN-AGRICOLE": [
            ("TERRASSEMENT", "Terrassement 520m³", 520, 22.00),  # 11.4k€
            ("FONDATIONS-H1", "Fondations hangar 1", 75, 165.00),  # 12.4k€
            ("FONDATIONS-H2", "Fondations hangar 2", 75, 165.00),  # 12.4k€
            ("DALLAGE-H1", "Dallage hangar 1 340m²", 340, 72.00),  # 24.5k€
            ("DALLAGE-H2", "Dallage hangar 2 340m²", 340, 72.00),  # 24.5k€
            ("MURS-PIGNON", "Murs pignons BA 180m²", 180, 148.00),  # 26.6k€
            ("MURS-REFEND", "Murs de refend 120m²", 120, 142.00),  # 17k€
            ("STRUCTURE", "Structure métallique 2 hangars", 1, 165000.00),  # 165k€
            ("DIVERS", "Seuils, finitions", 1, 18000.00),  # 18k€
        ],
    }

    for chantier_code, lots in lots_data.items():
        budget_id = budget_ids.get(chantier_code)
        if not budget_id:
            continue

        for ordre, (code_lot, libelle, quantite, prix_unitaire) in enumerate(lots, 1):
            # Verifier si lot existe
            existing = db.query(LotBudgetaireModel).filter(
                LotBudgetaireModel.budget_id == budget_id,
                LotBudgetaireModel.code_lot == code_lot
            ).first()

            if existing:
                lot_ids[(chantier_code, code_lot)] = existing.id
                continue

            lot = LotBudgetaireModel(
                budget_id=budget_id,
                code_lot=code_lot,
                libelle=libelle,
                unite="ENS",
                quantite_prevue=quantite,
                prix_unitaire_ht=prix_unitaire,
                ordre=ordre,
                created_by=admin_id,
            )
            db.add(lot)
            db.flush()
            lot_ids[(chantier_code, code_lot)] = lot.id

    db.commit()
    print(f"  [CREE] {len(lot_ids)} lots budgétaires")
    return lot_ids


def seed_achats(db: Session, user_ids: dict, chantier_ids: dict, fournisseur_ids: dict, lot_ids: dict):
    """
    Cree des achats réalistes avec scénarios de dérive financière.

    MÉTRIQUES CIBLES RÉALISTES (gros œuvre BTP):
    - Marge nette chantier: 8-12% (objectif standard)
    - Marge MOE: 25-30% sur le taux horaire
    - Marge matériaux: 20-30%
    - Marge sous-traitance: 15-20%

    SCÉNARIOS DE DÉRIVE:
    - TRIALP: 45% avancement, marge 2% (critique - ST liquidé)
    - GYMNASE: 75% avancement, marge -3.5% (perte - amiante)
    - TOUR: 35% avancement, marge 6% (sous pression - hausse acier)
    - TOURNON: 15% avancement, marge 10.5% (sain - démarrage)
    - CHIGNIN: 55% avancement, marge 14% (excellent - client fidèle)

    STATUTS ACHATS:
    - "paye" = réalisé (facturé et payé)
    - "livre" = engagé (livré, en attente paiement)
    - "commande" = engagé (commandé)
    - "valide" = engagé (validé, non commandé)
    """
    print("\n=== Creation des achats avec scénarios de dérive ===")
    admin_id = user_ids.get("admin@example.com") or 1
    chef_id = user_ids.get("martin.chef@example.com") or admin_id

    # Recuperer les IDs fournisseurs
    fournisseur_negoce = fournisseur_ids.get("Négoce Matériaux Pro")
    fournisseur_location = fournisseur_ids.get("Location Matériel BTP")
    fournisseur_st = fournisseur_ids.get("Sous-Traitance Élec Plus")

    today = date.today()

    # =================================================================
    # TRIALP - DÉRIVE CRITIQUE
    # Budget: 1.2M€, Avancement: 45%, Marge cible: 2% (très tendu)
    # Engagé total cible: ~530k€, Réalisé: ~450k€
    # Problèmes: ST liquidé, erreur métré +180m³, pénalités retard
    # =================================================================
    achats_trialp = [
        # === RÉALISÉ (paye) - 450k€ ===
        {"chantier": "2025-11-TRIALP", "lot": "TERRASSEMENT", "fournisseur": fournisseur_negoce,
         "libelle": "Terrassement décapage 850m³", "quantite": 850, "unite": "m3",
         "prix_unitaire": 28.00, "statut": "facture", "jours_avant": 75, "type": "materiau"},

        {"chantier": "2025-11-TRIALP", "lot": "FONDATIONS", "fournisseur": fournisseur_negoce,
         "libelle": "Béton C30/37 fondations 420m³", "quantite": 420, "unite": "m3",
         "prix_unitaire": 168.00, "statut": "facture", "jours_avant": 60, "type": "materiau"},

        {"chantier": "2025-11-TRIALP", "lot": "FONDATIONS", "fournisseur": fournisseur_negoce,
         "libelle": "Acier HA fondations 28T", "quantite": 28000, "unite": "kg",
         "prix_unitaire": 1.35, "statut": "facture", "jours_avant": 58, "type": "materiau"},

        {"chantier": "2025-11-TRIALP", "lot": "FONDATIONS", "fournisseur": fournisseur_negoce,
         "libelle": "Main d'œuvre fondations", "quantite": 520, "unite": "h",
         "prix_unitaire": 48.00, "statut": "facture", "jours_avant": 55, "type": "main_oeuvre"},

        # ERREUR MÉTRÉ - Supplément béton non prévu (+180m³) - IMPRÉVU
        {"chantier": "2025-11-TRIALP", "lot": "FONDATIONS", "fournisseur": fournisseur_negoce,
         "libelle": "IMPRÉVU: Béton supplément erreur métré +180m³", "quantite": 180, "unite": "m3",
         "prix_unitaire": 175.00, "statut": "facture", "jours_avant": 45, "type": "materiau"},

        {"chantier": "2025-11-TRIALP", "lot": "DALLE-BA", "fournisseur": fournisseur_negoce,
         "libelle": "Béton C25/30 dalle 1200m²", "quantite": 240, "unite": "m3",
         "prix_unitaire": 148.00, "statut": "facture", "jours_avant": 40, "type": "materiau"},

        {"chantier": "2025-11-TRIALP", "lot": "DALLE-BA", "fournisseur": fournisseur_negoce,
         "libelle": "Treillis soudé ST25 1200m²", "quantite": 1320, "unite": "m2",
         "prix_unitaire": 4.80, "statut": "facture", "jours_avant": 42, "type": "materiau"},

        {"chantier": "2025-11-TRIALP", "lot": "DALLE-BA", "fournisseur": fournisseur_negoce,
         "libelle": "Main d'œuvre dalle", "quantite": 380, "unite": "h",
         "prix_unitaire": 45.00, "statut": "facture", "jours_avant": 35, "type": "main_oeuvre"},

        # ST FERRAILLAGE LIQUIDÉ - Reprise en régie (surcoût +40%)
        {"chantier": "2025-11-TRIALP", "lot": "FERRAILLAGE", "fournisseur": fournisseur_negoce,
         "libelle": "Acier HA voiles - reprise régie (ST liquidé)", "quantite": 45000, "unite": "kg",
         "prix_unitaire": 1.48, "statut": "facture", "jours_avant": 30, "type": "materiau"},

        {"chantier": "2025-11-TRIALP", "lot": "FERRAILLAGE", "fournisseur": fournisseur_negoce,
         "libelle": "MO ferraillage régie (surcoût ST liquidé)", "quantite": 480, "unite": "h",
         "prix_unitaire": 52.00, "statut": "facture", "jours_avant": 25, "type": "main_oeuvre"},

        {"chantier": "2025-11-TRIALP", "lot": "VOILES-BA", "fournisseur": fournisseur_location,
         "libelle": "Location banches 45 jours", "quantite": 45, "unite": "jour",
         "prix_unitaire": 320.00, "statut": "facture", "jours_avant": 20, "type": "materiel"},

        # === ENGAGÉ NON PAYÉ (livre/commande) - 80k€ ===
        {"chantier": "2025-11-TRIALP", "lot": "VOILES-BA", "fournisseur": fournisseur_negoce,
         "libelle": "Béton C30/37 voiles 680m²", "quantite": 136, "unite": "m3",
         "prix_unitaire": 172.00, "statut": "livre", "jours_avant": 10, "type": "materiau"},

        {"chantier": "2025-11-TRIALP", "lot": "STRUCTURE-METAL", "fournisseur": fournisseur_st,
         "libelle": "Acompte 30% charpente métallique hall", "quantite": 1, "unite": "ENS",
         "prix_unitaire": 48000.00, "statut": "commande", "jours_avant": 5, "type": "sous_traitance"},
    ]

    # =================================================================
    # TOUR LOGEMENTS - DÉRIVE LÉGÈRE
    # Budget: 750k€, Avancement: 35%, Marge cible: 6% (sous pression)
    # Engagé total cible: ~280k€, Réalisé: ~210k€
    # Problèmes: hausse acier +15%, heures sup retard livraison
    # =================================================================
    achats_tour = [
        # === RÉALISÉ (paye) - 210k€ ===
        {"chantier": "2025-07-TOUR-LOGEMENTS", "lot": "TERRASSEMENT", "fournisseur": fournisseur_negoce,
         "libelle": "Terrassement VRD 620m³", "quantite": 620, "unite": "m3",
         "prix_unitaire": 32.00, "statut": "facture", "jours_avant": 60, "type": "materiau"},

        {"chantier": "2025-07-TOUR-LOGEMENTS", "lot": "TERRASSEMENT", "fournisseur": fournisseur_negoce,
         "libelle": "Évacuation terres 480m³", "quantite": 480, "unite": "m3",
         "prix_unitaire": 28.00, "statut": "facture", "jours_avant": 55, "type": "materiau"},

        {"chantier": "2025-07-TOUR-LOGEMENTS", "lot": "FONDATIONS", "fournisseur": fournisseur_negoce,
         "libelle": "Béton C30/37 semelles filantes", "quantite": 195, "unite": "m3",
         "prix_unitaire": 168.00, "statut": "facture", "jours_avant": 45, "type": "materiau"},

        {"chantier": "2025-07-TOUR-LOGEMENTS", "lot": "FONDATIONS", "fournisseur": fournisseur_negoce,
         "libelle": "Main d'œuvre fondations", "quantite": 320, "unite": "h",
         "prix_unitaire": 46.00, "statut": "facture", "jours_avant": 42, "type": "main_oeuvre"},

        # HAUSSE ACIER +15% non anticipée (budget à 1.20€, réel 1.38€)
        {"chantier": "2025-07-TOUR-LOGEMENTS", "lot": "FERRAILLAGE", "fournisseur": fournisseur_negoce,
         "libelle": "Acier HA Ø8-16 (HAUSSE +15%)", "quantite": 18500, "unite": "kg",
         "prix_unitaire": 1.38, "statut": "facture", "jours_avant": 35, "type": "materiau"},

        {"chantier": "2025-07-TOUR-LOGEMENTS", "lot": "DALLE-RDC", "fournisseur": fournisseur_negoce,
         "libelle": "Béton C25/30 dalle RDC 620m²", "quantite": 93, "unite": "m3",
         "prix_unitaire": 148.00, "statut": "facture", "jours_avant": 25, "type": "materiau"},

        {"chantier": "2025-07-TOUR-LOGEMENTS", "lot": "DALLE-RDC", "fournisseur": fournisseur_negoce,
         "libelle": "Main d'œuvre dalle + finitions", "quantite": 240, "unite": "h",
         "prix_unitaire": 45.00, "statut": "facture", "jours_avant": 20, "type": "main_oeuvre"},

        # HEURES SUP rattrapage retard livraison béton
        {"chantier": "2025-07-TOUR-LOGEMENTS", "lot": "HEURES-SUP", "fournisseur": fournisseur_negoce,
         "libelle": "Heures supplémentaires rattrapage retard", "quantite": 96, "unite": "h",
         "prix_unitaire": 62.00, "statut": "facture", "jours_avant": 15, "type": "main_oeuvre"},

        # === ENGAGÉ NON PAYÉ (livre/commande) - 70k€ ===
        {"chantier": "2025-07-TOUR-LOGEMENTS", "lot": "VOILES", "fournisseur": fournisseur_negoce,
         "libelle": "Béton C30/37 voiles bât A", "quantite": 112, "unite": "m3",
         "prix_unitaire": 172.00, "statut": "livre", "jours_avant": 8, "type": "materiau"},

        {"chantier": "2025-07-TOUR-LOGEMENTS", "lot": "VOILES", "fournisseur": fournisseur_negoce,
         "libelle": "Acier HA voiles 12T", "quantite": 12000, "unite": "kg",
         "prix_unitaire": 1.42, "statut": "livre", "jours_avant": 10, "type": "materiau"},

        {"chantier": "2025-07-TOUR-LOGEMENTS", "lot": "VOILES", "fournisseur": fournisseur_location,
         "libelle": "Location banches 30 jours", "quantite": 30, "unite": "jour",
         "prix_unitaire": 280.00, "statut": "commande", "jours_avant": 3, "type": "materiel"},
    ]

    # =================================================================
    # GYMNASE EPIERRE - PERTE
    # Budget: 520k€ (450k + 70k avenant), Avancement: 75%, Marge: -3.5%
    # Engagé total cible: ~510k€, Réalisé: ~420k€
    # Problèmes: amiante 45k€, malfaçon dalle 28k€, retards
    # =================================================================
    achats_gymnase = [
        # === RÉALISÉ (paye) - 420k€ ===
        {"chantier": "2025-02-EPIERRE-GYMNASE", "lot": "DEMOLITION", "fournisseur": fournisseur_negoce,
         "libelle": "Démolition extension existante", "quantite": 200, "unite": "m2",
         "prix_unitaire": 68.00, "statut": "facture", "jours_avant": 150, "type": "materiau"},

        # AMIANTE IMPRÉVU - 45k€ (non dans le DCE initial)
        {"chantier": "2025-02-EPIERRE-GYMNASE", "lot": "DESAMIANTAGE", "fournisseur": fournisseur_st,
         "libelle": "IMPRÉVU: Désamiantage (découvert en démolition)", "quantite": 1, "unite": "ENS",
         "prix_unitaire": 47500.00, "statut": "facture", "jours_avant": 130, "type": "sous_traitance"},

        {"chantier": "2025-02-EPIERRE-GYMNASE", "lot": "TERRASSEMENT", "fournisseur": fournisseur_negoce,
         "libelle": "Terrassement fouilles 380m³", "quantite": 380, "unite": "m3",
         "prix_unitaire": 29.00, "statut": "facture", "jours_avant": 110, "type": "materiau"},

        {"chantier": "2025-02-EPIERRE-GYMNASE", "lot": "FONDATIONS", "fournisseur": fournisseur_negoce,
         "libelle": "Béton C30/37 fondations", "quantite": 115, "unite": "m3",
         "prix_unitaire": 168.00, "statut": "facture", "jours_avant": 95, "type": "materiau"},

        {"chantier": "2025-02-EPIERRE-GYMNASE", "lot": "FONDATIONS", "fournisseur": fournisseur_negoce,
         "libelle": "Acier HA fondations 9T", "quantite": 9000, "unite": "kg",
         "prix_unitaire": 1.35, "statut": "facture", "jours_avant": 92, "type": "materiau"},

        {"chantier": "2025-02-EPIERRE-GYMNASE", "lot": "FONDATIONS", "fournisseur": fournisseur_negoce,
         "libelle": "Main d'œuvre fondations", "quantite": 280, "unite": "h",
         "prix_unitaire": 46.00, "statut": "facture", "jours_avant": 88, "type": "main_oeuvre"},

        {"chantier": "2025-02-EPIERRE-GYMNASE", "lot": "DALLE", "fournisseur": fournisseur_negoce,
         "libelle": "Béton C25/30 dalle 800m²", "quantite": 128, "unite": "m3",
         "prix_unitaire": 148.00, "statut": "facture", "jours_avant": 75, "type": "materiau"},

        # MALFAÇON DALLE - Reprise 32k€ (fissures, planéité non conforme)
        {"chantier": "2025-02-EPIERRE-GYMNASE", "lot": "DALLE", "fournisseur": fournisseur_negoce,
         "libelle": "REPRISE: Dalle fissurée + ragréage", "quantite": 400, "unite": "m2",
         "prix_unitaire": 78.00, "statut": "facture", "jours_avant": 55, "type": "materiau"},

        {"chantier": "2025-02-EPIERRE-GYMNASE", "lot": "ELEVATION", "fournisseur": fournisseur_negoce,
         "libelle": "Béton C30/37 murs porteurs", "quantite": 98, "unite": "m3",
         "prix_unitaire": 172.00, "statut": "facture", "jours_avant": 45, "type": "materiau"},

        {"chantier": "2025-02-EPIERRE-GYMNASE", "lot": "ELEVATION", "fournisseur": fournisseur_negoce,
         "libelle": "Acier HA murs 8T", "quantite": 8000, "unite": "kg",
         "prix_unitaire": 1.38, "statut": "facture", "jours_avant": 48, "type": "materiau"},

        {"chantier": "2025-02-EPIERRE-GYMNASE", "lot": "POTEAUX", "fournisseur": fournisseur_negoce,
         "libelle": "Poteaux BA préfabriqués 24U", "quantite": 24, "unite": "U",
         "prix_unitaire": 1350.00, "statut": "facture", "jours_avant": 35, "type": "materiau"},

        {"chantier": "2025-02-EPIERRE-GYMNASE", "lot": "POTEAUX", "fournisseur": fournisseur_location,
         "libelle": "Location grue 12 jours", "quantite": 12, "unite": "jour",
         "prix_unitaire": 920.00, "statut": "facture", "jours_avant": 32, "type": "materiel"},

        {"chantier": "2025-02-EPIERRE-GYMNASE", "lot": "POUTRES", "fournisseur": fournisseur_negoce,
         "libelle": "Poutres BA 145ml", "quantite": 145, "unite": "ml",
         "prix_unitaire": 285.00, "statut": "facture", "jours_avant": 25, "type": "materiau"},

        # === ENGAGÉ NON PAYÉ (livre/commande) - 90k€ ===
        {"chantier": "2025-02-EPIERRE-GYMNASE", "lot": "POUTRES", "fournisseur": fournisseur_negoce,
         "libelle": "Poutres BA complément 35ml", "quantite": 35, "unite": "ml",
         "prix_unitaire": 295.00, "statut": "livre", "jours_avant": 12, "type": "materiau"},

        {"chantier": "2025-02-EPIERRE-GYMNASE", "lot": "PLANCHER", "fournisseur": fournisseur_negoce,
         "libelle": "Prédalles + poutrelles 420m²", "quantite": 420, "unite": "m2",
         "prix_unitaire": 85.00, "statut": "livre", "jours_avant": 8, "type": "materiau"},

        {"chantier": "2025-02-EPIERRE-GYMNASE", "lot": "PLANCHER", "fournisseur": fournisseur_negoce,
         "libelle": "Béton table compression", "quantite": 42, "unite": "m3",
         "prix_unitaire": 152.00, "statut": "commande", "jours_avant": 5, "type": "materiau"},

        {"chantier": "2025-02-EPIERRE-GYMNASE", "lot": "FINITIONS", "fournisseur": fournisseur_negoce,
         "libelle": "Enduits + finitions GO", "quantite": 1, "unite": "ENS",
         "prix_unitaire": 28000.00, "statut": "valide", "jours_avant": 3, "type": "materiau"},
    ]

    # =================================================================
    # TOURNON COMMERCIAL - SAIN
    # Budget: 850k€, Avancement: 15%, Marge cible: 10.5%
    # Engagé total cible: ~140k€, Réalisé: ~95k€
    # Chantier en démarrage, tout se passe bien
    # =================================================================
    achats_tournon = [
        # === RÉALISÉ (paye) - 95k€ ===
        {"chantier": "2025-03-TOURNON-COMMERCIAL", "lot": "INSTALLATION", "fournisseur": fournisseur_negoce,
         "libelle": "Installation chantier (base vie, clôture)", "quantite": 1, "unite": "ENS",
         "prix_unitaire": 12500.00, "statut": "facture", "jours_avant": 45, "type": "materiau"},

        {"chantier": "2025-03-TOURNON-COMMERCIAL", "lot": "TERRASSEMENT", "fournisseur": fournisseur_negoce,
         "libelle": "Décapage terre végétale 1200m²", "quantite": 360, "unite": "m3",
         "prix_unitaire": 26.00, "statut": "facture", "jours_avant": 35, "type": "materiau"},

        {"chantier": "2025-03-TOURNON-COMMERCIAL", "lot": "TERRASSEMENT", "fournisseur": fournisseur_negoce,
         "libelle": "Terrassement fouilles", "quantite": 280, "unite": "m3",
         "prix_unitaire": 32.00, "statut": "facture", "jours_avant": 28, "type": "materiau"},

        {"chantier": "2025-03-TOURNON-COMMERCIAL", "lot": "TERRASSEMENT", "fournisseur": fournisseur_negoce,
         "libelle": "Évacuation terres excédentaires", "quantite": 420, "unite": "m3",
         "prix_unitaire": 28.00, "statut": "facture", "jours_avant": 25, "type": "materiau"},

        {"chantier": "2025-03-TOURNON-COMMERCIAL", "lot": "FONDATIONS", "fournisseur": fournisseur_negoce,
         "libelle": "Béton C30/37 semelles isolées", "quantite": 85, "unite": "m3",
         "prix_unitaire": 165.00, "statut": "facture", "jours_avant": 18, "type": "materiau"},

        {"chantier": "2025-03-TOURNON-COMMERCIAL", "lot": "FONDATIONS", "fournisseur": fournisseur_negoce,
         "libelle": "Acier HA fondations 6T", "quantite": 6000, "unite": "kg",
         "prix_unitaire": 1.32, "statut": "facture", "jours_avant": 20, "type": "materiau"},

        # === ENGAGÉ NON PAYÉ (livre/commande) - 45k€ ===
        {"chantier": "2025-03-TOURNON-COMMERCIAL", "lot": "FONDATIONS", "fournisseur": fournisseur_negoce,
         "libelle": "Main d'œuvre fondations", "quantite": 185, "unite": "h",
         "prix_unitaire": 46.00, "statut": "livre", "jours_avant": 10, "type": "main_oeuvre"},

        {"chantier": "2025-03-TOURNON-COMMERCIAL", "lot": "DALLE", "fournisseur": fournisseur_negoce,
         "libelle": "Béton C25/30 dalle (acompte)", "quantite": 120, "unite": "m3",
         "prix_unitaire": 148.00, "statut": "commande", "jours_avant": 5, "type": "materiau"},

        {"chantier": "2025-03-TOURNON-COMMERCIAL", "lot": "DALLE", "fournisseur": fournisseur_negoce,
         "libelle": "Treillis soudé ST25", "quantite": 950, "unite": "m2",
         "prix_unitaire": 4.65, "statut": "commande", "jours_avant": 5, "type": "materiau"},
    ]

    # =================================================================
    # CHIGNIN AGRICOLE - TRÈS RENTABLE
    # Budget: 380k€, Avancement: 55%, Marge cible: 14% (excellent)
    # Engagé total cible: ~195k€, Réalisé: ~165k€
    # Client fidèle, équipe expérimentée, pas d'imprévus
    # =================================================================
    achats_chignin = [
        # === RÉALISÉ (paye) - 165k€ ===
        {"chantier": "2025-04-CHIGNIN-AGRICOLE", "lot": "TERRASSEMENT", "fournisseur": fournisseur_negoce,
         "libelle": "Terrassement plateforme 650m³", "quantite": 650, "unite": "m3",
         "prix_unitaire": 21.00, "statut": "facture", "jours_avant": 65, "type": "materiau"},

        {"chantier": "2025-04-CHIGNIN-AGRICOLE", "lot": "TERRASSEMENT", "fournisseur": fournisseur_negoce,
         "libelle": "Compactage + réglage", "quantite": 600, "unite": "m2",
         "prix_unitaire": 8.50, "statut": "facture", "jours_avant": 60, "type": "materiau"},

        {"chantier": "2025-04-CHIGNIN-AGRICOLE", "lot": "FONDATIONS-H1", "fournisseur": fournisseur_negoce,
         "libelle": "Béton C25/30 fondations hangar 1", "quantite": 72, "unite": "m3",
         "prix_unitaire": 152.00, "statut": "facture", "jours_avant": 50, "type": "materiau"},

        {"chantier": "2025-04-CHIGNIN-AGRICOLE", "lot": "FONDATIONS-H1", "fournisseur": fournisseur_negoce,
         "libelle": "Acier HA fondations H1 4.5T", "quantite": 4500, "unite": "kg",
         "prix_unitaire": 1.28, "statut": "facture", "jours_avant": 52, "type": "materiau"},

        {"chantier": "2025-04-CHIGNIN-AGRICOLE", "lot": "FONDATIONS-H1", "fournisseur": fournisseur_negoce,
         "libelle": "Main d'œuvre fondations H1", "quantite": 145, "unite": "h",
         "prix_unitaire": 44.00, "statut": "facture", "jours_avant": 48, "type": "main_oeuvre"},

        {"chantier": "2025-04-CHIGNIN-AGRICOLE", "lot": "DALLAGE-H1", "fournisseur": fournisseur_negoce,
         "libelle": "Béton C25/30 dallage hangar 1", "quantite": 54, "unite": "m3",
         "prix_unitaire": 145.00, "statut": "facture", "jours_avant": 38, "type": "materiau"},

        {"chantier": "2025-04-CHIGNIN-AGRICOLE", "lot": "DALLAGE-H1", "fournisseur": fournisseur_negoce,
         "libelle": "Treillis + joints dallage H1", "quantite": 320, "unite": "m2",
         "prix_unitaire": 12.50, "statut": "facture", "jours_avant": 40, "type": "materiau"},

        {"chantier": "2025-04-CHIGNIN-AGRICOLE", "lot": "FONDATIONS-H2", "fournisseur": fournisseur_negoce,
         "libelle": "Béton C25/30 fondations hangar 2", "quantite": 72, "unite": "m3",
         "prix_unitaire": 152.00, "statut": "facture", "jours_avant": 28, "type": "materiau"},

        {"chantier": "2025-04-CHIGNIN-AGRICOLE", "lot": "FONDATIONS-H2", "fournisseur": fournisseur_negoce,
         "libelle": "Acier HA fondations H2 4.5T", "quantite": 4500, "unite": "kg",
         "prix_unitaire": 1.28, "statut": "facture", "jours_avant": 30, "type": "materiau"},

        {"chantier": "2025-04-CHIGNIN-AGRICOLE", "lot": "FONDATIONS-H2", "fournisseur": fournisseur_negoce,
         "libelle": "Main d'œuvre fondations H2", "quantite": 145, "unite": "h",
         "prix_unitaire": 44.00, "statut": "facture", "jours_avant": 25, "type": "main_oeuvre"},

        # === ENGAGÉ NON PAYÉ (livre/commande) - 30k€ ===
        {"chantier": "2025-04-CHIGNIN-AGRICOLE", "lot": "DALLAGE-H2", "fournisseur": fournisseur_negoce,
         "libelle": "Béton C25/30 dallage hangar 2", "quantite": 54, "unite": "m3",
         "prix_unitaire": 145.00, "statut": "livre", "jours_avant": 12, "type": "materiau"},

        {"chantier": "2025-04-CHIGNIN-AGRICOLE", "lot": "DALLAGE-H2", "fournisseur": fournisseur_negoce,
         "libelle": "Treillis + joints dallage H2", "quantite": 320, "unite": "m2",
         "prix_unitaire": 12.50, "statut": "livre", "jours_avant": 14, "type": "materiau"},

        {"chantier": "2025-04-CHIGNIN-AGRICOLE", "lot": "MURS-PIGNONS", "fournisseur": fournisseur_negoce,
         "libelle": "Parpaings murs pignons (acompte)", "quantite": 2400, "unite": "U",
         "prix_unitaire": 1.85, "statut": "commande", "jours_avant": 5, "type": "materiau"},
    ]

    tous_achats = achats_trialp + achats_tour + achats_gymnase + achats_tournon + achats_chignin
    created_count = 0
    total_engage = 0

    # Facteurs de correction pour obtenir des marges variées
    # Marge = (Prix Vente - Achats - Coûts fixes) / Prix Vente
    # Coûts fixes = 600k€ répartis au prorata du CA (4.3M€)
    #
    # Scénarios de marge cibles :
    # - TRIALP (critique) : -5% → ST liquidé, surcoûts régie
    # - GYMNASE (perte) : -3% → Amiante découverte, reprise dalle
    # - TOUR (correct) : 15% → Hausse acier compensée par productivité
    # - TOURNON (bon) : 22% → Chantier bien géré, démarrage
    # - CHIGNIN (excellent) : 28% → Client fidèle, équipe rodée
    #
    # Marge moyenne pondérée cible : ~10% (8.8% obtenu)
    # Formule BTP: Marge = (Prix Vente - Coût Revient) / Prix Vente
    # Coût Revient = Achats réalisés + Coût MO + Quote-part coûts fixes
    # Coûts fixes société: 600k€/an répartis au prorata du CA (4.3M€)
    FACTEURS_CORRECTION = {
        "2025-02-EPIERRE-GYMNASE": 0.371,     # 8% marge
        "2025-03-TOURNON-COMMERCIAL": 0.360,  # 18% marge
        "2025-04-CHIGNIN-AGRICOLE": 0.457,    # 18% marge
        "2025-07-TOUR-LOGEMENTS": 0.459,      # 12% marge
        "2025-11-TRIALP": 0.290,              # -2% marge
    }

    for achat_data in tous_achats:
        chantier_id = chantier_ids.get(achat_data["chantier"])
        lot_key = (achat_data["chantier"], achat_data["lot"])
        lot_id = lot_ids.get(lot_key)
        fournisseur_id = achat_data["fournisseur"]

        if not chantier_id or not fournisseur_id:
            continue

        date_commande = today - timedelta(days=achat_data["jours_avant"])

        # Appliquer le facteur de correction pour calibrer les marges
        facteur = FACTEURS_CORRECTION.get(achat_data["chantier"], 1.0)
        prix_unitaire_corrige = achat_data["prix_unitaire"] * facteur

        montant_ht = achat_data["quantite"] * prix_unitaire_corrige

        achat = AchatModel(
            chantier_id=chantier_id,
            fournisseur_id=fournisseur_id,
            lot_budgetaire_id=lot_id,
            type_achat=achat_data.get("type", "materiau"),
            libelle=achat_data["libelle"],
            quantite=achat_data["quantite"],
            unite=achat_data["unite"],
            prix_unitaire_ht=prix_unitaire_corrige,
            taux_tva=20.0,
            date_commande=date_commande,
            statut=achat_data["statut"],
            demandeur_id=chef_id,
            valideur_id=admin_id if achat_data["statut"] in ["valide", "commande", "livre"] else None,
            validated_at=datetime.now() - timedelta(days=achat_data["jours_avant"] - 1) if achat_data["statut"] in ["valide", "commande", "livre"] else None,
            created_by=chef_id,
        )
        db.add(achat)
        created_count += 1
        total_engage += montant_ht

    db.commit()
    print(f"  [CREE] {created_count} achats")
    print(f"  [INFO] Total engagé: {total_engage:,.0f} € HT")


def seed_situations_factures(db: Session, user_ids: dict, chantier_ids: dict, budget_ids: dict, lot_ids: dict):
    """Cree des situations de travaux et factures pour tous les chantiers actifs.

    Les montants sont calibres pour obtenir une marge moyenne d'environ 10% :
    - Marge BTP = (Prix Vente - Cout Revient) / Prix Vente
    - Cout Revient = Achats realises + Cout MO (pointages valorises)

    Scenarios :
    - TOURNON (sain) : 15% avancement, marge 10%
    - TOUR-LOGEMENTS (derive legere) : 50% avancement, marge 6%
    - TRIALP (derive critique) : 30% avancement, marge 2%
    - GYMNASE (perte) : 75% avancement, marge -4%
    - CHIGNIN (rentable) : 55% avancement, marge 14%
    """
    print("\n=== Creation des situations et factures ===")
    admin_id = user_ids.get("admin@example.com") or 1
    today = date.today()
    created_situations = 0
    created_factures = 0

    # Configuration des situations par chantier
    # Les prix de vente sont calibres pour obtenir les marges cibles
    # en fonction des achats realises et du cout MO genere par les pointages
    SITUATIONS_CONFIG = [
        {
            "chantier_code": "2025-03-TOURNON-COMMERCIAL",
            "numero": "SIT-2026-TOURNON",
            "fac_numero": "FAC-2026-TOURNON",
            "prix_vente_ht": 127500.00,  # 15% de 850k
            "periode_debut": date(2025, 10, 1),
            "periode_fin": date(2026, 1, 31),
            "statut": "emise",
            "jours_avant": 10,
            "description": "Situation n°1 - Fondations et infrastructure",
        },
        {
            "chantier_code": "2025-07-TOUR-LOGEMENTS",
            "numero": "SIT-2026-TOUR",
            "fac_numero": "FAC-2026-TOUR",
            "prix_vente_ht": 375000.00,  # 50% de 750k
            "periode_debut": date(2025, 7, 1),
            "periode_fin": date(2026, 1, 31),
            "statut": "validee",
            "jours_avant": 5,
            "description": "Situation n°3 - Gros oeuvre R+1 a R+3",
        },
        {
            "chantier_code": "2025-11-TRIALP",
            "numero": "SIT-2026-TRIALP",
            "fac_numero": "FAC-2026-TRIALP",
            "prix_vente_ht": 360000.00,  # 30% de 1.2M
            "periode_debut": date(2025, 11, 1),
            "periode_fin": date(2026, 1, 31),
            "statut": "emise",
            "jours_avant": 8,
            "description": "Situation n°2 - Structure metallique et voiles",
        },
        {
            "chantier_code": "2025-02-EPIERRE-GYMNASE",
            "numero": "SIT-2026-GYMNASE",
            "fac_numero": "FAC-2026-GYMNASE",
            "prix_vente_ht": 390000.00,  # 75% de 520k (budget revise avec avenant)
            "periode_debut": date(2025, 2, 1),
            "periode_fin": date(2026, 1, 15),
            "statut": "facturee",
            "jours_avant": 15,
            "description": "Situation n°4 - Extension complete + desamiantage",
        },
        {
            "chantier_code": "2025-04-CHIGNIN-AGRICOLE",
            "numero": "SIT-2026-CHIGNIN",
            "fac_numero": "FAC-2026-CHIGNIN",
            "prix_vente_ht": 210000.00,  # 55% de 380k
            "periode_debut": date(2025, 4, 1),
            "periode_fin": date(2026, 1, 20),
            "statut": "validee",
            "jours_avant": 3,
            "description": "Situation n°2 - Hangar 1 termine + Hangar 2 en cours",
        },
    ]

    for config in SITUATIONS_CONFIG:
        chantier_code = config["chantier_code"]

        if chantier_code not in budget_ids:
            print(f"  [SKIP] {chantier_code} - pas de budget")
            continue

        chantier_id = chantier_ids[chantier_code]
        budget_id = budget_ids[chantier_code]

        # Verifier si situation existe deja
        existing_sit = db.query(SituationTravauxModel).filter(
            SituationTravauxModel.chantier_id == chantier_id,
            SituationTravauxModel.numero == config["numero"]
        ).first()

        if not existing_sit:
            situation = SituationTravauxModel(
                chantier_id=chantier_id,
                budget_id=budget_id,
                numero=config["numero"],
                periode_debut=config["periode_debut"],
                periode_fin=config["periode_fin"],
                montant_cumule_precedent_ht=0,
                montant_periode_ht=config["prix_vente_ht"],
                montant_cumule_ht=config["prix_vente_ht"],
                retenue_garantie_pct=5.0,
                taux_tva=20.0,
                statut=config["statut"],
                created_by=admin_id,
                emise_at=datetime.now() - timedelta(days=config["jours_avant"]) if config["statut"] in ["emise", "validee", "facturee"] else None,
                validated_by=admin_id if config["statut"] in ["validee", "facturee"] else None,
                validated_at=datetime.now() - timedelta(days=config["jours_avant"] - 1) if config["statut"] in ["validee", "facturee"] else None,
            )
            db.add(situation)
            db.flush()
            created_situations += 1
            print(f"  [CREE] Situation {config['numero']} - {config['prix_vente_ht']:,.0f} EUR")
        else:
            situation = existing_sit
            # Mettre a jour le montant si necessaire
            if float(existing_sit.montant_cumule_ht) != config["prix_vente_ht"]:
                existing_sit.montant_periode_ht = config["prix_vente_ht"]
                existing_sit.montant_cumule_ht = config["prix_vente_ht"]
                print(f"  [MAJ] Situation {config['numero']} - {config['prix_vente_ht']:,.0f} EUR")

        # Facture associee
        existing_fac = db.query(FactureClientModel).filter(
            FactureClientModel.numero_facture == config["fac_numero"]
        ).first()

        if not existing_fac:
            montant_ht = config["prix_vente_ht"]
            montant_tva = montant_ht * 0.20
            montant_ttc = montant_ht + montant_tva
            retenue = montant_ttc * 0.05

            facture = FactureClientModel(
                chantier_id=chantier_id,
                situation_id=situation.id,
                numero_facture=config["fac_numero"],
                type_facture="situation",
                montant_ht=montant_ht,
                taux_tva=20.0,
                montant_tva=montant_tva,
                montant_ttc=montant_ttc,
                retenue_garantie_montant=retenue,
                montant_net=montant_ttc - retenue,
                date_emission=today - timedelta(days=config["jours_avant"]),
                date_echeance=today + timedelta(days=30 - config["jours_avant"]),
                statut="emise" if config["statut"] != "facturee" else "envoyee",
                created_by=admin_id,
            )
            db.add(facture)
            created_factures += 1

    db.commit()
    print(f"  [TOTAL] {created_situations} situations de travaux")
    print(f"  [TOTAL] {created_factures} factures client")

    # Afficher le resume des prix de vente pour verification
    print("\n  [RECAP] Prix de vente factures (situations) :")
    total_pv = 0
    for config in SITUATIONS_CONFIG:
        print(f"    - {config['chantier_code'].split('-')[-1]}: {config['prix_vente_ht']:>12,.0f} EUR")
        total_pv += config["prix_vente_ht"]
    print(f"    {'TOTAL':>30}: {total_pv:>12,.0f} EUR")


def seed_ressources_logistique(db: Session, user_ids: dict) -> dict:
    """
    Cree les ressources matérielles avec tarifs journaliers réalistes.
    Retourne un dict code -> ressource_id.

    TARIFS JOURNALIERS DE RÉFÉRENCE (location externe 2025-2026):
    - Grue mobile 40T: 850 €/jour
    - Nacelle 18m: 180 €/jour
    - Manitou MT1440: 320 €/jour
    - Mini-pelle 3T: 250 €/jour
    - Pelleteuse 14T: 450 €/jour
    - Camion benne 19T: 380 €/jour
    """
    print("\n=== Creation des ressources logistique ===")
    ressource_ids = {}
    admin_id = user_ids.get("admin@example.com") or 1

    ressources_data = [
        # Engins de levage
        {"code": "GRU-001", "nom": "Grue mobile Liebherr 40T", "categorie": CategorieRessource.ENGIN_LEVAGE,
         "tarif": 850.00, "couleur": "#DC2626", "description": "Grue mobile 40T, portée 30m. Location externe."},
        {"code": "NAC-001", "nom": "Nacelle articulée 18m", "categorie": CategorieRessource.ENGIN_LEVAGE,
         "tarif": 180.00, "couleur": "#EA580C", "description": "Nacelle diesel 18m hauteur travail."},
        {"code": "MAN-001", "nom": "Manitou MT1440 télescopique", "categorie": CategorieRessource.ENGIN_LEVAGE,
         "tarif": 320.00, "couleur": "#D97706", "description": "Chariot télescopique 14m, charge 4T."},

        # Engins de terrassement
        {"code": "PEL-001", "nom": "Mini-pelle Kubota 3T", "categorie": CategorieRessource.ENGIN_TERRASSEMENT,
         "tarif": 250.00, "couleur": "#65A30D", "description": "Mini-pelle 3T, profondeur 2.5m. Propriété entreprise."},
        {"code": "PEL-002", "nom": "Pelleteuse CAT 14T", "categorie": CategorieRessource.ENGIN_TERRASSEMENT,
         "tarif": 450.00, "couleur": "#16A34A", "description": "Pelleteuse 14T chenilles. Location longue durée."},
        {"code": "COM-001", "nom": "Compacteur vibrant 1T", "categorie": CategorieRessource.ENGIN_TERRASSEMENT,
         "tarif": 120.00, "couleur": "#059669", "description": "Rouleau vibrant pour compactage tranchées."},

        # Véhicules
        {"code": "CAM-001", "nom": "Camion benne 6x4 19T", "categorie": CategorieRessource.VEHICULE,
         "tarif": 380.00, "couleur": "#0891B2", "description": "Camion benne 19T PTAC. Chauffeur non inclus."},
        {"code": "CAM-002", "nom": "Camion grue auxiliaire", "categorie": CategorieRessource.VEHICULE,
         "tarif": 520.00, "couleur": "#0284C7", "description": "Porteur grue 10T.m. Chauffeur non inclus."},
        {"code": "FOU-001", "nom": "Fourgon Renault Master", "categorie": CategorieRessource.VEHICULE,
         "tarif": 95.00, "couleur": "#2563EB", "description": "Fourgon L3H2 20m³. Usage chantier."},

        # Gros outillage
        {"code": "BET-001", "nom": "Bétonnière 350L", "categorie": CategorieRessource.GROS_OUTILLAGE,
         "tarif": 45.00, "couleur": "#7C3AED", "description": "Bétonnière électrique 350L."},
        {"code": "VIB-001", "nom": "Aiguille vibrante haute fréquence", "categorie": CategorieRessource.GROS_OUTILLAGE,
         "tarif": 35.00, "couleur": "#9333EA", "description": "Vibrateur 50mm pour béton."},
        {"code": "DEC-001", "nom": "Décapeuse thermique", "categorie": CategorieRessource.GROS_OUTILLAGE,
         "tarif": 85.00, "couleur": "#A855F7", "description": "Décapeuse sol thermique."},

        # Équipements
        {"code": "ECH-001", "nom": "Échafaudage roulant alu 8m", "categorie": CategorieRessource.EQUIPEMENT,
         "tarif": 65.00, "couleur": "#DB2777", "description": "Échafaudage roulant 8m hauteur travail."},
        {"code": "ETA-001", "nom": "Lot étais métalliques (x50)", "categorie": CategorieRessource.EQUIPEMENT,
         "tarif": 120.00, "couleur": "#E11D48", "description": "50 étais 2-4m pour coffrage."},
        {"code": "BAN-001", "nom": "Banches 2.70m (x10)", "categorie": CategorieRessource.EQUIPEMENT,
         "tarif": 280.00, "couleur": "#F43F5E", "description": "10 banches métalliques 2.70m."},
    ]

    for res_data in ressources_data:
        existing = db.query(RessourceModel).filter(
            RessourceModel.code == res_data["code"]
        ).first()

        if existing:
            ressource_ids[res_data["code"]] = existing.id
            continue

        ressource = RessourceModel(
            code=res_data["code"],
            nom=res_data["nom"],
            categorie=res_data["categorie"],
            tarif_journalier=res_data["tarif"],
            couleur=res_data["couleur"],
            description=res_data.get("description"),
            validation_requise=res_data["categorie"].validation_requise,
            actif=True,
            created_by=admin_id,
        )
        db.add(ressource)
        db.flush()
        ressource_ids[res_data["code"]] = ressource.id

    db.commit()
    print(f"  [CREE] {len(ressource_ids)} ressources matérielles")
    return ressource_ids


def seed_reservations_logistique(db: Session, user_ids: dict, chantier_ids: dict, ressource_ids: dict):
    """
    Cree des réservations de matériel avec différents statuts.
    Inclut des conflits pour tester la validation.
    """
    print("\n=== Creation des réservations logistique ===")
    admin_id = user_ids.get("admin@example.com") or 1
    chef_trialp = user_ids.get("martin.chef@example.com") or admin_id
    chef_tour = user_ids.get("bernard.chef@example.com") or admin_id
    chef_tournon = user_ids.get("thomas.chef@example.com") or admin_id

    today = date.today()
    created_count = 0

    reservations_data = [
        # === TRIALP (gros chantier - beaucoup de matériel) ===
        # Grue mobile - 2 semaines
        {"ressource": "GRU-001", "chantier": "2025-11-TRIALP", "demandeur": chef_trialp,
         "jours_depuis": -5, "duree_jours": 10, "statut": StatutReservation.VALIDEE,
         "commentaire": "Levage structure métallique hall"},

        # Pelleteuse - en cours
        {"ressource": "PEL-002", "chantier": "2025-11-TRIALP", "demandeur": chef_trialp,
         "jours_depuis": -3, "duree_jours": 5, "statut": StatutReservation.VALIDEE,
         "commentaire": "Terrassement zone bureaux"},

        # Camion benne - livraisons
        {"ressource": "CAM-001", "chantier": "2025-11-TRIALP", "demandeur": chef_trialp,
         "jours_depuis": -7, "duree_jours": 15, "statut": StatutReservation.VALIDEE,
         "commentaire": "Évacuation déblais et livraisons"},

        # Banches - réservation future
        {"ressource": "BAN-001", "chantier": "2025-11-TRIALP", "demandeur": chef_trialp,
         "jours_depuis": 5, "duree_jours": 20, "statut": StatutReservation.EN_ATTENTE,
         "commentaire": "Voiles béton zone hall"},

        # === TOUR LOGEMENTS (chantier moyen) ===
        # Grue - déjà passée
        {"ressource": "GRU-001", "chantier": "2025-07-TOUR-LOGEMENTS", "demandeur": chef_tour,
         "jours_depuis": -20, "duree_jours": 5, "statut": StatutReservation.VALIDEE,
         "commentaire": "Levage prédalle"},

        # Mini-pelle
        {"ressource": "PEL-001", "chantier": "2025-07-TOUR-LOGEMENTS", "demandeur": chef_tour,
         "jours_depuis": -2, "duree_jours": 3, "statut": StatutReservation.VALIDEE,
         "commentaire": "Tranchées réseaux"},

        # Nacelle pour façades
        {"ressource": "NAC-001", "chantier": "2025-07-TOUR-LOGEMENTS", "demandeur": chef_tour,
         "jours_depuis": 3, "duree_jours": 5, "statut": StatutReservation.EN_ATTENTE,
         "commentaire": "Travaux façade bâtiment A"},

        # Étais
        {"ressource": "ETA-001", "chantier": "2025-07-TOUR-LOGEMENTS", "demandeur": chef_tour,
         "jours_depuis": -10, "duree_jours": 30, "statut": StatutReservation.VALIDEE,
         "commentaire": "Coffrage planchers étages"},

        # === TOURNON COMMERCIAL (démarrage) ===
        # Mini-pelle pour terrassement initial
        {"ressource": "PEL-001", "chantier": "2025-03-TOURNON-COMMERCIAL", "demandeur": chef_tournon,
         "jours_depuis": 1, "duree_jours": 4, "statut": StatutReservation.EN_ATTENTE,
         "commentaire": "Décapage terrain"},

        # Compacteur
        {"ressource": "COM-001", "chantier": "2025-03-TOURNON-COMMERCIAL", "demandeur": chef_tournon,
         "jours_depuis": 4, "duree_jours": 2, "statut": StatutReservation.EN_ATTENTE,
         "commentaire": "Compactage fond de forme"},

        # === Réservation REFUSÉE (conflit avec TRIALP) ===
        {"ressource": "GRU-001", "chantier": "2025-07-TOUR-LOGEMENTS", "demandeur": chef_tour,
         "jours_depuis": -3, "duree_jours": 2, "statut": StatutReservation.REFUSEE,
         "commentaire": "Levage escalier", "motif_refus": "Conflit avec TRIALP - grue déjà réservée"},

        # === Réservation ANNULÉE ===
        {"ressource": "MAN-001", "chantier": "2025-11-TRIALP", "demandeur": chef_trialp,
         "jours_depuis": -15, "duree_jours": 3, "statut": StatutReservation.ANNULEE,
         "commentaire": "Annulé - utilisation grue à la place"},
    ]

    for res_data in reservations_data:
        ressource_id = ressource_ids.get(res_data["ressource"])
        chantier_id = chantier_ids.get(res_data["chantier"])
        demandeur_id = res_data["demandeur"]

        if not ressource_id or not chantier_id:
            continue

        date_debut = today + timedelta(days=res_data["jours_depuis"])

        # Créer une réservation par jour de la durée
        for day_offset in range(res_data["duree_jours"]):
            date_res = date_debut + timedelta(days=day_offset)

            # Vérifier si existe déjà
            existing = db.query(ReservationModel).filter(
                ReservationModel.ressource_id == ressource_id,
                ReservationModel.date_reservation == date_res,
                ReservationModel.chantier_id == chantier_id,
            ).first()

            if existing:
                continue

            reservation = ReservationModel(
                ressource_id=ressource_id,
                chantier_id=chantier_id,
                demandeur_id=demandeur_id,
                date_reservation=date_res,
                heure_debut=time(7, 30),
                heure_fin=time(17, 30),
                statut=res_data["statut"],
                commentaire=res_data.get("commentaire"),
                motif_refus=res_data.get("motif_refus"),
                valideur_id=admin_id if res_data["statut"] in [StatutReservation.VALIDEE, StatutReservation.REFUSEE] else None,
                validated_at=datetime.now() - timedelta(days=abs(res_data["jours_depuis"]) + 2) if res_data["statut"] in [StatutReservation.VALIDEE, StatutReservation.REFUSEE] else None,
            )
            db.add(reservation)
            created_count += 1

    db.commit()
    print(f"  [CREE] {created_count} réservations")


def seed_articles_devis(db: Session, user_ids: dict) -> dict:
    """
    Cree la bibliothèque d'articles avec prix réalistes gros œuvre 2025-2026.
    Retourne un dict code -> article_id.

    PRIX UNITAIRES DE RÉFÉRENCE:
    - Main d'œuvre: 32-58 €/h selon qualification
    - Béton C25/30: 145 €/m³, C30/37: 165 €/m³
    - Acier HA: 1.20-1.40 €/kg
    - Coffrage: 45-80 €/m²
    - Fondations: 165-185 €/m³
    - Dallage: 72-95 €/m²
    """
    print("\n=== Creation des articles devis (bibliothèque prix) ===")
    article_ids = {}
    admin_id = user_ids.get("admin@example.com") or 1

    articles_data = [
        # === MAIN D'ŒUVRE (taux horaires facturés) ===
        {"code": "MO-MAN-01", "designation": "Manœuvre gros œuvre", "unite": "heure",
         "prix": 32.00, "categorie": "main_oeuvre", "description": "Aide maçon, nettoyage, manutention"},
        {"code": "MO-MAC-01", "designation": "Maçon qualifié N2", "unite": "heure",
         "prix": 45.00, "categorie": "main_oeuvre", "description": "Maçonnerie courante, pose"},
        {"code": "MO-COF-01", "designation": "Coffreur bancheur", "unite": "heure",
         "prix": 50.00, "categorie": "main_oeuvre", "description": "Coffrage traditionnel et banches"},
        {"code": "MO-FER-01", "designation": "Ferrailleur", "unite": "heure",
         "prix": 48.00, "categorie": "main_oeuvre", "description": "Façonnage et pose armatures"},
        {"code": "MO-CHE-01", "designation": "Chef d'équipe N3", "unite": "heure",
         "prix": 58.00, "categorie": "main_oeuvre", "description": "Encadrement équipe gros œuvre"},

        # === MATÉRIAUX BÉTON ===
        {"code": "MAT-BET-25", "designation": "Béton C25/30 livré toupie", "unite": "m3",
         "prix": 145.00, "categorie": "gros_oeuvre", "description": "Béton prêt à l'emploi classe C25/30"},
        {"code": "MAT-BET-30", "designation": "Béton C30/37 livré toupie", "unite": "m3",
         "prix": 165.00, "categorie": "gros_oeuvre", "description": "Béton haute résistance C30/37"},
        {"code": "MAT-BET-35", "designation": "Béton C35/45 livré toupie", "unite": "m3",
         "prix": 185.00, "categorie": "gros_oeuvre", "description": "Béton très haute résistance"},

        # === MATÉRIAUX ACIER ===
        {"code": "MAT-ACI-08", "designation": "Acier HA Ø8mm", "unite": "kg",
         "prix": 1.20, "categorie": "gros_oeuvre", "description": "Rond à béton haute adhérence 8mm"},
        {"code": "MAT-ACI-10", "designation": "Acier HA Ø10mm", "unite": "kg",
         "prix": 1.22, "categorie": "gros_oeuvre", "description": "Rond à béton haute adhérence 10mm"},
        {"code": "MAT-ACI-12", "designation": "Acier HA Ø12mm", "unite": "kg",
         "prix": 1.25, "categorie": "gros_oeuvre", "description": "Rond à béton haute adhérence 12mm"},
        {"code": "MAT-ACI-16", "designation": "Acier HA Ø16mm", "unite": "kg",
         "prix": 1.30, "categorie": "gros_oeuvre", "description": "Rond à béton haute adhérence 16mm"},
        {"code": "MAT-TRE-01", "designation": "Treillis soudé ST25", "unite": "m2",
         "prix": 4.50, "categorie": "gros_oeuvre", "description": "Treillis 2.50x6m maille 150x150"},

        # === MATÉRIAUX MAÇONNERIE ===
        {"code": "MAT-PAR-20", "designation": "Parpaing creux 20x20x50", "unite": "u",
         "prix": 1.35, "categorie": "gros_oeuvre", "description": "Bloc béton creux standard"},
        {"code": "MAT-PAR-BA", "designation": "Parpaing bancher 20x20x50", "unite": "u",
         "prix": 2.80, "categorie": "gros_oeuvre", "description": "Bloc à bancher pour murs BA"},
        {"code": "MAT-CIM-01", "designation": "Ciment CEM II 35kg", "unite": "u",
         "prix": 8.50, "categorie": "gros_oeuvre", "description": "Sac ciment portland composé"},
        {"code": "MAT-SAB-01", "designation": "Sable 0/4 lavé", "unite": "m3",
         "prix": 45.00, "categorie": "gros_oeuvre", "description": "Sable pour béton et mortier"},
        {"code": "MAT-GRA-01", "designation": "Gravier 4/20", "unite": "m3",
         "prix": 55.00, "categorie": "gros_oeuvre", "description": "Gravillon pour béton"},

        # === COFFRAGE ===
        {"code": "MAT-COF-PAN", "designation": "Panneau coffrage CTB-X", "unite": "m2",
         "prix": 12.00, "categorie": "gros_oeuvre", "description": "Panneau contreplaqué coffrage"},
        {"code": "MAT-COF-BAN", "designation": "Location banche métallique", "unite": "jour",
         "prix": 8.50, "categorie": "materiel", "description": "Banche 2.70m location journée"},

        # === OUVRAGES COMPOSÉS (déboursés intégrés) ===
        {"code": "OUV-FON-SF", "designation": "Semelle filante BA", "unite": "ml",
         "prix": 185.00, "categorie": "gros_oeuvre", "description": "Semelle 40x30, béton C30, acier inclus"},
        {"code": "OUV-FON-SI", "designation": "Semelle isolée 80x80x40", "unite": "u",
         "prix": 145.00, "categorie": "gros_oeuvre", "description": "Semelle sous poteau, béton + acier"},
        {"code": "OUV-DAL-15", "designation": "Dallage béton 15cm", "unite": "m2",
         "prix": 85.00, "categorie": "gros_oeuvre", "description": "Dallage sur terre-plein, TS inclus"},
        {"code": "OUV-DAL-20", "designation": "Dallage béton 20cm", "unite": "m2",
         "prix": 95.00, "categorie": "gros_oeuvre", "description": "Dallage industriel renforcé"},
        {"code": "OUV-VOI-20", "designation": "Voile BA 20cm", "unite": "m2",
         "prix": 175.00, "categorie": "gros_oeuvre", "description": "Mur porteur BA coffré 2 faces"},
        {"code": "OUV-POT-25", "designation": "Poteau BA 25x25", "unite": "ml",
         "prix": 145.00, "categorie": "gros_oeuvre", "description": "Poteau béton armé section 25x25"},
        {"code": "OUV-POU-01", "designation": "Poutre BA rect.", "unite": "ml",
         "prix": 220.00, "categorie": "gros_oeuvre", "description": "Poutre BA section courante"},
        {"code": "OUV-PLA-BA", "designation": "Plancher BA 20+5", "unite": "m2",
         "prix": 125.00, "categorie": "gros_oeuvre", "description": "Plancher hourdis 16+5, poutrelles"},

        # === TERRASSEMENT ===
        {"code": "TER-DEC-01", "designation": "Décapage terre végétale", "unite": "m3",
         "prix": 8.50, "categorie": "terrassement", "description": "Décapage 30cm, mise en dépôt"},
        {"code": "TER-FOU-01", "designation": "Fouilles en masse", "unite": "m3",
         "prix": 15.00, "categorie": "terrassement", "description": "Terrassement mécanique pleine masse"},
        {"code": "TER-FOU-TR", "designation": "Fouilles en tranchée", "unite": "m3",
         "prix": 28.00, "categorie": "terrassement", "description": "Tranchées pour réseaux"},
        {"code": "TER-EVA-01", "designation": "Évacuation terres", "unite": "m3",
         "prix": 25.00, "categorie": "terrassement", "description": "Chargement et transport décharge"},
        {"code": "TER-REM-01", "designation": "Remblai compacté", "unite": "m3",
         "prix": 22.00, "categorie": "terrassement", "description": "Mise en place et compactage"},

        # === LOCATION MATÉRIEL ===
        {"code": "LOC-GRU-01", "designation": "Location grue mobile 40T", "unite": "jour",
         "prix": 850.00, "categorie": "materiel", "description": "Grue + grutier, 8h/jour"},
        {"code": "LOC-PEL-01", "designation": "Location mini-pelle 3T", "unite": "jour",
         "prix": 250.00, "categorie": "materiel", "description": "Mini-pelle sans chauffeur"},
        {"code": "LOC-PEL-02", "designation": "Location pelleteuse 14T", "unite": "jour",
         "prix": 450.00, "categorie": "materiel", "description": "Pelle chenilles sans chauffeur"},
        {"code": "LOC-BET-01", "designation": "Location bétonnière 350L", "unite": "jour",
         "prix": 45.00, "categorie": "materiel", "description": "Bétonnière électrique"},
        {"code": "LOC-VIB-01", "designation": "Location aiguille vibrante", "unite": "jour",
         "prix": 35.00, "categorie": "materiel", "description": "Vibrateur béton 50mm"},
        {"code": "LOC-ECH-01", "designation": "Location échafaudage", "unite": "jour",
         "prix": 12.00, "categorie": "materiel", "description": "Échafaudage roulant/m²"},
    ]

    for art_data in articles_data:
        existing = db.query(ArticleDevisModel).filter(
            ArticleDevisModel.code == art_data["code"]
        ).first()

        if existing:
            article_ids[art_data["code"]] = existing.id
            continue

        article = ArticleDevisModel(
            code=art_data["code"],
            designation=art_data["designation"],
            unite=art_data["unite"],
            prix_unitaire_ht=art_data["prix"],
            categorie=art_data["categorie"],
            description=art_data.get("description"),
            taux_tva=20.0,
            actif=True,
            created_by=admin_id,
        )
        db.add(article)
        db.flush()
        article_ids[art_data["code"]] = article.id

    db.commit()
    print(f"  [CREE] {len(article_ids)} articles dans la bibliothèque")
    return article_ids


def seed_devis(db: Session, user_ids: dict, chantier_ids: dict, article_ids: dict):
    """
    Cree des devis complets avec différents statuts et marges.

    SCÉNARIOS:
    - DEV-2026-001: Accepté, gymnase (correspond au chantier)
    - DEV-2026-002: En négociation, grand projet logements
    - DEV-2026-003: Accepté, agricole rentable
    - DEV-2026-004: Refusé, trop cher vs concurrence
    - DEV-2026-005: Brouillon, extension particulier
    """
    print("\n=== Creation des devis complets ===")
    admin_id = user_ids.get("admin@example.com") or 1
    conducteur_id = user_ids.get("dupont.admin@example.com") or admin_id

    today = date.today()

    devis_data = [
        # DEV-001: Gymnase - Accepté (correspond au chantier en cours)
        {
            "numero": "DEV-2026-001",
            "client_nom": "Mairie Ville-E",
            "client_adresse": "1 Place de la Mairie, 00000 Ville-E",
            "client_email": "mairie@ville-e.fr",
            "chantier_code": "2025-02-EPIERRE-GYMNASE",
            "objet": "Extension et rénovation du gymnase municipal",
            "statut": "accepte",
            "total_ht": 520000.00,
            "marge_globale_pct": 8.0,  # Marge réduite (problèmes survenus)
            "retenue_garantie_pct": 5.0,
            "jours_validite": 90,
            "lots": [
                {"titre": "Lot 1 - Démolition", "total_ht": 13000.00},
                {"titre": "Lot 2 - Terrassement", "total_ht": 10600.00},
                {"titre": "Lot 3 - Fondations", "total_ht": 16600.00},
                {"titre": "Lot 4 - Dalle BA", "total_ht": 65600.00},
                {"titre": "Lot 5 - Élévation murs", "total_ht": 69300.00},
                {"titre": "Lot 6 - Poteaux et poutres", "total_ht": 86400.00},
                {"titre": "Lot 7 - Finitions GO", "total_ht": 11400.00},
            ]
        },
        # DEV-002: Logements sociaux - En négociation
        {
            "numero": "DEV-2026-002",
            "client_nom": "Savoie Habitat",
            "client_adresse": "25 Rue des Logements, 00000 Ville-T",
            "client_email": "contact@savoie-habitat.fr",
            "chantier_code": "2026-03-RAVOIRE-CAPITE",
            "objet": "Construction 32 logements sociaux - Gros œuvre",
            "statut": "en_negociation",
            "total_ht": 717000.00,
            "marge_globale_pct": 11.0,
            "retenue_garantie_pct": 5.0,
            "jours_validite": 60,
            "lots": [
                {"titre": "Lot 1 - Terrassement VRD", "total_ht": 85000.00},
                {"titre": "Lot 2 - Fondations", "total_ht": 95000.00},
                {"titre": "Lot 3 - Infrastructure", "total_ht": 120000.00},
                {"titre": "Lot 4 - Superstructure", "total_ht": 280000.00},
                {"titre": "Lot 5 - Toiture terrasse", "total_ht": 75000.00},
                {"titre": "Lot 6 - Finitions GO", "total_ht": 62000.00},
            ]
        },
        # DEV-003: Agricole - Accepté (client fidèle)
        {
            "numero": "DEV-2026-003",
            "client_nom": "GAEC Dupont Frères",
            "client_adresse": "67 Route Agricole, 00000 Ville-J",
            "client_email": "gaec.dupont@email.fr",
            "chantier_code": "2025-04-CHIGNIN-AGRICOLE",
            "objet": "Construction 2 hangars agricoles 300m² chacun",
            "statut": "accepte",
            "total_ht": 380000.00,
            "marge_globale_pct": 14.0,  # Bonne marge client fidèle
            "retenue_garantie_pct": 0.0,  # Pas de RG particulier
            "jours_validite": 90,
            "lots": [
                {"titre": "Lot 1 - Terrassement", "total_ht": 11400.00},
                {"titre": "Lot 2 - Fondations Hangar 1", "total_ht": 12400.00},
                {"titre": "Lot 3 - Fondations Hangar 2", "total_ht": 12400.00},
                {"titre": "Lot 4 - Dallages", "total_ht": 49000.00},
                {"titre": "Lot 5 - Murs pignons", "total_ht": 43600.00},
                {"titre": "Lot 6 - Structure métallique", "total_ht": 165000.00},
                {"titre": "Lot 7 - Finitions", "total_ht": 18000.00},
            ]
        },
        # DEV-004: Refusé - Trop cher
        {
            "numero": "DEV-2026-004",
            "client_nom": "Promoteur Alpes Immo",
            "client_adresse": "15 Avenue Commerce, 00000 Ville-X",
            "client_email": "projets@alpes-immo.fr",
            "chantier_code": None,
            "objet": "Résidence 45 logements - Gros œuvre",
            "statut": "refuse",
            "total_ht": 2100000.00,
            "marge_globale_pct": 6.0,  # Marge déjà basse
            "retenue_garantie_pct": 5.0,
            "jours_validite": 45,
            "lots": [
                {"titre": "Lot 1 - Terrassement", "total_ht": 180000.00},
                {"titre": "Lot 2 - Fondations", "total_ht": 320000.00},
                {"titre": "Lot 3 - Infrastructure", "total_ht": 450000.00},
                {"titre": "Lot 4 - Superstructure", "total_ht": 850000.00},
                {"titre": "Lot 5 - Toiture", "total_ht": 200000.00},
                {"titre": "Lot 6 - Finitions", "total_ht": 100000.00},
            ]
        },
        # DEV-005: Brouillon - Extension particulier
        {
            "numero": "DEV-2026-005",
            "client_nom": "M. et Mme Martin",
            "client_adresse": "42 Rue des Fleurs, 00000 Ville-Y",
            "client_email": "famille.martin@email.fr",
            "chantier_code": None,
            "objet": "Extension maison individuelle 40m²",
            "statut": "brouillon",
            "total_ht": 85000.00,
            "marge_globale_pct": 12.0,
            "retenue_garantie_pct": 0.0,
            "jours_validite": 30,
            "lots": [
                {"titre": "Lot 1 - Terrassement", "total_ht": 4500.00},
                {"titre": "Lot 2 - Fondations", "total_ht": 12000.00},
                {"titre": "Lot 3 - Élévation", "total_ht": 35000.00},
                {"titre": "Lot 4 - Plancher", "total_ht": 18000.00},
                {"titre": "Lot 5 - Finitions", "total_ht": 8500.00},
            ]
        },
    ]

    created_devis = 0
    created_lots = 0

    for dev_data in devis_data:
        # Vérifier si devis existe
        existing = db.query(DevisModel).filter(
            DevisModel.numero == dev_data["numero"]
        ).first()

        if existing:
            print(f"  [EXISTE] Devis {dev_data['numero']}")
            continue

        chantier_id = chantier_ids.get(dev_data["chantier_code"]) if dev_data["chantier_code"] else None

        devis = DevisModel(
            numero=dev_data["numero"],
            client_nom=dev_data["client_nom"],
            client_adresse=dev_data["client_adresse"],
            client_email=dev_data["client_email"],
            chantier_id=chantier_id,
            objet=dev_data["objet"],
            statut=dev_data["statut"],
            total_ht=dev_data["total_ht"],
            total_ttc=dev_data["total_ht"] * 1.20,
            marge_globale_pct=dev_data["marge_globale_pct"],
            retenue_garantie_pct=dev_data["retenue_garantie_pct"],
            date_validite=today + timedelta(days=dev_data["jours_validite"]),
            date_creation=today - timedelta(days=30),
            conducteur_id=conducteur_id,
            created_by=admin_id,
        )
        db.add(devis)
        db.flush()
        created_devis += 1

        # Créer les lots
        for ordre, lot_data in enumerate(dev_data["lots"], 1):
            lot = LotDevisModel(
                devis_id=devis.id,
                titre=lot_data["titre"],
                numero=str(ordre),
                ordre=ordre,
                total_ht=lot_data["total_ht"],
                total_ttc=lot_data["total_ht"] * 1.20,
                created_by=admin_id,
            )
            db.add(lot)
            created_lots += 1

        # Ajouter une entrée dans le journal
        journal = JournalDevisModel(
            devis_id=devis.id,
            action="creation",
            details=f"Création du devis {dev_data['numero']} pour {dev_data['client_nom']}",
            auteur_id=admin_id,
        )
        db.add(journal)

    db.commit()
    print(f"  [CREE] {created_devis} devis")
    print(f"  [CREE] {created_lots} lots de devis")


def main():
    """Point d'entree principal."""
    print("=" * 60)
    print("SEED DEMO DATA - Hub Chantier")
    print("=" * 60)

    # Initialiser la base de donnees
    init_db()

    # Câbler l'intégration Planning → Pointages (FDH-10)
    from modules.pointages.infrastructure.event_handlers import setup_planning_integration
    setup_planning_integration(SessionLocal)
    print("Intégration Planning → Pointages câblée (FDH-10)")

    # Creer une session
    db = SessionLocal()

    try:
        # 1. Creer les utilisateurs
        user_ids = seed_users(db)

        # 2. Creer les chantiers
        chantier_ids = seed_chantiers(db, user_ids)

        # 3. Creer les affectations (planning)
        # Note: Les pointages seront créés automatiquement via FDH-10
        seed_affectations(db, user_ids, chantier_ids)

        # 4. Creer les taches
        seed_taches(db, chantier_ids)

        # 5. Creer les fournisseurs
        fournisseur_ids = seed_fournisseurs(db, user_ids)

        # 6. Creer les budgets financiers
        budget_ids = seed_budgets_financiers(db, user_ids, chantier_ids)

        # 7. Creer les lots budgetaires
        lot_ids = seed_lots_budgetaires(db, user_ids, budget_ids)

        # 8. Creer les achats
        seed_achats(db, user_ids, chantier_ids, fournisseur_ids, lot_ids)

        # 9. Creer les situations et factures (prix de vente)
        seed_situations_factures(db, user_ids, chantier_ids, budget_ids, lot_ids)

        # 10. Creer les pointages valides (cout MO)
        seed_pointages_valides(db, user_ids, chantier_ids)

        # 11. Creer les templates de formulaire
        template_ids = seed_templates_formulaires(db, user_ids)

        # 12. Creer les formulaires remplis
        seed_formulaires_remplis(db, user_ids, chantier_ids, template_ids)

        # 13. Creer les ressources logistique (matériel)
        ressource_ids = seed_ressources_logistique(db, user_ids)

        # 14. Creer les réservations logistique
        seed_reservations_logistique(db, user_ids, chantier_ids, ressource_ids)

        # 15. Creer les articles de la bibliothèque devis
        article_ids = seed_articles_devis(db, user_ids)

        # 16. Creer les devis complets
        seed_devis(db, user_ids, chantier_ids, article_ids)

        print("\n" + "=" * 60)
        print("SEED TERMINE AVEC SUCCES!")
        print("=" * 60)
        print("\nComptes de test disponibles:")
        print("-" * 40)
        print("Admin:      admin@example.com / Admin123!")
        print("Admin:      dupont.admin@example.com / Test123!")
        print("Chef:       martin.chef@example.com / Test123!")
        print("Compagnon:  robert.macon@example.com / Test123!")
        print("-" * 40)

    except Exception as e:
        print(f"\n[ERREUR] {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
