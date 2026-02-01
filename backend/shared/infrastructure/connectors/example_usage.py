"""
Exemple d'utilisation des connecteurs webhooks.

Ce script démontre comment utiliser les connecteurs Pennylane et Silae
pour transformer des événements Hub Chantier en payloads API.
"""

from datetime import datetime
from shared.infrastructure.event_bus.domain_event import DomainEvent
from shared.infrastructure.connectors import get_connector
from shared.infrastructure.connectors.registry import (
    list_connectors,
    find_connector_for_event,
)


def example_pennylane_achat():
    """Exemple: Transformer un achat en facture fournisseur Pennylane."""
    print("\n=== Exemple Pennylane - Achat (Facture Fournisseur) ===")

    # 1. Créer l'événement
    event = DomainEvent(
        event_type="achat.created",
        aggregate_id="ACH-2026-001",
        data={
            "date": "2026-01-31",
            "montant": 1500.00,
            "libelle": "Achat ciment et béton - Chantier Dupont",
            "numero_facture": "F-2026-001",
            "category_id": "MATERIEL"
        },
        metadata={
            "user_id": 1,
            "user_email": "admin@greg.fr"
        },
        occurred_at=datetime(2026, 1, 31, 10, 30, 0)
    )

    # 2. Récupérer le connecteur
    connector = get_connector("pennylane")

    # 3. Transformer l'événement
    payload = connector.transform_event(event)

    # 4. Afficher le résultat
    print(f"Endpoint API: {payload['endpoint']}")
    print(f"Données: {payload['data']}")
    print(f"Métadonnées: {payload['metadata']}")


def example_pennylane_situation():
    """Exemple: Transformer une situation de travaux en facture client Pennylane."""
    print("\n=== Exemple Pennylane - Situation de Travaux (Facture Client) ===")

    event = DomainEvent(
        event_type="situation_travaux.created",
        aggregate_id="SIT-2026-003",
        data={
            "date": "2026-01-31",
            "montant": 35000.00,
            "libelle": "Situation mensuelle janvier 2026",
            "numero": 1,
            "chantier_nom": "Immeuble Résidence Soleil"
        }
    )

    connector = get_connector("pennylane")
    payload = connector.transform_event(event)

    print(f"Endpoint API: {payload['endpoint']}")
    print(f"Montant: {payload['data']['amount']} EUR")
    print(f"Libellé: {payload['data']['label']}")
    print(f"Numéro facture: {payload['data']['invoice_number']}")


def example_silae_feuille_heures():
    """Exemple: Transformer une feuille d'heures en export Silae."""
    print("\n=== Exemple Silae - Feuille d'Heures ===")

    event = DomainEvent(
        event_type="feuille_heures.validated",
        aggregate_id="FH-2026-042",
        data={
            "employe_code": "EMP001",
            "periode": "2026-01",
            "heures": [
                {
                    "date": "2026-01-15",
                    "type": "normal",
                    "quantite": 8.0,
                    "chantier_code": "CHT-DUPONT"
                },
                {
                    "date": "2026-01-16",
                    "type": "normal",
                    "quantite": 7.5,
                    "chantier_code": "CHT-DUPONT"
                },
                {
                    "date": "2026-01-17",
                    "type": "supplementaire",
                    "quantite": 2.0,
                    "chantier_code": "CHT-MARTIN"
                }
            ]
        }
    )

    connector = get_connector("silae")
    payload = connector.transform_event(event)

    print(f"Endpoint API: {payload['endpoint']}")
    print(f"Employé: {payload['data']['employee_code']}")
    print(f"Période: {payload['data']['period']}")
    print(f"Nombre de lignes: {len(payload['data']['hours'])}")
    for idx, heure in enumerate(payload['data']['hours'], 1):
        print(f"  Ligne {idx}: {heure['date']} - {heure['type']} - {heure['quantity']}h - {heure.get('cost_center', 'N/A')}")


def example_list_connectors():
    """Exemple: Lister tous les connecteurs disponibles."""
    print("\n=== Liste des Connecteurs Disponibles ===")

    connectors = list_connectors()

    for name, events in connectors.items():
        print(f"\n{name.upper()}:")
        for event_type in events:
            print(f"  - {event_type}")


def example_find_connector():
    """Exemple: Trouver quel connecteur supporte un événement."""
    print("\n=== Recherche de Connecteur par Événement ===")

    events_to_test = [
        "achat.created",
        "feuille_heures.validated",
        "user.created",  # Non supporté
        "paiement.created",
    ]

    for event_type in events_to_test:
        connector_name = find_connector_for_event(event_type)
        if connector_name:
            print(f"✓ {event_type} → {connector_name}")
        else:
            print(f"✗ {event_type} → Aucun connecteur")


def example_error_handling():
    """Exemple: Gestion d'erreurs."""
    print("\n=== Gestion d'Erreurs ===")

    from shared.infrastructure.connectors.base_connector import ConnectorError

    # Cas 1: Événement non supporté
    try:
        connector = get_connector("pennylane")
        event = DomainEvent(
            event_type="user.created",  # Non supporté par Pennylane
            data={"email": "test@test.fr"}
        )
        connector.transform_event(event)
    except ConnectorError as e:
        print(f"✗ Erreur attendue: {e}")

    # Cas 2: Champs manquants
    try:
        connector = get_connector("pennylane")
        event = DomainEvent(
            event_type="achat.created",
            data={
                "date": "2026-01-31",
                # montant et libelle manquants
            }
        )
        connector.transform_event(event)
    except ConnectorError as e:
        print(f"✗ Erreur attendue: {e}")


def main():
    """Exécuter tous les exemples."""
    print("=" * 70)
    print("EXEMPLES D'UTILISATION DES CONNECTEURS WEBHOOKS")
    print("=" * 70)

    example_list_connectors()
    example_find_connector()
    example_pennylane_achat()
    example_pennylane_situation()
    example_silae_feuille_heures()
    example_error_handling()

    print("\n" + "=" * 70)
    print("Tous les exemples ont été exécutés avec succès !")
    print("=" * 70)


if __name__ == "__main__":
    main()
