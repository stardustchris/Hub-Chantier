"""Dependency injection pour le module Devis.

Fournit les factories FastAPI pour les repositories et use cases.

DEV-08: Ajout des factories pour les use cases de versioning.
DEV-11: Ajout des factories pour les use cases de presentation.
DEV-14: Ajout des factories pour les use cases de signature electronique.
DEV-23: Ajout des factories pour les use cases d'attestation TVA.
DEV-24: Ajout des factories pour les use cases de relances automatiques.
DEV-25: Ajout des factories pour les use cases de frais de chantier.
"""

from fastapi import Depends
from sqlalchemy.orm import Session

from shared.infrastructure.database import get_db

from ...domain.repositories.devis_repository import DevisRepository
from ...domain.repositories.lot_devis_repository import LotDevisRepository
from ...domain.repositories.ligne_devis_repository import LigneDevisRepository
from ...domain.repositories.debourse_detail_repository import DebourseDetailRepository
from ...domain.repositories.article_repository import ArticleRepository
from ...domain.repositories.journal_devis_repository import JournalDevisRepository
from ...domain.repositories.comparatif_repository import ComparatifRepository
from ...domain.repositories.attestation_tva_repository import AttestationTVARepository
from ...domain.repositories.frais_chantier_repository import FraisChantierRepository
from ...domain.repositories.signature_devis_repository import SignatureDevisRepository
from ...domain.repositories.relance_devis_repository import RelanceDevisRepository

from ...application.use_cases.devis_use_cases import (
    CreateDevisUseCase,
    UpdateDevisUseCase,
    GetDevisUseCase,
    ListDevisUseCase,
    DeleteDevisUseCase,
)
from ...application.use_cases.workflow_use_cases import (
    SoumettreDevisUseCase,
    ValiderDevisUseCase,
    RetournerBrouillonUseCase,
    MarquerVuUseCase,
    PasserEnNegociationUseCase,
    AccepterDevisUseCase,
    RefuserDevisUseCase,
    PerduDevisUseCase,
    MarquerExpireUseCase,
)
from ...application.use_cases.search_use_cases import SearchDevisUseCase
from ...application.use_cases.dashboard_use_cases import GetDashboardDevisUseCase
from ...application.use_cases.lot_use_cases import (
    CreateLotDevisUseCase,
    UpdateLotDevisUseCase,
    DeleteLotDevisUseCase,
    ReorderLotsUseCase,
)
from ...application.use_cases.ligne_use_cases import (
    CreateLigneDevisUseCase,
    UpdateLigneDevisUseCase,
    DeleteLigneDevisUseCase,
)
from ...application.use_cases.calcul_totaux_use_cases import CalculerTotauxDevisUseCase
from ...application.use_cases.journal_use_cases import GetJournalDevisUseCase
from ...application.use_cases.version_use_cases import (
    CreerRevisionUseCase,
    CreerVarianteUseCase,
    ListerVersionsUseCase,
    GenererComparatifUseCase,
    GetComparatifUseCase,
    FigerVersionUseCase,
)
from ...application.use_cases.article_use_cases import (
    CreateArticleUseCase,
    UpdateArticleUseCase,
    ListArticlesUseCase,
    GetArticleUseCase,
    DeleteArticleUseCase,
)
from ...application.use_cases.attestation_tva_use_cases import (
    GenererAttestationTVAUseCase,
    GetAttestationTVAUseCase,
    VerifierEligibiliteTVAUseCase,
)
from ...application.use_cases.frais_chantier_use_cases import (
    CreateFraisChantierUseCase,
    UpdateFraisChantierUseCase,
    DeleteFraisChantierUseCase,
    ListFraisChantierUseCase,
    CalculerRepartitionFraisUseCase,
)
from ...application.use_cases.presentation_use_cases import (
    UpdateOptionsPresentationUseCase,
    GetOptionsPresentationUseCase,
    ListTemplatesPresentationUseCase,
)
from ...application.use_cases.signature_use_cases import (
    SignerDevisUseCase,
    GetSignatureUseCase,
    RevoquerSignatureUseCase,
    VerifierSignatureUseCase,
)
from ...application.use_cases.relance_use_cases import (
    PlanifierRelancesUseCase,
    ExecuterRelancesUseCase,
    AnnulerRelancesUseCase,
    GetRelancesDevisUseCase,
    UpdateConfigRelancesUseCase,
)
from ...application.use_cases.conversion_use_cases import (
    ConvertirDevisUseCase,
    GetConversionInfoUseCase,
)

