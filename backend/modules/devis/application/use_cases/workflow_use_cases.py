"""Use Cases pour le workflow des devis.

DEV-15: Suivi statut devis - Transitions de statut avec:
  - State machine du domaine (StatutDevis + methodes entite Devis)
  - Guards role-based (qui peut changer quoi)
  - Domain Events sur changement de statut
  - Journal avec ancien/nouveau statut (DEV-18)
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from ...domain.entities.devis import (
    TransitionStatutDevisInvalideError,
)
from ...domain.entities.journal_devis import JournalDevis
from ...domain.events.devis_events import DevisStatutChangeEvent
from ...domain.services.workflow_guards import (
    TransitionNonAutoriseeError,
    WorkflowGuards,
)
from ...domain.value_objects import StatutDevis
from ...domain.repositories.devis_repository import DevisRepository
from ...domain.repositories.journal_devis_repository import JournalDevisRepository
from ..dtos.devis_dtos import DevisDTO


def _build_statut_change_event(
    devis_id: int,
    numero: str,
    ancien_statut: StatutDevis,
    nouveau_statut: StatutDevis,
    auteur_id: Optional[int],
    motif: Optional[str] = None,
) -> DevisStatutChangeEvent:
    """Construit un domain event de changement de statut."""
    return DevisStatutChangeEvent(
        devis_id=devis_id,
        numero=numero,
        ancien_statut=ancien_statut.value,
        nouveau_statut=nouveau_statut.value,
        auteur_id=auteur_id,
        motif=motif,
        timestamp=datetime.utcnow(),
    )


def _log_transition(
    journal_repository: JournalDevisRepository,
    devis_id: int,
    action: str,
    ancien_statut: str,
    nouveau_statut: str,
    message: str,
    auteur_id: Optional[int],
    motif: Optional[str] = None,
) -> None:
    """Enregistre une transition dans le journal avec les valeurs avant/apres (DEV-18)."""
    details = {
        "message": message,
        "ancien_statut": ancien_statut,
        "nouveau_statut": nouveau_statut,
    }
    if motif:
        details["motif"] = motif.strip()

    journal_repository.save(
        JournalDevis(
            devis_id=devis_id,
            action=action,
            details_json=details,
            auteur_id=auteur_id,
            created_at=datetime.utcnow(),
        )
    )


class SoumettreDevisUseCase:
    """Transition: Brouillon -> En validation.

    DEV-15: Soumission pour validation interne.
    Guards: admin, conducteur, commercial.
    """

    def __init__(
        self,
        devis_repository: DevisRepository,
        journal_repository: JournalDevisRepository,
    ):
        self._devis_repository = devis_repository
        self._journal_repository = journal_repository

    def execute(
        self, devis_id: int, submitted_by: int, role: Optional[str] = None
    ) -> DevisDTO:
        """Soumet un devis pour validation interne.

        Args:
            devis_id: L'ID du devis.
            submitted_by: L'ID de l'utilisateur.
            role: Le role de l'utilisateur (pour guard, optionnel backward compat).

        Raises:
            DevisNotFoundError: Si le devis n'existe pas.
            TransitionStatutDevisInvalideError: Si la transition n'est pas autorisee.
            TransitionNonAutoriseeError: Si le role n'a pas le droit.
        """
        from .devis_use_cases import DevisNotFoundError

        if role:
            WorkflowGuards.verifier_transition(role, "soumettre")

        devis = self._devis_repository.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        ancien_statut = devis.statut
        devis.soumettre_validation()
        devis = self._devis_repository.save(devis)

        # DEV-15: Domain event
        event = _build_statut_change_event(
            devis.id, devis.numero, ancien_statut, devis.statut, submitted_by
        )

        # DEV-18: Journal avec avant/apres
        _log_transition(
            self._journal_repository,
            devis_id=devis.id,
            action="soumission",
            ancien_statut=ancien_statut.value,
            nouveau_statut=devis.statut.value,
            message="Devis soumis pour validation interne",
            auteur_id=submitted_by,
        )

        return DevisDTO.from_entity(devis)


class ValiderDevisUseCase:
    """Transition: En validation -> Envoye.

    DEV-15: Validation interne puis envoi.
    Guards: admin, conducteur, commercial (admin si >= 50k EUR).
    """

    def __init__(
        self,
        devis_repository: DevisRepository,
        journal_repository: JournalDevisRepository,
    ):
        self._devis_repository = devis_repository
        self._journal_repository = journal_repository

    def execute(
        self, devis_id: int, validated_by: int, role: Optional[str] = None
    ) -> DevisDTO:
        """Valide un devis et l'envoie au client.

        Args:
            devis_id: L'ID du devis.
            validated_by: L'ID de l'utilisateur.
            role: Le role de l'utilisateur (pour guard, optionnel backward compat).

        Raises:
            DevisNotFoundError: Si le devis n'existe pas.
            TransitionStatutDevisInvalideError: Si la transition n'est pas autorisee.
            TransitionNonAutoriseeError: Si le role n'a pas le droit.
        """
        from .devis_use_cases import DevisNotFoundError

        devis = self._devis_repository.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        # Guard avec verification seuil 50k EUR
        if role:
            montant_ht = float(devis.montant_total_ht) if devis.montant_total_ht else 0
            WorkflowGuards.verifier_transition(role, "valider", montant_ht=montant_ht)

        ancien_statut = devis.statut
        devis.envoyer()
        devis = self._devis_repository.save(devis)

        event = _build_statut_change_event(
            devis.id, devis.numero, ancien_statut, devis.statut, validated_by
        )

        _log_transition(
            self._journal_repository,
            devis_id=devis.id,
            action="validation_envoi",
            ancien_statut=ancien_statut.value,
            nouveau_statut=devis.statut.value,
            message="Devis valide et envoye au client",
            auteur_id=validated_by,
        )

        return DevisDTO.from_entity(devis)


class RetournerBrouillonUseCase:
    """Transition: En validation -> Brouillon.

    DEV-15: Retour en brouillon pour corrections.
    Guards: admin, conducteur.
    """

    def __init__(
        self,
        devis_repository: DevisRepository,
        journal_repository: JournalDevisRepository,
    ):
        self._devis_repository = devis_repository
        self._journal_repository = journal_repository

    def execute(
        self, devis_id: int, returned_by: int, motif: Optional[str] = None,
        role: Optional[str] = None,
    ) -> DevisDTO:
        """Retourne un devis en brouillon.

        Raises:
            DevisNotFoundError: Si le devis n'existe pas.
            TransitionStatutDevisInvalideError: Si la transition n'est pas autorisee.
            TransitionNonAutoriseeError: Si le role n'a pas le droit.
        """
        from .devis_use_cases import DevisNotFoundError

        if role:
            WorkflowGuards.verifier_transition(role, "retourner_brouillon")

        devis = self._devis_repository.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        ancien_statut = devis.statut
        devis.retourner_brouillon()
        devis = self._devis_repository.save(devis)

        message = "Devis retourne en brouillon"
        if motif:
            message += f" - Motif: {motif.strip()}"

        event = _build_statut_change_event(
            devis.id, devis.numero, ancien_statut, devis.statut, returned_by, motif
        )

        _log_transition(
            self._journal_repository,
            devis_id=devis.id,
            action="retour_brouillon",
            ancien_statut=ancien_statut.value,
            nouveau_statut=devis.statut.value,
            message=message,
            auteur_id=returned_by,
            motif=motif,
        )

        return DevisDTO.from_entity(devis)


class MarquerVuUseCase:
    """Transition: Envoye -> Vu.

    DEV-15: Le client a vu le devis (action systeme ou tracking).
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

        ancien_statut = devis.statut
        devis.marquer_vu()
        devis = self._devis_repository.save(devis)

        event = _build_statut_change_event(
            devis.id, devis.numero, ancien_statut, devis.statut, None
        )

        _log_transition(
            self._journal_repository,
            devis_id=devis.id,
            action="vu",
            ancien_statut=ancien_statut.value,
            nouveau_statut=devis.statut.value,
            message="Devis consulte par le client",
            auteur_id=None,
        )

        return DevisDTO.from_entity(devis)


