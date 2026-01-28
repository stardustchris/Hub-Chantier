"""
Exemples de création et utilisation des 16 événements de domaine.

Ce fichier montre comment instancier et utiliser chaque événement.
"""

from datetime import date, time, datetime
from modules.planning.domain.events import AffectationCreatedEvent, AffectationUpdatedEvent, AffectationDeletedEvent
from modules.pointages.domain.events import HeuresCreatedEvent, HeuresUpdatedEvent, HeuresValidatedEvent, HeuresRejectedEvent
from modules.chantiers.domain.events import ChantierCreatedEvent, ChantierUpdatedEvent, ChantierDeletedEvent, ChantierStatutChangedEvent
from modules.signalements.domain.events import SignalementCreatedEvent, SignalementUpdatedEvent, SignalementClosedEvent
from modules.documents.domain.events import DocumentUploadedEvent, DocumentDeletedEvent


def example_planning_events():
    """Exemples : Module Planning"""
    print("\n" + "="*60)
    print("MODULE 1 : PLANNING")
    print("="*60)

    # 1. Affectation créée
    affectation_created = AffectationCreatedEvent(
        affectation_id=1,
        user_id=5,
        chantier_id=10,
        date_affectation=date(2026, 1, 28),
        heure_debut=time(8, 0),
        heure_fin=time(17, 0),
        note="Affectation standard",
        metadata={'user_id': 1, 'ip_address': '192.168.1.1'}
    )
    print(f"\n1. AffectationCreatedEvent")
    print(f"   event_type: {affectation_created.event_type}")
    print(f"   aggregate_id: {affectation_created.aggregate_id}")
    print(f"   data: {affectation_created.data}")

    # 2. Affectation mise à jour
    affectation_updated = AffectationUpdatedEvent(
        affectation_id=1,
        user_id=5,
        chantier_id=10,
        date_affectation=date(2026, 1, 28),
        changes={'heure_debut': '09:00', 'heure_fin': '18:00'},
        metadata={'user_id': 2}
    )
    print(f"\n2. AffectationUpdatedEvent")
    print(f"   event_type: {affectation_updated.event_type}")
    print(f"   changes: {affectation_updated.data['changes']}")

    # 3. Affectation supprimée
    affectation_deleted = AffectationDeletedEvent(
        affectation_id=1,
        user_id=5,
        chantier_id=10,
        date_affectation=date(2026, 1, 28),
        metadata={'user_id': 2}
    )
    print(f"\n3. AffectationDeletedEvent")
    print(f"   event_type: {affectation_deleted.event_type}")
    print(f"   aggregate_id: {affectation_deleted.aggregate_id}")


def example_pointages_events():
    """Exemples : Module Pointages"""
    print("\n" + "="*60)
    print("MODULE 2 : POINTAGES")
    print("="*60)

    # 4. Heures créées
    heures_created = HeuresCreatedEvent(
        heures_id=1,
        user_id=5,
        chantier_id=10,
        date=date(2026, 1, 28),
        heures_travaillees=8.0,
        heures_supplementaires=2.0,
        metadata={'user_id': 5}
    )
    print(f"\n4. HeuresCreatedEvent")
    print(f"   event_type: {heures_created.event_type}")
    print(f"   data: {heures_created.data}")

    # 5. Heures mises à jour
    heures_updated = HeuresUpdatedEvent(
        heures_id=1,
        user_id=5,
        chantier_id=10,
        date=date(2026, 1, 28),
        heures_travaillees=8.5,
        heures_supplementaires=1.5,
        changes={'heures_travaillees': 8.5},
        metadata={'user_id': 5}
    )
    print(f"\n5. HeuresUpdatedEvent")
    print(f"   event_type: {heures_updated.event_type}")
    print(f"   changes: {heures_updated.data['changes']}")

    # 6. Heures validées (⚠️ CRITIQUE POUR SYNC PAIE)
    heures_validated = HeuresValidatedEvent(
        heures_id=1,
        user_id=5,
        chantier_id=10,
        date=date(2026, 1, 28),
        heures_travaillees=8.0,
        heures_supplementaires=2.0,
        validated_by=3,  # Responsable qui valide
        validated_at=datetime.utcnow(),
        metadata={'user_id': 3, 'ip_address': '192.168.1.1'}
    )
    print(f"\n6. HeuresValidatedEvent ⚠️ CRITIQUE")
    print(f"   event_type: {heures_validated.event_type}")
    print(f"   validated_by: {heures_validated.data['validated_by']}")
    print(f"   [Cette événement déclenche la SYNC PAIE]")

    # 7. Heures rejetées
    heures_rejected = HeuresRejectedEvent(
        heures_id=1,
        user_id=5,
        chantier_id=10,
        date=date(2026, 1, 28),
        rejected_by=3,
        reason="Incohérence avec le planning",
        metadata={'user_id': 3}
    )
    print(f"\n7. HeuresRejectedEvent")
    print(f"   event_type: {heures_rejected.event_type}")
    print(f"   reason: {heures_rejected.data['reason']}")


