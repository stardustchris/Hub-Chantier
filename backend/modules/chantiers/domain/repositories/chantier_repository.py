"""Interface ChantierRepository - Abstraction pour la persistence des chantiers."""

from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities import Chantier, ContactChantierEntity, PhaseChantierEntity
from ..value_objects import CodeChantier, StatutChantier


class ChantierRepository(ABC):
    """
    Interface abstraite pour la persistence des chantiers.

    Cette interface définit le contrat pour l'accès aux données chantier.
    L'implémentation concrète se trouve dans la couche Infrastructure.

    Note:
        Le Domain ne connaît pas l'implémentation (SQLAlchemy, etc.).
    """

    @abstractmethod
    def find_by_id(self, chantier_id: int) -> Optional[Chantier]:
        """
        Trouve un chantier par son ID.

        Args:
            chantier_id: L'identifiant unique du chantier.

        Returns:
            Le chantier trouvé ou None.
        """
        pass

    @abstractmethod
    def find_by_code(self, code: CodeChantier) -> Optional[Chantier]:
        """
        Trouve un chantier par son code unique.

        Args:
            code: Le code du chantier (ex: A001).

        Returns:
            Le chantier trouvé ou None.
        """
        pass

    @abstractmethod
    def save(self, chantier: Chantier) -> Chantier:
        """
        Persiste un chantier (création ou mise à jour).

        Args:
            chantier: Le chantier à sauvegarder.

        Returns:
            Le chantier sauvegardé (avec ID si création).
        """
        pass

    @abstractmethod
    def delete(self, chantier_id: int) -> bool:
        """
        Supprime un chantier.

        Args:
            chantier_id: L'identifiant du chantier à supprimer.

        Returns:
            True si supprimé, False si non trouvé.
        """
        pass

    @abstractmethod
    def find_all(self, skip: int = 0, limit: int = 100) -> List[Chantier]:
        """
        Récupère tous les chantiers avec pagination.

        Args:
            skip: Nombre d'éléments à sauter.
            limit: Nombre maximum d'éléments à retourner.

        Returns:
            Liste des chantiers.
        """
        pass

    @abstractmethod
    def count(self) -> int:
        """
        Compte le nombre total de chantiers.

        Returns:
            Nombre total de chantiers.
        """
        pass

    @abstractmethod
    def find_by_statut(
        self, statut: StatutChantier, skip: int = 0, limit: int = 100
    ) -> List[Chantier]:
        """
        Trouve les chantiers par statut.

        Args:
            statut: Le statut à filtrer.
            skip: Nombre d'éléments à sauter.
            limit: Nombre maximum à retourner.

        Returns:
            Liste des chantiers avec ce statut.
        """
        pass

    @abstractmethod
    def find_active(self, skip: int = 0, limit: int = 100) -> List[Chantier]:
        """
        Trouve les chantiers actifs (non fermés).

        Args:
            skip: Nombre d'éléments à sauter.
            limit: Nombre maximum à retourner.

        Returns:
            Liste des chantiers actifs.
        """
        pass

    @abstractmethod
    def find_by_conducteur(
        self, conducteur_id: int, skip: int = 0, limit: int = 100
    ) -> List[Chantier]:
        """
        Trouve les chantiers d'un conducteur.

        Args:
            conducteur_id: ID du conducteur.
            skip: Nombre d'éléments à sauter.
            limit: Nombre maximum à retourner.

        Returns:
            Liste des chantiers du conducteur.
        """
        pass

    @abstractmethod
    def find_by_chef_chantier(
        self, chef_id: int, skip: int = 0, limit: int = 100
    ) -> List[Chantier]:
        """
        Trouve les chantiers d'un chef de chantier.

        Args:
            chef_id: ID du chef de chantier.
            skip: Nombre d'éléments à sauter.
            limit: Nombre maximum à retourner.

        Returns:
            Liste des chantiers du chef.
        """
        pass

    @abstractmethod
    def find_by_responsable(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Chantier]:
        """
        Trouve les chantiers dont l'utilisateur est responsable
        (conducteur OU chef de chantier).

        Args:
            user_id: ID de l'utilisateur.
            skip: Nombre d'éléments à sauter.
            limit: Nombre maximum à retourner.

        Returns:
            Liste des chantiers de l'utilisateur.
        """
        pass

    @abstractmethod
    def exists_by_code(self, code: CodeChantier) -> bool:
        """
        Vérifie si un code chantier est déjà utilisé.

        Args:
            code: Le code à vérifier.

        Returns:
            True si le code existe déjà.
        """
        pass

    @abstractmethod
    def get_last_code(self) -> Optional[str]:
        """
        Récupère le dernier code chantier utilisé.

        Returns:
            Le dernier code ou None si aucun chantier.
        """
        pass

    @abstractmethod
    def search(
        self,
        query: str,
        statut: Optional[StatutChantier] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Chantier]:
        """
        Recherche des chantiers par nom ou code.

        Args:
            query: Terme de recherche.
            statut: Filtre optionnel par statut.
            skip: Nombre d'éléments à sauter.
            limit: Nombre maximum à retourner.

        Returns:
            Liste des chantiers correspondants.
        """
        pass

    # =========================================================================
    # Ouvriers (sous-ressource de Chantier)
    # =========================================================================

    @abstractmethod
    def list_ouvrier_ids(self, chantier_id: int) -> List[int]:
        """Liste les IDs des ouvriers assignés à un chantier."""
        pass

    @abstractmethod
    def assign_ouvrier(self, chantier_id: int, user_id: int) -> bool:
        """Assigne un ouvrier au chantier. Retourne False si déjà assigné."""
        pass

    @abstractmethod
    def remove_ouvrier(self, chantier_id: int, user_id: int) -> bool:
        """Retire un ouvrier du chantier. Retourne True si supprimé."""
        pass

    # =========================================================================
    # Contacts (sous-ressource de Chantier - CHT-07)
    # =========================================================================

    @abstractmethod
    def list_contacts(self, chantier_id: int) -> List[ContactChantierEntity]:
        """Liste tous les contacts d'un chantier."""
        pass

    @abstractmethod
    def create_contact(
        self, chantier_id: int, nom: str, telephone: str, profession: Optional[str] = None
    ) -> ContactChantierEntity:
        """Crée un contact pour un chantier."""
        pass

    @abstractmethod
    def update_contact(
        self, chantier_id: int, contact_id: int,
        nom: Optional[str] = None, telephone: Optional[str] = None,
        profession: Optional[str] = None,
    ) -> Optional[ContactChantierEntity]:
        """Met à jour un contact. Retourne None si non trouvé."""
        pass

    @abstractmethod
    def delete_contact(self, chantier_id: int, contact_id: int) -> bool:
        """Supprime un contact. Retourne False si non trouvé."""
        pass

    # =========================================================================
    # Phases (sous-ressource de Chantier)
    # =========================================================================

    @abstractmethod
    def list_phases(self, chantier_id: int) -> List[PhaseChantierEntity]:
        """Liste toutes les phases d'un chantier, ordonnées."""
        pass

    @abstractmethod
    def create_phase(
        self, chantier_id: int, nom: str,
        description: Optional[str] = None, ordre: Optional[int] = None,
        date_debut: Optional[str] = None, date_fin: Optional[str] = None,
    ) -> PhaseChantierEntity:
        """Crée une phase pour un chantier."""
        pass

    @abstractmethod
    def update_phase(
        self, chantier_id: int, phase_id: int,
        nom: Optional[str] = None, description: Optional[str] = None,
        ordre: Optional[int] = None,
        date_debut: Optional[str] = None, date_fin: Optional[str] = None,
    ) -> Optional[PhaseChantierEntity]:
        """Met à jour une phase. Retourne None si non trouvée."""
        pass

    @abstractmethod
    def delete_phase(self, chantier_id: int, phase_id: int) -> bool:
        """Supprime une phase. Retourne False si non trouvée."""
        pass
