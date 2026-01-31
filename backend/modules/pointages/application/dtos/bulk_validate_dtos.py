"""DTOs pour la validation par lot de pointages (GAP-FDH-004)."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class BulkValidatePointagesDTO:
    """
    DTO pour la validation par lot de pointages.

    Attributes:
        pointage_ids: Liste des IDs de pointages à valider.
        validateur_id: ID du validateur (chef/conducteur/admin).
    """

    pointage_ids: List[int]
    validateur_id: int


@dataclass
class PointageValidationResult:
    """
    Résultat de validation d'un pointage individuel.

    Attributes:
        pointage_id: ID du pointage.
        success: True si validé avec succès, False en cas d'erreur.
        error: Message d'erreur si success=False.
    """

    pointage_id: int
    success: bool
    error: Optional[str] = None


@dataclass
class BulkValidatePointagesResultDTO:
    """
    Résultat de la validation par lot.

    Attributes:
        validated: Liste des IDs de pointages validés avec succès.
        failed: Liste des résultats d'échec avec raison.
        total_count: Nombre total de pointages traités.
        success_count: Nombre de pointages validés.
        failure_count: Nombre de pointages en échec.
    """

    validated: List[int]
    failed: List[PointageValidationResult]
    total_count: int
    success_count: int
    failure_count: int
