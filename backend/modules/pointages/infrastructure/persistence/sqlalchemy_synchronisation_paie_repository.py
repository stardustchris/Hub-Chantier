"""Implementations SQLAlchemy du suivi de synchronisation avec la paie externe."""

import json

from sqlalchemy.orm import Session

from ...domain.entities import StatutSynchronisation, SynchronisationPaie
from ...domain.repositories import (
    CorrespondanceExterneRepository,
    SynchronisationPaieRepository,
)
from .models import CorrespondancePaieExterneModel, SynchronisationPaieModel

SYSTEME_COSTRUCTOR = "costructor"


class SQLAlchemySynchronisationPaieRepository(SynchronisationPaieRepository):
    """Suivi des envois de pointages, en base."""

    def __init__(self, session: Session, systeme: str = SYSTEME_COSTRUCTOR):
        """
        Initialise le depot.

        Args:
            session: Session SQLAlchemy.
            systeme: Systeme de paie externe suivi (isole les suivis par systeme).
        """
        self._session = session
        self._systeme = systeme

    def find_by_pointage_id(self, pointage_id: int) -> SynchronisationPaie | None:
        """Retourne le suivi d'un pointage, ou None."""
        model = (
            self._session.query(SynchronisationPaieModel)
            .filter(SynchronisationPaieModel.pointage_id == pointage_id)
            .first()
        )
        return self._to_entity(model) if model else None

    def save(self, synchronisation: SynchronisationPaie) -> SynchronisationPaie:
        """Cree ou met a jour le suivi, et valide la transaction.

        Le commit est immediat : une saisie creee chez le systeme externe doit
        etre memorisee meme si l'envoi du pointage suivant echoue.
        """
        model = (
            self._session.query(SynchronisationPaieModel)
            .filter(SynchronisationPaieModel.pointage_id == synchronisation.pointage_id)
            .first()
        )
        if model is None:
            model = SynchronisationPaieModel(
                pointage_id=synchronisation.pointage_id, systeme=self._systeme
            )
            self._session.add(model)

        model.statut = synchronisation.statut.value
        model.saisies_externes = json.dumps(synchronisation.saisies_externes)
        model.message = synchronisation.message
        model.tentatives = synchronisation.tentatives
        model.derniere_tentative = synchronisation.derniere_tentative
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def find_by_statuts(
        self, statuts: list[StatutSynchronisation]
    ) -> list[SynchronisationPaie]:
        """Liste les suivis dans l'un des statuts donnes."""
        models = (
            self._session.query(SynchronisationPaieModel)
            .filter(SynchronisationPaieModel.systeme == self._systeme)
            .filter(SynchronisationPaieModel.statut.in_([s.value for s in statuts]))
            .order_by(SynchronisationPaieModel.pointage_id)
            .all()
        )
        return [self._to_entity(m) for m in models]

    @staticmethod
    def _to_entity(model: SynchronisationPaieModel) -> SynchronisationPaie:
        return SynchronisationPaie(
            id=model.id,
            pointage_id=model.pointage_id,
            statut=StatutSynchronisation(model.statut),
            saisies_externes=json.loads(model.saisies_externes or "[]"),
            message=model.message,
            tentatives=model.tentatives,
            derniere_tentative=model.derniere_tentative,
        )


class SQLAlchemyCorrespondanceExterneRepository(CorrespondanceExterneRepository):
    """Identifiants externes des compagnons et chantiers, en base."""

    def __init__(self, session: Session, systeme: str = SYSTEME_COSTRUCTOR):
        """
        Initialise le depot.

        Args:
            session: Session SQLAlchemy.
            systeme: Systeme de paie externe (une correspondance Graneet ne sert
                pas pour Costructor).
        """
        self._session = session
        self._systeme = systeme

    def _query(self, type_entite: str, entite_id: int):
        return self._session.query(CorrespondancePaieExterneModel).filter(
            CorrespondancePaieExterneModel.systeme == self._systeme,
            CorrespondancePaieExterneModel.type_entite == type_entite,
            CorrespondancePaieExterneModel.entite_id == entite_id,
        )

    def get_identifiant_externe(self, type_entite: str, entite_id: int) -> str | None:
        """Retourne l'identifiant externe d'une entite, ou None."""
        model = self._query(type_entite, entite_id).first()
        return model.identifiant_externe if model else None

    def definir(self, type_entite: str, entite_id: int, identifiant_externe: str) -> None:
        """Cree ou remplace la correspondance d'une entite."""
        model = self._query(type_entite, entite_id).first()
        if model is None:
            model = CorrespondancePaieExterneModel(
                systeme=self._systeme, type_entite=type_entite, entite_id=entite_id
            )
            self._session.add(model)
        model.identifiant_externe = identifiant_externe
        self._session.commit()

    def supprimer(self, type_entite: str, entite_id: int) -> None:
        """Supprime la correspondance d'une entite."""
        self._query(type_entite, entite_id).delete()
        self._session.commit()

    def lister(self) -> list[tuple[str, int, str]]:
        """Liste toutes les correspondances."""
        models = (
            self._session.query(CorrespondancePaieExterneModel)
            .filter(CorrespondancePaieExterneModel.systeme == self._systeme)
            .order_by(
                CorrespondancePaieExterneModel.type_entite,
                CorrespondancePaieExterneModel.entite_id,
            )
            .all()
        )
        return [(m.type_entite, m.entite_id, m.identifiant_externe) for m in models]
