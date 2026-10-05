"""Interfaces de persistance de la synchronisation avec une paie externe."""

from abc import ABC, abstractmethod

from ..entities.synchronisation_paie import StatutSynchronisation, SynchronisationPaie


class SynchronisationPaieRepository(ABC):
    """Persistance du suivi des envois de pointages vers la paie externe."""

    @abstractmethod
    def find_by_pointage_id(self, pointage_id: int) -> SynchronisationPaie | None:
        """Retourne le suivi d'un pointage, ou None s'il n'a jamais ete envoye."""

    @abstractmethod
    def save(self, synchronisation: SynchronisationPaie) -> SynchronisationPaie:
        """Cree ou met a jour le suivi d'un pointage."""

    @abstractmethod
    def find_by_statuts(
        self, statuts: list[StatutSynchronisation]
    ) -> list[SynchronisationPaie]:
        """Liste les suivis dans l'un des statuts donnes."""


class CorrespondanceExterneRepository(ABC):
    """Identifiants des compagnons et chantiers dans le systeme de paie externe.

    Hub Chantier et le systeme externe ont chacun leurs identifiants : un
    compagnon ou un chantier sans correspondance ne peut pas etre envoye.
    """

    TYPE_UTILISATEUR = "utilisateur"
    TYPE_CHANTIER = "chantier"

    @abstractmethod
    def get_identifiant_externe(self, type_entite: str, entite_id: int) -> str | None:
        """Retourne l'identifiant externe d'une entite, ou None s'il manque."""

    @abstractmethod
    def definir(self, type_entite: str, entite_id: int, identifiant_externe: str) -> None:
        """Cree ou remplace la correspondance d'une entite."""

    @abstractmethod
    def supprimer(self, type_entite: str, entite_id: int) -> None:
        """Supprime la correspondance d'une entite."""

    @abstractmethod
    def lister(self) -> list[tuple[str, int, str]]:
        """Liste toutes les correspondances (type, id Hub Chantier, id externe)."""
