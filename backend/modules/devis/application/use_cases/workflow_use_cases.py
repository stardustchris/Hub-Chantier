"""Use Cases pour le workflow des devis.

DEV-15: Suivi statut devis - Transitions de statut.
"""

from datetime import datetime
from typing import Optional

from ...domain.entities.journal_devis import JournalDevis
from ...domain.repositories.devis_repository import DevisRepository
from ...domain.repositories.journal_devis_repository import JournalDevisRepository
from ..dtos.devis_dtos import DevisDTO


class DevisTransitionError(Exception):
    """Erreur levee pour une transition de statut invalide."""

    def __init__(self, devis_id: int, statut_actuel: str, statut_cible: str):
        self.devis_id = devis_id
        self.statut_actuel = statut_actuel
        self.statut_cible = statut_cible
        super().__init__(
            f"Transition invalide pour le devis {devis_id}: "
            f"'{statut_actuel}' -> '{statut_cible}'"
        )


# Matrice des transitions autorisees
TRANSITIONS_AUTORISEES = {
    "brouillon": ["en_validation"],
    "en_validation": ["approuve", "brouillon"],
    "approuve": ["envoye"],
    "envoye": ["accepte", "refuse", "perdu"],
    "accepte": [],
    "refuse": [],
    "perdu": [],
    "expire": ["en_validation"],
}


def _validate_transition(devis_id: int, statut_actuel: str, statut_cible: str) -> None:
    """Valide qu'une transition est autorisee."""
    allowed = TRANSITIONS_AUTORISEES.get(statut_actuel, [])
    if statut_cible not in allowed:
        raise DevisTransitionError(devis_id, statut_actuel, statut_cible)


class SoumettreDevisUseCase:
    """Transition: Brouillon -> En validation.

    DEV-15: Soumission pour validation interne.
    """

    def __init__(
        self,
        devis_repository: DevisRepository,
        journal_repository: JournalDevisRepository,
    ):
        self._devis_repository = devis_repository
        self._journal_repository = journal_repository

    def execute(self, devis_id: int, submitted_by: int) -> DevisDTO:
        """Soumet un devis pour validation interne.

        Raises:
            DevisNotFoundError: Si le devis n'existe pas.
            DevisTransitionError: Si la transition n'est pas autorisee.
        """
        from .devis_use_cases import DevisNotFoundError

        devis = self._devis_repository.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        _validate_transition(devis_id, devis.statut, "en_validation")

        devis.statut = "en_validation"
        devis.updated_at = datetime.utcnow()
        devis = self._devis_repository.save(devis)

        self._journal_repository.save(
            JournalDevis(
                devis_id=devis_id,
                action="soumission",
                details="Devis soumis pour validation interne",
                auteur_id=submitted_by,
                created_at=datetime.utcnow(),
            )
        )

        return DevisDTO.from_entity(devis)


class ValiderDevisUseCase:
    """Transition: En validation -> Approuve.

    DEV-15: Validation interne par direction.
    """

    def __init__(
        self,
        devis_repository: DevisRepository,
        journal_repository: JournalDevisRepository,
    ):
        self._devis_repository = devis_repository
        self._journal_repository = journal_repository

    def execute(self, devis_id: int, validated_by: int) -> DevisDTO:
        """Valide un devis (marque comme approuve).

        Raises:
            DevisNotFoundError: Si le devis n'existe pas.
            DevisTransitionError: Si la transition n'est pas autorisee.
        """
        from .devis_use_cases import DevisNotFoundError

        devis = self._devis_repository.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        _validate_transition(devis_id, devis.statut, "approuve")

        devis.statut = "approuve"
        devis.updated_at = datetime.utcnow()
        devis = self._devis_repository.save(devis)

        self._journal_repository.save(
            JournalDevis(
                devis_id=devis_id,
                action="validation",
                details="Devis approuve par la direction",
                auteur_id=validated_by,
                created_at=datetime.utcnow(),
            )
        )

        return DevisDTO.from_entity(devis)


class EnvoyerDevisUseCase:
    """Transition: Approuve -> Envoye.

    DEV-15: Envoi au client.
    """

    def __init__(
        self,
        devis_repository: DevisRepository,
        journal_repository: JournalDevisRepository,
    ):
        self._devis_repository = devis_repository
        self._journal_repository = journal_repository

    def execute(self, devis_id: int, sent_by: int) -> DevisDTO:
        """Marque un devis comme envoye au client.

        Raises:
            DevisNotFoundError: Si le devis n'existe pas.
            DevisTransitionError: Si la transition n'est pas autorisee.
        """
        from .devis_use_cases import DevisNotFoundError

        devis = self._devis_repository.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        _validate_transition(devis_id, devis.statut, "envoye")

        devis.statut = "envoye"
        devis.updated_at = datetime.utcnow()
        devis = self._devis_repository.save(devis)

        self._journal_repository.save(
            JournalDevis(
                devis_id=devis_id,
                action="envoi",
                details="Devis envoye au client",
                auteur_id=sent_by,
                created_at=datetime.utcnow(),
            )
        )

        return DevisDTO.from_entity(devis)