from ...application.use_cases.convertir_devis_en_chantier_use_case import (
    ConvertirDevisEnChantierUseCase,
)

from ..persistence.sqlalchemy_devis_repository import SQLAlchemyDevisRepository
from ..persistence.sqlalchemy_lot_devis_repository import SQLAlchemyLotDevisRepository
from ..persistence.sqlalchemy_ligne_devis_repository import SQLAlchemyLigneDevisRepository
from ..persistence.sqlalchemy_debourse_detail_repository import SQLAlchemyDebourseDetailRepository
from ..persistence.sqlalchemy_article_repository import SQLAlchemyArticleRepository
from ..persistence.sqlalchemy_journal_devis_repository import SQLAlchemyJournalDevisRepository
from ..persistence.sqlalchemy_comparatif_repository import SQLAlchemyComparatifRepository
from ..persistence.sqlalchemy_attestation_tva_repository import SQLAlchemyAttestationTVARepository
from ..persistence.sqlalchemy_frais_chantier_repository import SQLAlchemyFraisChantierRepository
from ..persistence.sqlalchemy_signature_devis_repository import SQLAlchemySignatureDevisRepository
from ..persistence.sqlalchemy_relance_devis_repository import SQLAlchemyRelanceDevisRepository


# ─────────────────────────────────────────────────────────────────────────────
# Repositories
# ─────────────────────────────────────────────────────────────────────────────

def get_devis_repository(db: Session = Depends(get_db)) -> DevisRepository:
    return SQLAlchemyDevisRepository(db)


def get_lot_devis_repository(db: Session = Depends(get_db)) -> LotDevisRepository:
    return SQLAlchemyLotDevisRepository(db)


def get_ligne_devis_repository(db: Session = Depends(get_db)) -> LigneDevisRepository:
    return SQLAlchemyLigneDevisRepository(db)


def get_debourse_detail_repository(db: Session = Depends(get_db)) -> DebourseDetailRepository:
    return SQLAlchemyDebourseDetailRepository(db)


def get_article_repository(db: Session = Depends(get_db)) -> ArticleRepository:
    return SQLAlchemyArticleRepository(db)


def get_journal_devis_repository(db: Session = Depends(get_db)) -> JournalDevisRepository:
    return SQLAlchemyJournalDevisRepository(db)


def get_comparatif_repository(db: Session = Depends(get_db)) -> ComparatifRepository:
    return SQLAlchemyComparatifRepository(db)


def get_attestation_tva_repository(db: Session = Depends(get_db)) -> AttestationTVARepository:
    return SQLAlchemyAttestationTVARepository(db)


def get_frais_chantier_repository(db: Session = Depends(get_db)) -> FraisChantierRepository:
    return SQLAlchemyFraisChantierRepository(db)


def get_signature_devis_repository(db: Session = Depends(get_db)) -> SignatureDevisRepository:
    return SQLAlchemySignatureDevisRepository(db)


def get_relance_devis_repository(db: Session = Depends(get_db)) -> RelanceDevisRepository:
    return SQLAlchemyRelanceDevisRepository(db)


# ─────────────────────────────────────────────────────────────────────────────
# Use Cases - Devis CRUD
# ─────────────────────────────────────────────────────────────────────────────

