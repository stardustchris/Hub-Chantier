"""Interface du repository pour les achats.

FIN-05: Saisie achat - CRUD et requêtes sur les achats.
FIN-06: Suivi achat - Filtrage par statut et agrégation.
"""

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import List, Optional

from ..entities import Achat
from ..value_objects import StatutAchat


class AchatRepository(ABC):
    """Interface abstraite pour la persistence des achats."""

    @abstractmethod
    def save(self, achat: Achat) -> Achat:
        """Persiste un achat (création ou mise à jour).

        Args:
            achat: L'achat à persister.

        Returns:
            L'achat avec son ID attribué.
        """
        pass

    @abstractmethod
    def find_by_id(self, achat_id: int) -> Optional[Achat]:
        """Recherche un achat par son ID.

        Args:
            achat_id: L'ID de l'achat.

        Returns:
            L'achat ou None si non trouvé.
        """
        pass

    @abstractmethod
    def find_by_chantier(
        self,
        chantier_id: int,
        statut: Optional[StatutAchat] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Achat]:
        """Liste les achats d'un chantier.

        Args:
            chantier_id: L'ID du chantier.
            statut: Filtrer par statut (optionnel).
            limit: Nombre maximum de résultats.
            offset: Décalage pour pagination.

        Returns:
            Liste des achats.
        """
        pass

    @abstractmethod
    def find_by_fournisseur(
        self,
        fournisseur_id: int,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Achat]:
        """Liste les achats d'un fournisseur.

        Args:
            fournisseur_id: L'ID du fournisseur.
            limit: Nombre maximum de résultats.
            offset: Décalage pour pagination.

        Returns:
            Liste des achats.
        """
        pass

    @abstractmethod
    def find_by_lot(
        self,
        lot_budgetaire_id: int,
        statuts: Optional[List[StatutAchat]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Achat]:
        """Liste les achats d'un lot budgétaire.

        Args:
            lot_budgetaire_id: L'ID du lot budgétaire.
            statuts: Filtrer par statuts (optionnel).
            limit: Nombre maximum de résultats.
            offset: Décalage pour pagination.

        Returns:
            Liste des achats.
        """
        pass

    @abstractmethod
    def find_en_attente_validation(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Achat]:
        """Liste les achats en attente de validation (statut = demande).

        Args:
            limit: Nombre maximum de résultats.
            offset: Décalage pour pagination.

        Returns:
            Liste des achats en attente.
        """
        pass

    @abstractmethod
    def count_by_chantier(
        self,
        chantier_id: int,
        statuts: Optional[List[StatutAchat]] = None,
    ) -> int:
        """Compte les achats d'un chantier.

        Args:
            chantier_id: L'ID du chantier.
            statuts: Filtrer par statuts (optionnel).

        Returns:
            Le nombre d'achats.
        """
        pass

    @abstractmethod
    def somme_by_lot(
        self,
        lot_budgetaire_id: int,
        statuts: Optional[List[StatutAchat]] = None,
    ) -> Decimal:
        """Calcule la somme HT des achats d'un lot budgétaire.

        Args:
            lot_budgetaire_id: L'ID du lot budgétaire.
            statuts: Filtrer par statuts (optionnel).

        Returns:
            La somme HT des achats.
        """
        pass

    @abstractmethod
    def somme_by_chantier(
        self,
        chantier_id: int,
        statuts: Optional[List[StatutAchat]] = None,
    ) -> Decimal:
        """Calcule la somme HT des achats d'un chantier.

        Args:
            chantier_id: L'ID du chantier.
            statuts: Filtrer par statuts (optionnel).

        Returns:
            La somme HT des achats.
        """
        pass

    @abstractmethod
    def delete(self, achat_id: int, deleted_by: Optional[int] = None) -> bool:
        """Supprime un achat (soft delete - H10).

        Args:
            achat_id: L'ID de l'achat à supprimer.
            deleted_by: L'ID de l'utilisateur qui supprime.

        Returns:
            True si supprimé, False si non trouvé.
        """
        pass

    @abstractmethod
    def search_suggestions(
        self,
        search: str,
        limit: int = 10,
    ) -> List[dict]:
        """Recherche les libellés d'achats passés pour autocomplete.

        Retourne des suggestions uniques (libelle + dernier prix + fournisseur).

        Args:
            search: Terme de recherche (ILIKE).
            limit: Nombre max de suggestions.

        Returns:
            Liste de dicts avec libelle, prix_unitaire_ht, unite, type_achat, fournisseur_id.
        """
        pass
