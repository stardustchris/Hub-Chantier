"""Interface BesoinChargeRepository - Abstraction pour la persistence des besoins."""

from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities import BesoinCharge
from ..value_objects import Semaine, TypeMetier


class BesoinChargeRepository(ABC):
    """
    Interface abstraite pour la persistence des besoins de charge.

    Cette interface definit le contrat pour l'acces aux donnees de besoins.
    L'implementation concrete se trouve dans la couche Infrastructure.

    Selon CDC Section 6 - Planning de Charge (PDC-01 a PDC-17).
    """

    @abstractmethod
    def save(self, besoin: BesoinCharge) -> BesoinCharge:
        """
        Persiste un besoin de charge (creation ou mise a jour).

        Args:
            besoin: Le besoin a sauvegarder.

        Returns:
            Le besoin sauvegarde (avec ID si creation).
        """
        pass

    @abstractmethod
    def find_by_id(self, id: int) -> Optional[BesoinCharge]:
        """
        Trouve un besoin par son ID.

        Args:
            id: L'identifiant unique du besoin.

        Returns:
            Le besoin trouve ou None.
        """
        pass

    @abstractmethod
    def find_by_chantier(
        self,
        chantier_id: int,
        semaine_debut: Semaine,
        semaine_fin: Semaine,
    ) -> List[BesoinCharge]:
        """
        Trouve les besoins d'un chantier sur une plage de semaines.

        Args:
            chantier_id: L'ID du chantier.
            semaine_debut: Premiere semaine (incluse).
            semaine_fin: Derniere semaine (incluse).

        Returns:
            Liste des besoins pour ce chantier.
        """
        pass

    @abstractmethod
    def find_by_semaine(self, semaine: Semaine) -> List[BesoinCharge]:
        """
        Trouve tous les besoins pour une semaine donnee.

        Args:
            semaine: La semaine recherchee.

        Returns:
            Liste des besoins pour cette semaine.
        """
        pass

    @abstractmethod
    def find_by_chantier_and_semaine(
        self,
        chantier_id: int,
        semaine: Semaine,
    ) -> List[BesoinCharge]:
        """
        Trouve les besoins d'un chantier pour une semaine.

        Args:
            chantier_id: L'ID du chantier.
            semaine: La semaine recherchee.

        Returns:
            Liste des besoins (un par type de metier).
        """
        pass

    @abstractmethod
    def find_by_chantier_semaine_and_type(
        self,
        chantier_id: int,
        semaine: Semaine,
        type_metier: TypeMetier,
    ) -> Optional[BesoinCharge]:
        """
        Trouve un besoin specifique par chantier, semaine et type.

        Args:
            chantier_id: L'ID du chantier.
            semaine: La semaine recherchee.
            type_metier: Le type de metier.

        Returns:
            Le besoin trouve ou None.
        """
        pass

    @abstractmethod
    def find_all_in_range(
        self,
        semaine_debut: Semaine,
        semaine_fin: Semaine,
    ) -> List[BesoinCharge]:
        """
        Trouve tous les besoins sur une plage de semaines.

        Utilise pour la vue tabulaire globale (PDC-01).

        Args:
            semaine_debut: Premiere semaine (incluse).
            semaine_fin: Derniere semaine (incluse).

        Returns:
            Liste de tous les besoins sur la periode.
        """
        pass

    @abstractmethod
    def delete(self, id: int) -> bool:
        """
        Supprime un besoin de charge.

        Args:
            id: L'identifiant du besoin a supprimer.

        Returns:
            True si supprime, False si non trouve.
        """
        pass

    @abstractmethod
    def delete_by_chantier(self, chantier_id: int) -> int:
        """
        Supprime tous les besoins d'un chantier.

        Utilise quand un chantier est ferme.

        Args:
            chantier_id: L'ID du chantier.

        Returns:
            Nombre de besoins supprimes.
        """
        pass

    @abstractmethod
    def sum_besoins_by_semaine(self, semaine: Semaine) -> float:
        """
        Calcule la somme des besoins pour une semaine.

        Args:
            semaine: La semaine.

        Returns:
            Total des heures de besoin.
        """
        pass

    @abstractmethod
    def sum_besoins_by_type_and_semaine(
        self,
        type_metier: TypeMetier,
        semaine: Semaine,
    ) -> float:
        """
        Calcule la somme des besoins par type pour une semaine.

        Args:
            type_metier: Le type de metier.
            semaine: La semaine.

        Returns:
            Total des heures de besoin pour ce type.
        """
        pass

    @abstractmethod
    def get_chantiers_with_besoins(
        self,
        semaine_debut: Semaine,
        semaine_fin: Semaine,
    ) -> List[int]:
        """
        Retourne les IDs des chantiers ayant des besoins sur une periode.

        Args:
            semaine_debut: Premiere semaine.
            semaine_fin: Derniere semaine.

        Returns:
            Liste des IDs de chantiers.
        """
        pass

    @abstractmethod
    def exists(
        self,
        chantier_id: int,
        semaine: Semaine,
        type_metier: TypeMetier,
        exclude_id: Optional[int] = None,
    ) -> bool:
        """
        Verifie si un besoin existe deja.

        Args:
            chantier_id: L'ID du chantier.
            semaine: La semaine.
            type_metier: Le type de metier.
            exclude_id: ID a exclure (pour les mises a jour).

        Returns:
            True si un besoin existe.
        """
        pass
