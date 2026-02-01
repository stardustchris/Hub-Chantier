#!/usr/bin/env python3
"""
Script pour republier les événements AffectationCreatedEvent pour les affectations existantes.

Ce script est utile pour tester FDH-10 en créant les pointages depuis les affectations déjà créées.

Usage:
    cd backend
    python -m scripts.republish_affectation_events
"""

import os
import sys
from datetime import date, timedelta
import asyncio

# Ajouter le chemin du backend pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session

from shared.infrastructure.database import SessionLocal, init_db
from shared.infrastructure.event_bus import event_bus
from modules.planning.infrastructure.persistence.affectation_model import AffectationModel
from modules.planning.domain.events.affectation_events import AffectationCreatedEvent


def main():
    """Point d'entrée principal."""
    print("=" * 60)
    print("REPUBLICATION DES ÉVÉNEMENTS AFFECTATIONCREATEDEVENT")
    print("=" * 60)

    # Initialiser la base de données
    init_db()

    # Câbler l'intégration Planning → Pointages (FDH-10)
    from modules.pointages.infrastructure.event_handlers import setup_planning_integration
    setup_planning_integration(SessionLocal)
    print("✓ Intégration Planning → Pointages câblée (FDH-10)")
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

        # Créer les événements
        events_to_publish = []
        for affectation in affectations:
            event = AffectationCreatedEvent(
                affectation_id=affectation.id,
                utilisateur_id=affectation.utilisateur_id,
                chantier_id=affectation.chantier_id,
                date=affectation.date,
                heures_prevues=affectation.heures_prevues,
                created_by=affectation.created_by or 0,
            )
            events_to_publish.append(event)

        print(f"Republication de {len(events_to_publish)} événements...")

        # Fonction asynchrone pour publier tous les événements
        async def publish_all():
            published_count = 0
            for event in events_to_publish:
                await event_bus.publish(event)
                published_count += 1

                if published_count % 10 == 0:
                    print(f"  Publié {published_count}/{len(events_to_publish)} événements...")
            return published_count

        # Exécuter la publication asynchrone
        published_count = asyncio.run(publish_all())

        print()
        print("=" * 60)
        print(f"✓ {published_count} événements republiés avec succès")
        print("=" * 60)
        print()
        print("Les pointages devraient maintenant être créés.")
        print("Exécutez le script de vérification pour confirmer.")

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