def get_create_devis_use_case(
    devis_repo: DevisRepository = Depends(get_devis_repository),
    journal_repo: JournalDevisRepository = Depends(get_journal_devis_repository),
) -> CreateDevisUseCase:
    return CreateDevisUseCase(devis_repo, journal_repo)


def get_update_devis_use_case(
    devis_repo: DevisRepository = Depends(get_devis_repository),
    journal_repo: JournalDevisRepository = Depends(get_journal_devis_repository),
) -> UpdateDevisUseCase:
    return UpdateDevisUseCase(devis_repo, journal_repo)


def get_get_devis_use_case(
    devis_repo: DevisRepository = Depends(get_devis_repository),
    lot_repo: LotDevisRepository = Depends(get_lot_devis_repository),
    ligne_repo: LigneDevisRepository = Depends(get_ligne_devis_repository),
    debourse_repo: DebourseDetailRepository = Depends(get_debourse_detail_repository),
) -> GetDevisUseCase:
    return GetDevisUseCase(devis_repo, lot_repo, ligne_repo, debourse_repo)


def get_list_devis_use_case(
    devis_repo: DevisRepository = Depends(get_devis_repository),
) -> ListDevisUseCase:
    return ListDevisUseCase(devis_repo)


def get_delete_devis_use_case(
    devis_repo: DevisRepository = Depends(get_devis_repository),
    journal_repo: JournalDevisRepository = Depends(get_journal_devis_repository),
) -> DeleteDevisUseCase:
    return DeleteDevisUseCase(devis_repo, journal_repo)


# ─────────────────────────────────────────────────────────────────────────────
# Use Cases - Workflow
# ─────────────────────────────────────────────────────────────────────────────

def get_soumettre_devis_use_case(
    devis_repo: DevisRepository = Depends(get_devis_repository),
    journal_repo: JournalDevisRepository = Depends(get_journal_devis_repository),
) -> SoumettreDevisUseCase:
    return SoumettreDevisUseCase(devis_repo, journal_repo)


def get_valider_devis_use_case(
    devis_repo: DevisRepository = Depends(get_devis_repository),
    journal_repo: JournalDevisRepository = Depends(get_journal_devis_repository),
) -> ValiderDevisUseCase:
    return ValiderDevisUseCase(devis_repo, journal_repo)


def get_retourner_brouillon_use_case(
    devis_repo: DevisRepository = Depends(get_devis_repository),
    journal_repo: JournalDevisRepository = Depends(get_journal_devis_repository),
) -> RetournerBrouillonUseCase:
    return RetournerBrouillonUseCase(devis_repo, journal_repo)


def get_accepter_devis_use_case(
    devis_repo: DevisRepository = Depends(get_devis_repository),
    journal_repo: JournalDevisRepository = Depends(get_journal_devis_repository),
) -> AccepterDevisUseCase:
    return AccepterDevisUseCase(devis_repo, journal_repo)


def get_refuser_devis_use_case(
    devis_repo: DevisRepository = Depends(get_devis_repository),
    journal_repo: JournalDevisRepository = Depends(get_journal_devis_repository),
) -> RefuserDevisUseCase:
    return RefuserDevisUseCase(devis_repo, journal_repo)


def get_perdu_devis_use_case(
    devis_repo: DevisRepository = Depends(get_devis_repository),
    journal_repo: JournalDevisRepository = Depends(get_journal_devis_repository),
) -> PerduDevisUseCase:
    return PerduDevisUseCase(devis_repo, journal_repo)


def get_marquer_vu_use_case(
    devis_repo: DevisRepository = Depends(get_devis_repository),
    journal_repo: JournalDevisRepository = Depends(get_journal_devis_repository),
) -> MarquerVuUseCase:
    return MarquerVuUseCase(devis_repo, journal_repo)


def get_passer_en_negociation_use_case(
    devis_repo: DevisRepository = Depends(get_devis_repository),
    journal_repo: JournalDevisRepository = Depends(get_journal_devis_repository),
) -> PasserEnNegociationUseCase:
    return PasserEnNegociationUseCase(devis_repo, journal_repo)


