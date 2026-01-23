"""Interface FormulaireRempliRepository - Abstraction pour la persistence des formulaires remplis."""

from abc import ABC, abstractmethod
from datetime import date
from typing import Optional, List

from ..entities import FormulaireRempli
from ..value_objects import StatutFormulaire


class FormulaireRempliRepository(ABC):
    """
    Interface abstraite pour la persistence des formulaires remplis.

    Cette interface definit le contrat pour l'acces aux donnees.
    L'implementation concrete se trouve dans la couche Infrastructure.
    """

    @abstractmethod
    def find_by_id(self, formulaire_id: int) -> Optional[FormulaireRempli]:
        """
        Trouve un formulaire par son ID.

        Args:
            formulaire_id: L'identifiant unique du formulaire.

        Returns:
            Le formulaire trouve ou None.
        """
        pass

    @abstractmethod
    def save(self, formulaire: FormulaireRempli) -> FormulaireRempli:
        """
        Persiste un formulaire (creation ou mise a jour).

        Args:
            formulaire: Le formulaire a sauvegarder.

        Returns:
            Le formulaire sauvegarde (avec ID si creation).
        """
        pass

    @abstractmethod
    def delete(self, formulaire_id: int) -> bool:
        """
        Supprime un formulaire.

        Args:
            formulaire_id: L'identifiant du formulaire a supprimer.

        Returns:
            True si supprime, False si non trouve.
        """
        pass

    @abstractmethod
    def find_by_chantier(
        self,
        chantier_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[FormulaireRempli]:
        """
        Trouve les formulaires d'un chantier (FOR-10).

        Args:
            chantier_id: ID du chantier.
            skip: Nombre d'elements a sauter.
            limit: Nombre maximum a retourner.

        Returns:
            Liste des formulaires du chantier.
        """
        pass

    @abstractmethod
    def find_by_template(
        self,
        template_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[FormulaireRempli]:
        """
        Trouve les formulaires bases sur un template.

        Args:
            template_id: ID du template.
            skip: Nombre d'elements a sauter.
            limit: Nombre maximum a retourner.

        Returns:
            Liste des formulaires.
        """
        pass

    @abstractmethod
    def find_by_user(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[FormulaireRempli]:
        """
        Trouve les formulaires remplis par un utilisateur.

        Args:
            user_id: ID de l'utilisateur.
            skip: Nombre d'elements a sauter.
            limit: Nombre maximum a retourner.

        Returns:
            Liste des formulaires.
        """
        pass

    @abstractmethod
    def find_by_statut(
        self,
        statut: StatutFormulaire,
        skip: int = 0,
        limit: int = 100
    ) -> List[FormulaireRempli]:
        """
        Trouve les formulaires par statut.

        Args:
            statut: Le statut a filtrer.
            skip: Nombre d'elements a sauter.
            limit: Nombre maximum a retourner.

        Returns:
            Liste des formulaires.
        """
        pass

    @abstractmethod
    def count_by_chantier(self, chantier_id: int) -> int:
        """
        Compte les formulaires d'un chantier.

        Args:
            chantier_id: ID du chantier.

        Returns:
            Nombre de formulaires.
        """
        pass

    @abstractmethod
    def find_history(self, formulaire_id: int) -> List[FormulaireRempli]:
        """
        Trouve l'historique d'un formulaire (FOR-08).

        Args:
            formulaire_id: ID du formulaire.

        Returns:
            Liste des versions (incluant parent_id chain).
        """
        pass

    @abstractmethod
    def search(
        self,
        chantier_id: Optional[int] = None,
        template_id: Optional[int] = None,
        user_id: Optional[int] = None,
        statut: Optional[StatutFormulaire] = None,
        date_debut: Optional[date] = None,
        date_fin: Optional[date] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[FormulaireRempli], int]:
        """
        Recherche des formulaires avec filtres multiples.

        Args:
            chantier_id: Filtrer par chantier (optionnel).
            template_id: Filtrer par template (optionnel).
            user_id: Filtrer par utilisateur (optionnel).
            statut: Filtrer par statut (optionnel).
            date_debut: Date de debut (optionnel).
            date_fin: Date de fin (optionnel).
            skip: Nombre d'elements a sauter.
            limit: Nombre maximum a retourner.

        Returns:
            Tuple (liste des formulaires, total count).
        """
        pass
