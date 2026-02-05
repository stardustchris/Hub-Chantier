"""Implementation SQLAlchemy du repository PieceJointeDevis.

DEV-07: Insertion multimedia.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from ...domain.entities.piece_jointe_devis import PieceJointeDevis
from ...domain.repositories.piece_jointe_repository import PieceJointeDevisRepository
from .piece_jointe_model import PieceJointeDevisModel


class SQLAlchemyPieceJointeDevisRepository(PieceJointeDevisRepository):
    """Implementation SQLAlchemy pour les pieces jointes de devis."""

    def __init__(self, session: Session):
        """Initialise le repository avec une session SQLAlchemy.

        Args:
            session: La session SQLAlchemy.
        """
        self._session = session

    def _to_entity(self, model: PieceJointeDevisModel) -> PieceJointeDevis:
        """Convertit un modele SQLAlchemy en entite domain.

        Args:
            model: Le modele SQLAlchemy source.

        Returns:
            L entite PieceJointeDevis correspondante.
        """
        return PieceJointeDevis(
            id=model.id,
            devis_id=model.devis_id,
            document_id=model.document_id,
            lot_devis_id=model.lot_devis_id,
            ligne_devis_id=model.ligne_devis_id,
            visible_client=model.visible_client,
            ordre=model.ordre,
            created_at=model.created_at,
            created_by=model.created_by,
            nom_fichier=model.nom_fichier,
            type_fichier=model.type_fichier,
            taille_octets=model.taille_octets,
            mime_type=model.mime_type,
        )

    def _to_model(self, entity: PieceJointeDevis) -> PieceJointeDevisModel:
        """Convertit une entite domain en modele SQLAlchemy.

        Args:
            entity: L entite PieceJointeDevis source.

        Returns:
            Le modele SQLAlchemy correspondant.
        """
        model = PieceJointeDevisModel()
        if entity.id:
            model.id = entity.id
        model.devis_id = entity.devis_id
        model.document_id = entity.document_id
        model.lot_devis_id = entity.lot_devis_id
        model.ligne_devis_id = entity.ligne_devis_id
        model.visible_client = entity.visible_client
        model.ordre = entity.ordre
        model.created_by = entity.created_by
        model.nom_fichier = entity.nom_fichier
        model.type_fichier = entity.type_fichier
        model.taille_octets = entity.taille_octets
        model.mime_type = entity.mime_type
        return model

    def find_by_devis_id(self, devis_id: int) -> List[PieceJointeDevis]:
        """Liste toutes les pieces jointes d un devis.

        Args:
            devis_id: L ID du devis.

        Returns:
            Liste des pieces jointes, triee par ordre.
        """
        models = (
            self._session.query(PieceJointeDevisModel)
            .filter(PieceJointeDevisModel.devis_id == devis_id)
            .order_by(PieceJointeDevisModel.ordre)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def find_by_id(self, piece_id: int) -> Optional[PieceJointeDevis]:
        """Trouve une piece jointe par son ID.

        Args:
            piece_id: L ID de la piece jointe.

        Returns:
            La piece jointe ou None si non trouvee.
        """
        model = (
            self._session.query(PieceJointeDevisModel)
            .filter(PieceJointeDevisModel.id == piece_id)
            .first()
        )
        return self._to_entity(model) if model else None

    def create(self, piece: PieceJointeDevis) -> PieceJointeDevis:
        """Cree une nouvelle piece jointe.

        Args:
            piece: La piece jointe a creer.

        Returns:
            La piece jointe avec son ID attribue.
        """
        model = self._to_model(piece)
        self._session.add(model)
        self._session.flush()
        return self._to_entity(model)

    def update(self, piece: PieceJointeDevis) -> PieceJointeDevis:
        """Met a jour une piece jointe.

        Args:
            piece: La piece jointe avec les champs mis a jour.

        Returns:
            La piece jointe mise a jour.
        """
        model = (
            self._session.query(PieceJointeDevisModel)
            .filter(PieceJointeDevisModel.id == piece.id)
            .first()
        )
        if model:
            model.visible_client = piece.visible_client
            model.ordre = piece.ordre
            self._session.flush()
            return self._to_entity(model)
        return piece

    def delete(self, piece_id: int) -> bool:
        """Supprime une piece jointe (ne supprime PAS le document GED).

        Args:
            piece_id: L ID de la piece jointe a supprimer.

        Returns:
            True si supprimee, False si non trouvee.
        """
        model = (
            self._session.query(PieceJointeDevisModel)
            .filter(PieceJointeDevisModel.id == piece_id)
            .first()
        )
        if model:
            self._session.delete(model)
            self._session.flush()
            return True
        return False