def get_marquer_expire_use_case(
    devis_repo: DevisRepository = Depends(get_devis_repository),
    journal_repo: JournalDevisRepository = Depends(get_journal_devis_repository),
) -> MarquerExpireUseCase:
    return MarquerExpireUseCase(devis_repo, journal_repo)


def get_reorder_lots_use_case(
    lot_repo: LotDevisRepository = Depends(get_lot_devis_repository),
    journal_repo: JournalDevisRepository = Depends(get_journal_devis_repository),
) -> ReorderLotsUseCase:
    return ReorderLotsUseCase(lot_repo, journal_repo)


def get_update_article_use_case(
    article_repo: ArticleRepository = Depends(get_article_repository),
    journal_repo: JournalDevisRepository = Depends(get_journal_devis_repository),
) -> UpdateArticleUseCase:
    return UpdateArticleUseCase(article_repo, journal_repo)


# ─────────────────────────────────────────────────────────────────────────────
# Use Cases - Search & Dashboard
# ─────────────────────────────────────────────────────────────────────────────

def get_search_devis_use_case(
    devis_repo: DevisRepository = Depends(get_devis_repository),
) -> SearchDevisUseCase:
    return SearchDevisUseCase(devis_repo)


def get_dashboard_devis_use_case(
    devis_repo: DevisRepository = Depends(get_devis_repository),
) -> GetDashboardDevisUseCase:
    return GetDashboardDevisUseCase(devis_repo)


# ─────────────────────────────────────────────────────────────────────────────
# Use Cases - Lots
# ─────────────────────────────────────────────────────────────────────────────

def get_create_lot_use_case(
    lot_repo: LotDevisRepository = Depends(get_lot_devis_repository),
    devis_repo: DevisRepository = Depends(get_devis_repository),
    journal_repo: JournalDevisRepository = Depends(get_journal_devis_repository),
) -> CreateLotDevisUseCase:
    return CreateLotDevisUseCase(lot_repo, devis_repo, journal_repo)


def get_update_lot_use_case(
    lot_repo: LotDevisRepository = Depends(get_lot_devis_repository),
    journal_repo: JournalDevisRepository = Depends(get_journal_devis_repository),
) -> UpdateLotDevisUseCase:
    return UpdateLotDevisUseCase(lot_repo, journal_repo)


def get_delete_lot_use_case(
    lot_repo: LotDevisRepository = Depends(get_lot_devis_repository),
    journal_repo: JournalDevisRepository = Depends(get_journal_devis_repository),
) -> DeleteLotDevisUseCase:
    return DeleteLotDevisUseCase(lot_repo, journal_repo)


# ─────────────────────────────────────────────────────────────────────────────
# Use Cases - Lignes
# ─────────────────────────────────────────────────────────────────────────────

def get_create_ligne_use_case(
    ligne_repo: LigneDevisRepository = Depends(get_ligne_devis_repository),
    lot_repo: LotDevisRepository = Depends(get_lot_devis_repository),
    debourse_repo: DebourseDetailRepository = Depends(get_debourse_detail_repository),
    journal_repo: JournalDevisRepository = Depends(get_journal_devis_repository),
) -> CreateLigneDevisUseCase:
    return CreateLigneDevisUseCase(ligne_repo, lot_repo, debourse_repo, journal_repo)


def get_update_ligne_use_case(
    ligne_repo: LigneDevisRepository = Depends(get_ligne_devis_repository),
    debourse_repo: DebourseDetailRepository = Depends(get_debourse_detail_repository),
    journal_repo: JournalDevisRepository = Depends(get_journal_devis_repository),
    lot_repo: LotDevisRepository = Depends(get_lot_devis_repository),
) -> UpdateLigneDevisUseCase:
    return UpdateLigneDevisUseCase(ligne_repo, debourse_repo, journal_repo, lot_repo)


