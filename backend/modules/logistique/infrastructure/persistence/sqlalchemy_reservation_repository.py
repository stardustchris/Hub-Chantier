"""Implémentation SQLAlchemy du repository Reservation."""

from datetime import datetime, date, timedelta
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from ...domain.entities import Reservation
from ...domain.repositories import ReservationRepository
from ...domain.value_objects import StatutReservation
from .models import ReservationModel


class SQLAlchemyReservationRepository(ReservationRepository):
    """Implémentation SQLAlchemy du repository Reservation."""

    def __init__(self, session: Session):
        self._session = session

    def _to_entity(self, model: ReservationModel) -> Reservation:
        """Convertit un modèle SQLAlchemy en entité domain."""
        return Reservation(
            id=model.id,
            ressource_id=model.ressource_id,
            chantier_id=model.chantier_id,
            demandeur_id=model.demandeur_id,
            date_reservation=model.date_reservation,
            heure_debut=model.heure_debut,
            heure_fin=model.heure_fin,
            statut=model.statut,
            motif_refus=model.motif_refus,
            commentaire=model.commentaire,
            valideur_id=model.valideur_id,
            validated_at=model.validated_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: Reservation) -> ReservationModel:
        """Convertit une entité domain en modèle SQLAlchemy."""
        return ReservationModel(
            id=entity.id,
            ressource_id=entity.ressource_id,
            chantier_id=entity.chantier_id,
            demandeur_id=entity.demandeur_id,
            date_reservation=entity.date_reservation,
            heure_debut=entity.heure_debut,
            heure_fin=entity.heure_fin,
            statut=entity.statut,
            motif_refus=entity.motif_refus,
            commentaire=entity.commentaire,
            valideur_id=entity.valideur_id,
            validated_at=entity.validated_at,
            created_at=entity.created_at or datetime.utcnow(),
            updated_at=entity.updated_at,
        )

    def save(self, reservation: Reservation) -> Reservation:
        """Persiste une réservation."""
        if reservation.id:
            # Mise à jour
            model = (
                self._session.query(ReservationModel)
                .filter(ReservationModel.id == reservation.id)
                .first()
            )
            if model:
                model.date_reservation = reservation.date_reservation
                model.heure_debut = reservation.heure_debut
                model.heure_fin = reservation.heure_fin
                model.statut = reservation.statut
                model.motif_refus = reservation.motif_refus
                model.commentaire = reservation.commentaire
                model.valideur_id = reservation.valideur_id
                model.validated_at = reservation.validated_at
                model.updated_at = datetime.utcnow()
        else:
            # Création
            model = self._to_model(reservation)
            self._session.add(model)

        self._session.flush()
        return self._to_entity(model)

    def find_by_id(self, reservation_id: int) -> Optional[Reservation]:
        """Recherche une réservation par son ID."""
        model = (
            self._session.query(ReservationModel)
            .filter(ReservationModel.id == reservation_id)
            .first()
        )
        return self._to_entity(model) if model else None

    def find_by_ressource_and_date_range(
        self,
        ressource_id: int,
        date_debut: date,
        date_fin: date,
        statuts: Optional[List[StatutReservation]] = None,
    ) -> List[Reservation]:
        """Liste les réservations d'une ressource sur une période."""
        query = self._session.query(ReservationModel).filter(
            ReservationModel.ressource_id == ressource_id,
            ReservationModel.date_reservation >= date_debut,
            ReservationModel.date_reservation <= date_fin,
        )

        if statuts:
            query = query.filter(ReservationModel.statut.in_(statuts))

        query = query.order_by(
            ReservationModel.date_reservation,
            ReservationModel.heure_debut,
        )

        return [self._to_entity(model) for model in query.all()]

    def find_by_chantier(
        self,
        chantier_id: int,
        statuts: Optional[List[StatutReservation]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Reservation]:
        """Liste les réservations d'un chantier."""
        query = self._session.query(ReservationModel).filter(
            ReservationModel.chantier_id == chantier_id
        )

        if statuts:
            query = query.filter(ReservationModel.statut.in_(statuts))

        query = query.order_by(
            ReservationModel.date_reservation.desc(),
            ReservationModel.heure_debut,
        )
        query = query.offset(offset).limit(limit)

        return [self._to_entity(model) for model in query.all()]

    def find_by_demandeur(
        self,
        demandeur_id: int,
        statuts: Optional[List[StatutReservation]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Reservation]:
        """Liste les réservations d'un demandeur."""
        query = self._session.query(ReservationModel).filter(
            ReservationModel.demandeur_id == demandeur_id
        )

        if statuts:
            query = query.filter(ReservationModel.statut.in_(statuts))

        query = query.order_by(
            ReservationModel.date_reservation.desc(),
            ReservationModel.heure_debut,
        )
        query = query.offset(offset).limit(limit)

        return [self._to_entity(model) for model in query.all()]

    def find_en_attente_validation(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Reservation]:
        """Liste les réservations en attente de validation."""
        query = (
            self._session.query(ReservationModel)
            .filter(ReservationModel.statut == StatutReservation.EN_ATTENTE)
            .order_by(
                ReservationModel.date_reservation,
                ReservationModel.heure_debut,
            )
            .offset(offset)
            .limit(limit)
        )

        return [self._to_entity(model) for model in query.all()]

    def find_conflits(self, reservation: Reservation) -> List[Reservation]:
        """Recherche les réservations en conflit.

        LOG-17: Conflit de réservation - Alerte si créneau déjà occupé.

        Deux réservations sont en conflit si:
        - Même ressource
        - Même date
        - Créneaux qui se chevauchent
        - Statut actif (en_attente ou validée)
        """
        query = self._session.query(ReservationModel).filter(
            ReservationModel.ressource_id == reservation.ressource_id,
            ReservationModel.date_reservation == reservation.date_reservation,
            ReservationModel.statut.in_(
                [StatutReservation.EN_ATTENTE, StatutReservation.VALIDEE]
            ),
        )

        # Exclure la réservation elle-même si elle a un ID
        if reservation.id:
            query = query.filter(ReservationModel.id != reservation.id)

        # Chevauchement: NOT (fin1 <= debut2 OR debut1 >= fin2)
        # Équivalent à: debut1 < fin2 AND fin1 > debut2
        query = query.filter(
            ReservationModel.heure_debut < reservation.heure_fin,
            ReservationModel.heure_fin > reservation.heure_debut,
        )

        return [self._to_entity(model) for model in query.all()]

    def find_a_rappeler_demain(self) -> List[Reservation]:
        """Liste les réservations pour demain (pour rappel J-1).

        LOG-15: Rappel J-1 - Notification veille de réservation.
        """
        demain = date.today() + timedelta(days=1)

        query = (
            self._session.query(ReservationModel)
            .filter(
                ReservationModel.date_reservation == demain,
                ReservationModel.statut == StatutReservation.VALIDEE,
            )
            .order_by(ReservationModel.heure_debut)
        )

        return [self._to_entity(model) for model in query.all()]

    def find_historique_ressource(
        self,
        ressource_id: int,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Reservation]:
        """Retourne l'historique des réservations d'une ressource.

        LOG-18: Historique par ressource - Journal complet.
        """
        query = (
            self._session.query(ReservationModel)
            .filter(ReservationModel.ressource_id == ressource_id)
            .order_by(
                ReservationModel.date_reservation.desc(),
                ReservationModel.heure_debut.desc(),
            )
            .offset(offset)
            .limit(limit)
        )

        return [self._to_entity(model) for model in query.all()]

    def count_by_ressource(
        self,
        ressource_id: int,
        statuts: Optional[List[StatutReservation]] = None,
    ) -> int:
        """Compte les réservations d'une ressource."""
        query = self._session.query(ReservationModel).filter(
            ReservationModel.ressource_id == ressource_id
        )

        if statuts:
            query = query.filter(ReservationModel.statut.in_(statuts))

        return query.count()

    def delete(self, reservation_id: int) -> bool:
        """Supprime une réservation."""
        result = (
            self._session.query(ReservationModel)
            .filter(ReservationModel.id == reservation_id)
            .delete()
        )
        self._session.flush()
        return result > 0
