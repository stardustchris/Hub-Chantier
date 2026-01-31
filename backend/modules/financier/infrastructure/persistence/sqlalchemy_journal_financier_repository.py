"""Implementation SQLAlchemy du repository JournalFinancier.

FIN-15: Audit trail pour toutes les modifications financieres.
Table append-only (pas de soft delete, pas de modification).
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from ...domain.repositories.journal_financier_repository import (
    JournalFinancierRepository,
    JournalEntry,
)
from .models import JournalFinancierModel


class SQLAlchemyJournalFinancierRepository(JournalFinancierRepository):
    """Implementation SQLAlchemy du repository JournalFinancier.

    Table append-only: pas de mise a jour, pas de suppression.
    """

    def __init__(self, session: Session):
        """Initialise le repository avec une session SQLAlchemy.

        Args:
            session: La session SQLAlchemy.
        """
        self._session = session

    def _to_entry(self, model: JournalFinancierModel) -> JournalEntry:
        """Convertit un modele SQLAlchemy en JournalEntry.

        Args:
            model: Le modele SQLAlchemy source.

        Returns:
            Le JournalEntry correspondant.
        """
        return JournalEntry(
            id=model.id,
            entite_type=model.entite_type,
            entite_id=model.entite_id,
            chantier_id=None,  # Sera enrichi cote use case si necessaire
            action=model.action,
            details=self._build_details(model),
            auteur_id=model.auteur_id,
            created_at=model.created_at,
        )

    def _build_details(self, model: JournalFinancierModel) -> Optional[str]:
        """Construit les details depuis les champs du modele.

        Args:
            model: Le modele SQLAlchemy source.

        Returns:
            String formatee avec les details.
        """
        parts = []
        if model.champ_modifie:
            parts.append(f"champ={model.champ_modifie}")
        if model.ancienne_valeur:
            parts.append(f"ancien={model.ancienne_valeur}")
        if model.nouvelle_valeur:
            parts.append(f"nouveau={model.nouvelle_valeur}")
        if model.motif:
            parts.append(f"motif={model.motif}")
        return " | ".join(parts) if parts else None

    def save(self, entry: JournalEntry) -> JournalEntry:
        """Persiste une entree du journal (append-only).

        Args:
            entry: L'entree a persister.

        Returns:
            L'entree avec son ID attribue.
        """
        model = JournalFinancierModel(
            entite_type=entry.entite_type,
            entite_id=entry.entite_id,
            action=entry.action,
            motif=entry.details,
            auteur_id=entry.auteur_id,
            created_at=entry.created_at or datetime.utcnow(),
        )
        self._session.add(model)
        self._session.flush()

        return JournalEntry(
            id=model.id,
            entite_type=model.entite_type,
            entite_id=model.entite_id,
            chantier_id=entry.chantier_id,
            action=model.action,
            details=entry.details,
            auteur_id=model.auteur_id,
            created_at=model.created_at,
        )

    def find_by_entite(
        self,
        entite_type: str,
        entite_id: int,
        limit: int = 100,
        offset: int = 0,
    ) -> List[JournalEntry]:
        """Liste les entrees du journal pour une entite.

        Args:
            entite_type: Type de l'entite (fournisseur, budget, achat, etc.).
            entite_id: ID de l'entite.
            limit: Nombre maximum de resultats.
            offset: Decalage pour pagination.

        Returns:
            Liste des entrees du journal.
        """
        query = (
            self._session.query(JournalFinancierModel)
            .filter(
                JournalFinancierModel.entite_type == entite_type,
                JournalFinancierModel.entite_id == entite_id,
            )
            .order_by(JournalFinancierModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        return [self._to_entry(model) for model in query.all()]

    def find_by_auteur(
        self,
        auteur_id: int,
        limit: int = 100,
        offset: int = 0,
    ) -> List[JournalEntry]:
        """Liste les entrees du journal d'un auteur.

        Args:
            auteur_id: ID de l'auteur.
            limit: Nombre maximum de resultats.
            offset: Decalage pour pagination.

        Returns:
            Liste des entrees du journal.
        """
        query = (
            self._session.query(JournalFinancierModel)
            .filter(JournalFinancierModel.auteur_id == auteur_id)
            .order_by(JournalFinancierModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        return [self._to_entry(model) for model in query.all()]

    def find_by_chantier(
        self,
        chantier_id: int,
        limit: int = 100,
        offset: int = 0,
    ) -> List[JournalEntry]:
        """Liste les entrees du journal d'un chantier.

        Recherche dans les entrees dont le motif contient le chantier_id
        ou via les achats/budgets lies au chantier.

        Args:
            chantier_id: ID du chantier.
            limit: Nombre maximum de resultats.
            offset: Decalage pour pagination.

        Returns:
            Liste des entrees du journal.
        """
        from .models import AchatModel, BudgetModel

        # Recuperer les IDs des achats et budgets du chantier
        achat_ids = (
            self._session.query(AchatModel.id)
            .filter(AchatModel.chantier_id == chantier_id)
            .all()
        )
        achat_id_list = [row[0] for row in achat_ids]

        budget_ids = (
            self._session.query(BudgetModel.id)
            .filter(BudgetModel.chantier_id == chantier_id)
            .all()
        )
        budget_id_list = [row[0] for row in budget_ids]

        from sqlalchemy import or_, and_

        # Construire les conditions de filtrage
        conditions = []
        if achat_id_list:
            conditions.append(
                and_(
                    JournalFinancierModel.entite_type == "achat",
                    JournalFinancierModel.entite_id.in_(achat_id_list),
                )
            )
        if budget_id_list:
            conditions.append(
                and_(
                    JournalFinancierModel.entite_type == "budget",
                    JournalFinancierModel.entite_id.in_(budget_id_list),
                )
            )

        if not conditions:
            return []

        query = (
            self._session.query(JournalFinancierModel)
            .filter(or_(*conditions))
            .order_by(JournalFinancierModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        return [self._to_entry(model) for model in query.all()]

    def count_by_entite(self, entite_type: str, entite_id: int) -> int:
        """Compte les entrees du journal pour une entite.

        Args:
            entite_type: Type de l'entite.
            entite_id: ID de l'entite.

        Returns:
            Le nombre d'entrees.
        """
        return (
            self._session.query(JournalFinancierModel)
            .filter(
                JournalFinancierModel.entite_type == entite_type,
                JournalFinancierModel.entite_id == entite_id,
            )
            .count()
        )
