"""Dependency injection pour le module Devis.

Fournit les factories FastAPI pour les repositories et use cases.
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
from ...application.use_cases.article_use_cases import (
    CreateArticleUseCase,
    UpdateArticleUseCase,
    ListArticlesUseCase,
    GetArticleUseCase,
    DeleteArticleUseCase,
)

from ..persistence.sqlalchemy_devis_repository import SQLAlchemyDevisRepository
from ..persistence.sqlalchemy_lot_devis_repository import SQLAlchemyLotDevisRepository
from ..persistence.sqlalchemy_ligne_devis_repository import SQLAlchemyLigneDevisRepository
from ..persistence.sqlalchemy_debourse_detail_repository import SQLAlchemyDebourseDetailRepository
from ..persistence.sqlalchemy_article_repository import SQLAlchemyArticleRepository
from ..persistence.sqlalchemy_journal_devis_repository import SQLAlchemyJournalDevisRepository


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
) -> CalculerTotauxDevisUseCase:
    return CalculerTotauxDevisUseCase(devis_repo, lot_repo, ligne_repo, debourse_repo, journal_repo)


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
