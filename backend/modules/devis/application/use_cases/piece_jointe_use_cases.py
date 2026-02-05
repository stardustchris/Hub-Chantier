"""Use cases pour les pieces jointes de devis.

DEV-07: Insertion multimedia.
"""

from typing import List, Optional

from ...domain.entities.piece_jointe_devis import PieceJointeDevis
from ...domain.repositories.piece_jointe_repository import PieceJointeDevisRepository
from ..dtos.piece_jointe_dtos import PieceJointeCreateDTO, PieceJointeDTO


def _entity_to_dto(p: PieceJointeDevis) -> PieceJointeDTO:
    """Convertit une entite PieceJointeDevis en DTO de sortie.

    Args:
        p: L entite PieceJointeDevis source.

    Returns:
        Le DTO de sortie correspondant.
    """
    return PieceJointeDTO(
        id=p.id,
        devis_id=p.devis_id,
        document_id=p.document_id,
        lot_devis_id=p.lot_devis_id,
        ligne_devis_id=p.ligne_devis_id,
        visible_client=p.visible_client,
        ordre=p.ordre,
        nom_fichier=p.nom_fichier,
        type_fichier=p.type_fichier,
        taille_octets=p.taille_octets,
        mime_type=p.mime_type,
        created_at=p.created_at.isoformat() if p.created_at else None,
    )


class ListerPiecesJointesUseCase:
    """Liste les pieces jointes d un devis."""

    def __init__(self, repository: PieceJointeDevisRepository):
        self._repository = repository

    def execute(self, devis_id: int) -> List[PieceJointeDTO]:
        """Liste les pieces jointes d un devis.

        Args:
            devis_id: L ID du devis.

        Returns:
            Liste des pieces jointes sous forme de DTOs.
        """
        pieces = self._repository.find_by_devis_id(devis_id)
        return [_entity_to_dto(p) for p in pieces]


class AjouterPieceJointeUseCase:
    """Ajoute une piece jointe a un devis."""

    def __init__(self, repository: PieceJointeDevisRepository):
        self._repository = repository

    def execute(
        self,
        dto: PieceJointeCreateDTO,
        nom_fichier: str,
        type_fichier: str,
        taille_octets: int,
        mime_type: str,
        created_by: Optional[int] = None,
    ) -> PieceJointeDTO:
        """Ajoute une piece jointe a un devis.

        Args:
            dto: Les donnees de creation.
            nom_fichier: Nom du fichier (depuis GED).
            type_fichier: Type du fichier (depuis GED).
            taille_octets: Taille en octets (depuis GED).
            mime_type: Type MIME (depuis GED).
            created_by: ID de l utilisateur createur.

        Returns:
            La piece jointe creee sous forme de DTO.
        """
        # Determiner le prochain ordre
        existing = self._repository.find_by_devis_id(dto.devis_id)
        next_ordre = max((p.ordre for p in existing), default=-1) + 1

        piece = PieceJointeDevis(
            devis_id=dto.devis_id,
            document_id=dto.document_id,
            lot_devis_id=dto.lot_devis_id,
            ligne_devis_id=dto.ligne_devis_id,
            visible_client=dto.visible_client,
            ordre=next_ordre,
            created_by=created_by,
            nom_fichier=nom_fichier,
            type_fichier=type_fichier,
            taille_octets=taille_octets,
            mime_type=mime_type,
        )
        created = self._repository.create(piece)
        return _entity_to_dto(created)


class SupprimerPieceJointeUseCase:
    """Supprime une piece jointe (ne supprime PAS le document GED)."""

    def __init__(self, repository: PieceJointeDevisRepository):
        self._repository = repository

    def execute(self, piece_id: int) -> bool:
        """Supprime une piece jointe.

        Args:
            piece_id: L ID de la piece jointe a supprimer.

        Returns:
            True si supprimee, False si non trouvee.
        """
        return self._repository.delete(piece_id)


class ToggleVisibiliteUseCase:
    """Bascule la visibilite client d une piece jointe."""

    def __init__(self, repository: PieceJointeDevisRepository):
        self._repository = repository

    def execute(self, piece_id: int, visible_client: bool) -> Optional[PieceJointeDTO]:
        """Change la visibilite client d une piece jointe.

        Args:
            piece_id: L ID de la piece jointe.
            visible_client: La nouvelle valeur de visibilite.

        Returns:
            La piece jointe mise a jour sous forme de DTO, ou None si non trouvee.
        """
        piece = self._repository.find_by_id(piece_id)
        if not piece:
            return None
        piece.visible_client = visible_client
        updated = self._repository.update(piece)
        return _entity_to_dto(updated)