class PasserEnNegociationUseCase:
    """Transition: Envoye/Vu/Expire -> En negociation.

    DEV-15: Passage en negociation.
    Guards: admin, conducteur, commercial.
    """

    def __init__(
        self,
        devis_repository: DevisRepository,
        journal_repository: JournalDevisRepository,
    ):
        self._devis_repository = devis_repository
        self._journal_repository = journal_repository

    def execute(
        self, devis_id: int, initiated_by: int, role: Optional[str] = None
    ) -> DevisDTO:
        """Passe un devis en negociation.

        Raises:
            DevisNotFoundError: Si le devis n'existe pas.
            TransitionStatutDevisInvalideError: Si la transition n'est pas autorisee.
            TransitionNonAutoriseeError: Si le role n'a pas le droit.
        """
        from .devis_use_cases import DevisNotFoundError

        if role:
            WorkflowGuards.verifier_transition(role, "negociation")

        devis = self._devis_repository.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        ancien_statut = devis.statut
        devis.passer_en_negociation()
        devis = self._devis_repository.save(devis)

        event = _build_statut_change_event(
            devis.id, devis.numero, ancien_statut, devis.statut, initiated_by
        )

        _log_transition(
            self._journal_repository,
            devis_id=devis.id,
            action="negociation",
            ancien_statut=ancien_statut.value,
            nouveau_statut=devis.statut.value,
            message="Devis passe en negociation",
            auteur_id=initiated_by,
        )

        return DevisDTO.from_entity(devis)


