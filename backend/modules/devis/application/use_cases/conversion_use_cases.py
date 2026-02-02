"""Use Cases pour la conversion devis -> chantier.

DEV-16: Conversion en chantier - Transformation automatique d'un devis
accepte et signe en chantier avec budget, lots et planning initial.

Architecture Clean : pas d'import cross-module. La conversion emet un
DevisConvertEvent que les modules chantier/financier consomment.
"""

from datetime import datetime
from typing import Callable, List, Optional

from ...domain.entities.devis import Devis, DevisValidationError
from ...domain.entities.journal_devis import JournalDevis
from ...domain.entities.lot_devis import LotDevis
from ...domain.events.devis_events import DevisConvertEvent, LotConversionData
from ...domain.repositories.devis_repository import DevisRepository
from ...domain.repositories.lot_devis_repository import LotDevisRepository
from ...domain.repositories.journal_devis_repository import JournalDevisRepository
from ...domain.repositories.signature_devis_repository import SignatureDevisRepository
from ...domain.value_objects import StatutDevis
from ..dtos.conversion_dtos import ConversionDevisDTO, ConversionInfoDTO


class ConversionDevisError(Exception):
    """Erreur lors de la conversion d'un devis en chantier."""

    def __init__(self, message: str = "Erreur lors de la conversion du devis"):
        self.message = message
        super().__init__(self.message)


class DevisNonConvertibleError(ConversionDevisError):
    """Le devis ne remplit pas les pre-requis pour la conversion."""

    pass


class DevisDejaConvertiError(ConversionDevisError):
    """Le devis a deja ete converti en chantier."""

    pass


class ConvertirDevisUseCase:
    """Cas d'utilisation : Convertir un devis accepte en chantier.

    DEV-16: Verifie les pre-requis (statut accepte, signature, non converti),
    prepare les donnees de conversion, emet un DevisConvertEvent et marque
    le devis comme converti.

    Le chantier_id est passe en parametre car il est genere par le module
    chantier (via l'event handler ou l'orchestrateur appelant).

    Attributes:
        _devis_repository: Repository pour acceder aux devis.
        _lot_repository: Repository pour acceder aux lots.
        _journal_repository: Repository pour le journal d'audit.
        _signature_repository: Repository pour verifier la signature.
        _event_publisher: Fonction pour publier les domain events.
    """

    def __init__(
        self,
        devis_repository: DevisRepository,
        lot_repository: LotDevisRepository,
        journal_repository: JournalDevisRepository,
        signature_repository: SignatureDevisRepository,
        event_publisher: Optional[Callable] = None,
    ):
        """Initialise le use case.

        Args:
            devis_repository: Repository devis (interface).
            lot_repository: Repository lots (interface).
            journal_repository: Repository journal (interface).
            signature_repository: Repository signatures (interface).
            event_publisher: Fonction pour publier les domain events.
        """
        self._devis_repository = devis_repository
        self._lot_repository = lot_repository
        self._journal_repository = journal_repository
        self._signature_repository = signature_repository
        self._event_publisher = event_publisher

    def execute(
        self,
        devis_id: int,
        converted_by: int,
        chantier_id: Optional[int] = None,
    ) -> ConversionDevisDTO:
        """Execute la conversion d'un devis en chantier.

        Args:
            devis_id: L'ID du devis a convertir.
            converted_by: L'ID de l'utilisateur effectuant la conversion.
            chantier_id: L'ID du chantier cree (optionnel, peut etre attribue
                         par l'event handler apres publication de l'event).

        Returns:
            ConversionDevisDTO contenant toutes les donnees de conversion.

        Raises:
            DevisNotFoundError: Si le devis n'existe pas.
            DevisNonConvertibleError: Si les pre-requis ne sont pas remplis.
            DevisDejaConvertiError: Si le devis a deja ete converti.
        """
        from .devis_use_cases import DevisNotFoundError

        # 1. Recuperer le devis
        devis = self._devis_repository.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        # 2. Verifier non deja converti
        if devis.est_converti:
            raise DevisDejaConvertiError(
                f"Le devis {devis.numero} a deja ete converti en chantier "
                f"(chantier_id={devis.converti_en_chantier_id})"
            )

        # 3. Verifier statut 'accepte'
        if devis.statut != StatutDevis.ACCEPTE:
            raise DevisNonConvertibleError(
                f"Le devis {devis.numero} doit etre en statut 'accepte' "
                f"pour etre converti (statut actuel: {devis.statut.label})"
            )

        # 4. Verifier signature existante
        signature = self._signature_repository.find_by_devis_id(devis_id)
        if not signature or not signature.valide:
            raise DevisNonConvertibleError(
                f"Le devis {devis.numero} doit etre signe par le client "
                f"avant la conversion en chantier"
            )

        # 5. Recuperer les lots du devis
        lots = self._lot_repository.find_by_devis(devis_id)

        # 6. Preparer la date de conversion
        date_conversion = datetime.utcnow()

        # 7. Emettre le DevisConvertEvent
        event = DevisConvertEvent(
            devis_id=devis.id,
            numero=devis.numero,
            client_nom=devis.client_nom,
            client_adresse=devis.client_adresse,
            client_email=devis.client_email,
            objet=devis.objet,
            montant_total_ht=devis.montant_total_ht,
            montant_total_ttc=devis.montant_total_ttc,
            retenue_garantie_pct=devis.retenue_garantie_pct,
            lots=[
                LotConversionData(
                    code_lot=lot.code_lot,
                    libelle=lot.libelle,
                    montant_debourse_ht=lot.montant_debourse_ht,
                    montant_vente_ht=lot.montant_vente_ht,
                )
                for lot in lots
                if not lot.est_supprime
            ],
            commercial_id=devis.commercial_id,
            conducteur_id=devis.conducteur_id,
            date_conversion=date_conversion,
        )

        if self._event_publisher:
            self._event_publisher(event)

        # 8. Marquer le devis comme converti
        if chantier_id is not None:
            devis.marquer_converti(chantier_id)
        else:
            # Marquer avec un ID temporaire (0) qui sera mis a jour
            # par l'event handler du module chantier
            devis.converti_en_chantier_id = 0
            devis.updated_at = datetime.utcnow()

        devis = self._devis_repository.save(devis)

        # 9. Journaliser
        self._journal_repository.save(
            JournalDevis(
                devis_id=devis_id,
                action="conversion_chantier",
                details_json={
                    "message": f"Devis {devis.numero} converti en chantier",
                    "chantier_id": chantier_id,
                    "montant_total_ht": str(devis.montant_total_ht),
                    "montant_total_ttc": str(devis.montant_total_ttc),
                    "retenue_garantie_pct": str(devis.retenue_garantie_pct),
                    "nb_lots": len([l for l in lots if not l.est_supprime]),
                },
                auteur_id=converted_by,
                created_at=date_conversion,
            )
        )

        # 10. Retourner le DTO de conversion
        return ConversionDevisDTO.from_entities(devis, lots, date_conversion)


