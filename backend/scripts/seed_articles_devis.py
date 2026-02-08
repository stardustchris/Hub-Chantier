#!/usr/bin/env python3
"""Script de seed pour la bibliotheque d'articles BTP (DEV-01).

Usage:
    cd backend
    python -m scripts.seed_articles_devis

Cree ~20 articles de base couvrant les corps de metier les plus courants.
Les articles ne sont crees que s'il n'y en a pas deja en base (safe re-run).
"""

import os
import sys
from datetime import datetime
from decimal import Decimal

# Ajouter le chemin du backend pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from shared.infrastructure.database import SessionLocal, init_db
from modules.devis.infrastructure.persistence.models import ArticleDevisModel


ARTICLES_SEED = [
    # Gros oeuvre
    {
        "code": "GO-001",
        "designation": "Beton arme C25/30",
        "unite": "m3",
        "prix_unitaire_ht": Decimal("120.00"),
        "categorie": "gros_oeuvre",
        "description": "Beton arme classe C25/30 mis en oeuvre, y compris coffrage et ferraillage courant",
    },
    {
        "code": "GO-002",
        "designation": "Parpaing 20x20x50",
        "unite": "u",
        "prix_unitaire_ht": Decimal("1.50"),
        "categorie": "gros_oeuvre",
        "description": "Parpaing creux 20x20x50 cm, pose comprise",
    },
    {
        "code": "GO-003",
        "designation": "Coffrage bois traditionnel",
        "unite": "m2",
        "prix_unitaire_ht": Decimal("35.00"),
        "categorie": "gros_oeuvre",
        "description": "Coffrage bois traditionnel, mise en oeuvre et decoffrage",
    },
    {
        "code": "GO-004",
        "designation": "Ferraillage acier HA",
        "unite": "kg",
        "prix_unitaire_ht": Decimal("1.80"),
        "categorie": "gros_oeuvre",
        "description": "Acier haute adherence, faconnage et pose inclus",
    },
    # Terrassement
    {
        "code": "TER-001",
        "designation": "Terrassement en pleine masse",
        "unite": "m3",
        "prix_unitaire_ht": Decimal("8.00"),
        "categorie": "terrassement",
        "description": "Terrassement mecanise en pleine masse, chargement compris",
    },
    {
        "code": "TER-002",
        "designation": "Remblai compacte",
        "unite": "m3",
        "prix_unitaire_ht": Decimal("12.00"),
        "categorie": "terrassement",
        "description": "Remblai en materiaux selectionnes, compactage par couches",
    },
    {
        "code": "TER-003",
        "designation": "Evacuation de terres",
        "unite": "m3",
        "prix_unitaire_ht": Decimal("15.00"),
        "categorie": "terrassement",
        "description": "Chargement, transport et mise en decharge des terres excedentaires",
    },
    # Electricite
    {
        "code": "ELEC-001",
        "designation": "Point lumineux",
        "unite": "u",
        "prix_unitaire_ht": Decimal("85.00"),
        "categorie": "electricite",
        "description": "Fourniture et pose d'un point lumineux complet (cable, interrupteur, DCL)",
    },
    {
        "code": "ELEC-002",
        "designation": "Prise de courant 2P+T",
        "unite": "u",
        "prix_unitaire_ht": Decimal("65.00"),
        "categorie": "electricite",
        "description": "Fourniture et pose d'une prise 2P+T 16A, encastree",
    },
    {
        "code": "ELEC-003",
        "designation": "Tableau electrique 2 rangees",
        "unite": "u",
        "prix_unitaire_ht": Decimal("450.00"),
        "categorie": "electricite",
        "description": "Tableau electrique 2 rangees equipe (disjoncteurs, inter diff)",
    },
    # Plomberie
    {
        "code": "PLB-001",
        "designation": "Alimentation eau froide/chaude",
        "unite": "ml",
        "prix_unitaire_ht": Decimal("45.00"),
        "categorie": "plomberie",
        "description": "Alimentation en multicouche, fourniture et pose",
    },
    {
        "code": "PLB-002",
        "designation": "Evacuation PVC diametre 100",
        "unite": "ml",
        "prix_unitaire_ht": Decimal("35.00"),
        "categorie": "plomberie",
        "description": "Evacuation en PVC diametre 100 mm, fourniture et pose",
    },
    {
        "code": "PLB-003",
        "designation": "Pose WC suspendu complet",
        "unite": "u",
        "prix_unitaire_ht": Decimal("380.00"),
        "categorie": "plomberie",
        "description": "Fourniture et pose WC suspendu avec bati-support",
    },
    # Peinture
    {
        "code": "PNT-001",
        "designation": "Peinture acrylique mate",
        "unite": "m2",
        "prix_unitaire_ht": Decimal("12.00"),
        "categorie": "peinture",
        "description": "Application peinture acrylique mate sur murs, 2 couches",
    },
    {
        "code": "PNT-002",
        "designation": "Enduit de lissage",
        "unite": "m2",
        "prix_unitaire_ht": Decimal("8.50"),
        "categorie": "peinture",
        "description": "Enduit de lissage sur murs avant peinture",
    },
    # Menuiserie
    {
        "code": "MEN-001",
        "designation": "Fenetre PVC double vitrage 120x120",
        "unite": "u",
        "prix_unitaire_ht": Decimal("320.00"),
        "categorie": "menuiserie",
        "description": "Fourniture et pose fenetre PVC oscillo-battante, double vitrage 4/16/4",
    },
    {
        "code": "MEN-002",
        "designation": "Porte interieure bois 83 cm",
        "unite": "u",
        "prix_unitaire_ht": Decimal("185.00"),
        "categorie": "menuiserie",
        "description": "Fourniture et pose porte interieure isoplane, huisserie comprise",
    },
    # Carrelage
    {
        "code": "CAR-001",
        "designation": "Carrelage sol gres cerame 60x60",
        "unite": "m2",
        "prix_unitaire_ht": Decimal("55.00"),
        "categorie": "carrelage",
        "description": "Fourniture et pose carrelage gres cerame 60x60, colle comprise",
    },
    # Isolation
    {
        "code": "ISO-001",
        "designation": "Isolation laine de verre 200mm",
        "unite": "m2",
        "prix_unitaire_ht": Decimal("25.00"),
        "categorie": "isolation",
        "description": "Fourniture et pose isolation en laine de verre 200 mm, R=5",
    },
    # Main d'oeuvre
    {
        "code": "MOE-001",
        "designation": "Main d'oeuvre ouvrier qualifie",
        "unite": "heure",
        "prix_unitaire_ht": Decimal("42.00"),
        "categorie": "main_oeuvre",
        "description": "Heure de main d'oeuvre ouvrier qualifie, charges comprises",
    },
]