class AccepterDevisUseCase:
    """Transition: Envoye/Vu/En negociation -> Accepte.

    DEV-15: Acceptation par le client.
    Guards: admin, conducteur.
    """

    def __init__(
        self,
        devis_repository: DevisRepository,
        journal_repository: JournalDevisRepository,
    ):
        self._devis_repository = devis_repository
        self._journal_repository = journal_repository

    def execute(
        self, devis_id: int, accepted_by: int, role: Optional[str] = None
    ) -> DevisDTO:
        """Marque un devis comme accepte.

        Raises:
            DevisNotFoundError: Si le devis n'existe pas.
            TransitionStatutDevisInvalideError: Si la transition n'est pas autorisee.
            TransitionNonAutoriseeError: Si le role n'a pas le droit.
        """
        from .devis_use_cases import DevisNotFoundError

        if role:
            WorkflowGuards.verifier_transition(role, "accepter")

        devis = self._devis_repository.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        ancien_statut = devis.statut
        devis.accepter()
        devis = self._devis_repository.save(devis)

        event = _build_statut_change_event(
            devis.id, devis.numero, ancien_statut, devis.statut, accepted_by
        )

        _log_transition(
            self._journal_repository,
            devis_id=devis.id,
            action="acceptation",
            ancien_statut=ancien_statut.value,
            nouveau_statut=devis.statut.value,
            message="Devis accepte par le client",
            auteur_id=accepted_by,
        )

        return DevisDTO.from_entity(devis)