def get_delete_ligne_use_case(
    ligne_repo: LigneDevisRepository = Depends(get_ligne_devis_repository),
    debourse_repo: DebourseDetailRepository = Depends(get_debourse_detail_repository),
    journal_repo: JournalDevisRepository = Depends(get_journal_devis_repository),
    lot_repo: LotDevisRepository = Depends(get_lot_devis_repository),
) -> DeleteLigneDevisUseCase:
    return DeleteLigneDevisUseCase(ligne_repo, debourse_repo, journal_repo, lot_repo)


# ─────────────────────────────────────────────────────────────────────────────
# Use Cases - Calcul & Journal & Articles
# ─────────────────────────────────────────────────────────────────────────────

def get_calculer_totaux_use_case(
    devis_repo: DevisRepository = Depends(get_devis_repository),
    lot_repo: LotDevisRepository = Depends(get_lot_devis_repository),
    ligne_repo: LigneDevisRepository = Depends(get_ligne_devis_repository),
    debourse_repo: DebourseDetailRepository = Depends(get_debourse_detail_repository),
    journal_repo: JournalDevisRepository = Depends(get_journal_devis_repository),
    frais_chantier_repo: FraisChantierRepository = Depends(get_frais_chantier_repository),
) -> CalculerTotauxDevisUseCase:
    return CalculerTotauxDevisUseCase(
        devis_repo, lot_repo, ligne_repo, debourse_repo, journal_repo, frais_chantier_repo
    )


def get_journal_devis_use_case(
    journal_repo: JournalDevisRepository = Depends(get_journal_devis_repository),
) -> GetJournalDevisUseCase:
    return GetJournalDevisUseCase(journal_repo)


def get_create_article_use_case(
    article_repo: ArticleRepository = Depends(get_article_repository),
    journal_repo: JournalDevisRepository = Depends(get_journal_devis_repository),
) -> CreateArticleUseCase:
    return CreateArticleUseCase(article_repo, journal_repo)


def get_list_articles_use_case(
    article_repo: ArticleRepository = Depends(get_article_repository),
) -> ListArticlesUseCase:
    return ListArticlesUseCase(article_repo)


def get_get_article_use_case(
    article_repo: ArticleRepository = Depends(get_article_repository),
) -> GetArticleUseCase:
    return GetArticleUseCase(article_repo)


def get_delete_article_use_case(
    article_repo: ArticleRepository = Depends(get_article_repository),
    journal_repo: JournalDevisRepository = Depends(get_journal_devis_repository),
) -> DeleteArticleUseCase:
    return DeleteArticleUseCase(article_repo, journal_repo)


# ─────────────────────────────────────────────────────────────────────────────
# Use Cases - Versioning (DEV-08)
# ─────────────────────────────────────────────────────────────────────────────

def get_creer_revision_use_case(
    devis_repo: DevisRepository = Depends(get_devis_repository),
    lot_repo: LotDevisRepository = Depends(get_lot_devis_repository),
    ligne_repo: LigneDevisRepository = Depends(get_ligne_devis_repository),
    debourse_repo: DebourseDetailRepository = Depends(get_debourse_detail_repository),
    journal_repo: JournalDevisRepository = Depends(get_journal_devis_repository),
) -> CreerRevisionUseCase:
    return CreerRevisionUseCase(devis_repo, lot_repo, ligne_repo, debourse_repo, journal_repo)


def get_creer_variante_use_case(
    devis_repo: DevisRepository = Depends(get_devis_repository),
    lot_repo: LotDevisRepository = Depends(get_lot_devis_repository),
    ligne_repo: LigneDevisRepository = Depends(get_ligne_devis_repository),
    debourse_repo: DebourseDetailRepository = Depends(get_debourse_detail_repository),
    journal_repo: JournalDevisRepository = Depends(get_journal_devis_repository),
) -> CreerVarianteUseCase:
    return CreerVarianteUseCase(devis_repo, lot_repo, ligne_repo, debourse_repo, journal_repo)