class AccepterDevisUseCase:
    """Transition: Envoye -> Accepte.

    DEV-15: Acceptation par le client.
    """

    def __init__(
        self,
        devis_repository: DevisRepository,
        journal_repository: JournalDevisRepository,
    ):
        self._devis_repository = devis_repository
        self._journal_repository = journal_repository

    def execute(self, devis_id: int, accepted_by: int) -> DevisDTO:
        """Marque un devis comme accepte.

        Raises:
            DevisNotFoundError: Si le devis n'existe pas.
            DevisTransitionError: Si la transition n'est pas autorisee.
        """
        from .devis_use_cases import DevisNotFoundError

        devis = self._devis_repository.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        _validate_transition(devis_id, devis.statut, "accepte")

        devis.statut = "accepte"
        devis.updated_at = datetime.utcnow()
        devis = self._devis_repository.save(devis)

        self._journal_repository.save(
            JournalDevis(
                devis_id=devis_id,
                action="acceptation",
                details="Devis accepte par le client",
                auteur_id=accepted_by,
                created_at=datetime.utcnow(),
            )
        )

        return DevisDTO.from_entity(devis)


class RefuserDevisUseCase:
    """Transition: Envoye -> Refuse.

    DEV-15: Refus par le client (motif obligatoire).
    """

    def __init__(
        self,
        devis_repository: DevisRepository,
        journal_repository: JournalDevisRepository,
    ):
        self._devis_repository = devis_repository
        self._journal_repository = journal_repository

    def execute(
        self, devis_id: int, refused_by: int, motif: str
    ) -> DevisDTO:
        """Marque un devis comme refuse.

        Args:
            devis_id: L'ID du devis.
            refused_by: L'ID de l'utilisateur.
            motif: Le motif du refus (obligatoire).

        Raises:
            DevisNotFoundError: Si le devis n'existe pas.
            DevisTransitionError: Si la transition n'est pas autorisee.
            ValueError: Si le motif est vide.
        """
        from .devis_use_cases import DevisNotFoundError

        if not motif or not motif.strip():
            raise ValueError("Le motif de refus est obligatoire")

        devis = self._devis_repository.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        _validate_transition(devis_id, devis.statut, "refuse")

        devis.statut = "refuse"
        devis.updated_at = datetime.utcnow()
        devis = self._devis_repository.save(devis)

        self._journal_repository.save(
            JournalDevis(
                devis_id=devis_id,
                action="refus",
                details=f"Devis refuse - Motif: {motif.strip()}",
                auteur_id=refused_by,
                created_at=datetime.utcnow(),
            )
        )

        return DevisDTO.from_entity(devis)


class PerduDevisUseCase:
    """Transition: Envoye -> Perdu.

    DEV-15: Marque comme perdu (motif obligatoire pour reporting).
    """

    def __init__(
        self,
        devis_repository: DevisRepository,
        journal_repository: JournalDevisRepository,
    ):
        self._devis_repository = devis_repository
        self._journal_repository = journal_repository

    def execute(
        self, devis_id: int, marked_by: int, motif: str
    ) -> DevisDTO:
        """Marque un devis comme perdu.

        Args:
            devis_id: L'ID du devis.
            marked_by: L'ID de l'utilisateur.
            motif: Le motif (obligatoire pour reporting).

        Raises:
            DevisNotFoundError: Si le devis n'existe pas.
            DevisTransitionError: Si la transition n'est pas autorisee.
            ValueError: Si le motif est vide.
        """
        from .devis_use_cases import DevisNotFoundError

        if not motif or not motif.strip():
            raise ValueError("Le motif est obligatoire")

        devis = self._devis_repository.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        _validate_transition(devis_id, devis.statut, "perdu")

        devis.statut = "perdu"
        devis.updated_at = datetime.utcnow()
        devis = self._devis_repository.save(devis)

        self._journal_repository.save(
            JournalDevis(
                devis_id=devis_id,
                action="perdu",
                details=f"Devis marque comme perdu - Motif: {motif.strip()}",
                auteur_id=marked_by,
                created_at=datetime.utcnow(),
            )
        )

        return DevisDTO.from_entity(devis)
