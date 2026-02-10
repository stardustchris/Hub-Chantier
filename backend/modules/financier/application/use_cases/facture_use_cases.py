"""Use Cases pour la gestion des factures client.

FIN-08: Facturation client - Creation, emission, envoi, paiement, annulation.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from ..ports.event_bus import EventBus

from ...domain.entities.facture_client import FactureClient
from ...domain.repositories.facture_repository import FactureRepository
from ...domain.repositories.situation_repository import SituationRepository
from ...domain.repositories import (
    JournalFinancierRepository,
    JournalEntry,
)
from ...domain.events import (
    FactureCreatedEvent,
    FactureEmiseEvent,
    FacturePayeeEvent,
)
from ..dtos.facture_dtos import FactureCreateDTO, FactureUpdateDTO, FactureDTO


class FactureNotFoundError(Exception):
    """Erreur levee quand une facture n'est pas trouvee."""

    def __init__(self, facture_id: int):
        self.facture_id = facture_id
        super().__init__(f"Facture {facture_id} non trouvee")


class FactureWorkflowError(Exception):
    """Erreur levee lors d'une transition de workflow invalide."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class SituationNonValideeError(Exception):
    """Erreur levee quand une situation n'est pas dans un statut valide pour facturation."""

    def __init__(self, situation_id: int):
        self.situation_id = situation_id
        super().__init__(
            f"La situation {situation_id} n'est pas validee pour facturation"
        )


def _generer_numero_facture(facture_repository: FactureRepository) -> str:
    """Genere un numero de facture atomique FAC-YYYY-NNNN.

    Utilise le repository pour obtenir le prochain numero de maniere atomique
    (SELECT FOR UPDATE ou equivalent) afin d'eviter les doublons en cas
    d'acces concurrent.

    Args:
        facture_repository: Le repository des factures.

    Returns:
        Le numero de facture genere.
    """
    year = datetime.utcnow().year
    next_num = facture_repository.next_numero_facture(year)
    return f"FAC-{year}-{next_num:04d}"


class CreateFactureFromSituationUseCase:
    """Use case pour creer une facture a partir d'une situation validee.

    FIN-08: Cree une facture de type 'situation' en copiant les montants.
    """

    def __init__(
        self,
        facture_repository: FactureRepository,
        situation_repository: SituationRepository,
        journal_repository: JournalFinancierRepository,
        event_bus: EventBus,
    ):
        self._facture_repository = facture_repository
        self._situation_repository = situation_repository
        self._journal_repository = journal_repository
        self._event_bus = event_bus

    def execute(self, situation_id: int, created_by: int) -> FactureDTO:
        """Cree une facture a partir d'une situation validee.

        Args:
            situation_id: L'ID de la situation source.
            created_by: L'ID de l'utilisateur createur.

        Returns:
            Le DTO de la facture creee.

        Raises:
            ValueError: Si la situation n'existe pas.
            SituationNonValideeError: Si la situation n'est pas validee.
        """
        situation = self._situation_repository.find_by_id(situation_id)
        if not situation:
            raise ValueError(f"Situation {situation_id} non trouvee")

        if situation.statut != "validee":
            raise SituationNonValideeError(situation_id)

        # Generer numero
        numero = _generer_numero_facture(self._facture_repository)

        # Calculer les montants depuis la situation
        montant_ht = situation.montant_cumule_ht
        montant_tva, montant_ttc, retenue_montant, montant_net = (
            FactureClient.calculer_montants(
                montant_ht,
                situation.taux_tva,
                situation.retenue_garantie_pct,
            )
        )

        # Creer la facture
        facture = FactureClient(
            chantier_id=situation.chantier_id,
            situation_id=situation_id,
            numero_facture=numero,
            type_facture="situation",
            montant_ht=montant_ht,
            taux_tva=situation.taux_tva,
            montant_tva=montant_tva,
            montant_ttc=montant_ttc,
            retenue_garantie_montant=retenue_montant,
            montant_net=montant_net,
            statut="brouillon",
            created_by=created_by,
            created_at=datetime.utcnow(),
        )

        facture = self._facture_repository.save(facture)

        # Journal
        self._journal_repository.save(
            JournalEntry(
                entite_type="facture",
                entite_id=facture.id,
                chantier_id=facture.chantier_id,
                action="creation",
                details=(
                    f"Creation facture {facture.numero_facture} "
                    f"depuis situation {situation.numero} - "
                    f"Montant TTC: {facture.montant_ttc} EUR"
                ),
                auteur_id=created_by,
                created_at=datetime.utcnow(),
            )
        )

        # Event
        self._event_bus.publish(
            FactureCreatedEvent(
                facture_id=facture.id,
                chantier_id=facture.chantier_id,
                numero_facture=facture.numero_facture,
                type_facture=facture.type_facture,
                montant_ttc=facture.montant_ttc,
                created_by=created_by,
            )
        )

        return FactureDTO.from_entity(facture)


