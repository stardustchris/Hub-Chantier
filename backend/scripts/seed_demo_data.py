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
from datetime import datetime, date, timedelta
from typing import List

# Ajouter le chemin du backend pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from shared.infrastructure.database import SessionLocal, init_db
from modules.auth.infrastructure.persistence.user_model import UserModel
from modules.chantiers.infrastructure.persistence.chantier_model import ChantierModel
from modules.planning.infrastructure.persistence.affectation_model import AffectationModel
from modules.pointages.infrastructure.persistence.models import PointageModel, FeuilleHeuresModel
from modules.taches.infrastructure.persistence import TacheModel

# Configuration du hashage de mot de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash un mot de passe."""
    return pwd_context.hash(password)


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
            print(f"  [EXISTE] {user_data['prenom']} {user_data['nom']} ({user_data['role']})")
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
    """Cree des pointages pour la semaine derniere."""
    print("\n=== Creation des pointages ===")

    # Semaine derniere
    today = date.today()
    last_monday = today - timedelta(days=today.weekday() + 7)

    # Compagnons avec leurs chantiers
    compagnons = [
        ("lucas.moreau@greg-construction.fr", "A001"),
        ("emma.garcia@greg-construction.fr", "A001"),
        ("thomas.leroy@greg-construction.fr", "A002"),
        ("julie.roux@greg-construction.fr", "A004"),
    ]

    created_count = 0
    for email, chantier_code in compagnons:
        user_id = user_ids.get(email)
        chantier_id = chantier_ids.get(chantier_code)

        if not user_id or not chantier_id:
            continue

        # Creer des pointages du lundi au vendredi
        for day_offset in range(5):
            pointage_date = last_monday + timedelta(days=day_offset)

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

            pointage = PointageModel(
                utilisateur_id=user_id,
                chantier_id=chantier_id,
                date_pointage=pointage_date,
                heures_normales_minutes=heures_normales_min,
                heures_supplementaires_minutes=heures_sup_min,
                statut="valide",
            )
            db.add(pointage)
            created_count += 1

    db.commit()
    print(f"  [CREE] {created_count} pointages pour la semaine du {last_monday}")


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
