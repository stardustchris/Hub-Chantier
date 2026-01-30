#!/usr/bin/env python3
"""Script de test pour vérifier l'API chantiers"""

from sqlalchemy import select
from modules.chantiers.infrastructure.persistence.sqlalchemy_chantier_repository import SQLAlchemyChantierRepository
from modules.chantiers.infrastructure.persistence.models import ChantierModel
from shared.infrastructure.database import get_db

def test_chantiers():
    """Test de récupération des chantiers"""
    db = next(get_db())
    repo = SQLAlchemyChantierRepository(db)

    try:
        # Tester find_all
        print("Test find_all()...")
        chantiers = repo.find_all(skip=0, limit=100)
        print(f"✓ Récupéré {len(chantiers)} chantiers")

        # Afficher les 5 premiers
        print("\nPremiers chantiers:")
        for i, chantier in enumerate(chantiers[:5], 1):
            print(f"  {i}. {chantier.code} - {chantier.nom} ({chantier.statut})")

        return True
    except Exception as e:
        print(f"✗ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_chantiers()
    exit(0 if success else 1)
