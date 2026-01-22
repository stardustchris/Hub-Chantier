#!/usr/bin/env python3
"""Script pour corriger/recréer l'utilisateur admin avec le bon rôle."""

import sys
import os

# Ajouter le dossier parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.infrastructure.database import SessionLocal, engine
from modules.auth.infrastructure.persistence.user_model import UserModel, Base
import bcrypt
from datetime import datetime

def main():
    # Créer les tables si elles n'existent pas
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Vérifier si l'utilisateur existe
        existing_user = db.query(UserModel).filter(UserModel.email == "admin@greg.fr").first()

        if existing_user:
            print(f"Utilisateur trouvé avec rôle: {existing_user.role}")
            # Supprimer l'utilisateur existant
            db.delete(existing_user)
            db.commit()
            print("Ancien utilisateur supprimé")

        # Créer le nouveau mot de passe hashé
        password_hash = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()

        # Créer l'utilisateur avec le bon rôle
        user = UserModel(
            email="admin@greg.fr",
            password_hash=password_hash,
            nom="Admin",
            prenom="Greg",
            role="admin",  # RÔLE CORRECT: admin, conducteur, chef_chantier, compagnon
            type_utilisateur="employe",  # TYPE CORRECT: employe, sous_traitant
            is_active=True,
            couleur="#3498DB",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        db.add(user)
        db.commit()

        print("=" * 50)
        print("Utilisateur admin créé avec succès!")
        print("=" * 50)
        print("Email: admin@greg.fr")
        print("Mot de passe: admin123")
        print("Rôle: admin")
        print("=" * 50)

    except Exception as e:
        print(f"Erreur: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
