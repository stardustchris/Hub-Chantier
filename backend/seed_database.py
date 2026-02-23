"""Script pour initialiser la base de données avec des données de test."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, date

# Import des modèles
from modules.auth.infrastructure.persistence.user_model import UserModel
from modules.chantiers.infrastructure.persistence.chantier_model import ChantierModel

# Créer la session
engine = create_engine("sqlite:///hub_chantier.db")
Session = sessionmaker(bind=engine)
session = Session()

try:
    # Vérifier si des utilisateurs existent déjà
    existing_users = session.query(UserModel).count()

    if existing_users > 0:
        print(f"✓ {existing_users} utilisateurs existent déjà")
    else:
        print("📝 Création des utilisateurs de test...")

        # Créer un utilisateur admin
        admin = UserModel(
            nom="Admin",
            prenom="Super",
            email="admin@greg-construction.fr",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyVK/U7rvQe.",  # password: admin123
            role="admin",
            telephone="+33601020304",
            actif=True,
            created_at=datetime.now(),
        )
        session.add(admin)
        print("  ✓ Utilisateur admin créé (admin@greg-construction.fr / admin123)")

        # Créer un conducteur
        conducteur = UserModel(
            nom="Dupont",
            prenom="Jean",
            email="conducteur@greg-construction.fr",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyVK/U7rvQe.",  # password: admin123
            role="conducteur",
            telephone="+33601020305",
            actif=True,
            created_at=datetime.now(),
        )
        session.add(conducteur)
        print("  ✓ Utilisateur conducteur créé (conducteur@greg-construction.fr / admin123)")

        session.commit()

    # Vérifier si des chantiers existent
    existing_chantiers = session.query(ChantierModel).count()

    if existing_chantiers > 0:
        print(f"✓ {existing_chantiers} chantiers existent déjà")
    else:
        print("\n📝 Création des chantiers de test...")

        # Créer le chantier de test "A001"
        chantier = ChantierModel(
            code="A001",
            nom="Residence Les Jardins",
            adresse="15 Avenue des Fleurs, 75001 Paris",
            description="Construction d'une résidence de 50 logements",
            statut="ouvert",
            couleur="#3B82F6",
            heures_estimees=2000.0,
            date_debut=date(2026, 1, 15),
            date_fin=date(2026, 12, 31),
            conducteur_ids=[],
            chef_chantier_ids=[],
            created_at=datetime.now(),
        )
        session.add(chantier)
        print("  ✓ Chantier A001 créé")

        session.commit()

    print("\n✅ Base de données initialisée avec succès !")
    print("\n🔐 Credentials:")
    print("   Admin: admin@greg-construction.fr / admin123")
    print("   Conducteur: conducteur@greg-construction.fr / admin123")

except Exception as e:
    print(f"\n❌ Erreur: {e}")
    session.rollback()
finally:
    session.close()
