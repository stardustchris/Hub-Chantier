"""Formatters pour l'API Pennylane v1."""

from datetime import datetime
from typing import Dict, Any, Optional
import logging

from shared.infrastructure.event_bus.domain_event import DomainEvent
from ..base_connector import ConnectorError
from ..security import sanitize_text, validate_code, validate_amount, SecurityError

logger = logging.getLogger(__name__)


def format_supplier_invoice(event: DomainEvent) -> Dict[str, Any]:
    """
    Formate un achat en facture fournisseur Pennylane.

    Event attendu: achat.created
    Données requises:
        - date: Date de l'achat
        - montant: Montant TTC
        - libelle: Description
        - numero_facture: Numéro de facture (optionnel)
        - category_id: ID catégorie Pennylane (optionnel)

    Args:
        event: Événement achat.created.

    Returns:
        Payload formaté pour POST /invoices/supplier.

    Raises:
        ConnectorError: Si des données requises sont manquantes.

    Example:
        >>> event = DomainEvent(
        ...     event_type="achat.created",
        ...     data={
        ...         "date": "2026-01-31",
        ...         "montant": 1500.00,
        ...         "libelle": "Achat matériaux chantier X"
        ...     }
        ... )
        >>> format_supplier_invoice(event)
        {
            "date": "2026-01-31",
            "amount": 1500.00,
            "label": "Achat matériaux chantier X",
            ...
        }
    """
    data = event.data

    # Validation des champs requis
    required_fields = ["date", "montant", "libelle"]
    missing = [f for f in required_fields if f not in data or not data[f]]
    if missing:
        raise ConnectorError(
            f"Champs requis manquants: {', '.join(missing)}",
            connector_name="pennylane",
            event_type=event.event_type
        )

    # Validation sécurité
    try:
        montant_valide = validate_amount(data["montant"], field_name="montant")
        libelle_safe = sanitize_text(data["libelle"], max_length=500)
    except SecurityError as e:
        raise ConnectorError(
            f"Erreur de validation: {e.message}",
            connector_name="pennylane",
            event_type=event.event_type
        )

    # Construction du payload Pennylane
    payload = {
        "date": data["date"],
        "amount": montant_valide,
        "label": libelle_safe,
    }

    # Champs optionnels
    if "numero_facture" in data and data["numero_facture"]:
        try:
            numero_safe = validate_code(
                data["numero_facture"],
                pattern=r'^[A-Z0-9_-]{1,50}$',
                field_name="numero_facture"
            )
            payload["invoice_number"] = numero_safe
        except SecurityError as e:
            raise ConnectorError(
                f"Numéro de facture invalide: {e.message}",
                connector_name="pennylane",
                event_type=event.event_type
            )

    if "category_id" in data and data["category_id"]:
        payload["category_id"] = str(data["category_id"])

    # Métadonnées Hub Chantier (pour traçabilité)
    if event.aggregate_id:
        payload["external_id"] = str(event.aggregate_id)

    logger.debug(f"Facture fournisseur formatée: {payload.get('invoice_number', 'N/A')}")

    return payload


