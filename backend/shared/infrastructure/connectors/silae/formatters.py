"""Formatters pour l'API Silae (paie)."""

from datetime import datetime
from typing import Dict, Any, List
import logging

from shared.infrastructure.event_bus.domain_event import DomainEvent
from ..base_connector import ConnectorError
from ..security import (
    validate_code,
    validate_amount,
    mask_employee_code,
    audit_log_employee_data,
    SecurityError
)

logger = logging.getLogger(__name__)


def format_employee_hours(event: DomainEvent) -> Dict[str, Any]:
    """
    Formate des heures en payload Silae.

    Events attendus:
        - feuille_heures.validated
        - pointage.validated

    Données requises:
        - employe_code: Code employé dans Silae
        - periode: Période au format YYYY-MM
        - heures: Liste des lignes d'heures [
            {
                "date": "2026-01-15",
                "type": "normal" | "supplementaire" | "nuit" | "dimanche",
                "quantite": 8.0,
                "chantier_code": "CHT001" (optionnel)
            }
        ]

    Args:
        event: Événement feuille_heures.validated ou pointage.validated.

    Returns:
        Payload formaté pour POST /employees/hours.

    Raises:
        ConnectorError: Si des données requises sont manquantes.

    Example:
        >>> event = DomainEvent(
        ...     event_type="feuille_heures.validated",
        ...     data={
        ...         "employe_code": "EMP001",
        ...         "periode": "2026-01",
        ...         "heures": [
        ...             {
        ...                 "date": "2026-01-15",
        ...                 "type": "normal",
        ...                 "quantite": 8.0,
        ...                 "chantier_code": "CHT001"
        ...             }
        ...         ]
        ...     }
        ... )
        >>> format_employee_hours(event)
        {
            "employee_code": "EMP001",
            "period": "2026-01",
            "hours": [...],
        }
    """
    data = event.data

    # Validation des champs requis
    required_fields = ["employe_code", "periode", "heures"]
    missing = [f for f in required_fields if f not in data or not data[f]]
    if missing:
        raise ConnectorError(
            f"Champs requis manquants: {', '.join(missing)}",
            connector_name="silae",
            event_type=event.event_type
        )

    # Validation sécurité: code employé
    try:
        employe_code_valide = validate_code(
            data["employe_code"],
            pattern=r'^[A-Z0-9_-]{1,50}$',
            field_name="employe_code"
        )
    except SecurityError as e:
        raise ConnectorError(
            f"Code employé invalide: {e.message}",
            connector_name="silae",
            event_type=event.event_type
        )

    # Validation du format période
    periode = data["periode"]
    try:
        datetime.strptime(periode, "%Y-%m")
    except ValueError:
        raise ConnectorError(
            f"Format de période invalide: {periode}. Attendu: YYYY-MM",
            connector_name="silae",
            event_type=event.event_type
        )

    # Validation des heures
    heures_list = data["heures"]
    if not isinstance(heures_list, list) or len(heures_list) == 0:
        raise ConnectorError(
            "Le champ 'heures' doit être une liste non vide",
            connector_name="silae",
            event_type=event.event_type
        )

    # Formater chaque ligne d'heures
    formatted_hours = []
    for idx, heure in enumerate(heures_list):
        # Validation des champs requis de la ligne
        required_hour_fields = ["date", "type", "quantite"]
        missing_hour = [f for f in required_hour_fields if f not in heure or heure[f] is None]
        if missing_hour:
            raise ConnectorError(
                f"Ligne {idx}: champs requis manquants: {', '.join(missing_hour)}",
                connector_name="silae",
                event_type=event.event_type
            )

        # Mapping Hub Chantier → Silae pour les types d'heures
        type_mapping = {
            "normal": "normal",
            "supplementaire": "overtime",
            "nuit": "night",
            "dimanche": "sunday",
            "ferie": "holiday",
        }
        silae_type = type_mapping.get(heure["type"].lower(), "normal")

        formatted_hour = {
            "date": heure["date"],
            "type": silae_type,
            "quantity": float(heure["quantite"]),
        }

        # Validation et ajout champs optionnels
        if "chantier_code" in heure and heure["chantier_code"]:
            try:
                chantier_code_valide = validate_code(
                    heure["chantier_code"],
                    pattern=r'^[A-Z0-9_-]{1,50}$',
                    field_name="chantier_code"
                )
                formatted_hour["cost_center"] = chantier_code_valide
            except SecurityError as e:
                raise ConnectorError(
                    f"Ligne {idx}: code chantier invalide: {e.message}",
                    connector_name="silae",
                    event_type=event.event_type
                )

        formatted_hours.append(formatted_hour)

    # Construction du payload Silae
    payload = {
        "employee_code": employe_code_valide,
        "period": periode,
        "hours": formatted_hours,
    }

    # Métadonnées Hub Chantier (pour traçabilité)
    if event.aggregate_id:
        payload["external_id"] = str(event.aggregate_id)

    # Log sécurisé (RGPD: masquage du code employé)
    employe_masked = mask_employee_code(employe_code_valide)
    logger.debug(
        f"Heures formatées pour employé {employe_masked}, "
        f"période {periode}, {len(formatted_hours)} lignes"
    )

    # Audit trail RGPD (hash du code employé)
    audit_log_employee_data(
        action="format_employee_hours",
        employee_code=employe_code_valide,
        period=periode,
        hours_count=len(formatted_hours),
        connector_name="silae"
    )

    return payload