class GetConversionInfoUseCase:
    """Cas d'utilisation : Verifier si la conversion est possible.

    DEV-16: Retourne les informations de pre-requis pour la conversion
    et indique les elements manquants.

    Attributes:
        _devis_repository: Repository pour acceder aux devis.
        _signature_repository: Repository pour verifier la signature.
    """

    def __init__(
        self,
        devis_repository: DevisRepository,
        signature_repository: SignatureDevisRepository,
    ):
        """Initialise le use case.

        Args:
            devis_repository: Repository devis (interface).
            signature_repository: Repository signatures (interface).
        """
        self._devis_repository = devis_repository
        self._signature_repository = signature_repository

    def execute(self, devis_id: int) -> ConversionInfoDTO:
        """Verifie les pre-requis de conversion pour un devis.

        Args:
            devis_id: L'ID du devis a verifier.

        Returns:
            ConversionInfoDTO indiquant si la conversion est possible
            et les pre-requis manquants.

        Raises:
            DevisNotFoundError: Si le devis n'existe pas.
        """
        from .devis_use_cases import DevisNotFoundError

        devis = self._devis_repository.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        pre_requis_manquants: List[str] = []

        # Verifier statut
        est_accepte = devis.statut == StatutDevis.ACCEPTE
        if not est_accepte:
            pre_requis_manquants.append(
                f"Le devis doit etre en statut 'accepte' "
                f"(statut actuel: {devis.statut.label})"
            )

        # Verifier signature
        signature = self._signature_repository.find_by_devis_id(devis_id)
        est_signe = signature is not None and signature.valide
        if not est_signe:
            pre_requis_manquants.append(
                "Le devis doit etre signe par le client"
            )

        # Verifier non deja converti
        deja_converti = devis.est_converti
        if deja_converti:
            pre_requis_manquants.append(
                f"Le devis a deja ete converti en chantier "
                f"(chantier_id={devis.converti_en_chantier_id})"
            )

        conversion_possible = (
            est_accepte
            and est_signe
            and not deja_converti
        )

        return ConversionInfoDTO(
            devis_id=devis.id,
            devis_numero=devis.numero,
            conversion_possible=conversion_possible,
            deja_converti=deja_converti,
            converti_en_chantier_id=devis.converti_en_chantier_id,
            statut_actuel=devis.statut.value,
            est_accepte=est_accepte,
            est_signe=est_signe,
            pre_requis_manquants=pre_requis_manquants,
        )
