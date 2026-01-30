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
"""

import os
import sys
from datetime import date, datetime, timedelta

# Ajouter le chemin du backend pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bcrypt
from sqlalchemy.orm import Session

from shared.infrastructure.database import SessionLocal, init_db
from modules.auth.infrastructure.persistence.user_model import UserModel
from modules.chantiers.infrastructure.persistence.chantier_model import ChantierModel
from modules.planning.infrastructure.persistence.affectation_model import AffectationModel
from modules.pointages.infrastructure.persistence.models import PointageModel
from modules.taches.infrastructure.persistence import TacheModel
from modules.formulaires.infrastructure.persistence import (
    TemplateFormulaireModel,
    ChampTemplateModel,
    FormulaireRempliModel,
    ChampRempliModel,
    PhotoFormulaireModel,
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
    # Admin
    {
        "email": "admin@greg-construction.fr",
        "password": "Admin123!",
        "nom": "ADMIN",
        "prenom": "Super",
        "role": "admin",
        "type_utilisateur": "employe",
        "telephone": "06 00 00 00 00",
        "metier": None,
        "code_utilisateur": "ADM001",
        "couleur": "#9B59B6",
    },
    {
        "email": "clementine.delsalle@greg-construction.fr",
        "password": "Test123!",
        "nom": "DELSALLE",
        "prenom": "Clémentine",
        "role": "admin",
        "type_utilisateur": "employe",
        "telephone": "06 12 34 56 01",
        "metier": "assistante_administrative",
        "code_utilisateur": "ADM002",
        "couleur": "#8E44AD",
    },
    # Chefs de chantier et d'équipe
    {
        "email": "robert.bianchini@greg-construction.fr",
        "password": "Test123!",
        "nom": "BIANCHINI",
        "prenom": "Robert",
        "role": "chef_chantier",
        "type_utilisateur": "employe",
        "telephone": "06 12 34 56 02",
        "metier": "chef_chantier",
        "code_utilisateur": "CHF001",
        "couleur": "#27AE60",
    },
    {
        "email": "nicolas.delsalle@greg-construction.fr",
        "password": "Test123!",
        "nom": "DELSALLE",
        "prenom": "Nicolas",
        "role": "chef_chantier",
        "type_utilisateur": "employe",
        "telephone": "06 12 34 56 03",
        "metier": "chef_equipe",
        "code_utilisateur": "CHF002",
        "couleur": "#E67E22",
    },
    {
        "email": "guillaume.louyer@greg-construction.fr",
        "password": "Test123!",
        "nom": "LOUYER",
        "prenom": "Guillaume",
        "role": "chef_chantier",
        "type_utilisateur": "employe",
        "telephone": "06 12 34 56 04",
        "metier": "chef_equipe",
        "code_utilisateur": "CHF003",
        "couleur": "#16A085",
    },
    {
        "email": "jeremy.montmayeur@greg-construction.fr",
        "password": "Test123!",
        "nom": "MONTMAYEUR",
        "prenom": "Jérémy",
        "role": "chef_chantier",
        "type_utilisateur": "employe",
        "telephone": "06 12 34 56 05",
        "metier": "chef_equipe",
        "code_utilisateur": "CHF004",
        "couleur": "#D35400",
    },
    # Compagnons - Maçons
    {
        "email": "sebastien.achkar@greg-construction.fr",
        "password": "Test123!",
        "nom": "ACHKAR",
        "prenom": "Sébastien",
        "role": "compagnon",
        "type_utilisateur": "employe",
        "telephone": "06 12 34 56 06",
        "metier": "macon",
        "code_utilisateur": "CMP001",
        "couleur": "#E74C3C",
    },
    {
        "email": "carlos.de-oliveira-covas@greg-construction.fr",
        "password": "Test123!",
        "nom": "DE OLIVEIRA COVAS",
        "prenom": "Carlos",
        "role": "compagnon",
        "type_utilisateur": "employe",
        "telephone": "06 12 34 56 07",
        "metier": "macon_coffreur",
        "code_utilisateur": "CMP002",
        "couleur": "#C0392B",
    },
    {
        "email": "abou.drame@greg-construction.fr",
        "password": "Test123!",
        "nom": "DRAME",
        "prenom": "Abou",
        "role": "compagnon",
        "type_utilisateur": "employe",
        "telephone": "06 12 34 56 08",
        "metier": "macon",
        "code_utilisateur": "CMP003",
        "couleur": "#E84393",
    },
    {
        "email": "loic.duinat@greg-construction.fr",
        "password": "Test123!",
        "nom": "DUINAT",
        "prenom": "Loic",
        "role": "compagnon",
        "type_utilisateur": "employe",
        "telephone": "06 12 34 56 09",
        "metier": "macon",
        "code_utilisateur": "CMP004",
        "couleur": "#F1C40F",
    },
    {
        "email": "manuel.figueiredo-de-almeida@greg-construction.fr",
        "password": "Test123!",
        "nom": "FIGUEIREDO DE ALMEIDA",
        "prenom": "Manuel",
        "role": "compagnon",
        "type_utilisateur": "employe",
        "telephone": "06 12 34 56 10",
        "metier": "macon",
        "code_utilisateur": "CMP005",
        "couleur": "#F39C12",
    },
    {
        "email": "babaker.haroun-moussa@greg-construction.fr",
        "password": "Test123!",
        "nom": "HAROUN MOUSSA",
        "prenom": "Babaker",
        "role": "compagnon",
        "type_utilisateur": "employe",
        "telephone": "06 12 34 56 11",
        "metier": "macon",
        "code_utilisateur": "CMP006",
        "couleur": "#3498DB",
    },
    {
        "email": "jose.moreira-ferreira-da-silva@greg-construction.fr",
        "password": "Test123!",
        "nom": "MOREIRA FERREIRA DA SILVA",
        "prenom": "José",
        "role": "compagnon",
        "type_utilisateur": "employe",
        "telephone": "06 12 34 56 12",
        "metier": "macon_polyvalent",
        "code_utilisateur": "CMP007",
        "couleur": "#2980B9",
    },
    # Compagnons - Ouvriers
    {
        "email": "lhassan.achibane@greg-construction.fr",
        "password": "Test123!",
        "nom": "ACHIBANE",
        "prenom": "Lhassan",
        "role": "compagnon",
        "type_utilisateur": "employe",
        "telephone": "06 12 34 56 13",
        "metier": "ouvrier",
        "code_utilisateur": "CMP008",
        "couleur": "#9B59B6",
    },
    {
        "email": "gabriel.alonzo@greg-construction.fr",
        "password": "Test123!",
        "nom": "ALONZO",
        "prenom": "Gabriel",
        "role": "compagnon",
        "type_utilisateur": "employe",
        "telephone": "06 12 34 56 14",
        "metier": "ouvrier",
        "code_utilisateur": "CMP009",
        "couleur": "#8E44AD",
    },
    {
        "email": "ricardo.costa-silva@greg-construction.fr",
        "password": "Test123!",
        "nom": "COSTA SILVA",
        "prenom": "Ricardo",
        "role": "compagnon",
        "type_utilisateur": "employe",
        "telephone": "06 12 34 56 15",
        "metier": "ouvrier",
        "code_utilisateur": "CMP010",
        "couleur": "#1ABC9C",
    },
    {
        "email": "pedro.francisco@greg-construction.fr",
        "password": "Test123!",
        "nom": "FRANCISCO",
        "prenom": "Pedro",
        "role": "compagnon",
        "type_utilisateur": "employe",
        "telephone": "06 12 34 56 16",
        "metier": "ouvrier",
        "code_utilisateur": "CMP011",
        "couleur": "#16A085",
    },
    {
        "email": "anthony.mele@greg-construction.fr",
        "password": "Test123!",
        "nom": "MELE",
        "prenom": "Anthony",
        "role": "compagnon",
        "type_utilisateur": "employe",
        "telephone": "06 12 34 56 17",
        "metier": "ouvrier",
        "code_utilisateur": "CMP012",
        "couleur": "#EC407A",
    },
    # Grutier
    {
        "email": "jose-alberto.borges@greg-construction.fr",
        "password": "Test123!",
        "nom": "BORGES",
        "prenom": "José Alberto",
        "role": "compagnon",
        "type_utilisateur": "employe",
        "telephone": "06 12 34 56 18",
        "metier": "grutier",
        "code_utilisateur": "CMP013",
        "couleur": "#3F51B5",
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
    # === CHANTIERS 2024-2025 (terminés ou en cours) ===
    {
        "code": "2024-10-MONTMELIAN",
        "nom": "Ensemble immobilier Montmélian",
        "adresse": "Montmélian, 73800",
        "description": "Ensemble immobilier de bureaux et 4 logements - ACE Solution",
        "statut": "receptionne",
        "couleur": "#3498DB",
        "contact_nom": "ACE Solution",
        "contact_telephone": "04 79 00 00 01",
        "heures_estimees": 5900,  # 886k€ / 150€/h
        "date_debut": date(2024, 10, 1),
        "date_fin": date(2025, 6, 30),
    },
    {
        "code": "2025-01-CHALLES-REHAB",
        "nom": "Réhabilitation 6 logements Challes",
        "adresse": "Challes-les-Eaux, 73190",
        "description": "Réhabilitation 6 logements - OPAC (Déconstruction 67k€ + Maçonnerie 80k€)",
        "statut": "receptionne",
        "couleur": "#E74C3C",
        "contact_nom": "OPAC Savoie",
        "contact_telephone": "04 79 00 00 02",
        "heures_estimees": 980,  # 147k€ / 150€/h
        "date_debut": date(2025, 1, 15),
        "date_fin": date(2025, 9, 30),
    },
    {
        "code": "2025-01-CHAMBERY-MEDICAL",
        "nom": "Pôle médical Chambéry",
        "adresse": "Chambéry, 73000",
        "description": "Pôle médical - Cristal Habitat (Démolition & Maçonnerie)",
        "statut": "receptionne",
        "couleur": "#27AE60",
        "contact_nom": "Cristal Habitat",
        "contact_telephone": "04 79 00 00 03",
        "heures_estimees": 187,  # 28k€ / 150€/h
        "date_debut": date(2025, 1, 20),
        "date_fin": date(2025, 5, 31),
    },
    {
        "code": "2025-01-STE-MARIE-SALLE",
        "nom": "Salle polyvalente Ste Marie de Cuines",
        "adresse": "Sainte-Marie-de-Cuines, 73130",
        "description": "Rénovation salle polyvalente - Commune",
        "statut": "receptionne",
        "couleur": "#9B59B6",
        "contact_nom": "Mairie Ste Marie de Cuines",
        "contact_telephone": "04 79 00 00 04",
        "heures_estimees": 1467,  # 220k€ / 150€/h
        "date_debut": date(2025, 1, 10),
        "date_fin": date(2025, 8, 31),
    },
    {
        "code": "2025-02-EPIERRE-GYMNASE",
        "nom": "Extension gymnase Epierre",
        "adresse": "Epierre, 73220",
        "description": "Extension + rénovation Gymnase - Commune (Terrassement 51.7k€ + Démolition & Maçonnerie 147k€)",
        "statut": "receptionne",
        "couleur": "#F1C40F",
        "contact_nom": "Mairie d'Epierre",
        "contact_telephone": "04 79 00 00 05",
        "heures_estimees": 1325,  # 198.7k€ / 150€/h
        "date_debut": date(2025, 2, 1),
        "date_fin": date(2025, 10, 31),
    },
    {
        "code": "2025-03-ALPESPACE-EXECO",
        "nom": "Bâtiment industriel EXECO",
        "adresse": "Alpespace, Sainte-Hélène-du-Lac, 73800",
        "description": "Bâtiment industriel - EXECO",
        "statut": "receptionne",
        "couleur": "#E67E22",
        "contact_nom": "EXECO",
        "contact_telephone": "04 79 00 00 06",
        "heures_estimees": 860,  # 129k€ / 150€/h
        "date_debut": date(2025, 3, 1),
        "date_fin": date(2025, 9, 30),
    },
    {
        "code": "2025-03-ALPESPACE-SOUDEM",
        "nom": "Bâtiment industriel SOUDEM",
        "adresse": "Alpespace, Sainte-Hélène-du-Lac, 73800",
        "description": "Bâtiment industriel - SOUDEM",
        "statut": "receptionne",
        "couleur": "#16A085",
        "contact_nom": "SOUDEM",
        "contact_telephone": "04 79 00 00 07",
        "heures_estimees": 660,  # 99k€ / 150€/h
        "date_debut": date(2025, 3, 15),
        "date_fin": date(2025, 10, 31),
    },
    {
        "code": "2025-03-BEAUFORT-FERME",
        "nom": "Réhabilitation ferme Beaufort",
        "adresse": "Beaufort, 73270",
        "description": "Réhabilitation de la ferme - Commune",
        "statut": "receptionne",
        "couleur": "#D35400",
        "contact_nom": "Mairie de Beaufort",
        "contact_telephone": "04 79 00 00 08",
        "heures_estimees": 1445,  # 216.8k€ / 150€/h
        "date_debut": date(2025, 3, 10),
        "date_fin": date(2025, 11, 30),
    },
    {
        "code": "2025-03-CHAMOUX-AGRICOLE",
        "nom": "Bâtiment agricole Chamoux",
        "adresse": "Chamoux-sur-Gelon, 73390",
        "description": "Bâtiment agricole - Particulier",
        "statut": "receptionne",
        "couleur": "#8E44AD",
        "contact_nom": "Particulier",
        "contact_telephone": "04 79 00 00 09",
        "heures_estimees": 380,  # 57k€ / 150€/h
        "date_debut": date(2025, 3, 20),
        "date_fin": date(2025, 7, 31),
    },
    {
        "code": "2025-03-TOURNON-COMMERCIAL",
        "nom": "Bâtiment commercial Tournon",
        "adresse": "Tournon, 73460",
        "description": "Bâtiment commercial - Particulier",
        "statut": "en_cours",
        "couleur": "#C0392B",
        "contact_nom": "Particulier",
        "contact_telephone": "04 79 00 00 10",
        "heures_estimees": 6666,  # 999.9k€ / 150€/h
        "date_debut": date(2025, 3, 1),
        "date_fin": date(2026, 3, 31),
    },
    {
        "code": "2025-04-CHIGNIN-AGRICOLE",
        "nom": "2 bâtiments agricoles Chignin",
        "adresse": "Chignin, 73800",
        "description": "2 bâtiments agricoles - Particulier",
        "statut": "en_cours",
        "couleur": "#E84393",
        "contact_nom": "Particulier",
        "contact_telephone": "04 79 00 00 11",
        "heures_estimees": 2800,  # 420k€ / 150€/h
        "date_debut": date(2025, 4, 1),
        "date_fin": date(2026, 2, 28),
    },
    {
        "code": "2025-04-UGINE-MAISONS",
        "nom": "Constructions maisons Ugine",
        "adresse": "Ugine, 73400",
        "description": "Constructions de maisons - OPAC",
        "statut": "en_cours",
        "couleur": "#2980B9",
        "contact_nom": "OPAC Savoie",
        "contact_telephone": "04 79 00 00 12",
        "heures_estimees": 900,  # 135k€ / 150€/h
        "date_debut": date(2025, 4, 15),
        "date_fin": date(2026, 1, 31),
    },
    {
        "code": "2025-05-CHATEAUNEUF-DENTAIRE",
        "nom": "Cabinet dentaire Châteauneuf",
        "adresse": "Châteauneuf, 73390",
        "description": "Cabinet dentaire - Particulier",
        "statut": "en_cours",
        "couleur": "#1ABC9C",
        "contact_nom": "Particulier",
        "contact_telephone": "04 79 00 00 13",
        "heures_estimees": 853,  # 128k€ / 150€/h
        "date_debut": date(2025, 5, 1),
        "date_fin": date(2025, 12, 31),
    },
    {
        "code": "2025-05-CHATEAUNEUF-MAIRIE",
        "nom": "Rénovation Mairie Châteauneuf",
        "adresse": "Châteauneuf, 73390",
        "description": "Rénovation de la Mairie - Commune (Démolition & Maçonnerie)",
        "statut": "en_cours",
        "couleur": "#EC407A",
        "contact_nom": "Mairie de Châteauneuf",
        "contact_telephone": "04 79 00 00 14",
        "heures_estimees": 1153,  # 173k€ / 150€/h
        "date_debut": date(2025, 5, 15),
        "date_fin": date(2026, 2, 28),
    },
    {
        "code": "2025-06-RAVOIRE-LOGEMENTS",
        "nom": "Logements La Ravoire",
        "adresse": "La Ravoire, 73490",
        "description": "Logements - Particulier",
        "statut": "en_cours",
        "couleur": "#3F51B5",
        "contact_nom": "Particulier",
        "contact_telephone": "04 79 00 00 15",
        "heures_estimees": 3393,  # 509k€ / 150€/h
        "date_debut": date(2025, 6, 1),
        "date_fin": date(2026, 6, 30),
    },
    {
        "code": "2025-07-FAVERGES-IME",
        "nom": "IME Faverges",
        "adresse": "Faverges, 74210",
        "description": "IME - Fondation OVE",
        "statut": "en_cours",
        "couleur": "#FF9800",
        "contact_nom": "Fondation OVE",
        "contact_telephone": "04 50 00 00 01",
        "heures_estimees": 580,  # 87k€ / 150€/h
        "date_debut": date(2025, 7, 1),
        "date_fin": date(2026, 3, 31),
    },
    {
        "code": "2025-07-TOUR-LOGEMENTS",
        "nom": "20 logements Tour-en-Savoie",
        "adresse": "Tour-en-Savoie, 73170",
        "description": "20 logements - CIS PROMOTION",
        "statut": "en_cours",
        "couleur": "#FF5722",
        "contact_nom": "CIS PROMOTION",
        "contact_telephone": "04 79 00 00 16",
        "heures_estimees": 5920,  # 888k€ / 150€/h
        "date_debut": date(2025, 7, 1),
        "date_fin": date(2026, 9, 30),
    },
    {
        "code": "2025-07-HAUTEVILLE-MAIRIE",
        "nom": "Réhabilitation mairie Hauteville",
        "adresse": "Hauteville, 73390",
        "description": "Réhabilitation mairie - Commune",
        "statut": "en_cours",
        "couleur": "#795548",
        "contact_nom": "Mairie d'Hauteville",
        "contact_telephone": "04 79 00 00 17",
        "heures_estimees": 740,  # 111k€ / 150€/h
        "date_debut": date(2025, 7, 15),
        "date_fin": date(2026, 4, 30),
    },
    {
        "code": "2025-11-TRIALP",
        "nom": "Reconstruction hall de tri TRIALP",
        "adresse": "TRIALP, 73000",
        "description": "Reconstruction hall de tri et bureaux - VALTRI",
        "statut": "en_cours",
        "couleur": "#607D8B",
        "contact_nom": "VALTRI",
        "contact_telephone": "04 79 00 00 18",
        "heures_estimees": 10353,  # 1552.9k€ / 150€/h
        "date_debut": date(2025, 11, 1),
        "date_fin": date(2027, 6, 30),
    },

    # === CHANTIERS 2026 (ouverts/à venir) ===
    {
        "code": "2026-02-BISSY-COLLEGE",
        "nom": "Restructuration collège Bissy",
        "adresse": "Bissy, Chambéry, 73000",
        "description": "Restructuration du collège - Public",
        "statut": "ouvert",
        "couleur": "#00BCD4",
        "contact_nom": "Département Savoie",
        "contact_telephone": "04 79 00 00 19",
        "heures_estimees": 5293,  # 794k€ / 150€/h
        "date_debut": date(2026, 2, 1),
        "date_fin": date(2027, 2, 28),
    },
    {
        "code": "2026-02-BISSY-DECONSTRUCTION",
        "nom": "Déconstruction collège Bissy",
        "adresse": "Bissy, Chambéry, 73000",
        "description": "Restructuration du collège - Public (Déconstruction)",
        "statut": "ouvert",
        "couleur": "#009688",
        "contact_nom": "Département Savoie",
        "contact_telephone": "04 79 00 00 20",
        "heures_estimees": 2049,  # 307.3k€ / 150€/h
        "date_debut": date(2027, 2, 1),
        "date_fin": date(2027, 8, 31),
    },
    {
        "code": "2026-03-RAVOIRE-CAPITE",
        "nom": "Logements sociaux La Capite",
        "adresse": "La Ravoire, 73490",
        "description": "Logements sociaux et villas - SCCV La Capite",
        "statut": "ouvert",
        "couleur": "#8BC34A",
        "contact_nom": "SCCV La Capite",
        "contact_telephone": "04 79 00 00 21",
        "heures_estimees": 4780,  # 717k€ / 150€/h
        "date_debut": date(2026, 3, 1),
        "date_fin": date(2027, 3, 31),
    },
    {
        "code": "2026-BOURGET-LOGEMENTS",
        "nom": "Construction logements Bourget-du-Lac",
        "adresse": "Bourget-du-Lac, 73370",
        "description": "Construction de logements - OPAC",
        "statut": "ouvert",
        "couleur": "#CDDC39",
        "contact_nom": "OPAC Savoie",
        "contact_telephone": "04 79 00 00 22",
        "heures_estimees": 3708,  # 556.2k€ / 150€/h
        "date_debut": date(2026, 4, 1),
        "date_fin": date(2027, 6, 30),
    },
]

TACHES_DATA = [
    # Taches pour chantier Tournon (en cours - commercial)
    {"chantier_code": "2025-03-TOURNON-COMMERCIAL", "titre": "Terrassement et fondations", "description": "Préparation du terrain et fondations", "statut": "termine", "heures_estimees": 800},
    {"chantier_code": "2025-03-TOURNON-COMMERCIAL", "titre": "Gros oeuvre - Murs porteurs", "description": "Élévation des murs porteurs", "statut": "en_cours", "heures_estimees": 1200},
    {"chantier_code": "2025-03-TOURNON-COMMERCIAL", "titre": "Structure planchers", "description": "Coffrage et coulage des planchers", "statut": "a_faire", "heures_estimees": 900},
    {"chantier_code": "2025-03-TOURNON-COMMERCIAL", "titre": "Façades", "description": "Maçonnerie de façade", "statut": "a_faire", "heures_estimees": 700},
    {"chantier_code": "2025-03-TOURNON-COMMERCIAL", "titre": "Finitions extérieures", "description": "Enduits et finitions", "statut": "a_faire", "heures_estimees": 500},

    # Taches pour chantier Chignin (en cours - agricole)
    {"chantier_code": "2025-04-CHIGNIN-AGRICOLE", "titre": "Fondations bâtiment 1", "description": "Fondations du premier bâtiment", "statut": "termine", "heures_estimees": 400},
    {"chantier_code": "2025-04-CHIGNIN-AGRICOLE", "titre": "Gros oeuvre bâtiment 1", "description": "Murs et structure bâtiment 1", "statut": "en_cours", "heures_estimees": 800},
    {"chantier_code": "2025-04-CHIGNIN-AGRICOLE", "titre": "Fondations bâtiment 2", "description": "Fondations du second bâtiment", "statut": "a_faire", "heures_estimees": 400},
    {"chantier_code": "2025-04-CHIGNIN-AGRICOLE", "titre": "Gros oeuvre bâtiment 2", "description": "Murs et structure bâtiment 2", "statut": "a_faire", "heures_estimees": 800},

    # Taches pour chantier 20 logements Tour-en-Savoie (en cours)
    {"chantier_code": "2025-07-TOUR-LOGEMENTS", "titre": "Terrassement général", "description": "Préparation terrain et VRD", "statut": "termine", "heures_estimees": 600},
    {"chantier_code": "2025-07-TOUR-LOGEMENTS", "titre": "Fondations bâtiment A", "description": "Fondations premier bâtiment", "statut": "termine", "heures_estimees": 800},
    {"chantier_code": "2025-07-TOUR-LOGEMENTS", "titre": "Gros oeuvre bâtiment A", "description": "Élévation murs et planchers", "statut": "en_cours", "heures_estimees": 1500},
    {"chantier_code": "2025-07-TOUR-LOGEMENTS", "titre": "Fondations bâtiment B", "description": "Fondations second bâtiment", "statut": "a_faire", "heures_estimees": 800},
    {"chantier_code": "2025-07-TOUR-LOGEMENTS", "titre": "Gros oeuvre bâtiment B", "description": "Élévation murs et planchers", "statut": "a_faire", "heures_estimees": 1500},

    # Taches pour chantier TRIALP (en cours - important)
    {"chantier_code": "2025-11-TRIALP", "titre": "Démolition hall existant", "description": "Démolition de l'ancien hall de tri", "statut": "en_cours", "heures_estimees": 1200},
    {"chantier_code": "2025-11-TRIALP", "titre": "Terrassement et VRD", "description": "Préparation du terrain", "statut": "a_faire", "heures_estimees": 800},
    {"chantier_code": "2025-11-TRIALP", "titre": "Fondations hall", "description": "Fondations du nouveau hall", "statut": "a_faire", "heures_estimees": 1500},
    {"chantier_code": "2025-11-TRIALP", "titre": "Structure hall", "description": "Structure métallique et maçonnerie", "statut": "a_faire", "heures_estimees": 2500},
    {"chantier_code": "2025-11-TRIALP", "titre": "Bureaux", "description": "Construction des bureaux", "statut": "a_faire", "heures_estimees": 1200},
    {"chantier_code": "2025-11-TRIALP", "titre": "Finitions", "description": "Finitions et aménagements", "statut": "a_faire", "heures_estimees": 1000},

    # Taches pour chantier La Ravoire logements (en cours)
    {"chantier_code": "2025-06-RAVOIRE-LOGEMENTS", "titre": "Fondations", "description": "Fondations de l'ensemble", "statut": "termine", "heures_estimees": 500},
    {"chantier_code": "2025-06-RAVOIRE-LOGEMENTS", "titre": "Gros oeuvre RDC+R1", "description": "Murs et planchers RDC et R+1", "statut": "en_cours", "heures_estimees": 1200},
    {"chantier_code": "2025-06-RAVOIRE-LOGEMENTS", "titre": "Gros oeuvre R+2+R3", "description": "Murs et planchers R+2 et R+3", "statut": "a_faire", "heures_estimees": 1200},
    {"chantier_code": "2025-06-RAVOIRE-LOGEMENTS", "titre": "Toiture", "description": "Charpente et couverture", "statut": "a_faire", "heures_estimees": 400},
]


def seed_users(db: Session) -> dict:
    """Cree les utilisateurs de demo. Retourne un dict email -> user_id."""
    print("\n=== Creation des utilisateurs ===")
    user_ids = {}

    for user_data in USERS_DATA:
        # Verifier si l'utilisateur existe deja
        existing = db.query(UserModel).filter(UserModel.email == user_data["email"]).first()
        if existing:
            # Mettre a jour le mot de passe pour s'assurer qu'il correspond
            existing.password_hash = hash_password(user_data["password"])
            existing.is_active = True  # S'assurer que le compte est actif
            print(f"  [MAJ] {user_data['prenom']} {user_data['nom']} ({user_data['role']}) - mot de passe mis a jour")
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
            metier=user_data.get("metier"),
            code_utilisateur=user_data.get("code_utilisateur"),
            couleur=user_data.get("couleur", "#3498DB"),
            is_active=True,
        )
        db.add(user)
        db.flush()  # Pour obtenir l'ID
        user_ids[user_data["email"]] = user.id
        print(f"  [CREE] {user_data['prenom']} {user_data['nom']} ({user_data['role']}) - ID: {user.id}")

    db.commit()
    return user_ids


def seed_chantiers(db: Session, user_ids: dict) -> dict:
    """Cree les chantiers de demo. Retourne un dict code -> chantier_id."""
    print("\n=== Creation des chantiers ===")
    chantier_ids = {}

    # Recuperer les IDs des conducteurs et chefs
    conducteur_ids = [
        user_ids.get("jean.dupont@greg-construction.fr"),
        user_ids.get("marie.martin@greg-construction.fr"),
    ]
    chef_ids = [
        user_ids.get("pierre.bernard@greg-construction.fr"),
        user_ids.get("sophie.petit@greg-construction.fr"),
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
        # TRIALP - Gros chantier (6 compagnons)
        ("sebastien.achkar@greg-construction.fr", "2025-11-TRIALP"),
        ("carlos.de-oliveira-covas@greg-construction.fr", "2025-11-TRIALP"),
        ("abou.drame@greg-construction.fr", "2025-11-TRIALP"),
        ("loic.duinat@greg-construction.fr", "2025-11-TRIALP"),
        ("manuel.figueiredo-de-almeida@greg-construction.fr", "2025-11-TRIALP"),
        ("babaker.haroun-moussa@greg-construction.fr", "2025-11-TRIALP"),

        # 20 logements Tour-en-Savoie (4 compagnons)
        ("jose.moreira-ferreira-da-silva@greg-construction.fr", "2025-07-TOUR-LOGEMENTS"),
        ("lhassan.achibane@greg-construction.fr", "2025-07-TOUR-LOGEMENTS"),
        ("gabriel.alonzo@greg-construction.fr", "2025-07-TOUR-LOGEMENTS"),
        ("ricardo.costa-silva@greg-construction.fr", "2025-07-TOUR-LOGEMENTS"),

        # Logements La Ravoire (2 compagnons)
        ("pedro.francisco@greg-construction.fr", "2025-06-RAVOIRE-LOGEMENTS"),
        ("anthony.mele@greg-construction.fr", "2025-06-RAVOIRE-LOGEMENTS"),

        # Grutier sur TRIALP
        ("jose-alberto.borges@greg-construction.fr", "2025-11-TRIALP"),

        # Chefs de chantier assignés
        ("robert.bianchini@greg-construction.fr", "2025-11-TRIALP"),  # Chef sur TRIALP
        ("nicolas.delsalle@greg-construction.fr", "2025-07-TOUR-LOGEMENTS"),  # Chef sur Tour
        ("guillaume.louyer@greg-construction.fr", "2025-06-RAVOIRE-LOGEMENTS"),  # Chef sur Ravoire
        ("jeremy.montmayeur@greg-construction.fr", "2025-03-TOURNON-COMMERCIAL"),  # Chef sur Tournon
    ]

    # Admin qui cree les affectations
    admin_id = user_ids.get("admin@greg-construction.fr") or 1

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


def seed_pointages(db: Session, user_ids: dict, chantier_ids: dict):
    """Cree des pointages pour la semaine courante et la semaine derniere."""
    print("\n=== Creation des pointages ===")

    # Semaine courante et semaine derniere
    today = date.today()
    current_monday = today - timedelta(days=today.weekday())
    last_monday = current_monday - timedelta(days=7)

    # Compagnons avec leurs chantiers (VRAIS compagnons du seed)
    compagnons = [
        ("sebastien.achkar@greg-construction.fr", "2025-03-TOURNON-COMMERCIAL"),
        ("carlos.de-oliveira-covas@greg-construction.fr", "2025-03-TOURNON-COMMERCIAL"),
        ("abou.drame@greg-construction.fr", "2025-04-CHIGNIN-AGRICOLE"),
        ("loic.duinat@greg-construction.fr", "2025-07-TOUR-LOGEMENTS"),
        ("manuel.figueiredo-de-almeida@greg-construction.fr", "2025-11-TRIALP"),
        ("babaker.haroun-moussa@greg-construction.fr", "2025-06-RAVOIRE-LOGEMENTS"),
    ]

    created_count = 0

    # Créer des pointages pour les deux semaines (courante et derniere)
    for week_monday in [current_monday, last_monday]:
        for email, chantier_code in compagnons:
            user_id = user_ids.get(email)
            chantier_id = chantier_ids.get(chantier_code)

            if not user_id or not chantier_id:
                continue

            # Créer des pointages du lundi au vendredi (ou jusqu'à aujourd'hui pour la semaine courante)
            for day_offset in range(5):
                pointage_date = week_monday + timedelta(days=day_offset)

                # Ne pas créer de pointages dans le futur
                if pointage_date > today:
                    continue

                # Verifier si existe deja
                existing = db.query(PointageModel).filter(
                    PointageModel.utilisateur_id == user_id,
                    PointageModel.date_pointage == pointage_date
                ).first()

                if existing:
                    continue

                # Heures variables selon le jour (en minutes)
                heures_normales_min = 480 if day_offset < 4 else 420  # 8h ou 7h
                heures_sup_min = 60 if day_offset == 3 else 0  # 1h sup le jeudi

                # Pour la semaine courante, statut "soumis" (en attente de validation)
                statut = "valide" if week_monday == last_monday else "soumis"

                pointage = PointageModel(
                    utilisateur_id=user_id,
                    chantier_id=chantier_id,
                    date_pointage=pointage_date,
                    heures_normales_minutes=heures_normales_min,
                    heures_supplementaires_minutes=heures_sup_min,
                    statut=statut,
                )
                db.add(pointage)
                created_count += 1

    db.commit()
    print(f"  [CREE] {created_count} pointages pour les semaines du {last_monday} et {current_monday}")


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
    admin_id = user_ids.get("admin@greg-construction.fr") or 1

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
    formulaires_data = [
        # Rapports journaliers sur Residence Les Jardins
        {
            "template": "Rapport journalier de chantier",
            "chantier": "A001",
            "user": "pierre.bernard@greg-construction.fr",
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
            "chantier": "A001",
            "user": "pierre.bernard@greg-construction.fr",
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
        # Rapport sur Centre Commercial
        {
            "template": "Rapport journalier de chantier",
            "chantier": "A002",
            "user": "sophie.petit@greg-construction.fr",
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
            "chantier": "A001",
            "user": "jean.dupont@greg-construction.fr",
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
            "chantier": "A002",
            "user": "marie.martin@greg-construction.fr",
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
            "chantier": "A004",
            "user": "sophie.petit@greg-construction.fr",
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
                {"nom": "temoins", "type_champ": "texte", "valeur": "Lucas MOREAU, Emma GARCIA"},
            ],
            "photos": [
                {"url": "https://picsum.photos/seed/palette-chute/800/600", "nom_fichier": "chute_palette_parpaings.jpg", "champ_nom": "photo_incident"},
                {"url": "https://picsum.photos/seed/zone-securisee/800/600", "nom_fichier": "zone_securisee_apres_incident.jpg", "champ_nom": "photo_incident"},
            ],
        },
        # Bon de livraison
        {
            "template": "Bon de livraison materiaux",
            "chantier": "A001",
            "user": "pierre.bernard@greg-construction.fr",
            "statut": "valide",
            "jours_avant": 4,
            "champs": [
                {"nom": "date_livraison", "type_champ": "date", "valeur": str(today - timedelta(days=4))},
                {"nom": "fournisseur", "type_champ": "texte", "valeur": "Point P - Agence Montreuil"},
                {"nom": "bon_numero", "type_champ": "texte", "valeur": "BL-2026-00847"},
                {"nom": "materiaux", "type_champ": "texte_long", "valeur": "500 parpaings 20x20x50, 30 sacs ciment CEM II, 2 palettes agglos"},
                {"nom": "conforme_commande", "type_champ": "radio", "valeur": "Oui"},
                {"nom": "etat_materiaux", "type_champ": "select", "valeur": "Bon etat"},
                {"nom": "remarques", "type_champ": "texte_long", "valeur": ""},
            ],
        },
        {
            "template": "Bon de livraison materiaux",
            "chantier": "A002",
            "user": "sophie.petit@greg-construction.fr",
            "statut": "soumis",
            "jours_avant": 1,
            "champs": [
                {"nom": "date_livraison", "type_champ": "date", "valeur": str(today - timedelta(days=1))},
                {"nom": "fournisseur", "type_champ": "texte", "valeur": "ArcelorMittal Distribution"},
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
            "chantier": "A001",
            "user": "pierre.bernard@greg-construction.fr",
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
            "chantier": "A004",
            "user": "sophie.petit@greg-construction.fr",
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
        valide_by = user_ids.get("jean.dupont@greg-construction.fr") if statut == "valide" else None
        valide_at = datetime.now() - timedelta(days=max(0, jours_avant - 1)) if statut == "valide" else None

        formulaire = FormulaireRempliModel(
            template_id=template_id,
            chantier_id=chantier_id,
            user_id=user_id,
            statut=statut,
            soumis_at=soumis_at,
            valide_by=valide_by,
            valide_at=valide_at,
            localisation_latitude=48.8566 if form_data["chantier"] == "A001" else 48.8634 if form_data["chantier"] == "A002" else 48.8049,
            localisation_longitude=2.3522 if form_data["chantier"] == "A001" else 2.4437 if form_data["chantier"] == "A002" else 2.1204,
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


def main():
    """Point d'entree principal."""
    print("=" * 60)
    print("SEED DEMO DATA - Hub Chantier")
    print("=" * 60)

    # Initialiser la base de donnees
    init_db()

    # Creer une session
    db = SessionLocal()

    try:
        # 1. Creer les utilisateurs
        user_ids = seed_users(db)

        # 2. Creer les chantiers
        chantier_ids = seed_chantiers(db, user_ids)

        # 3. Creer les affectations (planning)
        seed_affectations(db, user_ids, chantier_ids)

        # 4. Creer les taches
        seed_taches(db, chantier_ids)

        # 5. Creer les pointages
        seed_pointages(db, user_ids, chantier_ids)

        # 6. Creer les templates de formulaire
        template_ids = seed_templates_formulaires(db, user_ids)

        # 7. Creer les formulaires remplis
        seed_formulaires_remplis(db, user_ids, chantier_ids, template_ids)

        print("\n" + "=" * 60)
        print("SEED TERMINE AVEC SUCCES!")
        print("=" * 60)
        print("\nComptes de test disponibles:")
        print("-" * 40)
        print("Admin:      admin@greg-construction.fr / Admin123!")
        print("Conducteur: jean.dupont@greg-construction.fr / Test123!")
        print("Chef:       pierre.bernard@greg-construction.fr / Test123!")
        print("Compagnon:  lucas.moreau@greg-construction.fr / Test123!")
        print("-" * 40)

    except Exception as e:
        print(f"\n[ERREUR] {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
