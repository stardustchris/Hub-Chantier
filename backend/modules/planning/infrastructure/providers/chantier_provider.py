"""Provider pour integration avec le module chantiers."""

from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from ...application.use_cases.charge.get_planning_charge import ChantierProvider
from ...domain.value_objects import Semaine

from shared.infrastructure.chantier_queries import (
    get_chantiers_actifs,
    get_chantier_by_id_dict,
)


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

    def get_chantiers_actifs(self, search: Optional[str] = None) -> List[Dict]:
        """
        Recupere la liste des chantiers actifs.

        Args:
            search: Terme de recherche optionnel.

        Returns:
            Liste de dicts avec id, code, nom, couleur, heures_estimees.
        """
        return get_chantiers_actifs(self.session, search=search)

    def get_chantier_by_id(self, chantier_id: int) -> Optional[Dict]:
        """
        Recupere un chantier par son ID.

        Args:
            chantier_id: ID du chantier.

        Returns:
            Dict avec infos chantier ou None.
        """
        return get_chantier_by_id_dict(self.session, chantier_id)

    def search_chantiers(self, query: str) -> List[Dict]:
        """
        Recherche des chantiers par nom ou code.

        Args:
            query: Terme de recherche.

        Returns:
            Liste de chantiers correspondants.
        """
        return get_chantiers_actifs(self.session, search=query)

    def get_chantiers_by_ids(self, chantier_ids: List[int]) -> List[Dict]:
        """
        Recupere plusieurs chantiers par leurs IDs (requête unique).

        Args:
            chantier_ids: Liste d'IDs.

        Returns:
            Liste de dicts avec infos chantiers.
        """
        if not chantier_ids:
            return []

        from shared.infrastructure.chantier_queries import get_chantiers_by_ids_full

        return get_chantiers_by_ids_full(self.session, chantier_ids)
