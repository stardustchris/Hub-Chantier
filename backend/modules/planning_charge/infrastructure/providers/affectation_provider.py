"""Provider pour integration avec le module planning."""

from typing import Dict, List
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from ...application.use_cases.get_planning_charge import AffectationProvider
from ...application.use_cases.get_occupation_details import AffectationProviderForOccupation
from ...domain.value_objects import Semaine


class SQLAlchemyAffectationProvider(AffectationProvider, AffectationProviderForOccupation):
    """
    Implementation SQLAlchemy de l'AffectationProvider.

    Recupere les heures planifiees depuis le module planning
    sans creer de dependance directe.
    """

    # Heures par jour de travail
    HEURES_PAR_JOUR = 7.0

    def __init__(self, session: Session):
        """
        Initialise le provider.

        Args:
            session: Session SQLAlchemy.
        """
        self.session = session

    def get_heures_planifiees_by_chantier_and_semaine(
        self,
        chantier_id: int,
        semaine: Semaine,
    ) -> float:
        """
        Recupere les heures planifiees pour un chantier et une semaine.

        Args:
            chantier_id: ID du chantier.
            semaine: La semaine.

        Returns:
            Total des heures planifiees.
        """
        from modules.planning.infrastructure.persistence import AffectationModel

        # Calculer les dates de debut et fin de semaine
        date_debut, date_fin = semaine.dates_debut_fin()

        # Compter les affectations
        count = self.session.query(func.count(AffectationModel.id)).filter(
            AffectationModel.chantier_id == chantier_id,
            AffectationModel.date >= date_debut,
            AffectationModel.date <= date_fin,
        ).scalar() or 0

        # Chaque affectation = 1 jour = 7h par defaut
        # TODO: Utiliser heure_debut/heure_fin si disponibles
        return count * self.HEURES_PAR_JOUR

    def get_heures_planifiees_by_semaine(
        self,
        semaine: Semaine,
    ) -> Dict[int, float]:
        """
        Recupere les heures planifiees par chantier pour une semaine.

        Args:
            semaine: La semaine.

        Returns:
            Dict {chantier_id: heures_planifiees}.
        """
        from modules.planning.infrastructure.persistence import AffectationModel

        date_debut, date_fin = semaine.dates_debut_fin()

        # Grouper par chantier
        results = self.session.query(
            AffectationModel.chantier_id,
            func.count(AffectationModel.id),
        ).filter(
            AffectationModel.date >= date_debut,
            AffectationModel.date <= date_fin,
        ).group_by(AffectationModel.chantier_id).all()

        return {
            chantier_id: count * self.HEURES_PAR_JOUR
            for chantier_id, count in results
        }

    def get_heures_planifiees_par_type_metier(
        self,
        semaine: Semaine,
    ) -> Dict[str, float]:
        """
        Recupere les heures planifiees par type de metier.

        Args:
            semaine: La semaine.

        Returns:
            Dict {type_metier: heures_planifiees}.
        """
        from modules.planning.infrastructure.persistence import AffectationModel
        from modules.auth.infrastructure.persistence import UserModel

        date_debut, date_fin = semaine.dates_debut_fin()

        # Joindre affectations avec users pour avoir le metier
        results = self.session.query(
            UserModel.metier,
            func.count(AffectationModel.id),
        ).join(
            AffectationModel,
            AffectationModel.utilisateur_id == UserModel.id,
        ).filter(
            AffectationModel.date >= date_debut,
            AffectationModel.date <= date_fin,
        ).group_by(UserModel.metier).all()

        heures_par_type = {}
        for metier, count in results:
            # Mapper le metier vers le type_metier
            type_metier = self._map_metier_to_type(metier)
            heures = count * self.HEURES_PAR_JOUR
            heures_par_type[type_metier] = heures_par_type.get(type_metier, 0.0) + heures

        return heures_par_type

    def get_heures_planifiees_total_semaine(self, semaine: Semaine) -> float:
        """
        Recupere le total des heures planifiees pour une semaine.

        Args:
            semaine: La semaine.

        Returns:
            Total des heures.
        """
        from modules.planning.infrastructure.persistence import AffectationModel

        date_debut, date_fin = semaine.dates_debut_fin()

        count = self.session.query(func.count(AffectationModel.id)).filter(
            AffectationModel.date >= date_debut,
            AffectationModel.date <= date_fin,
        ).scalar() or 0

        return count * self.HEURES_PAR_JOUR

    def _map_metier_to_type(self, metier: str) -> str:
        """
        Mappe un metier utilisateur vers un type de metier planning charge.

        Args:
            metier: Le metier de l'utilisateur.

        Returns:
            Le type de metier correspondant.
        """
        if not metier:
            return "employe"

        metier_lower = metier.lower()

        mapping = {
            "macon": "macon",
            "maçon": "macon",
            "coffreur": "coffreur",
            "ferrailleur": "ferrailleur",
            "grutier": "grutier",
            "charpentier": "charpentier",
            "couvreur": "couvreur",
            "electricien": "electricien",
            "électricien": "electricien",
        }

        for key, value in mapping.items():
            if key in metier_lower:
                return value

        # Par defaut
        return "employe"
