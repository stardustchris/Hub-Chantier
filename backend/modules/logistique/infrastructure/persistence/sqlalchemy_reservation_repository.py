"""Implementation SQLAlchemy du repository Reservation.

CDC Section 11 - LOG-07 a LOG-18.
"""
from datetime import date
from typing import Optional, List

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from .models import ReservationModel
from ...domain.entities import Reservation
from ...domain.value_objects import StatutReservation
from ...domain.repositories import ReservationRepository


class SQLAlchemyReservationRepository(ReservationRepository):
    """Implementation SQLAlchemy du repository Reservation."""

    def __init__(self, session: Session):
        """Initialise le repository.

        Args:
            session: Session SQLAlchemy.
        """
        self._session = session

    def save(self, reservation: Reservation) -> Reservation:
        """Sauvegarde une reservation.

        Args:
            reservation: Reservation a sauvegarder.

        Returns:
            La reservation sauvegardee avec son ID.
        """
        if reservation.id:
            # Update
            model = self._session.query(ReservationModel).filter(
                ReservationModel.id == reservation.id
            ).first()
            if model:
                self._entity_to_model(reservation, model)
        else:
            # Create
            model = ReservationModel()
            self._entity_to_model(reservation, model)
            self._session.add(model)

        self._session.flush()
        return self._model_to_entity(model)

    def find_by_id(self, reservation_id: int) -> Optional[Reservation]:
        """Trouve une reservation par ID.

        Args:
            reservation_id: ID de la reservation.

        Returns:
            La reservation ou None.
        """
        model = self._session.query(ReservationModel).filter(
            and_(
                ReservationModel.id == reservation_id,
                ReservationModel.deleted_at.is_(None),
            )
        ).first()

        if not model:
            return None

        return self._model_to_entity(model)

    def find_all(
        self,
        ressource_id: Optional[int] = None,
        chantier_id: Optional[int] = None,
        demandeur_id: Optional[int] = None,
        statut: Optional[str] = None,
        date_debut: Optional[date] = None,
        date_fin: Optional[date] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Reservation]:
        """Liste les reservations.

        Args:
            ressource_id: Filtrer par ressource.
            chantier_id: Filtrer par chantier.
            demandeur_id: Filtrer par demandeur.
            statut: Filtrer par statut.
            date_debut: Date de debut minimum.
            date_fin: Date de fin maximum.
            skip: Offset de pagination.
            limit: Limite de pagination.

        Returns:
            Liste des reservations.
        """
        query = self._session.query(ReservationModel).filter(
            ReservationModel.deleted_at.is_(None)
        )

        if ressource_id:
            query = query.filter(ReservationModel.ressource_id == ressource_id)

        if chantier_id:
            query = query.filter(ReservationModel.chantier_id == chantier_id)

        if demandeur_id:
            query = query.filter(ReservationModel.demandeur_id == demandeur_id)

        if statut:
            query = query.filter(ReservationModel.statut == statut)

        if date_debut:
            query = query.filter(ReservationModel.date_fin >= date_debut)

        if date_fin:
            query = query.filter(ReservationModel.date_debut <= date_fin)

        query = query.order_by(
            ReservationModel.date_debut,
            ReservationModel.heure_debut,
        ).offset(skip).limit(limit)

        return [self._model_to_entity(m) for m in query.all()]

    def count(
        self,
        ressource_id: Optional[int] = None,
        chantier_id: Optional[int] = None,
        demandeur_id: Optional[int] = None,
        statut: Optional[str] = None,
        date_debut: Optional[date] = None,
        date_fin: Optional[date] = None,
    ) -> int:
        """Compte les reservations.

        Args:
            ressource_id: Filtrer par ressource.
            chantier_id: Filtrer par chantier.
            demandeur_id: Filtrer par demandeur.
            statut: Filtrer par statut.
            date_debut: Date de debut minimum.
            date_fin: Date de fin maximum.

        Returns:
            Nombre de reservations.
        """
        query = self._session.query(ReservationModel).filter(
            ReservationModel.deleted_at.is_(None)
        )

        if ressource_id:
            query = query.filter(ReservationModel.ressource_id == ressource_id)

        if chantier_id:
            query = query.filter(ReservationModel.chantier_id == chantier_id)

        if demandeur_id:
            query = query.filter(ReservationModel.demandeur_id == demandeur_id)

        if statut:
            query = query.filter(ReservationModel.statut == statut)

        if date_debut:
            query = query.filter(ReservationModel.date_fin >= date_debut)

        if date_fin:
            query = query.filter(ReservationModel.date_debut <= date_fin)

        return query.count()

    def find_conflits(
        self,
        ressource_id: int,
        date_debut: date,
        date_fin: date,
        heure_debut: str,
        heure_fin: str,
        exclude_reservation_id: Optional[int] = None,
    ) -> List[Reservation]:
        """Trouve les reservations en conflit (LOG-17).

        Args:
            ressource_id: ID de la ressource.
            date_debut: Date de debut.
            date_fin: Date de fin.
            heure_debut: Heure de debut.
            heure_fin: Heure de fin.
            exclude_reservation_id: ID de reservation a exclure.

        Returns:
            Liste des reservations en conflit.
        """
        # Seules les reservations validees ou en attente peuvent causer un conflit
        statuts_conflictuels = [
            StatutReservation.VALIDEE.value,
            StatutReservation.EN_ATTENTE.value,
        ]

        query = self._session.query(ReservationModel).filter(
            and_(
                ReservationModel.ressource_id == ressource_id,
                ReservationModel.statut.in_(statuts_conflictuels),
                ReservationModel.deleted_at.is_(None),
                # Chevauchement de dates
                ReservationModel.date_debut <= date_fin,
                ReservationModel.date_fin >= date_debut,
                # Chevauchement d'heures (simplifie)
                ReservationModel.heure_debut < heure_fin,
                ReservationModel.heure_fin > heure_debut,
            )
        )

        if exclude_reservation_id:
            query = query.filter(ReservationModel.id != exclude_reservation_id)

        return [self._model_to_entity(m) for m in query.all()]

    def find_by_ressource_and_period(
        self,
        ressource_id: int,
        date_debut: date,
        date_fin: date,
    ) -> List[Reservation]:
        """Trouve les reservations d'une ressource sur une periode (LOG-03).

        Args:
            ressource_id: ID de la ressource.
            date_debut: Date de debut.
            date_fin: Date de fin.

        Returns:
            Liste des reservations.
        """
        return self.find_all(
            ressource_id=ressource_id,
            date_debut=date_debut,
            date_fin=date_fin,
            skip=0,
            limit=1000,  # Max raisonnable pour une semaine
        )

    def delete(self, reservation_id: int) -> bool:
        """Supprime une reservation (soft delete RGPD).

        Args:
            reservation_id: ID de la reservation.

        Returns:
            True si supprimee.
        """
        from datetime import datetime

        model = self._session.query(ReservationModel).filter(
            and_(
                ReservationModel.id == reservation_id,
                ReservationModel.deleted_at.is_(None),
            )
        ).first()

        if model:
            model.deleted_at = datetime.now()
            model.updated_at = datetime.now()
            return True
        return False

    def _model_to_entity(self, model: ReservationModel) -> Reservation:
        """Convertit un modele en entite."""
        reservation = Reservation(
            ressource_id=model.ressource_id,
            chantier_id=model.chantier_id,
            demandeur_id=model.demandeur_id,
            date_debut=model.date_debut,
            date_fin=model.date_fin,
            heure_debut=model.heure_debut,
            heure_fin=model.heure_fin,
            note=model.note,
        )
        reservation.id = model.id
        reservation.valideur_id = model.valideur_id
        reservation.statut = StatutReservation(model.statut)
        reservation.motif_refus = model.motif_refus
        reservation.validated_at = model.validated_at
        reservation.refused_at = model.refused_at
        reservation.cancelled_at = model.cancelled_at
        reservation.created_at = model.created_at
        reservation.updated_at = model.updated_at
        return reservation

    def _entity_to_model(self, entity: Reservation, model: ReservationModel) -> None:
        """Copie les champs d'une entite vers un modele."""
        model.ressource_id = entity.ressource_id
        model.chantier_id = entity.chantier_id
        model.demandeur_id = entity.demandeur_id
        model.valideur_id = entity.valideur_id
        model.date_debut = entity.date_debut
        model.date_fin = entity.date_fin
        model.heure_debut = entity.heure_debut
        model.heure_fin = entity.heure_fin
        model.statut = entity.statut.value
        model.motif_refus = entity.motif_refus
        model.note = entity.note
        model.validated_at = entity.validated_at
        model.refused_at = entity.refused_at
        model.cancelled_at = entity.cancelled_at
        model.created_at = entity.created_at
        model.updated_at = entity.updated_at
