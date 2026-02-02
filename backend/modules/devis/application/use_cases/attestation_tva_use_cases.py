"""Use Cases pour la gestion des attestations TVA.

DEV-23: Generation attestation TVA reglementaire.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from ...domain.entities.attestation_tva import (
    AttestationTVA,
    AttestationTVAValidationError,
)
from ...domain.repositories.devis_repository import DevisRepository
from ...domain.repositories.attestation_tva_repository import AttestationTVARepository
from ...domain.repositories.journal_devis_repository import JournalDevisRepository
from ...domain.entities.journal_devis import JournalDevis
from ...domain.value_objects.taux_tva import TauxTVA, TauxTVAInvalideError
from ..dtos.attestation_tva_dtos import (
    AttestationTVACreateDTO,
    AttestationTVADTO,
    EligibiliteTVADTO,
)
from .devis_use_cases import DevisNotFoundError


class AttestationTVAError(Exception):
    """Exception generique pour les erreurs liees aux attestations TVA."""

    def __init__(self, message: str = "Erreur attestation TVA"):
        self.message = message
        super().__init__(self.message)


class AttestationTVADejaExistanteError(AttestationTVAError):
    """Erreur levee quand une attestation TVA existe deja pour un devis."""

    def __init__(self, devis_id: int):
        self.devis_id = devis_id
        super().__init__(
            f"Une attestation TVA existe deja pour le devis {devis_id}"
        )


class AttestationTVANotFoundError(AttestationTVAError):
    """Erreur levee quand une attestation TVA n'est pas trouvee."""

    def __init__(self, devis_id: int):
        self.devis_id = devis_id
        super().__init__(
            f"Aucune attestation TVA trouvee pour le devis {devis_id}"
        )


class TVANonEligibleError(AttestationTVAError):
    """Erreur levee quand le devis n'est pas eligible a la TVA reduite."""

    def __init__(self, devis_id: int, taux_tva: Decimal):
        self.devis_id = devis_id
        self.taux_tva = taux_tva
        super().__init__(
            f"Le devis {devis_id} a un taux de TVA de {taux_tva}% "
            f"et n'est pas eligible a la TVA reduite"
        )