def get_lister_versions_use_case(
    devis_repo: DevisRepository = Depends(get_devis_repository),
) -> ListerVersionsUseCase:
    return ListerVersionsUseCase(devis_repo)


def get_generer_comparatif_use_case(
    devis_repo: DevisRepository = Depends(get_devis_repository),
    lot_repo: LotDevisRepository = Depends(get_lot_devis_repository),
    ligne_repo: LigneDevisRepository = Depends(get_ligne_devis_repository),
    comparatif_repo: ComparatifRepository = Depends(get_comparatif_repository),
    journal_repo: JournalDevisRepository = Depends(get_journal_devis_repository),
) -> GenererComparatifUseCase:
    return GenererComparatifUseCase(devis_repo, lot_repo, ligne_repo, comparatif_repo, journal_repo)


def get_get_comparatif_use_case(
    comparatif_repo: ComparatifRepository = Depends(get_comparatif_repository),
) -> GetComparatifUseCase:
    return GetComparatifUseCase(comparatif_repo)


def get_figer_version_use_case(
    devis_repo: DevisRepository = Depends(get_devis_repository),
    journal_repo: JournalDevisRepository = Depends(get_journal_devis_repository),
) -> FigerVersionUseCase:
    return FigerVersionUseCase(devis_repo, journal_repo)


# ─────────────────────────────────────────────────────────────────────────────
# Use Cases - Attestation TVA (DEV-23)
# ─────────────────────────────────────────────────────────────────────────────

def get_generer_attestation_tva_use_case(
    devis_repo: DevisRepository = Depends(get_devis_repository),
    attestation_repo: AttestationTVARepository = Depends(get_attestation_tva_repository),
    journal_repo: JournalDevisRepository = Depends(get_journal_devis_repository),
) -> GenererAttestationTVAUseCase:
    return GenererAttestationTVAUseCase(devis_repo, attestation_repo, journal_repo)


def get_get_attestation_tva_use_case(
    devis_repo: DevisRepository = Depends(get_devis_repository),
    attestation_repo: AttestationTVARepository = Depends(get_attestation_tva_repository),
) -> GetAttestationTVAUseCase:
    return GetAttestationTVAUseCase(devis_repo, attestation_repo)


def get_verifier_eligibilite_tva_use_case(
    devis_repo: DevisRepository = Depends(get_devis_repository),
) -> VerifierEligibiliteTVAUseCase:
    return VerifierEligibiliteTVAUseCase(devis_repo)


# ─────────────────────────────────────────────────────────────────────────────
# Use Cases - Frais de chantier (DEV-25)
# ─────────────────────────────────────────────────────────────────────────────

def get_create_frais_chantier_use_case(
    frais_repo: FraisChantierRepository = Depends(get_frais_chantier_repository),
    devis_repo: DevisRepository = Depends(get_devis_repository),
    journal_repo: JournalDevisRepository = Depends(get_journal_devis_repository),
) -> CreateFraisChantierUseCase:
    return CreateFraisChantierUseCase(frais_repo, devis_repo, journal_repo)


def get_update_frais_chantier_use_case(
    frais_repo: FraisChantierRepository = Depends(get_frais_chantier_repository),
    devis_repo: DevisRepository = Depends(get_devis_repository),
    journal_repo: JournalDevisRepository = Depends(get_journal_devis_repository),
) -> UpdateFraisChantierUseCase:
    return UpdateFraisChantierUseCase(frais_repo, devis_repo, journal_repo)


def get_delete_frais_chantier_use_case(
    frais_repo: FraisChantierRepository = Depends(get_frais_chantier_repository),
    devis_repo: DevisRepository = Depends(get_devis_repository),
    journal_repo: JournalDevisRepository = Depends(get_journal_devis_repository),
) -> DeleteFraisChantierUseCase:
    return DeleteFraisChantierUseCase(frais_repo, devis_repo, journal_repo)


