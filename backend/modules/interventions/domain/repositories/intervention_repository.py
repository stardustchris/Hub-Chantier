"""Interface du repository Intervention."""

from abc import ABC, abstractmethod
from datetime import date
from typing import Optional, List

from ..entities import Intervention
from ..value_objects import StatutIntervention, PrioriteIntervention, TypeIntervention


class InterventionRepository(ABC):
    """Interface abstraite pour le repository des interventions."""

    @abstractmethod
    async def save(self, intervention: Intervention) -> Intervention:
        """Sauvegarde une intervention (creation ou mise a jour).

        Args:
            intervention: L'intervention a sauvegarder.

        Returns:
            L'intervention avec son ID assigne.
        """
        pass

    @abstractmethod
    async def get_by_id(self, intervention_id: int) -> Optional[Intervention]:
        """Recupere une intervention par son ID.

        Args:
            intervention_id: L'identifiant de l'intervention.

        Returns:
            L'intervention ou None si non trouvee.
        """
        pass

    @abstractmethod
    async def get_by_code(self, code: str) -> Optional[Intervention]:
        """Recupere une intervention par son code.

        Args:
            code: Le code unique de l'intervention.

        Returns:
            L'intervention ou None si non trouvee.
        """
        pass

    @abstractmethod
    async def list_all(
        self,
        statut: Optional[StatutIntervention] = None,
        priorite: Optional[PrioriteIntervention] = None,
        type_intervention: Optional[TypeIntervention] = None,
        date_debut: Optional[date] = None,
        date_fin: Optional[date] = None,
        chantier_origine_id: Optional[int] = None,
        include_deleted: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Intervention]:
        """Liste les interventions avec filtres optionnels.

        INT-02: Liste des interventions - Tableau Chantier/Client/Adresse/Statut

        Args:
            statut: Filtrer par statut.
            priorite: Filtrer par priorite.
            type_intervention: Filtrer par type.
            date_debut: Filtrer par date planifiee >= date_debut.
            date_fin: Filtrer par date planifiee <= date_fin.
            chantier_origine_id: Filtrer par chantier d'origine.
            include_deleted: Inclure les interventions supprimees.
            limit: Nombre maximum de resultats.
            offset: Decalage pour la pagination.

        Returns:
            Liste des interventions correspondantes.
        """
        pass

    @abstractmethod
    async def count(
        self,
        statut: Optional[StatutIntervention] = None,
        priorite: Optional[PrioriteIntervention] = None,
        type_intervention: Optional[TypeIntervention] = None,
        include_deleted: bool = False,
    ) -> int:
        """Compte les interventions avec filtres optionnels.

        Args:
            statut: Filtrer par statut.
            priorite: Filtrer par priorite.
            type_intervention: Filtrer par type.
            include_deleted: Inclure les interventions supprimees.

        Returns:
            Nombre d'interventions.
        """
        pass

    @abstractmethod
    async def list_by_utilisateur(
        self,
        utilisateur_id: int,
        date_debut: Optional[date] = None,
        date_fin: Optional[date] = None,
        include_deleted: bool = False,
    ) -> List[Intervention]:
        """Liste les interventions d'un technicien.

        INT-06: Planning hebdomadaire - Utilisateurs en lignes

        Args:
            utilisateur_id: ID du technicien.
            date_debut: Date de debut de la periode.
            date_fin: Date de fin de la periode.
            include_deleted: Inclure les interventions supprimees.

        Returns:
            Liste des interventions du technicien.
        """
        pass

    @abstractmethod
    async def list_by_date_range(
        self,
        date_debut: date,
        date_fin: date,
        include_deleted: bool = False,
    ) -> List[Intervention]:
        """Liste les interventions pour une periode.

        INT-06: Planning hebdomadaire - Jours en colonnes

        Args:
            date_debut: Date de debut de la periode.
            date_fin: Date de fin de la periode.
            include_deleted: Inclure les interventions supprimees.

        Returns:
            Liste des interventions de la periode.
        """
        pass

    @abstractmethod
    async def delete(self, intervention_id: int, deleted_by: int) -> bool:
        """Supprime une intervention (soft delete).

        Args:
            intervention_id: ID de l'intervention.
            deleted_by: ID de l'utilisateur qui supprime.

        Returns:
            True si supprimee, False sinon.
        """
        pass

    @abstractmethod
    async def generate_code(self) -> str:
        """Genere un nouveau code unique pour une intervention.

        Format: INT-YYYY-NNNN (ex: INT-2026-0001)

        Returns:
            Le code genere.
        """
        pass
