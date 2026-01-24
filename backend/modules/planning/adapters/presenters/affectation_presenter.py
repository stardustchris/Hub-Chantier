"""Presenter pour enrichir les affectations avec les infos utilisateur/chantier.

Ce presenter respecte Clean Architecture en:
- Recevant des DTOs de la couche Application
- Enrichissant les donnees pour la presentation
- Utilisant le service shared EntityInfoService (pas d'import direct)

L'enrichissement (nom utilisateur, couleur chantier) est une preoccupation
de PRESENTATION, pas de logique metier. Il doit donc etre dans Adapters.
"""

from typing import List, Optional, Dict, Any

from shared.application.ports import EntityInfoService
from ...application.dtos import AffectationDTO


class AffectationPresenter:
    """Presenter pour enrichir les affectations.

    Enrichit les DTOs d'affectation avec les informations d'affichage
    (nom utilisateur, couleur chantier, etc.) en utilisant le service
    shared EntityInfoService.

    Args:
        entity_info: Service pour recuperer les infos utilisateur/chantier.

    Example:
        ```python
        presenter = AffectationPresenter(entity_info_service)
        enriched = presenter.present_many(affectations)
        ```
    """

    def __init__(self, entity_info: EntityInfoService):
        """Initialise le presenter.

        Args:
            entity_info: Service d'information des entites.
        """
        self._entity_info = entity_info
        self._user_cache: Dict[int, Dict[str, Any]] = {}
        self._chantier_cache: Dict[int, Dict[str, Any]] = {}

    def present(self, affectation: AffectationDTO) -> Dict[str, Any]:
        """Enrichit une affectation avec les infos d'affichage.

        Args:
            affectation: DTO d'affectation a enrichir.

        Returns:
            Dictionnaire avec toutes les donnees pour l'API.
        """
        # Recuperer infos utilisateur (avec cache)
        user_info = self._get_cached_user_info(affectation.utilisateur_id)

        # Recuperer infos chantier (avec cache)
        chantier_info = self._get_cached_chantier_info(affectation.chantier_id)

        return {
            "id": affectation.id,
            "utilisateur_id": affectation.utilisateur_id,
            "utilisateur_nom": user_info.get("nom"),
            "utilisateur_couleur": user_info.get("couleur"),
            "utilisateur_metier": user_info.get("metier"),
            "chantier_id": affectation.chantier_id,
            "chantier_nom": chantier_info.get("nom"),
            "chantier_couleur": chantier_info.get("couleur"),
            "date": affectation.date,
            "heure_debut": affectation.heure_debut,
            "heure_fin": affectation.heure_fin,
            "type_affectation": affectation.type_affectation,
            "note": affectation.note,
            "created_at": affectation.created_at,
            "updated_at": affectation.updated_at,
        }

    def present_many(self, affectations: List[AffectationDTO]) -> List[Dict[str, Any]]:
        """Enrichit plusieurs affectations.

        Utilise un cache pour eviter les requetes repetees.

        Args:
            affectations: Liste de DTOs a enrichir.

        Returns:
            Liste de dictionnaires enrichis.
        """
        # Pre-charger le cache pour les IDs uniques
        user_ids = {a.utilisateur_id for a in affectations}
        chantier_ids = {a.chantier_id for a in affectations}

        for user_id in user_ids:
            if user_id not in self._user_cache:
                self._get_cached_user_info(user_id)

        for chantier_id in chantier_ids:
            if chantier_id not in self._chantier_cache:
                self._get_cached_chantier_info(chantier_id)

        return [self.present(a) for a in affectations]

    def _get_cached_user_info(self, user_id: int) -> Dict[str, Any]:
        """Recupere les infos utilisateur avec cache.

        Args:
            user_id: ID de l'utilisateur.

        Returns:
            Dictionnaire avec nom, couleur, metier.
        """
        if user_id not in self._user_cache:
            info = self._entity_info.get_user_info(user_id)
            if info:
                self._user_cache[user_id] = {
                    "nom": info.nom,
                    "couleur": info.couleur,
                    "metier": info.metier,
                }
            else:
                self._user_cache[user_id] = {}

        return self._user_cache[user_id]

    def _get_cached_chantier_info(self, chantier_id: int) -> Dict[str, Any]:
        """Recupere les infos chantier avec cache.

        Args:
            chantier_id: ID du chantier.

        Returns:
            Dictionnaire avec nom, couleur.
        """
        if chantier_id not in self._chantier_cache:
            info = self._entity_info.get_chantier_info(chantier_id)
            if info:
                self._chantier_cache[chantier_id] = {
                    "nom": info.nom,
                    "couleur": info.couleur,
                }
            else:
                self._chantier_cache[chantier_id] = {}

        return self._chantier_cache[chantier_id]

    def clear_cache(self) -> None:
        """Vide le cache (utile pour les tests)."""
        self._user_cache.clear()
        self._chantier_cache.clear()
