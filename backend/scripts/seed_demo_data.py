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
    # Admin (deja existant probablement)
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
    # Conducteurs de travaux
    {
        "email": "jean.dupont@greg-construction.fr",
        "password": "Test123!",
        "nom": "DUPONT",
        "prenom": "Jean",
        "role": "conducteur",
        "type_utilisateur": "employe",
        "telephone": "06 12 34 56 78",
        "metier": None,
        "code_utilisateur": "CDT001",
        "couleur": "#3498DB",
    },
    {
        "email": "marie.martin@greg-construction.fr",
        "password": "Test123!",
        "nom": "MARTIN",
        "prenom": "Marie",
        "role": "conducteur",
        "type_utilisateur": "employe",
        "telephone": "06 23 45 67 89",
        "metier": None,
        "code_utilisateur": "CDT002",
        "couleur": "#1ABC9C",
    },
    # Chefs de chantier
    {
        "email": "pierre.bernard@greg-construction.fr",
        "password": "Test123!",
        "nom": "BERNARD",
        "prenom": "Pierre",
        "role": "chef_chantier",
        "type_utilisateur": "employe",
        "telephone": "06 34 56 78 90",
        "metier": "macon",
        "code_utilisateur": "CHF001",
        "couleur": "#27AE60",
    },
    {
        "email": "sophie.petit@greg-construction.fr",
        "password": "Test123!",
        "nom": "PETIT",
        "prenom": "Sophie",
        "role": "chef_chantier",
        "type_utilisateur": "employe",
        "telephone": "06 45 67 89 01",
        "metier": "coffreur",
        "code_utilisateur": "CHF002",
        "couleur": "#E67E22",
    },
    # Compagnons
    {
        "email": "lucas.moreau@greg-construction.fr",
        "password": "Test123!",
        "nom": "MOREAU",
        "prenom": "Lucas",
        "role": "compagnon",
        "type_utilisateur": "employe",
        "telephone": "06 56 78 90 12",
        "metier": "macon",
        "code_utilisateur": "CMP001",
        "couleur": "#E74C3C",
    },
    {
        "email": "emma.garcia@greg-construction.fr",
        "password": "Test123!",
        "nom": "GARCIA",
        "prenom": "Emma",
        "role": "compagnon",
        "type_utilisateur": "employe",
        "telephone": "06 67 89 01 23",
        "metier": "ferrailleur",
        "code_utilisateur": "CMP002",
        "couleur": "#F1C40F",
    },
    {
        "email": "thomas.leroy@greg-construction.fr",
        "password": "Test123!",
        "nom": "LEROY",
        "prenom": "Thomas",
        "role": "compagnon",
        "type_utilisateur": "sous_traitant",
        "telephone": "06 78 90 12 34",
        "metier": "electricien",
        "code_utilisateur": "CMP003",
        "couleur": "#EC407A",
    },
    {
        "email": "julie.roux@greg-construction.fr",
        "password": "Test123!",
        "nom": "ROUX",
        "prenom": "Julie",
        "role": "compagnon",
        "type_utilisateur": "employe",
        "telephone": "06 89 01 23 45",
        "metier": "plombier",
        "code_utilisateur": "CMP004",
        "couleur": "#3F51B5",
    },
    # === INTERIMAIRES ===
    {
        "email": "kevin.blanc@interim-btp.fr",
        "password": "Test123!",
        "nom": "BLANC",
        "prenom": "Kevin",
        "role": "compagnon",
        "type_utilisateur": "interimaire",
        "telephone": "06 11 22 33 44",
        "metier": "macon",
        "code_utilisateur": "INT001",
        "couleur": "#FF9800",
    },
    {
        "email": "mehdi.benali@interim-btp.fr",
        "password": "Test123!",
        "nom": "BENALI",
        "prenom": "Mehdi",
        "role": "compagnon",
        "type_utilisateur": "interimaire",
        "telephone": "06 22 33 44 55",
        "metier": "coffreur",
        "code_utilisateur": "INT002",
        "couleur": "#FF5722",
    },
    {
        "email": "youssef.amrani@interim-btp.fr",
        "password": "Test123!",
        "nom": "AMRANI",
        "prenom": "Youssef",
        "role": "compagnon",
        "type_utilisateur": "interimaire",
        "telephone": "06 33 44 55 66",
        "metier": "ferrailleur",
        "code_utilisateur": "INT003",
        "couleur": "#795548",
    },
    {
        "email": "antoine.faure@interim-btp.fr",
        "password": "Test123!",
        "nom": "FAURE",
        "prenom": "Antoine",
        "role": "compagnon",
        "type_utilisateur": "interimaire",
        "telephone": "06 44 55 66 77",
        "metier": "macon",
        "code_utilisateur": "INT004",
        "couleur": "#607D8B",
    },
    # === SOUS-TRAITANTS ===
    {
        "email": "marc.dubois@elec-pro.fr",
        "password": "Test123!",
        "nom": "DUBOIS",
        "prenom": "Marc",
        "role": "compagnon",
        "type_utilisateur": "sous_traitant",
        "telephone": "06 55 66 77 88",
        "metier": "electricien",
        "code_utilisateur": "ST001",
        "couleur": "#00BCD4",
    },
    {
        "email": "paul.mercier@plomberie-mercier.fr",
        "password": "Test123!",
        "nom": "MERCIER",
        "prenom": "Paul",
        "role": "compagnon",
        "type_utilisateur": "sous_traitant",
        "telephone": "06 66 77 88 99",
        "metier": "plombier",
        "code_utilisateur": "ST002",
        "couleur": "#009688",
    },
    {
        "email": "david.lambert@toiture-lambert.fr",
        "password": "Test123!",
        "nom": "LAMBERT",
        "prenom": "David",
        "role": "compagnon",
        "type_utilisateur": "sous_traitant",
        "telephone": "06 77 88 99 00",
        "metier": "couvreur",
        "code_utilisateur": "ST003",
        "couleur": "#8BC34A",
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
    {
        "code": "A001",
        "nom": "Residence Les Jardins",
        "adresse": "15 Avenue des Fleurs, 75001 Paris",
        "description": "Construction d'un immeuble de 24 logements sur 4 etages avec parking souterrain",
        "statut": "en_cours",
        "couleur": "#3498DB",
        "latitude": 48.8566,
        "longitude": 2.3522,
        "contact_nom": "M. Lefevre",
        "contact_telephone": "01 23 45 67 89",
        "heures_estimees": 2400,
        "date_debut": date.today() - timedelta(days=60),
        "date_fin": date.today() + timedelta(days=120),
    },
    {
        "code": "A002",
        "nom": "Centre Commercial Grand Place",
        "adresse": "Zone Commerciale Nord, 93100 Montreuil",
        "description": "Extension du centre commercial - 2000m2 de surface commerciale",
        "statut": "en_cours",
        "couleur": "#E74C3C",
        "latitude": 48.8634,
        "longitude": 2.4437,
        "contact_nom": "Mme Dubois",
        "contact_telephone": "01 34 56 78 90",
        "heures_estimees": 3600,
        "date_debut": date.today() - timedelta(days=30),
        "date_fin": date.today() + timedelta(days=180),
    },
    {
        "code": "A003",
        "nom": "Ecole Primaire Jean Jaures",
        "adresse": "8 Rue de la Republique, 94200 Ivry-sur-Seine",
        "description": "Renovation complete et extension - nouveau batiment de 6 classes",
        "statut": "ouvert",
        "couleur": "#27AE60",
        "latitude": 48.8156,
        "longitude": 2.3847,
        "contact_nom": "Direction Education",
        "contact_telephone": "01 45 67 89 01",
        "heures_estimees": 1800,
        "date_debut": date.today() + timedelta(days=30),
        "date_fin": date.today() + timedelta(days=150),
    },
    {
        "code": "A004",
        "nom": "Villa Moderne Duplex",
        "adresse": "42 Chemin des Vignes, 78000 Versailles",
        "description": "Construction villa contemporaine 180m2 avec piscine",
        "statut": "en_cours",
        "couleur": "#9B59B6",
        "latitude": 48.8049,
        "longitude": 2.1204,
        "contact_nom": "M. et Mme Fontaine",
        "contact_telephone": "06 12 34 56 78",
        "heures_estimees": 1200,
        "date_debut": date.today() - timedelta(days=45),
        "date_fin": date.today() + timedelta(days=75),
    },
    {
        "code": "A005",
        "nom": "Bureaux Tech Valley",
        "adresse": "Tech Park, 92100 Boulogne-Billancourt",
        "description": "Amenagement de 500m2 de bureaux en open space avec salles de reunion",
        "statut": "receptionne",
        "couleur": "#F1C40F",
        "latitude": 48.8397,
        "longitude": 2.2399,
        "contact_nom": "StartupCorp SAS",
        "contact_telephone": "01 56 78 90 12",
        "heures_estimees": 600,
        "date_debut": date.today() - timedelta(days=90),
        "date_fin": date.today() - timedelta(days=15),
    },
]