class CreateFactureAcompteUseCase:
    """Use case pour creer une facture d'acompte (sans situation).

    FIN-08: Facture d'acompte avec montant HT manuel.
    """

    def __init__(
        self,
        facture_repository: FactureRepository,
        journal_repository: JournalFinancierRepository,
        event_bus: EventBus,
    ):
        self._facture_repository = facture_repository
        self._journal_repository = journal_repository
        self._event_bus = event_bus

    def execute(self, dto: FactureCreateDTO, created_by: int) -> FactureDTO:
        """Cree une facture d'acompte.

        Args:
            dto: Les donnees de la facture.
            created_by: L'ID de l'utilisateur createur.

        Returns:
            Le DTO de la facture creee.
        """
        # Generer numero
        numero = _generer_numero_facture(self._facture_repository)

        # Calculer les montants
        montant_tva, montant_ttc, retenue_montant, montant_net = (
            FactureClient.calculer_montants(
                dto.montant_ht,
                dto.taux_tva,
                dto.retenue_garantie_pct,
            )
        )

        # Creer la facture
        facture = FactureClient(
            chantier_id=dto.chantier_id,
            situation_id=None,
            numero_facture=numero,
            type_facture=dto.type_facture,
            montant_ht=dto.montant_ht,
            taux_tva=dto.taux_tva,
            montant_tva=montant_tva,
            montant_ttc=montant_ttc,
            retenue_garantie_montant=retenue_montant,
            montant_net=montant_net,
            statut="brouillon",
            notes=dto.notes,
            created_by=created_by,
            created_at=datetime.utcnow(),
        )

        facture = self._facture_repository.save(facture)

        # Journal
        self._journal_repository.save(
            JournalEntry(
                entite_type="facture",
                entite_id=facture.id,
                chantier_id=facture.chantier_id,
                action="creation",
                details=(
                    f"Creation facture acompte {facture.numero_facture} - "
                    f"Montant TTC: {facture.montant_ttc} EUR"
                ),
                auteur_id=created_by,
                created_at=datetime.utcnow(),
            )
        )

        # Event
        self._event_bus.publish(
            FactureCreatedEvent(
                facture_id=facture.id,
                chantier_id=facture.chantier_id,
                numero_facture=facture.numero_facture,
                type_facture=facture.type_facture,
                montant_ttc=facture.montant_ttc,
                created_by=created_by,
            )
        )

        return FactureDTO.from_entity(facture)


class EmettreFactureUseCase:
    """Use case pour emettre une facture (brouillon -> emise)."""

    def __init__(
        self,
        facture_repository: FactureRepository,
        journal_repository: JournalFinancierRepository,
        event_bus: EventBus,
    ):
        self._facture_repository = facture_repository
        self._journal_repository = journal_repository
        self._event_bus = event_bus

    def execute(self, facture_id: int, emis_par: int) -> FactureDTO:
        """Emet une facture.

        Args:
            facture_id: L'ID de la facture.
            emis_par: L'ID de l'utilisateur qui emet.

        Returns:
            Le DTO de la facture emise.

        Raises:
            FactureNotFoundError: Si la facture n'existe pas.
            FactureWorkflowError: Si la transition est invalide.
        """
        facture = self._facture_repository.find_by_id(facture_id)
        if not facture:
            raise FactureNotFoundError(facture_id)

        try:
            facture.emettre()
        except ValueError as e:
            raise FactureWorkflowError(str(e))

        facture = self._facture_repository.save(facture)

        # Journal
        self._journal_repository.save(
            JournalEntry(
                entite_type="facture",
                entite_id=facture.id,
                chantier_id=facture.chantier_id,
                action="emission",
                details=(
                    f"Emission facture {facture.numero_facture} - "
                    f"Date emission: {facture.date_emission}"
                ),
                auteur_id=emis_par,
                created_at=datetime.utcnow(),
            )
        )

        # Event
        self._event_bus.publish(
            FactureEmiseEvent(
                facture_id=facture.id,
                chantier_id=facture.chantier_id,
                numero_facture=facture.numero_facture,
                montant_ttc=facture.montant_ttc,
            )
        )

        return FactureDTO.from_entity(facture)


class EnvoyerFactureUseCase:
    """Use case pour envoyer une facture (emise -> envoyee)."""

    def __init__(
        self,
        facture_repository: FactureRepository,
        journal_repository: JournalFinancierRepository,
    ):
        self._facture_repository = facture_repository
        self._journal_repository = journal_repository

    def execute(self, facture_id: int, envoye_par: int) -> FactureDTO:
        """Envoie une facture au client.

        Args:
            facture_id: L'ID de la facture.
            envoye_par: L'ID de l'utilisateur qui envoie.

        Returns:
            Le DTO de la facture envoyee.

        Raises:
            FactureNotFoundError: Si la facture n'existe pas.
            FactureWorkflowError: Si la transition est invalide.
        """
        facture = self._facture_repository.find_by_id(facture_id)
        if not facture:
            raise FactureNotFoundError(facture_id)

        try:
            facture.envoyer()
        except ValueError as e:
            raise FactureWorkflowError(str(e))

        facture = self._facture_repository.save(facture)

        # Journal
        self._journal_repository.save(
            JournalEntry(
                entite_type="facture",
                entite_id=facture.id,
                chantier_id=facture.chantier_id,
                action="modification",
                details=f"Envoi facture {facture.numero_facture} au client",
                auteur_id=envoye_par,
                created_at=datetime.utcnow(),
            )
        )

        return FactureDTO.from_entity(facture)