def get_list_frais_chantier_use_case(
    frais_repo: FraisChantierRepository = Depends(get_frais_chantier_repository),
    devis_repo: DevisRepository = Depends(get_devis_repository),
) -> ListFraisChantierUseCase:
    return ListFraisChantierUseCase(frais_repo, devis_repo)


def get_calculer_repartition_frais_use_case(
    frais_repo: FraisChantierRepository = Depends(get_frais_chantier_repository),
    devis_repo: DevisRepository = Depends(get_devis_repository),
    lot_repo: LotDevisRepository = Depends(get_lot_devis_repository),
) -> CalculerRepartitionFraisUseCase:
    return CalculerRepartitionFraisUseCase(frais_repo, devis_repo, lot_repo)


# ─────────────────────────────────────────────────────────────────────────────
# Use Cases - Options de presentation (DEV-11)
# ─────────────────────────────────────────────────────────────────────────────

def get_update_options_presentation_use_case(
    devis_repo: DevisRepository = Depends(get_devis_repository),
    journal_repo: JournalDevisRepository = Depends(get_journal_devis_repository),
) -> UpdateOptionsPresentationUseCase:
    return UpdateOptionsPresentationUseCase(devis_repo, journal_repo)


def get_get_options_presentation_use_case(
    devis_repo: DevisRepository = Depends(get_devis_repository),
) -> GetOptionsPresentationUseCase:
    return GetOptionsPresentationUseCase(devis_repo)


def get_list_templates_presentation_use_case() -> ListTemplatesPresentationUseCase:
    return ListTemplatesPresentationUseCase()


# ─────────────────────────────────────────────────────────────────────────────
# Use Cases - Signature electronique (DEV-14)
# ─────────────────────────────────────────────────────────────────────────────

def get_signer_devis_use_case(
    devis_repo: DevisRepository = Depends(get_devis_repository),
    signature_repo: SignatureDevisRepository = Depends(get_signature_devis_repository),
    journal_repo: JournalDevisRepository = Depends(get_journal_devis_repository),
) -> SignerDevisUseCase:
    return SignerDevisUseCase(devis_repo, signature_repo, journal_repo)


def get_get_signature_use_case(
    devis_repo: DevisRepository = Depends(get_devis_repository),
    signature_repo: SignatureDevisRepository = Depends(get_signature_devis_repository),
) -> GetSignatureUseCase:
    return GetSignatureUseCase(devis_repo, signature_repo)


def get_revoquer_signature_use_case(
    devis_repo: DevisRepository = Depends(get_devis_repository),
    signature_repo: SignatureDevisRepository = Depends(get_signature_devis_repository),
    journal_repo: JournalDevisRepository = Depends(get_journal_devis_repository),
) -> RevoquerSignatureUseCase:
    return RevoquerSignatureUseCase(devis_repo, signature_repo, journal_repo)


def get_verifier_signature_use_case(
    devis_repo: DevisRepository = Depends(get_devis_repository),
    signature_repo: SignatureDevisRepository = Depends(get_signature_devis_repository),
) -> VerifierSignatureUseCase:
    return VerifierSignatureUseCase(devis_repo, signature_repo)


# ─────────────────────────────────────────────────────────────────────────────
# Use Cases - Conversion en chantier (DEV-16)
# ─────────────────────────────────────────────────────────────────────────────

def get_convertir_devis_use_case(
    devis_repo: DevisRepository = Depends(get_devis_repository),
    lot_repo: LotDevisRepository = Depends(get_lot_devis_repository),
    journal_repo: JournalDevisRepository = Depends(get_journal_devis_repository),
    signature_repo: SignatureDevisRepository = Depends(get_signature_devis_repository),
) -> ConvertirDevisUseCase:
    return ConvertirDevisUseCase(
        devis_repo, lot_repo, journal_repo, signature_repo
    )


def get_get_conversion_info_use_case(
    devis_repo: DevisRepository = Depends(get_devis_repository),
    signature_repo: SignatureDevisRepository = Depends(get_signature_devis_repository),
) -> GetConversionInfoUseCase:
    return GetConversionInfoUseCase(devis_repo, signature_repo)


