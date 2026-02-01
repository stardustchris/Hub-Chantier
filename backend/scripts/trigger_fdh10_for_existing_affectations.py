#!/usr/bin/env python3
"""
Script pour déclencher FDH-10 sur les affectations existantes.

Ce script appelle directement le handler pour créer les pointages depuis les affectations déjà créées.

Usage:
    cd backend
    python -m scripts.trigger_fdh10_for_existing_affectations
"""

import os
import sys
from datetime import date, timedelta

# Ajouter le chemin du backend pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session

from shared.infrastructure.database import SessionLocal, init_db
from modules.planning.infrastructure.persistence.affectation_model import AffectationModel
from modules.planning.domain.events.affectation_events import AffectationCreatedEvent
from modules.pointages.infrastructure.event_handlers import handle_affectation_created


def main():
    """Point d'entrée principal."""
    print("=" * 60)
    print("DÉCLENCHEMENT FDH-10 POUR AFFECTATIONS EXISTANTES")
    print("=" * 60)

    # Initialiser la base de données
    init_db()
    print("✓ Base de données initialisée")
    print()

    # Créer une session
    db = SessionLocal()

    try:
        # Obtenir le lundi de cette semaine
        today = date.today()
        monday = today - timedelta(days=today.weekday())
        friday = monday + timedelta(days=4)

        print(f"Recherche des affectations de la semaine: {monday} à {friday}")

        # Récupérer toutes les affectations de la semaine
        affectations = db.query(AffectationModel).filter(
            AffectationModel.date >= monday,
            AffectationModel.date <= friday
        ).all()

        print(f"✓ {len(affectations)} affectations trouvées")
        print()

        # Créer les événements et appeler directement le handler
        print(f"Appel direct du handler pour {len(affectations)} affectations...")
        processed_count = 0
        created_count = 0
        skipped_count = 0

        for affectation in affectations:
            # Créer l'événement
            event = AffectationCreatedEvent(
                affectation_id=affectation.id,
                utilisateur_id=affectation.utilisateur_id,
                chantier_id=affectation.chantier_id,
                date=affectation.date,
                heures_prevues=affectation.heures_prevues,
                created_by=affectation.created_by or 0,
            )

            # Appeler directement le handler
            try:
                handle_affectation_created(event, db)
                created_count += 1
            except Exception as e:
                # Vérifier si c'est une erreur de doublon (déjà existant)
                if "UNIQUE constraint failed" in str(e) or "duplicate key" in str(e):
                    skipped_count += 1
                else:
                    print(f"  [ERREUR] Affectation {affectation.id}: {e}")
                    raise

            processed_count += 1

            if processed_count % 10 == 0:
                print(f"  Traité {processed_count}/{len(affectations)} affectations...")

        db.commit()

        print()
        print("=" * 60)
        print(f"✓ {processed_count} affectations traitées")
        print(f"  - {created_count} pointages créés")
        print(f"  - {skipped_count} pointages déjà existants (ignorés)")
        print("=" * 60)
        print()
        print("Les pointages ont été créés avec succès.")

    except Exception as e:
        print(f"\n[ERREUR] {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