def example_chantiers_events():
    """Exemples : Module Chantiers"""
    print("\n" + "="*60)
    print("MODULE 3 : CHANTIERS")
    print("="*60)

    # 8. Chantier créé
    chantier_created = ChantierCreatedEvent(
        chantier_id=10,
        nom="Rénovation Rue de la Paix",
        adresse="123 Rue de la Paix, 75000 Paris",
        statut="ouvert",
        metadata={'user_id': 1}
    )
    print(f"\n8. ChantierCreatedEvent")
    print(f"   event_type: {chantier_created.event_type}")
    print(f"   data: {chantier_created.data}")

    # 9. Chantier mis à jour
    chantier_updated = ChantierUpdatedEvent(
        chantier_id=10,
        nom="Rénovation Rue de la Paix - Phase 2",
        adresse="123 Rue de la Paix, 75000 Paris",
        statut="en_cours",
        changes={'nom': 'Rénovation Rue de la Paix - Phase 2'},
        metadata={'user_id': 2}
    )
    print(f"\n9. ChantierUpdatedEvent")
    print(f"   event_type: {chantier_updated.event_type}")
    print(f"   changes: {chantier_updated.data['changes']}")

    # 10. Chantier supprimé
    chantier_deleted = ChantierDeletedEvent(
        chantier_id=10,
        nom="Rénovation Rue de la Paix",
        adresse="123 Rue de la Paix, 75000 Paris",
        metadata={'user_id': 1}
    )
    print(f"\n10. ChantierDeletedEvent")
    print(f"    event_type: {chantier_deleted.event_type}")
    print(f"    aggregate_id: {chantier_deleted.aggregate_id}")

    # 11. Statut du chantier changé
    chantier_statut_changed = ChantierStatutChangedEvent(
        chantier_id=10,
        ancien_statut="ouvert",
        nouveau_statut="en_cours",
        nom="Rénovation Rue de la Paix",
        adresse="123 Rue de la Paix, 75000 Paris",
        metadata={'user_id': 2}
    )
    print(f"\n11. ChantierStatutChangedEvent")
    print(f"    event_type: {chantier_statut_changed.event_type}")
    print(f"    ancien_statut -> nouveau_statut: {chantier_statut_changed.data['ancien_statut']} -> {chantier_statut_changed.data['nouveau_statut']}")


def example_signalements_events():
    """Exemples : Module Signalements"""
    print("\n" + "="*60)
    print("MODULE 4 : SIGNALEMENTS")
    print("="*60)

    # 12. Signalement créé
    signalement_created = SignalementCreatedEvent(
        signalement_id=1,
        chantier_id=10,
        user_id=5,
        titre="Équipement de sécurité manquant",
        gravite="haute",
        metadata={'user_id': 5}
    )
    print(f"\n12. SignalementCreatedEvent")
    print(f"    event_type: {signalement_created.event_type}")
    print(f"    titre: {signalement_created.data['titre']}")
    print(f"    gravite: {signalement_created.data['gravite']}")

    # 13. Signalement mis à jour
    signalement_updated = SignalementUpdatedEvent(
        signalement_id=1,
        chantier_id=10,
        user_id=5,
        titre="Équipement de sécurité manquant",
        gravite="critique",
        changes={'gravite': 'critique'},
        metadata={'user_id': 3}
    )
    print(f"\n13. SignalementUpdatedEvent")
    print(f"    event_type: {signalement_updated.event_type}")
    print(f"    changes: {signalement_updated.data['changes']}")

    # 14. Signalement fermé
    signalement_closed = SignalementClosedEvent(
        signalement_id=1,
        chantier_id=10,
        user_id=5,
        titre="Équipement de sécurité manquant",
        gravite="haute",
        closed_by=3,
        resolution="Équipement fourni et installé",
        metadata={'user_id': 3}
    )
    print(f"\n14. SignalementClosedEvent")
    print(f"    event_type: {signalement_closed.event_type}")
    print(f"    resolution: {signalement_closed.data['resolution']}")