def aggregate_pointages_to_hours(pointages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Agrège plusieurs pointages en lignes d'heures pour Silae.

    Utile quand un événement pointage.validated contient plusieurs pointages
    à agréger par date/type avant envoi à Silae.

    Args:
        pointages: Liste de pointages [
            {
                "date": "2026-01-15",
                "heure_debut": "08:00",
                "heure_fin": "17:00",
                "type": "normal",
                "chantier_code": "CHT001"
            },
            ...
        ]

    Returns:
        Liste d'heures agrégées par date/type.

    Example:
        >>> pointages = [
        ...     {"date": "2026-01-15", "heure_debut": "08:00", "heure_fin": "12:00", "type": "normal"},
        ...     {"date": "2026-01-15", "heure_debut": "13:00", "heure_fin": "17:00", "type": "normal"},
        ... ]
        >>> aggregate_pointages_to_hours(pointages)
        [
            {
                "date": "2026-01-15",
                "type": "normal",
                "quantite": 8.0
            }
        ]
    """
    from collections import defaultdict

    # Agréger par (date, type, chantier)
    aggregated = defaultdict(float)
    metadata = {}  # Pour garder les métadonnées (chantier_code)

    for pointage in pointages:
        date = pointage["date"]
        type_heure = pointage.get("type", "normal")
        chantier = pointage.get("chantier_code", "")

        # Calculer la durée en heures
        try:
            heure_debut = datetime.strptime(pointage["heure_debut"], "%H:%M")
            heure_fin = datetime.strptime(pointage["heure_fin"], "%H:%M")
            duree_hours = (heure_fin - heure_debut).total_seconds() / 3600
        except (ValueError, KeyError) as e:
            logger.warning(f"Pointage invalide ignoré: {pointage}. Erreur: {e}")
            continue

        # Clé d'agrégation
        key = (date, type_heure, chantier)
        aggregated[key] += duree_hours
        metadata[key] = {"chantier_code": chantier}

    # Convertir en liste d'heures
    heures = []
    for (date, type_heure, chantier), quantite in aggregated.items():
        heure = {
            "date": date,
            "type": type_heure,
            "quantite": round(quantite, 2),
        }
        if chantier:
            heure["chantier_code"] = chantier

        heures.append(heure)

    logger.debug(f"Agrégation: {len(pointages)} pointages → {len(heures)} lignes d'heures")

    return heures
