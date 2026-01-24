"""Provider pour integration avec le module chantiers."""

from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from ...application.use_cases.get_planning_charge import ChantierProvider
from ...domain.value_objects import Semaine


class SQLAlchemyChantierProvider(ChantierProvider):
    """
    Implementation SQLAlchemy du ChantierProvider.

    Recupere les informations des chantiers depuis la base de donnees
    sans creer de dependance directe vers le module chantiers.
    """

    def __init__(self, session: Session):
        """
        Initialise le provider.

        Args:
            session: Session SQLAlchemy.
        """
        self.session = session

    def get_chantiers_actifs(self) -> List[Dict]:
        """
        Recupere la liste des chantiers actifs.

        Returns:
            Liste de dicts avec id, code, nom, couleur, heures_estimees.
        """
        # Import differe pour eviter dependance circulaire
        from modules.chantiers.infrastructure.persistence import ChantierModel

        models = self.session.query(ChantierModel).filter(
            ChantierModel.statut.in_(["ouvert", "en_cours"]),
            ChantierModel.is_deleted == False,
        ).order_by(ChantierModel.code).all()

        return [
            {
                "id": m.id,
                "code": m.code,
                "nom": m.nom,
                "couleur": m.couleur or "#3498DB",
                "heures_estimees": m.heures_estimees or 0.0,
            }
            for m in models
        ]

    def get_chantier_by_id(self, chantier_id: int) -> Optional[Dict]:
        """
        Recupere un chantier par son ID.

        Args:
            chantier_id: ID du chantier.

        Returns:
            Dict avec infos chantier ou None.
        """
        from modules.chantiers.infrastructure.persistence import ChantierModel

        model = self.session.query(ChantierModel).filter(
            ChantierModel.id == chantier_id,
            ChantierModel.is_deleted == False,
        ).first()

        if not model:
            return None

        return {
            "id": model.id,
            "code": model.code,
            "nom": model.nom,
            "couleur": model.couleur or "#3498DB",
            "heures_estimees": model.heures_estimees or 0.0,
        }

    def search_chantiers(self, query: str) -> List[Dict]:
        """
        Recherche des chantiers par nom ou code.

        Args:
            query: Terme de recherche.

        Returns:
            Liste de chantiers correspondants.
        """
        from modules.chantiers.infrastructure.persistence import ChantierModel

        search_term = f"%{query}%"

        models = self.session.query(ChantierModel).filter(
            ChantierModel.is_deleted == False,
            ChantierModel.statut.in_(["ouvert", "en_cours"]),
            (ChantierModel.nom.ilike(search_term)) |
            (ChantierModel.code.ilike(search_term)),
        ).order_by(ChantierModel.code).all()

        return [
            {
                "id": m.id,
                "code": m.code,
                "nom": m.nom,
                "couleur": m.couleur or "#3498DB",
                "heures_estimees": m.heures_estimees or 0.0,
            }
            for m in models
        ]

    def get_chantiers_by_ids(self, chantier_ids: List[int]) -> List[Dict]:
        """
        Recupere plusieurs chantiers par leurs IDs.

        Args:
            chantier_ids: Liste d'IDs.

        Returns:
            Liste de dicts avec infos chantiers.
        """
        if not chantier_ids:
            return []

        from modules.chantiers.infrastructure.persistence import ChantierModel

        models = self.session.query(ChantierModel).filter(
            ChantierModel.id.in_(chantier_ids),
            ChantierModel.is_deleted == False,
        ).order_by(ChantierModel.code).all()

        return [
            {
                "id": m.id,
                "code": m.code,
                "nom": m.nom,
                "couleur": m.couleur or "#3498DB",
                "heures_estimees": m.heures_estimees or 0.0,
            }
            for m in models
        ]
