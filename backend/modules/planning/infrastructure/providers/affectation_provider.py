"""Provider pour integration avec le module planning."""

from typing import Dict, List, Tuple
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
    # Heures par semaine
    HEURES_PAR_SEMAINE = 35.0

    def __init__(self, session: Session):
        """
        Initialise le provider.

        Args:
            session: Session SQLAlchemy.
        """
        self.session = session

    # =========================================================================
    # Implementation AffectationProvider (get_planning_charge)
    # =========================================================================

    def get_heures_planifiees_par_chantier_et_semaine(
        self,
        chantier_ids: List[int],
        semaine_debut: Semaine,
        semaine_fin: Semaine,
    ) -> Dict[Tuple[int, str], float]:
        """
        Recupere les heures planifiees par chantier et semaine.

        Args:
            chantier_ids: Liste des IDs de chantiers.
            semaine_debut: Premiere semaine.
            semaine_fin: Derniere semaine.

        Returns:
            Dict {(chantier_id, semaine_code): heures_planifiees}.
        """
        if not chantier_ids:
            return {}

        from ..persistence import AffectationModel

        date_debut, _ = semaine_debut.date_range()
        _, date_fin = semaine_fin.date_range()

        # Grouper par chantier et date
        results = self.session.query(
            AffectationModel.chantier_id,
            AffectationModel.date,
            func.count(AffectationModel.id),
        ).filter(
            AffectationModel.chantier_id.in_(chantier_ids),
            AffectationModel.date >= date_debut,
            AffectationModel.date <= date_fin,
        ).group_by(
            AffectationModel.chantier_id,
            AffectationModel.date,
        ).all()

        # Aggreger par semaine
        heures_index: Dict[Tuple[int, str], float] = {}
        for chantier_id, affectation_date, count in results:
            semaine = Semaine.from_date(affectation_date)
            key = (chantier_id, semaine.code)
            heures = count * self.HEURES_PAR_JOUR
            heures_index[key] = heures_index.get(key, 0.0) + heures

        return heures_index

    def get_capacite_par_semaine(
        self,
        semaine_debut: Semaine,
        semaine_fin: Semaine,
    ) -> Dict[str, float]:
        """
        Calcule la capacite disponible par semaine.

        La capacite = nombre_utilisateurs_actifs * heures_travail_semaine.

        Args:
            semaine_debut: Premiere semaine.
            semaine_fin: Derniere semaine.

        Returns:
            Dict {semaine_code: capacite_heures}.
        """
        from modules.auth.infrastructure.persistence import UserModel

        # Compter les utilisateurs actifs
        count_actifs = self.session.query(func.count(UserModel.id)).filter(
            UserModel.is_active == True,
        ).scalar() or 0

        # Generer les semaines
        semaines = self._generate_semaines(semaine_debut, semaine_fin)

        # Capacite = nb utilisateurs * 35h pour chaque semaine
        capacite = count_actifs * self.HEURES_PAR_SEMAINE

        return {s.code: capacite for s in semaines}

    def get_utilisateurs_non_planifies_par_semaine(
        self,
        semaine_debut: Semaine,
        semaine_fin: Semaine,
    ) -> Dict[str, int]:
        """
        Compte les utilisateurs non planifies par semaine (PDC-15).

        Args:
            semaine_debut: Premiere semaine.
            semaine_fin: Derniere semaine.

        Returns:
            Dict {semaine_code: nombre_non_planifies}.
        """
        from modules.auth.infrastructure.persistence import UserModel
        from ..persistence import AffectationModel

        semaines = self._generate_semaines(semaine_debut, semaine_fin)

        # Compter le total d'utilisateurs actifs
        total_actifs = self.session.query(func.count(UserModel.id)).filter(
            UserModel.is_active == True,
        ).scalar() or 0

        result = {}
        for semaine in semaines:
            date_debut, date_fin = semaine.date_range()

            # Compter les utilisateurs ayant au moins une affectation cette semaine
            utilisateurs_planifies = self.session.query(
                func.count(func.distinct(AffectationModel.utilisateur_id))
            ).filter(
                AffectationModel.date >= date_debut,
                AffectationModel.date <= date_fin,
            ).scalar() or 0

            # Non planifies = total - planifies
            non_planifies = max(total_actifs - utilisateurs_planifies, 0)
            result[semaine.code] = non_planifies

        return result

    # =========================================================================
    # Implementation AffectationProviderForOccupation (get_occupation_details)
    # =========================================================================

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
        from ..persistence import AffectationModel
        from modules.auth.infrastructure.persistence import UserModel

        date_debut, date_fin = semaine.date_range()

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

        heures_par_type: Dict[str, float] = {}
        for metier, count in results:
            # Mapper le metier vers le type_metier
            type_metier = self._map_metier_to_type(metier)
            heures = count * self.HEURES_PAR_JOUR
            heures_par_type[type_metier] = heures_par_type.get(type_metier, 0.0) + heures

        return heures_par_type

    # =========================================================================
    # Methodes utilitaires
    # =========================================================================

    def _generate_semaines(
        self,
        debut: Semaine,
        fin: Semaine,
    ) -> List[Semaine]:
        """Genere la liste des semaines entre debut et fin."""
        semaines = []
        current = debut
        while current <= fin:
            semaines.append(current)
            current = current.next()
        return semaines

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