class RefuserDevisUseCase:
    """Transition: Envoye/Vu/En negociation -> Refuse.

    DEV-15: Refus par le client (motif obligatoire).
    Guards: admin, conducteur, commercial.
    """

    def __init__(
        self,
        devis_repository: DevisRepository,
        journal_repository: JournalDevisRepository,
    ):
        self._devis_repository = devis_repository
        self._journal_repository = journal_repository

    def execute(
        self, devis_id: int, refused_by: int, motif: str,
        role: Optional[str] = None,
    ) -> DevisDTO:
        """Marque un devis comme refuse.

        Args:
            devis_id: L'ID du devis.
            refused_by: L'ID de l'utilisateur.
            motif: Le motif du refus (obligatoire).
            role: Le role de l'utilisateur (pour guard, optionnel).

        Raises:
            DevisNotFoundError: Si le devis n'existe pas.
            TransitionStatutDevisInvalideError: Si la transition n'est pas autorisee.
            TransitionNonAutoriseeError: Si le role n'a pas le droit.
            ValueError: Si le motif est vide.
        """
        from .devis_use_cases import DevisNotFoundError

        if not motif or not motif.strip():
            raise ValueError("Le motif de refus est obligatoire")

        if role:
            WorkflowGuards.verifier_transition(role, "refuser")

        devis = self._devis_repository.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        ancien_statut = devis.statut
        devis.refuser()
        devis = self._devis_repository.save(devis)

        event = _build_statut_change_event(
            devis.id, devis.numero, ancien_statut, devis.statut, refused_by, motif
        )

        _log_transition(
            self._journal_repository,
            devis_id=devis.id,
            action="refus",
            ancien_statut=ancien_statut.value,
            nouveau_statut=devis.statut.value,
            message=f"Devis refuse - Motif: {motif.strip()}",
            auteur_id=refused_by,
            motif=motif,
        )

        return DevisDTO.from_entity(devis)


class PerduDevisUseCase:
    """Transition: En negociation -> Perdu.

    DEV-15: Marque comme perdu (motif obligatoire pour reporting).
    Guards: admin, conducteur.
    """

    def __init__(
        self,
        devis_repository: DevisRepository,
        journal_repository: JournalDevisRepository,
    ):
        self._devis_repository = devis_repository
        self._journal_repository = journal_repository

    def execute(
        self, devis_id: int, marked_by: int, motif: str,
        role: Optional[str] = None,
    ) -> DevisDTO:
        """Marque un devis comme perdu.

        Args:
            devis_id: L'ID du devis.
            marked_by: L'ID de l'utilisateur.
            motif: Le motif (obligatoire pour reporting).
            role: Le role de l'utilisateur (pour guard, optionnel).

        Raises:
            DevisNotFoundError: Si le devis n'existe pas.
            TransitionStatutDevisInvalideError: Si la transition n'est pas autorisee.
            TransitionNonAutoriseeError: Si le role n'a pas le droit.
            ValueError: Si le motif est vide.
        """
        from .devis_use_cases import DevisNotFoundError

        if not motif or not motif.strip():
            raise ValueError("Le motif est obligatoire")

        if role:
            WorkflowGuards.verifier_transition(role, "perdu")

        devis = self._devis_repository.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        ancien_statut = devis.statut
        devis.marquer_perdu()
        devis = self._devis_repository.save(devis)

        event = _build_statut_change_event(
            devis.id, devis.numero, ancien_statut, devis.statut, marked_by, motif
        )

        _log_transition(
            self._journal_repository,
            devis_id=devis.id,
            action="perdu",
            ancien_statut=ancien_statut.value,
            nouveau_statut=devis.statut.value,
            message=f"Devis marque comme perdu - Motif: {motif.strip()}",
            auteur_id=marked_by,
            motif=motif,
        )

        return DevisDTO.from_entity(devis)


