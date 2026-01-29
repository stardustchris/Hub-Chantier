"""Provider pour integration avec le module auth (utilisateurs)."""

from typing import Dict
from sqlalchemy.orm import Session
from sqlalchemy import text

from ...application.use_cases.charge.get_occupation_details import UtilisateurProvider
from ...domain.value_objects import Semaine

from shared.infrastructure.user_queries import (
    count_active_users,
    count_active_users_by_metier,
)


class SQLAlchemyUtilisateurProvider(UtilisateurProvider):
    """
    Implementation SQLAlchemy de l'UtilisateurProvider.

    Recupere les informations sur les utilisateurs et leur capacite
    par type de metier, sans importer UserModel directement.
    """

    # Heures de travail par semaine (base 35h)
    HEURES_PAR_SEMAINE = 35.0

    def __init__(self, session: Session):
        """
        Initialise le provider.

        Args:
            session: Session SQLAlchemy.
        """
        self.session = session

    def get_capacite_par_type_metier(
        self,
        semaine: Semaine,
    ) -> Dict[str, float]:
        """
        Recupere la capacite disponible par type de metier.

        La capacite = nombre d'utilisateurs actifs du type * heures/semaine.

        Args:
            semaine: La semaine concernee.

        Returns:
            Dict {type_metier: capacite_heures}.
        """
        counts = self.get_count_par_type_metier()

        return {
            type_metier: count * self.HEURES_PAR_SEMAINE
            for type_metier, count in counts.items()
        }

    def get_count_par_type_metier(self) -> Dict[str, int]:
        """
        Compte les utilisateurs actifs par type de metier.

        Returns:
            Dict {type_metier: count}.
        """
        raw_counts = count_active_users_by_metier(self.session)

        counts: Dict[str, int] = {}
        for metier, count in raw_counts.items():
            type_metier = self._map_metier_to_type(metier)
            counts[type_metier] = counts.get(type_metier, 0) + count

        return counts

    def get_total_utilisateurs_actifs(self) -> int:
        """
        Compte le nombre total d'utilisateurs actifs.

        Returns:
            Nombre d'utilisateurs actifs.
        """
        return count_active_users(self.session)

    def get_utilisateurs_disponibles_semaine(
        self,
        semaine: Semaine,
    ) -> int:
        """
        Compte les utilisateurs disponibles (non affectes) pour une semaine.

        Args:
            semaine: La semaine.

        Returns:
            Nombre d'utilisateurs non affectes.
        """
        date_debut, date_fin = semaine.date_range()

        # Raw SQL: get distinct user IDs with affectations this week
        rows = self.session.execute(
            text(
                "SELECT DISTINCT utilisateur_id FROM affectations "
                "WHERE date >= :debut AND date <= :fin"
            ),
            {"debut": date_debut, "fin": date_fin},
        ).fetchall()

        affectes_ids = [row[0] for row in rows]

        # Count active users NOT in that set
        from shared.infrastructure.user_queries import count_active_users_not_in_ids
        return count_active_users_not_in_ids(self.session, affectes_ids)

    def _map_metier_to_type(self, metier: str) -> str:
        """
        Mappe un metier utilisateur vers un type de metier.

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
            "sous-traitant": "sous_traitant",
            "sous traitant": "sous_traitant",
            "prestataire": "sous_traitant",
        }

        for key, value in mapping.items():
            if key in metier_lower:
                return value

        return "employe"