class GenererAttestationTVAUseCase:
    """Use case pour generer une attestation TVA.

    DEV-23: Verifie le taux TVA du devis et cree l'attestation
    CERFA correspondante (1300-SD ou 1301-SD).

    Attributes:
        _devis_repository: Repository pour acceder aux devis.
        _attestation_repository: Repository pour persister les attestations.
        _journal_repository: Repository pour le journal d'audit.
    """

    def __init__(
        self,
        devis_repository: DevisRepository,
        attestation_repository: AttestationTVARepository,
        journal_repository: JournalDevisRepository,
    ):
        """Initialise le use case.

        Args:
            devis_repository: Repository Devis (interface).
            attestation_repository: Repository AttestationTVA (interface).
            journal_repository: Repository Journal (interface).
        """
        self._devis_repository = devis_repository
        self._attestation_repository = attestation_repository
        self._journal_repository = journal_repository

    def execute(
        self,
        devis_id: int,
        dto: AttestationTVACreateDTO,
        created_by: int,
    ) -> AttestationTVADTO:
        """Genere une attestation TVA pour un devis.

        Args:
            devis_id: L'ID du devis.
            dto: Les donnees de l'attestation.
            created_by: L'ID de l'utilisateur createur.

        Returns:
            Le DTO de l'attestation creee.

        Raises:
            DevisNotFoundError: Si le devis n'existe pas.
            TVANonEligibleError: Si le taux TVA n'est pas eligible.
            AttestationTVADejaExistanteError: Si une attestation existe deja.
            AttestationTVAValidationError: Si les donnees sont invalides.
        """
        # 1. Recuperer le devis
        devis = self._devis_repository.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        # 2. Verifier eligibilite TVA reduite
        taux_decimal = devis.taux_tva_defaut
        try:
            taux_vo = TauxTVA(taux_decimal)
        except TauxTVAInvalideError:
            raise TVANonEligibleError(devis_id, taux_decimal)

        if not taux_vo.necessite_attestation:
            raise TVANonEligibleError(devis_id, taux_decimal)

        # 3. Verifier qu'aucune attestation n'existe deja
        existante = self._attestation_repository.find_by_devis_id(devis_id)
        if existante:
            raise AttestationTVADejaExistanteError(devis_id)

        # 4. Creer l'attestation
        type_cerfa = taux_vo.type_cerfa
        attestation = AttestationTVA(
            devis_id=devis_id,
            type_cerfa=type_cerfa,
            taux_tva=float(taux_decimal),
            nom_client=dto.nom_client or devis.client_nom,
            adresse_client=dto.adresse_client or devis.client_adresse or "",
            telephone_client=dto.telephone_client or devis.client_telephone,
            adresse_immeuble=dto.adresse_immeuble,
            nature_immeuble=dto.nature_immeuble,
            date_construction_plus_2ans=dto.date_construction_plus_2ans,
            description_travaux=dto.description_travaux,
            nature_travaux=dto.nature_travaux,
            atteste_par=dto.atteste_par,
            generee_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # 5. Persister
        attestation = self._attestation_repository.save(attestation)

        # 6. Journal
        self._journal_repository.save(
            JournalDevis(
                devis_id=devis_id,
                action="generation_attestation_tva",
                details_json={
                    "message": (
                        f"Generation attestation TVA CERFA {type_cerfa} "
                        f"(taux {taux_decimal}%)"
                    ),
                    "type_cerfa": type_cerfa,
                    "taux_tva": str(taux_decimal),
                },
                auteur_id=created_by,
                created_at=datetime.utcnow(),
            )
        )

        return AttestationTVADTO.from_entity(attestation)


class GetAttestationTVAUseCase:
    """Use case pour recuperer l'attestation TVA d'un devis.

    Attributes:
        _devis_repository: Repository pour verifier l'existence du devis.
        _attestation_repository: Repository pour acceder aux attestations.
    """

    def __init__(
        self,
        devis_repository: DevisRepository,
        attestation_repository: AttestationTVARepository,
    ):
        """Initialise le use case.

        Args:
            devis_repository: Repository Devis (interface).
            attestation_repository: Repository AttestationTVA (interface).
        """
        self._devis_repository = devis_repository
        self._attestation_repository = attestation_repository

    def execute(self, devis_id: int) -> AttestationTVADTO:
        """Recupere l'attestation TVA d'un devis.

        Args:
            devis_id: L'ID du devis.

        Returns:
            Le DTO de l'attestation.

        Raises:
            DevisNotFoundError: Si le devis n'existe pas.
            AttestationTVANotFoundError: Si aucune attestation n'existe.
        """
        # 1. Verifier que le devis existe
        devis = self._devis_repository.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        # 2. Recuperer l'attestation
        attestation = self._attestation_repository.find_by_devis_id(devis_id)
        if not attestation:
            raise AttestationTVANotFoundError(devis_id)

        return AttestationTVADTO.from_entity(attestation)


class VerifierEligibiliteTVAUseCase:
    """Use case pour verifier l'eligibilite d'un devis a la TVA reduite.

    Attributes:
        _devis_repository: Repository pour acceder aux devis.
    """

    def __init__(self, devis_repository: DevisRepository):
        """Initialise le use case.

        Args:
            devis_repository: Repository Devis (interface).
        """
        self._devis_repository = devis_repository

    def execute(self, devis_id: int) -> EligibiliteTVADTO:
        """Verifie si un devis est eligible a la TVA reduite.

        Args:
            devis_id: L'ID du devis.

        Returns:
            Le DTO d'eligibilite avec les details.

        Raises:
            DevisNotFoundError: Si le devis n'existe pas.
        """
        devis = self._devis_repository.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        taux_decimal = devis.taux_tva_defaut

        # Verifier si le taux est un taux connu
        try:
            taux_vo = TauxTVA(taux_decimal)
        except TauxTVAInvalideError:
            return EligibiliteTVADTO(
                devis_id=devis_id,
                taux_tva_defaut=str(taux_decimal),
                est_eligible=False,
                type_cerfa=None,
                libelle_tva=f"TVA {taux_decimal}%",
                message=(
                    f"Le taux de TVA {taux_decimal}% n'est pas un taux standard. "
                    f"Les taux autorises sont: 5.5%, 10%, 20%."
                ),
            )

        est_eligible = taux_vo.necessite_attestation

        if est_eligible:
            message = (
                f"Le devis est eligible a la TVA reduite ({taux_vo.libelle}). "
                f"Une attestation CERFA {taux_vo.type_cerfa} est requise."
            )
        else:
            message = (
                f"Le devis applique le taux standard ({taux_vo.libelle}). "
                f"Aucune attestation TVA n'est requise."
            )

        return EligibiliteTVADTO(
            devis_id=devis_id,
            taux_tva_defaut=str(taux_decimal),
            est_eligible=est_eligible,
            type_cerfa=taux_vo.type_cerfa,
            libelle_tva=taux_vo.libelle,
            message=message,
        )
