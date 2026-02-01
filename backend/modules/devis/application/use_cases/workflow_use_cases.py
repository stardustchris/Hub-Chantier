"""Use Cases pour le workflow des devis.

DEV-15: Suivi statut devis - Transitions de statut.
Utilise la state machine du domaine (StatutDevis + methodes entite Devis).
"""

from datetime import datetime
from typing import Optional

from ...domain.entities.devis import (
    TransitionStatutDevisInvalideError,
)
from ...domain.entities.journal_devis import JournalDevis
from ...domain.value_objects import StatutDevis
from ...domain.repositories.devis_repository import DevisRepository
from ...domain.repositories.journal_devis_repository import JournalDevisRepository
from ..dtos.devis_dtos import DevisDTO


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
            TransitionStatutDevisInvalideError: Si la transition n'est pas autorisee.
        """
        from .devis_use_cases import DevisNotFoundError

        devis = self._devis_repository.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        devis.soumettre_validation()
        devis = self._devis_repository.save(devis)

        self._journal_repository.save(
            JournalDevis(
                devis_id=devis_id,
                action="soumission",
                details_json={"message": "Devis soumis pour validation interne"},
                auteur_id=submitted_by,
                created_at=datetime.utcnow(),
            )
        )

        return DevisDTO.from_entity(devis)


class ValiderDevisUseCase:
    """Transition: En validation -> Envoye.

    DEV-15: Validation interne puis envoi.
    """

    def __init__(
        self,
        devis_repository: DevisRepository,
        journal_repository: JournalDevisRepository,
    ):
        self._devis_repository = devis_repository
        self._journal_repository = journal_repository

    def execute(self, devis_id: int, validated_by: int) -> DevisDTO:
        """Valide un devis et l'envoie au client.

        Raises:
            DevisNotFoundError: Si le devis n'existe pas.
            TransitionStatutDevisInvalideError: Si la transition n'est pas autorisee.
        """
        from .devis_use_cases import DevisNotFoundError

        devis = self._devis_repository.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        devis.envoyer()
        devis = self._devis_repository.save(devis)

        self._journal_repository.save(
            JournalDevis(
                devis_id=devis_id,
                action="validation_envoi",
                details_json={"message": "Devis valide et envoye au client"},
                auteur_id=validated_by,
                created_at=datetime.utcnow(),
            )
        )

        return DevisDTO.from_entity(devis)


class RetournerBrouillonUseCase:
    """Transition: En validation -> Brouillon.

    DEV-15: Retour en brouillon pour corrections.
    """

    def __init__(
        self,
        devis_repository: DevisRepository,
        journal_repository: JournalDevisRepository,
    ):
        self._devis_repository = devis_repository
        self._journal_repository = journal_repository

    def execute(self, devis_id: int, returned_by: int, motif: Optional[str] = None) -> DevisDTO:
        """Retourne un devis en brouillon.

        Raises:
            DevisNotFoundError: Si le devis n'existe pas.
            TransitionStatutDevisInvalideError: Si la transition n'est pas autorisee.
        """
        from .devis_use_cases import DevisNotFoundError

        devis = self._devis_repository.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        devis.retourner_brouillon()
        devis = self._devis_repository.save(devis)

        details = "Devis retourne en brouillon"
        if motif:
            details += f" - Motif: {motif.strip()}"

        self._journal_repository.save(
            JournalDevis(
                devis_id=devis_id,
                action="retour_brouillon",
                details_json={"message": details},
                auteur_id=returned_by,
                created_at=datetime.utcnow(),
            )
        )

        return DevisDTO.from_entity(devis)


class MarquerVuUseCase:
    """Transition: Envoye -> Vu.

    DEV-15: Le client a vu le devis.
    """

    def __init__(
        self,
        devis_repository: DevisRepository,
        journal_repository: JournalDevisRepository,
    ):
        self._devis_repository = devis_repository
        self._journal_repository = journal_repository

    def execute(self, devis_id: int) -> DevisDTO:
        """Marque un devis comme vu par le client.

        Raises:
            DevisNotFoundError: Si le devis n'existe pas.
            TransitionStatutDevisInvalideError: Si la transition n'est pas autorisee.
        """
        from .devis_use_cases import DevisNotFoundError

        devis = self._devis_repository.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        devis.marquer_vu()
        devis = self._devis_repository.save(devis)

        self._journal_repository.save(
            JournalDevis(
                devis_id=devis_id,
                action="vu",
                details_json={"message": "Devis consulte par le client"},
                auteur_id=None,
                created_at=datetime.utcnow(),
            )
        )

        return DevisDTO.from_entity(devis)


class PasserEnNegociationUseCase:
    """Transition: Envoye/Vu/Expire -> En negociation.

    DEV-15: Passage en negociation.
    """

    def __init__(
        self,
        devis_repository: DevisRepository,
        journal_repository: JournalDevisRepository,
    ):
        self._devis_repository = devis_repository
        self._journal_repository = journal_repository

    def execute(self, devis_id: int, initiated_by: int) -> DevisDTO:
        """Passe un devis en negociation.

        Raises:
            DevisNotFoundError: Si le devis n'existe pas.
            TransitionStatutDevisInvalideError: Si la transition n'est pas autorisee.
        """
        from .devis_use_cases import DevisNotFoundError

        devis = self._devis_repository.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        devis.passer_en_negociation()
        devis = self._devis_repository.save(devis)

        self._journal_repository.save(
            JournalDevis(
                devis_id=devis_id,
                action="negociation",
                details_json={"message": "Devis passe en negociation"},
                auteur_id=initiated_by,
                created_at=datetime.utcnow(),
            )
        )

        return DevisDTO.from_entity(devis)


class AccepterDevisUseCase:
    """Transition: Envoye/Vu/En negociation -> Accepte.

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
            TransitionStatutDevisInvalideError: Si la transition n'est pas autorisee.
        """
        from .devis_use_cases import DevisNotFoundError

        devis = self._devis_repository.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        devis.accepter()
        devis = self._devis_repository.save(devis)

        self._journal_repository.save(
            JournalDevis(
                devis_id=devis_id,
                action="acceptation",
                details_json={"message": "Devis accepte par le client"},
                auteur_id=accepted_by,
                created_at=datetime.utcnow(),
            )
        )

        return DevisDTO.from_entity(devis)


class RefuserDevisUseCase:
    """Transition: Envoye/Vu/En negociation -> Refuse.

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
            TransitionStatutDevisInvalideError: Si la transition n'est pas autorisee.
            ValueError: Si le motif est vide.
        """
        from .devis_use_cases import DevisNotFoundError

        if not motif or not motif.strip():
            raise ValueError("Le motif de refus est obligatoire")

        devis = self._devis_repository.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        devis.refuser()
        devis = self._devis_repository.save(devis)

        self._journal_repository.save(
            JournalDevis(
                devis_id=devis_id,
                action="refus",
                details_json={"message": f"Devis refuse - Motif: {motif.strip()}"},
                auteur_id=refused_by,
                created_at=datetime.utcnow(),
            )
        )

        return DevisDTO.from_entity(devis)


class PerduDevisUseCase:
    """Transition: En negociation -> Perdu.

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
            TransitionStatutDevisInvalideError: Si la transition n'est pas autorisee.
            ValueError: Si le motif est vide.
        """
        from .devis_use_cases import DevisNotFoundError

        if not motif or not motif.strip():
            raise ValueError("Le motif est obligatoire")

        devis = self._devis_repository.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        devis.marquer_perdu()
        devis = self._devis_repository.save(devis)

        self._journal_repository.save(
            JournalDevis(
                devis_id=devis_id,
                action="perdu",
                details_json={"message": f"Devis marque comme perdu - Motif: {motif.strip()}"},
                auteur_id=marked_by,
                created_at=datetime.utcnow(),
            )
        )

        return DevisDTO.from_entity(devis)


class MarquerExpireUseCase:
    """Transition: Envoye/Vu -> Expire.

    DEV-15: Expiration automatique quand date validite depassee.
    """

    def __init__(
        self,
        devis_repository: DevisRepository,
        journal_repository: JournalDevisRepository,
    ):
        self._devis_repository = devis_repository
        self._journal_repository = journal_repository

    def execute_batch(self) -> int:
        """Marque tous les devis expires (date validite depassee).

        Returns:
            Le nombre de devis marques comme expires.
        """
        devis_expires = self._devis_repository.find_expires()
        count = 0

        for devis in devis_expires:
            try:
                devis.marquer_expire()
                self._devis_repository.save(devis)

                self._journal_repository.save(
                    JournalDevis(
                        devis_id=devis.id,
                        action="expiration",
                        details_json={"message": "Devis expire automatiquement (date de validite depassee)"},
                        auteur_id=None,
                        created_at=datetime.utcnow(),
                    )
                )
                count += 1
            except TransitionStatutDevisInvalideError:
                continue

        return count
