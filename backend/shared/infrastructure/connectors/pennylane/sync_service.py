"""Service de synchronisation periodique avec Pennylane.

CONN-10: Sync factures fournisseurs Pennylane.
CONN-11: Sync encaissements clients Pennylane.
CONN-12: Import fournisseurs Pennylane.
CONN-13: Matching intelligent.
"""

import logging
from dataclasses import dataclass
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import List, Optional, Tuple

from .api_client import (
    PennylaneApiClient,
    PennylaneSupplierInvoice,
    PennylaneCustomerInvoice,
    PennylaneSupplier,
    PennylaneApiError,
)

logger = logging.getLogger(__name__)


@dataclass
class SyncResult:
    """Resultat d'une synchronisation."""

    sync_type: str
    records_processed: int
    records_created: int
    records_updated: int
    records_pending: int
    errors: List[str]
    started_at: datetime
    completed_at: datetime

    @property
    def duration_seconds(self) -> float:
        """Duree de la synchronisation en secondes."""
        return (self.completed_at - self.started_at).total_seconds()

    @property
    def has_errors(self) -> bool:
        """Indique si des erreurs sont survenues."""
        return len(self.errors) > 0

    @property
    def success_rate(self) -> float:
        """Taux de succes (0-100)."""
        if self.records_processed == 0:
            return 100.0
        success = self.records_created + self.records_updated
        return (success / self.records_processed) * 100


@dataclass
class MatchResult:
    """Resultat d'un matching intelligent."""

    is_matched: bool
    achat_id: Optional[int] = None
    confidence: float = 0.0
    ecart_pct: Optional[float] = None
    reason: Optional[str] = None