class MarquerExpireUseCase:
    """Transition: Envoye/Vu -> Expire.

    DEV-15: Expiration automatique quand date validite depassee.
    Pas de guard (action systeme automatique).
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
                ancien_statut = devis.statut
                devis.marquer_expire()
                self._devis_repository.save(devis)

                event = _build_statut_change_event(
                    devis.id, devis.numero, ancien_statut, devis.statut, None
                )

                _log_transition(
                    self._journal_repository,
                    devis_id=devis.id,
                    action="expiration",
                    ancien_statut=ancien_statut.value,
                    nouveau_statut=devis.statut.value,
                    message="Devis expire automatiquement (date de validite depassee)",
                    auteur_id=None,
                )
                count += 1
            except TransitionStatutDevisInvalideError:
                continue

        return count


class GetWorkflowInfoUseCase:
    """Use case pour recuperer les informations du workflow d'un devis.

    DEV-15: Retourne le statut actuel, les transitions possibles,
    et les roles autorises pour chaque transition.
    """

    def __init__(self, devis_repository: DevisRepository):
        self._devis_repository = devis_repository

    def execute(self, devis_id: int) -> dict:
        """Recupere les informations de workflow d'un devis.

        Returns:
            Dictionnaire avec statut actuel, transitions possibles et roles.
        """
        from .devis_use_cases import DevisNotFoundError

        devis = self._devis_repository.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        transitions_possibles = devis.statut.transitions_possibles()

        transitions_info = []
        for statut_cible in transitions_possibles:
            # Determiner le nom de la transition
            transition_name = _get_transition_name(devis.statut, statut_cible)
            roles = WorkflowGuards.TRANSITIONS_PAR_ROLE.get(transition_name, set())
            transitions_info.append({
                "statut_cible": statut_cible.value,
                "statut_cible_label": statut_cible.label,
                "statut_cible_couleur": statut_cible.couleur,
                "transition": transition_name,
                "roles_autorises": sorted(roles),
                "motif_requis": statut_cible in {StatutDevis.REFUSE, StatutDevis.PERDU},
            })

        return {
            "devis_id": devis.id,
            "numero": devis.numero,
            "statut_actuel": devis.statut.value,
            "statut_label": devis.statut.label,
            "statut_couleur": devis.statut.couleur,
            "est_modifiable": devis.est_modifiable,
            "est_final": devis.statut.est_final,
            "transitions_possibles": transitions_info,
        }


def _get_transition_name(statut_actuel: StatutDevis, statut_cible: StatutDevis) -> str:
    """Retourne le nom de la transition pour lookup dans les guards."""
    mapping = {
        (StatutDevis.BROUILLON, StatutDevis.EN_VALIDATION): "soumettre",
        (StatutDevis.EN_VALIDATION, StatutDevis.BROUILLON): "retourner_brouillon",
        (StatutDevis.EN_VALIDATION, StatutDevis.ENVOYE): "valider",
        (StatutDevis.ENVOYE, StatutDevis.VU): "marquer_vu",
        (StatutDevis.ENVOYE, StatutDevis.EN_NEGOCIATION): "negociation",
        (StatutDevis.ENVOYE, StatutDevis.ACCEPTE): "accepter",
        (StatutDevis.ENVOYE, StatutDevis.REFUSE): "refuser",
        (StatutDevis.ENVOYE, StatutDevis.EXPIRE): "expirer",
        (StatutDevis.VU, StatutDevis.EN_NEGOCIATION): "negociation",
        (StatutDevis.VU, StatutDevis.ACCEPTE): "accepter",
        (StatutDevis.VU, StatutDevis.REFUSE): "refuser",
        (StatutDevis.VU, StatutDevis.EXPIRE): "expirer",
        (StatutDevis.EN_NEGOCIATION, StatutDevis.ENVOYE): "envoyer",
        (StatutDevis.EN_NEGOCIATION, StatutDevis.ACCEPTE): "accepter",
        (StatutDevis.EN_NEGOCIATION, StatutDevis.REFUSE): "refuser",
        (StatutDevis.EN_NEGOCIATION, StatutDevis.PERDU): "perdu",
        (StatutDevis.ACCEPTE, StatutDevis.CONVERTI): "convertir",
        (StatutDevis.EXPIRE, StatutDevis.EN_NEGOCIATION): "negociation",
    }
    return mapping.get((statut_actuel, statut_cible), "inconnu")