def seed_articles(db: Session) -> int:
    """Insere les articles de seed si la table est vide.

    Args:
        db: Session SQLAlchemy.

    Returns:
        Le nombre d'articles inseres.
    """
    existing_count = db.query(ArticleDevisModel).filter(
        ArticleDevisModel.deleted_at.is_(None)
    ).count()

    if existing_count > 0:
        print(f"[SKIP] {existing_count} articles deja en base, aucune insertion.")
        return 0

    now = datetime.utcnow()
    count = 0

    for data in ARTICLES_SEED:
        model = ArticleDevisModel(
            code=data["code"],
            designation=data["designation"],
            unite=data["unite"],
            prix_unitaire_ht=data["prix_unitaire_ht"],
            categorie=data["categorie"],
            description=data.get("description"),
            taux_tva=Decimal("20"),
            actif=True,
            created_at=now,
            created_by=1,  # Admin par defaut
        )
        db.add(model)
        count += 1

    db.commit()
    print(f"[OK] {count} articles de base inseres.")
    return count


def main() -> None:
    """Point d'entree du script de seed."""
    print("=" * 60)
    print("  Seed Articles BTP - Bibliotheque de prix (DEV-01)")
    print("=" * 60)

    init_db()
    db = SessionLocal()

    try:
        inserted = seed_articles(db)
        if inserted:
            print(f"\nCategories couvertes :")
            cats = sorted(set(a["categorie"] for a in ARTICLES_SEED))
            for cat in cats:
                nb = sum(1 for a in ARTICLES_SEED if a["categorie"] == cat)
                print(f"  - {cat}: {nb} article{'s' if nb > 1 else ''}")
        print("\nTermine.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