def format_customer_invoice(event: DomainEvent) -> Dict[str, Any]:
    """
    Formate une situation de travaux en facture client Pennylane.

    Event attendu: situation_travaux.created
    Données requises:
        - date: Date de la situation
        - montant: Montant HT
        - libelle: Description
        - numero: Numéro de situation (optionnel)
        - chantier_nom: Nom du chantier (optionnel)

    Args:
        event: Événement situation_travaux.created.

    Returns:
        Payload formaté pour POST /invoices/customer.

    Raises:
        ConnectorError: Si des données requises sont manquantes.

    Example:
        >>> event = DomainEvent(
        ...     event_type="situation_travaux.created",
        ...     data={
        ...         "date": "2026-01-31",
        ...         "montant": 25000.00,
        ...         "libelle": "Situation #1 - Chantier ABC",
        ...         "numero": 1
        ...     }
        ... )
        >>> format_customer_invoice(event)
        {
            "date": "2026-01-31",
            "amount": 25000.00,
            "label": "Situation #1 - Chantier ABC",
            ...
        }
    """
    data = event.data

    # Validation des champs requis
    required_fields = ["date", "montant", "libelle"]
    missing = [f for f in required_fields if f not in data or not data[f]]
    if missing:
        raise ConnectorError(
            f"Champs requis manquants: {', '.join(missing)}",
            connector_name="pennylane",
            event_type=event.event_type
        )

    # Validation sécurité
    try:
        montant_valide = validate_amount(data["montant"], field_name="montant")
        libelle_safe = sanitize_text(data["libelle"], max_length=500)
    except SecurityError as e:
        raise ConnectorError(
            f"Erreur de validation: {e.message}",
            connector_name="pennylane",
            event_type=event.event_type
        )

    # Construction du payload Pennylane
    payload = {
        "date": data["date"],
        "amount": montant_valide,
        "label": libelle_safe,
    }

    # Champs optionnels
    if "numero" in data and data["numero"]:
        payload["invoice_number"] = f"SIT-{data['numero']:04d}"

    if "chantier_nom" in data and data["chantier_nom"]:
        try:
            chantier_nom_safe = sanitize_text(data["chantier_nom"], max_length=200)
            payload["label"] = f"{payload['label']} - {chantier_nom_safe}"
        except SecurityError as e:
            raise ConnectorError(
                f"Nom de chantier invalide: {e.message}",
                connector_name="pennylane",
                event_type=event.event_type
            )

    if "category_id" in data and data["category_id"]:
        payload["category_id"] = str(data["category_id"])

    # Métadonnées Hub Chantier
    if event.aggregate_id:
        payload["external_id"] = str(event.aggregate_id)

    logger.debug(f"Facture client formatée: {payload.get('invoice_number', 'N/A')}")

    return payload


def format_transaction(event: DomainEvent) -> Dict[str, Any]:
    """
    Formate un paiement en transaction Pennylane.

    Event attendu: paiement.created
    Données requises:
        - date: Date du paiement
        - montant: Montant
        - libelle: Description
        - type: Type de paiement (optionnel: virement, cheque, especes)

    Args:
        event: Événement paiement.created.

    Returns:
        Payload formaté pour POST /transactions.

    Raises:
        ConnectorError: Si des données requises sont manquantes.

    Example:
        >>> event = DomainEvent(
        ...     event_type="paiement.created",
        ...     data={
        ...         "date": "2026-01-31",
        ...         "montant": 5000.00,
        ...         "libelle": "Paiement facture #123",
        ...         "type": "virement"
        ...     }
        ... )
        >>> format_transaction(event)
        {
            "date": "2026-01-31",
            "amount": 5000.00,
            "label": "Paiement facture #123",
            ...
        }
    """
    data = event.data

    # Validation des champs requis
    required_fields = ["date", "montant", "libelle"]
    missing = [f for f in required_fields if f not in data or not data[f]]
    if missing:
        raise ConnectorError(
            f"Champs requis manquants: {', '.join(missing)}",
            connector_name="pennylane",
            event_type=event.event_type
        )

    # Validation sécurité
    try:
        montant_valide = validate_amount(data["montant"], field_name="montant")
        libelle_safe = sanitize_text(data["libelle"], max_length=500)
    except SecurityError as e:
        raise ConnectorError(
            f"Erreur de validation: {e.message}",
            connector_name="pennylane",
            event_type=event.event_type
        )

    # Construction du payload Pennylane
    payload = {
        "date": data["date"],
        "amount": montant_valide,
        "label": libelle_safe,
    }

    # Champs optionnels
    if "type" in data and data["type"]:
        # Mapping Hub Chantier → Pennylane
        payment_type_mapping = {
            "virement": "bank_transfer",
            "cheque": "check",
            "especes": "cash",
            "cb": "card",
        }
        pennylane_type = payment_type_mapping.get(data["type"].lower(), "other")
        payload["payment_method"] = pennylane_type

    if "category_id" in data and data["category_id"]:
        payload["category_id"] = str(data["category_id"])

    # Métadonnées Hub Chantier
    if event.aggregate_id:
        payload["external_id"] = str(event.aggregate_id)

    logger.debug(f"Transaction formatée: {payload.get('payment_method', 'N/A')}")

    return payload