class MarquerPayeeFactureUseCase:
    """Use case pour marquer une facture comme payee (envoyee -> payee).

    Marque egalement la situation associee comme facturee.
    """

    def __init__(
        self,
        facture_repository: FactureRepository,
        situation_repository: SituationRepository,
        journal_repository: JournalFinancierRepository,
        event_bus: EventBus,
    ):
        self._facture_repository = facture_repository
        self._situation_repository = situation_repository
        self._journal_repository = journal_repository
        self._event_bus = event_bus

    def execute(self, facture_id: int, paye_par: int) -> FactureDTO:
        """Marque une facture comme payee.

        Args:
            facture_id: L'ID de la facture.
            paye_par: L'ID de l'utilisateur qui marque le paiement.

        Returns:
            Le DTO de la facture payee.

        Raises:
            FactureNotFoundError: Si la facture n'existe pas.
            FactureWorkflowError: Si la transition est invalide.
        """
        facture = self._facture_repository.find_by_id(facture_id)
        if not facture:
            raise FactureNotFoundError(facture_id)

        try:
            facture.marquer_payee()
        except ValueError as e:
            raise FactureWorkflowError(str(e))

        facture = self._facture_repository.save(facture)

        # Si la facture est liee a une situation, la marquer comme facturee
        if facture.situation_id:
            situation = self._situation_repository.find_by_id(
                facture.situation_id
            )
            if situation and situation.statut == "validee":
                situation.marquer_facturee()
                self._situation_repository.save(situation)

        # Journal
        self._journal_repository.save(
            JournalEntry(
                entite_type="facture",
                entite_id=facture.id,
                chantier_id=facture.chantier_id,
                action="facturation",
                details=(
                    f"Paiement facture {facture.numero_facture} - "
                    f"Montant TTC: {facture.montant_ttc} EUR"
                ),
                auteur_id=paye_par,
                created_at=datetime.utcnow(),
            )
        )

        # Event
        self._event_bus.publish(
            FacturePayeeEvent(
                facture_id=facture.id,
                chantier_id=facture.chantier_id,
                numero_facture=facture.numero_facture,
                montant_ttc=facture.montant_ttc,
            )
        )

        return FactureDTO.from_entity(facture)


class AnnulerFactureUseCase:
    """Use case pour annuler une facture (brouillon/emise -> annulee)."""

    def __init__(
        self,
        facture_repository: FactureRepository,
        journal_repository: JournalFinancierRepository,
    ):
        self._facture_repository = facture_repository
        self._journal_repository = journal_repository

    def execute(self, facture_id: int, annule_par: int) -> FactureDTO:
        """Annule une facture.

        Args:
            facture_id: L'ID de la facture.
            annule_par: L'ID de l'utilisateur qui annule.

        Returns:
            Le DTO de la facture annulee.

        Raises:
            FactureNotFoundError: Si la facture n'existe pas.
            FactureWorkflowError: Si la transition est invalide.
        """
        facture = self._facture_repository.find_by_id(facture_id)
        if not facture:
            raise FactureNotFoundError(facture_id)

        try:
            facture.annuler()
        except ValueError as e:
            raise FactureWorkflowError(str(e))

        facture = self._facture_repository.save(facture)

        # Journal
        self._journal_repository.save(
            JournalEntry(
                entite_type="facture",
                entite_id=facture.id,
                chantier_id=facture.chantier_id,
                action="suppression",
                details=f"Annulation facture {facture.numero_facture}",
                auteur_id=annule_par,
                created_at=datetime.utcnow(),
            )
        )

        return FactureDTO.from_entity(facture)


class GetFactureUseCase:
    """Use case pour recuperer une facture."""

    def __init__(self, facture_repository: FactureRepository):
        self._facture_repository = facture_repository

    def execute(self, facture_id: int) -> FactureDTO:
        """Recupere une facture par son ID.

        Args:
            facture_id: L'ID de la facture.

        Returns:
            Le DTO de la facture.

        Raises:
            FactureNotFoundError: Si la facture n'existe pas.
        """
        facture = self._facture_repository.find_by_id(facture_id)
        if not facture:
            raise FactureNotFoundError(facture_id)

        return FactureDTO.from_entity(facture)


class ListFacturesUseCase:
    """Use case pour lister les factures d'un chantier."""

    def __init__(self, facture_repository: FactureRepository):
        self._facture_repository = facture_repository

    def execute(self, chantier_id: int) -> List[FactureDTO]:
        """Liste les factures d'un chantier.

        Args:
            chantier_id: L'ID du chantier.

        Returns:
            Liste des DTOs de factures.
        """
        factures = self._facture_repository.find_by_chantier_id(chantier_id)
        return [FactureDTO.from_entity(f) for f in factures]