# ─────────────────────────────────────────────────────────────────────────────
# Use Cases - Relances automatiques (DEV-24)
# ─────────────────────────────────────────────────────────────────────────────

def get_planifier_relances_use_case(
    devis_repo: DevisRepository = Depends(get_devis_repository),
    relance_repo: RelanceDevisRepository = Depends(get_relance_devis_repository),
    journal_repo: JournalDevisRepository = Depends(get_journal_devis_repository),
) -> PlanifierRelancesUseCase:
    return PlanifierRelancesUseCase(devis_repo, relance_repo, journal_repo)


def get_executer_relances_use_case(
    relance_repo: RelanceDevisRepository = Depends(get_relance_devis_repository),
    journal_repo: JournalDevisRepository = Depends(get_journal_devis_repository),
) -> ExecuterRelancesUseCase:
    return ExecuterRelancesUseCase(relance_repo, journal_repo)


def get_annuler_relances_use_case(
    devis_repo: DevisRepository = Depends(get_devis_repository),
    relance_repo: RelanceDevisRepository = Depends(get_relance_devis_repository),
    journal_repo: JournalDevisRepository = Depends(get_journal_devis_repository),
) -> AnnulerRelancesUseCase:
    return AnnulerRelancesUseCase(devis_repo, relance_repo, journal_repo)


def get_get_relances_devis_use_case(
    devis_repo: DevisRepository = Depends(get_devis_repository),
    relance_repo: RelanceDevisRepository = Depends(get_relance_devis_repository),
) -> GetRelancesDevisUseCase:
    return GetRelancesDevisUseCase(devis_repo, relance_repo)


def get_update_config_relances_use_case(
    devis_repo: DevisRepository = Depends(get_devis_repository),
    journal_repo: JournalDevisRepository = Depends(get_journal_devis_repository),
) -> UpdateConfigRelancesUseCase:
    return UpdateConfigRelancesUseCase(devis_repo, journal_repo)


# Use Cases - Conversion Devis -> Chantier (DEV-16)
# ─────────────────────────────────────────────────────────────────────────────

def get_convertir_devis_en_chantier_use_case(
    db: Session = Depends(get_db),
    devis_repo: DevisRepository = Depends(get_devis_repository),
    lot_devis_repo: LotDevisRepository = Depends(get_lot_devis_repository),
    journal_repo: JournalDevisRepository = Depends(get_journal_devis_repository),
    signature_repo: SignatureDevisRepository = Depends(get_signature_devis_repository),
) -> ConvertirDevisEnChantierUseCase:
    """Retourne le use case de conversion devis -> chantier.

    Injecte le ChantierCreationAdapter (couche Infrastructure shared)
    qui encapsule les imports cross-module (chantiers, financier).
    Le use case n'a plus de dependance directe sur ces modules.
    """
    from shared.infrastructure.adapters import ChantierCreationAdapter
    from modules.chantiers.infrastructure.persistence import SQLAlchemyChantierRepository
    from modules.financier.infrastructure.persistence import (
        SQLAlchemyBudgetRepository,
        SQLAlchemyLotBudgetaireRepository,
    )

    chantier_repo = SQLAlchemyChantierRepository(db)
    budget_repo = SQLAlchemyBudgetRepository(db)
    lot_budgetaire_repo = SQLAlchemyLotBudgetaireRepository(db)

    chantier_creation_port = ChantierCreationAdapter(
        chantier_repo=chantier_repo,
        budget_repo=budget_repo,
        lot_budgetaire_repo=lot_budgetaire_repo,
    )

    return ConvertirDevisEnChantierUseCase(
        devis_repo=devis_repo,
        lot_devis_repo=lot_devis_repo,
        journal_repo=journal_repo,
        chantier_creation_port=chantier_creation_port,
        signature_repo=signature_repo,
    )