class PennylaneSyncService:
    """Service de synchronisation periodique avec Pennylane.

    Responsabilites:
    - Synchroniser les factures fournisseurs payees (CONN-10)
    - Synchroniser les encaissements clients (CONN-11)
    - Synchroniser les fournisseurs (CONN-12)
    - Matching intelligent factures -> achats (CONN-13)

    Example:
        >>> sync_service = PennylaneSyncService(
        ...     api_client=client,
        ...     achat_repository=achat_repo,
        ...     fournisseur_repository=fournisseur_repo,
        ...     facture_repository=facture_repo,
        ...     sync_log_repository=sync_log_repo,
        ...     mapping_repository=mapping_repo,
        ...     pending_repository=pending_repo,
        ... )
        >>> result = await sync_service.sync_supplier_invoices()
        >>> print(f"Traite: {result.records_processed}, Cree: {result.records_created}")
    """

    # Configuration du matching
    MONTANT_TOLERANCE_PCT = 10.0  # Tolerance de +/- 10% sur le montant
    FENETRE_JOURS = 30  # Fenetre temporelle de 30 jours

    def __init__(
        self,
        api_client: PennylaneApiClient,
        achat_repository,  # AchatRepository
        fournisseur_repository,  # FournisseurRepository
        facture_repository,  # FactureClientRepository
        sync_log_repository,  # PennylaneSyncLogRepository
        mapping_repository,  # PennylaneMappingAnalytiqueRepository
        pending_repository,  # PennylanePendingReconciliationRepository
    ):
        """Initialise le service de synchronisation.

        Args:
            api_client: Client API Pennylane.
            achat_repository: Repository des achats.
            fournisseur_repository: Repository des fournisseurs.
            facture_repository: Repository des factures client.
            sync_log_repository: Repository des logs de sync.
            mapping_repository: Repository des mappings analytiques.
            pending_repository: Repository des reconciliations en attente.
        """
        self.api_client = api_client
        self.achat_repo = achat_repository
        self.fournisseur_repo = fournisseur_repository
        self.facture_repo = facture_repository
        self.sync_log_repo = sync_log_repository
        self.mapping_repo = mapping_repository
        self.pending_repo = pending_repository

    async def sync_supplier_invoices(
        self,
        updated_since: Optional[datetime] = None,
    ) -> SyncResult:
        """Synchronise les factures fournisseurs payees.

        CONN-10: Import factures fournisseurs payees depuis Pennylane.

        Workflow:
        1. Recuperer les factures payees depuis Pennylane
        2. Pour chaque facture non importee:
           a. Trouver/creer le fournisseur (par SIRET)
           b. Trouver le chantier (par code analytique)
           c. Matching intelligent avec achat existant
           d. Si match: mettre a jour l'achat
           e. Si pas de match: creer une reconciliation en attente

        Args:
            updated_since: Date de derniere synchronisation.

        Returns:
            Resultat de la synchronisation.
        """
        started_at = datetime.utcnow()
        errors: List[str] = []
        records_processed = 0
        records_created = 0
        records_updated = 0
        records_pending = 0

        try:
            # Recuperer les factures payees
            invoices = await self.api_client.get_all_supplier_invoices(
                is_paid=True,
                updated_since=updated_since,
            )

            logger.info(f"Pennylane: {len(invoices)} factures fournisseurs a traiter")

            for invoice in invoices:
                records_processed += 1

                try:
                    # Verifier si deja importee (idempotence)
                    existing_achat = self.achat_repo.find_by_pennylane_invoice_id(
                        invoice.id
                    )
                    if existing_achat:
                        logger.debug(f"Facture {invoice.id} deja importee -> skip")
                        continue

                    # Trouver/creer le fournisseur
                    fournisseur = await self._find_or_create_fournisseur(invoice)
                    if not fournisseur:
                        errors.append(
                            f"Fournisseur non trouve pour facture {invoice.id}"
                        )
                        records_pending += 1
                        await self._create_pending_reconciliation(invoice, None)
                        continue

                    # Trouver le chantier par code analytique
                    chantier_id = await self._find_chantier_by_code_analytique(
                        invoice.analytic_code
                    )
                    if not chantier_id:
                        logger.warning(
                            f"Code analytique inconnu: {invoice.analytic_code} "
                            f"pour facture {invoice.id}"
                        )
                        records_pending += 1
                        await self._create_pending_reconciliation(invoice, None)
                        continue

                    # Matching intelligent
                    match_result = self._find_matching_achat(
                        invoice=invoice,
                        fournisseur_id=fournisseur.id,
                        chantier_id=chantier_id,
                    )

                    if match_result.is_matched and match_result.achat_id:
                        # Mettre a jour l'achat existant
                        await self._update_achat_with_invoice(
                            achat_id=match_result.achat_id,
                            invoice=invoice,
                        )
                        records_updated += 1
                        logger.info(
                            f"Facture {invoice.id} matchee avec achat {match_result.achat_id} "
                            f"(confiance: {match_result.confidence:.0%})"
                        )
                    else:
                        # Creer une reconciliation en attente
                        await self._create_pending_reconciliation(
                            invoice=invoice,
                            suggested_achat_id=match_result.achat_id,
                        )
                        records_pending += 1
                        logger.info(
                            f"Facture {invoice.id} en attente de reconciliation: "
                            f"{match_result.reason}"
                        )

                except Exception as e:
                    error_msg = f"Erreur traitement facture {invoice.id}: {e}"
                    logger.error(error_msg)
                    errors.append(error_msg)

        except PennylaneApiError as e:
            error_msg = f"Erreur API Pennylane: {e.message}"
            logger.error(error_msg)
            errors.append(error_msg)

        completed_at = datetime.utcnow()

        return SyncResult(
            sync_type="supplier_invoices",
            records_processed=records_processed,
            records_created=records_created,
            records_updated=records_updated,
            records_pending=records_pending,
            errors=errors,
            started_at=started_at,
            completed_at=completed_at,
        )

    async def sync_customer_invoices(
        self,
        updated_since: Optional[datetime] = None,
    ) -> SyncResult:
        """Synchronise les encaissements clients.

        CONN-11: Import encaissements depuis Pennylane.

        Workflow:
        1. Recuperer les factures clients depuis Pennylane
        2. Pour chaque facture avec paiement:
           a. Trouver la facture Hub par numero
           b. Mettre a jour le montant encaisse et la date

        Args:
            updated_since: Date de derniere synchronisation.

        Returns:
            Resultat de la synchronisation.
        """
        started_at = datetime.utcnow()
        errors: List[str] = []
        records_processed = 0
        records_created = 0
        records_updated = 0
        records_pending = 0

        try:
            invoices = await self.api_client.get_all_customer_invoices(
                updated_since=updated_since,
            )

            logger.info(f"Pennylane: {len(invoices)} factures clients a traiter")

            for invoice in invoices:
                records_processed += 1

                try:
                    # Chercher la facture Hub par numero
                    facture = self.facture_repo.find_by_numero(invoice.invoice_number)
                    if not facture:
                        # Chercher par ID Pennylane
                        facture = self.facture_repo.find_by_pennylane_invoice_id(
                            invoice.id
                        )

                    if not facture:
                        logger.debug(
                            f"Facture client {invoice.invoice_number} non trouvee dans Hub"
                        )
                        continue

                    # Mettre a jour les encaissements si la facture est payee
                    if invoice.is_paid and invoice.paid_date:
                        facture.enregistrer_encaissement(
                            montant=invoice.amount_paid or invoice.amount_ttc,
                            date_paiement=invoice.paid_date.date(),
                        )
                        facture.pennylane_invoice_id = invoice.id
                        self.facture_repo.save(facture)
                        records_updated += 1
                        logger.info(
                            f"Encaissement enregistre pour facture {facture.numero_facture}"
                        )

                except Exception as e:
                    error_msg = f"Erreur traitement facture client {invoice.id}: {e}"
                    logger.error(error_msg)
                    errors.append(error_msg)

        except PennylaneApiError as e:
            error_msg = f"Erreur API Pennylane: {e.message}"
            logger.error(error_msg)
            errors.append(error_msg)

        completed_at = datetime.utcnow()

        return SyncResult(
            sync_type="customer_invoices",
            records_processed=records_processed,
            records_created=records_created,
            records_updated=records_updated,
            records_pending=records_pending,
            errors=errors,
            started_at=started_at,
            completed_at=completed_at,
        )

    async def sync_suppliers(self) -> SyncResult:
        """Synchronise les fournisseurs.

        CONN-12: Import fournisseurs depuis Pennylane.

        Workflow:
        1. Recuperer tous les fournisseurs Pennylane
        2. Pour chaque fournisseur:
           a. Chercher par SIRET ou ID Pennylane
           b. Creer ou mettre a jour

        Returns:
            Resultat de la synchronisation.
        """
        started_at = datetime.utcnow()
        errors: List[str] = []
        records_processed = 0
        records_created = 0
        records_updated = 0
        records_pending = 0

        try:
            suppliers = await self.api_client.get_all_suppliers()

            logger.info(f"Pennylane: {len(suppliers)} fournisseurs a traiter")

            for supplier in suppliers:
                records_processed += 1

                try:
                    # Chercher le fournisseur existant
                    fournisseur = None
                    if supplier.siret:
                        fournisseur = self.fournisseur_repo.find_by_siret(supplier.siret)
                    if not fournisseur:
                        fournisseur = self.fournisseur_repo.find_by_pennylane_id(
                            supplier.id
                        )

                    if fournisseur:
                        # Mettre a jour
                        fournisseur.pennylane_supplier_id = supplier.id
                        fournisseur.delai_paiement_jours = supplier.payment_delay_days
                        if supplier.iban:
                            fournisseur.iban = supplier.iban
                        if supplier.bic:
                            fournisseur.bic = supplier.bic
                        fournisseur.marquer_sync_pennylane()
                        self.fournisseur_repo.save(fournisseur)
                        records_updated += 1
                    else:
                        # Creer nouveau fournisseur
                        from modules.financier.domain.entities import Fournisseur
                        from modules.financier.domain.value_objects import TypeFournisseur

                        nouveau_fournisseur = Fournisseur(
                            raison_sociale=supplier.name,
                            type=TypeFournisseur.NEGOCE_MATERIAUX,  # Par defaut
                            siret=supplier.siret,
                            adresse=supplier.address,
                            email=supplier.email,
                            telephone=supplier.phone,
                            pennylane_supplier_id=supplier.id,
                            delai_paiement_jours=supplier.payment_delay_days,
                            iban=supplier.iban,
                            bic=supplier.bic,
                            source_donnee="PENNYLANE",
                            derniere_sync_pennylane=datetime.utcnow(),
                        )
                        self.fournisseur_repo.save(nouveau_fournisseur)
                        records_created += 1
                        logger.info(f"Fournisseur cree: {supplier.name}")

                except Exception as e:
                    error_msg = f"Erreur traitement fournisseur {supplier.id}: {e}"
                    logger.error(error_msg)
                    errors.append(error_msg)

        except PennylaneApiError as e:
            error_msg = f"Erreur API Pennylane: {e.message}"
            logger.error(error_msg)
            errors.append(error_msg)

        completed_at = datetime.utcnow()

        return SyncResult(
            sync_type="suppliers",
            records_processed=records_processed,
            records_created=records_created,
            records_updated=records_updated,
            records_pending=records_pending,
            errors=errors,
            started_at=started_at,
            completed_at=completed_at,
        )

    def _find_matching_achat(
        self,
        invoice: PennylaneSupplierInvoice,
        fournisseur_id: int,
        chantier_id: int,
    ) -> MatchResult:
        """Matching intelligent: trouve l'achat correspondant a une facture.

        CONN-13: Algorithme de matching:
        - Meme fournisseur + meme chantier
        - Montant dans tolerance +/- 10%
        - Statut COMMANDE ou LIVRE
        - Fenetre temporelle < 30 jours

        Args:
            invoice: Facture Pennylane a matcher.
            fournisseur_id: ID du fournisseur Hub.
            chantier_id: ID du chantier Hub.

        Returns:
            Resultat du matching avec confiance et ecart.
        """
        # Recuperer les achats candidats
        achats_candidats = self.achat_repo.find_for_matching(
            fournisseur_id=fournisseur_id,
            chantier_id=chantier_id,
            statuts=["commande", "livre"],
            sans_pennylane_id=True,  # Pas deja matche
        )

        if not achats_candidats:
            return MatchResult(
                is_matched=False,
                reason="Aucun achat candidat trouve (fournisseur + chantier + statut)",
            )

        best_match: Optional[Tuple[int, float, float]] = None  # (achat_id, confidence, ecart_pct)
        montant_facture = float(invoice.amount_ht)

        for achat in achats_candidats:
            montant_achat = float(achat.total_ht)

            # Calculer l'ecart en pourcentage
            if montant_achat == 0:
                continue

            ecart_pct = abs(montant_facture - montant_achat) / montant_achat * 100

            # Verifier la tolerance
            if ecart_pct > self.MONTANT_TOLERANCE_PCT:
                continue

            # Verifier la fenetre temporelle
            if invoice.invoice_date and achat.date_commande:
                delta_jours = abs((invoice.invoice_date.date() - achat.date_commande).days)
                if delta_jours > self.FENETRE_JOURS:
                    continue
            else:
                # Sans date, on accepte mais avec confiance reduite
                delta_jours = self.FENETRE_JOURS

            # Calculer la confiance
            # Plus l'ecart est faible et la date proche, plus la confiance est haute
            confiance_montant = 1 - (ecart_pct / self.MONTANT_TOLERANCE_PCT)
            confiance_date = 1 - (delta_jours / self.FENETRE_JOURS)
            confidence = (confiance_montant * 0.7 + confiance_date * 0.3)

            if best_match is None or confidence > best_match[1]:
                best_match = (achat.id, confidence, ecart_pct)

        if best_match:
            achat_id, confidence, ecart_pct = best_match

            # Si confiance > 80%, match automatique
            if confidence >= 0.8:
                return MatchResult(
                    is_matched=True,
                    achat_id=achat_id,
                    confidence=confidence,
                    ecart_pct=ecart_pct,
                    reason=f"Match auto (confiance {confidence:.0%}, ecart {ecart_pct:.1f}%)",
                )
            else:
                # Suggestion mais validation manuelle requise
                return MatchResult(
                    is_matched=False,
                    achat_id=achat_id,
                    confidence=confidence,
                    ecart_pct=ecart_pct,
                    reason=f"Match suggere mais confiance faible ({confidence:.0%})",
                )

        return MatchResult(
            is_matched=False,
            reason="Aucun achat dans la tolerance de montant/date",
        )

    async def _find_or_create_fournisseur(
        self,
        invoice: PennylaneSupplierInvoice,
    ):
        """Trouve ou cree le fournisseur correspondant a une facture.

        Args:
            invoice: Facture Pennylane.

        Returns:
            Le fournisseur ou None.
        """
        # Chercher par SIRET
        if invoice.supplier_siret:
            fournisseur = self.fournisseur_repo.find_by_siret(invoice.supplier_siret)
            if fournisseur:
                return fournisseur

        # Chercher par ID Pennylane
        if invoice.supplier_id:
            fournisseur = self.fournisseur_repo.find_by_pennylane_id(invoice.supplier_id)
            if fournisseur:
                return fournisseur

        # Pas de creation automatique si on ne connait pas le fournisseur
        # Ca sera gere par la reconciliation manuelle
        return None

    async def _find_chantier_by_code_analytique(
        self,
        code_analytique: Optional[str],
    ) -> Optional[int]:
        """Trouve le chantier par son code analytique.

        Args:
            code_analytique: Code analytique Pennylane.

        Returns:
            ID du chantier ou None.
        """
        if not code_analytique:
            return None

        mapping = self.mapping_repo.find_by_code_analytique(code_analytique)
        if mapping:
            return mapping.chantier_id

        return None

    async def _update_achat_with_invoice(
        self,
        achat_id: int,
        invoice: PennylaneSupplierInvoice,
    ) -> None:
        """Met a jour un achat avec les donnees de la facture Pennylane.

        Args:
            achat_id: ID de l'achat a mettre a jour.
            invoice: Facture Pennylane.
        """
        achat = self.achat_repo.find_by_id(achat_id)
        if not achat:
            return

        # Mettre a jour les champs Pennylane
        achat.montant_ht_reel = invoice.amount_ht
        achat.date_facture_reelle = (
            invoice.invoice_date.date() if invoice.invoice_date else None
        )
        achat.pennylane_invoice_id = invoice.id

        # Passer en statut FACTURE si pas deja fait
        from modules.financier.domain.value_objects import StatutAchat

        if achat.statut in (StatutAchat.COMMANDE, StatutAchat.LIVRE):
            achat.marquer_facture(invoice.invoice_number or f"PL-{invoice.id}")

        self.achat_repo.save(achat)

    async def _create_pending_reconciliation(
        self,
        invoice: PennylaneSupplierInvoice,
        suggested_achat_id: Optional[int],
    ) -> None:
        """Cree une reconciliation en attente.

        Args:
            invoice: Facture Pennylane.
            suggested_achat_id: ID de l'achat suggere (optionnel).
        """
        from modules.financier.domain.entities import PennylanePendingReconciliation

        # Verifier si deja en attente
        existing = self.pending_repo.find_by_pennylane_invoice_id(invoice.id)
        if existing:
            return

        pending = PennylanePendingReconciliation(
            pennylane_invoice_id=invoice.id,
            supplier_name=invoice.supplier_name,
            supplier_siret=invoice.supplier_siret,
            amount_ht=invoice.amount_ht,
            code_analytique=invoice.analytic_code,
            invoice_date=invoice.invoice_date.date() if invoice.invoice_date else None,
            suggested_achat_id=suggested_achat_id,
            created_at=datetime.utcnow(),
        )

        self.pending_repo.save(pending)