def example_documents_events():
    """Exemples : Module Documents"""
    print("\n" + "="*60)
    print("MODULE 5 : DOCUMENTS")
    print("="*60)

    # 15. Document téléchargé
    document_uploaded = DocumentUploadedEvent(
        document_id=1,
        nom="plans_architecture.pdf",
        type_document="plan",
        chantier_id=10,
        user_id=5,
        metadata={'user_id': 5}
    )
    print(f"\n15. DocumentUploadedEvent")
    print(f"    event_type: {document_uploaded.event_type}")
    print(f"    nom: {document_uploaded.data['nom']}")
    print(f"    type_document: {document_uploaded.data['type_document']}")

    # 16. Document supprimé
    document_deleted = DocumentDeletedEvent(
        document_id=1,
        nom="plans_architecture.pdf",
        type_document="plan",
        chantier_id=10,
        user_id=5,
        metadata={'user_id': 5}
    )
    print(f"\n16. DocumentDeletedEvent")
    print(f"    event_type: {document_deleted.event_type}")
    print(f"    aggregate_id: {document_deleted.aggregate_id}")


def show_event_structure():
    """Montre la structure complète d'un événement"""
    print("\n" + "="*60)
    print("STRUCTURE COMPLÈTE D'UN ÉVÉNEMENT DOMAINE")
    print("="*60)

    event = AffectationCreatedEvent(
        affectation_id=1,
        user_id=5,
        chantier_id=10,
        date_affectation=date(2026, 1, 28),
        metadata={'user_id': 1, 'ip_address': '192.168.1.1', 'user_agent': 'Mozilla/5.0'}
    )

    print(f"\nProprietés héritées de DomainEvent:")
    print(f"  event_id: {event.event_id} (UUID unique)")
    print(f"  event_type: {event.event_type}")
    print(f"  aggregate_id: {event.aggregate_id}")
    print(f"  occurred_at: {event.occurred_at}")

    print(f"\nPayload data:")
    for key, value in event.data.items():
        print(f"  {key}: {value}")

    print(f"\nMétadonnées:")
    for key, value in event.metadata.items():
        print(f"  {key}: {value}")

    print(f"\nSérialisation (to_dict):")
    event_dict = event.to_dict()
    print(f"  event_id: {event_dict['event_id']}")
    print(f"  event_type: {event_dict['event_type']}")
    print(f"  aggregate_id: {event_dict['aggregate_id']}")
    print(f"  data: {event_dict['data']}")
    print(f"  metadata: {event_dict['metadata']}")
    print(f"  occurred_at: {event_dict['occurred_at']}")


if __name__ == '__main__':
    try:
        print("\n")
        print("╔════════════════════════════════════════════════════════════╗")
        print("║       EXEMPLES : CRÉATION DES 16 ÉVÉNEMENTS DE DOMAINE     ║")
        print("╚════════════════════════════════════════════════════════════╝")

        example_planning_events()
        example_pointages_events()
        example_chantiers_events()
        example_signalements_events()
        example_documents_events()
        show_event_structure()

        print("\n" + "="*60)
        print("✓ TOUS LES EXEMPLES EXÉCUTÉS AVEC SUCCÈS")
        print("="*60 + "\n")

    except Exception as e:
        print(f"\n✗ ERREUR: {e}")
        import traceback
        traceback.print_exc()