TACHES_DATA = [
    # Taches pour chantier A001 (Residence Les Jardins)
    {"chantier_code": "A001", "titre": "Terrassement et fondations", "description": "Excavation et coulage des fondations", "statut": "termine", "heures_estimees": 400},
    {"chantier_code": "A001", "titre": "Gros oeuvre RDC", "description": "Murs porteurs et plancher RDC", "statut": "termine", "heures_estimees": 300},
    {"chantier_code": "A001", "titre": "Gros oeuvre 1er etage", "description": "Murs et plancher 1er etage", "statut": "a_faire", "heures_estimees": 300},
    {"chantier_code": "A001", "titre": "Gros oeuvre 2eme etage", "description": "Murs et plancher 2eme etage", "statut": "a_faire", "heures_estimees": 300},
    {"chantier_code": "A001", "titre": "Toiture", "description": "Charpente et couverture", "statut": "a_faire", "heures_estimees": 250},

    # Taches pour chantier A002 (Centre Commercial)
    {"chantier_code": "A002", "titre": "Demolition zone est", "description": "Demolition des anciens locaux", "statut": "termine", "heures_estimees": 200},
    {"chantier_code": "A002", "titre": "Fondations extension", "description": "Fondations de la nouvelle aile", "statut": "a_faire", "heures_estimees": 350},
    {"chantier_code": "A002", "titre": "Structure metallique", "description": "Montage de l'ossature metallique", "statut": "a_faire", "heures_estimees": 500},

    # Taches pour chantier A004 (Villa)
    {"chantier_code": "A004", "titre": "Fondations villa", "description": "Terrassement et fondations", "statut": "termine", "heures_estimees": 100},
    {"chantier_code": "A004", "titre": "Elevation murs", "description": "Construction des murs", "statut": "a_faire", "heures_estimees": 200},
    {"chantier_code": "A004", "titre": "Piscine", "description": "Construction de la piscine", "statut": "a_faire", "heures_estimees": 150},
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

    # Compagnons a affecter
    compagnons = [
        ("lucas.moreau@greg-construction.fr", "A001"),
        ("emma.garcia@greg-construction.fr", "A001"),
        ("thomas.leroy@greg-construction.fr", "A002"),
        ("julie.roux@greg-construction.fr", "A004"),
    ]

    # Admin qui cree les affectations
    admin_id = user_ids.get("admin@greg-construction.fr") or user_ids.get("greg@greg-construction.fr") or 1

    created_count = 0
    for email, chantier_code in compagnons:
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

    # Compagnons avec leurs chantiers
    compagnons = [
        ("lucas.moreau@greg-construction.fr", "A001"),
        ("emma.garcia@greg-construction.fr", "A001"),
        ("thomas.leroy@greg-construction.fr", "A002"),
        ("julie.roux@greg-construction.fr", "A004"),
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
