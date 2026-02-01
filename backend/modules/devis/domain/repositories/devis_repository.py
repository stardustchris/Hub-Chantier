"""Interface du repository pour les devis.

DEV-03: Creation devis structure - CRUD des devis.
DEV-15: Suivi statut devis - Filtrage par statut.
DEV-17: Dashboard devis - Agregations pour KPI.
DEV-19: Recherche et filtres - Filtres avances.
"""

from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal
from typing import Dict, List, Optional

from ..entities import Devis
from ..value_objects import StatutDevis


class DevisRepository(ABC):
    """Interface abstraite pour la persistence des devis."""

    @abstractmethod
    def save(self, devis: Devis) -> Devis:
        """Persiste un devis (creation ou mise a jour).

        Args:
            devis: Le devis a persister.

        Returns:
            Le devis avec son ID attribue.
        """
        pass

    @abstractmethod
    def find_by_id(self, devis_id: int) -> Optional[Devis]:
        """Recherche un devis par son ID.

        Args:
            devis_id: L'ID du devis.

        Returns:
            Le devis ou None si non trouve.
        """
        pass

    @abstractmethod
    def find_by_numero(self, numero: str) -> Optional[Devis]:
        """Recherche un devis par son numero.

        Args:
            numero: Le numero du devis.

        Returns:
            Le devis ou None si non trouve.
        """
        pass

    @abstractmethod
    def find_all(
        self,
        statut: Optional[StatutDevis] = None,
        statuts: Optional[List[StatutDevis]] = None,
        commercial_id: Optional[int] = None,
        conducteur_id: Optional[int] = None,
        client_nom: Optional[str] = None,
        date_creation_min: Optional[date] = None,
        date_creation_max: Optional[date] = None,
        montant_min: Optional[Decimal] = None,
        montant_max: Optional[Decimal] = None,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Devis]:
        """Liste les devis avec filtres avances (DEV-19).

        Args:
            statut: Filtrer par statut unique (optionnel).
            statuts: Filtrer par liste de statuts (optionnel).
            commercial_id: Filtrer par commercial assigne (optionnel).
            conducteur_id: Filtrer par conducteur assigne (optionnel).
            client_nom: Filtrer par nom client (recherche partielle).
            date_creation_min: Date de creation minimale.
            date_creation_max: Date de creation maximale.
            montant_min: Montant HT minimum.
            montant_max: Montant HT maximum.
            search: Recherche textuelle sur numero/client/objet.
            limit: Nombre maximum de resultats.
            offset: Decalage pour pagination.

        Returns:
            Liste des devis.
        """
        pass

    @abstractmethod
    def count(
        self,
        statut: Optional[StatutDevis] = None,
        statuts: Optional[List[StatutDevis]] = None,
        commercial_id: Optional[int] = None,
    ) -> int:
        """Compte le nombre de devis avec filtres.

        Args:
            statut: Filtrer par statut unique (optionnel).
            statuts: Filtrer par liste de statuts (optionnel).
            commercial_id: Filtrer par commercial assigne (optionnel).

        Returns:
            Le nombre de devis.
        """
        pass

    @abstractmethod
    def count_by_statut(self) -> Dict[str, int]:
        """Compte les devis par statut (DEV-17: KPI pipeline).

        Returns:
            Dictionnaire {statut: count}.
        """
        pass

    @abstractmethod
    def somme_montant_by_statut(self) -> Dict[str, Decimal]:
        """Somme des montants HT par statut (DEV-17: KPI pipeline).

        Returns:
            Dictionnaire {statut: somme_montant_ht}.
        """
        pass

    @abstractmethod
    def find_expires(self) -> List[Devis]:
        """Trouve les devis dont la date de validite est depassee
        et qui sont dans un statut pouvant expirer.

        Returns:
            Liste des devis a marquer comme expires.
        """
        pass

    @abstractmethod
    def delete(self, devis_id: int, deleted_by: Optional[int] = None) -> bool:
        """Supprime un devis (soft delete - H10).

        Args:
            devis_id: L'ID du devis a supprimer.
            deleted_by: L'ID de l'utilisateur qui supprime.

        Returns:
            True si supprime, False si non trouve.
        """
        pass
