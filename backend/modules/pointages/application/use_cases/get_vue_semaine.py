"""Use Case: Obtenir les vues Chantiers et Compagnons (FDH-01)."""

from datetime import date, timedelta
from typing import List, Dict
from collections import defaultdict

from ...domain.repositories import PointageRepository
from ...domain.value_objects import Duree
from ..dtos import (
    VueChantierDTO,
    VueCompagnonDTO,
    PointageUtilisateurDTO,
    ChantierPointageDTO,
    PointageJourCompagnonDTO,
)


JOURS_SEMAINE = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]


class GetVueSemaineUseCase:
    """
    Retourne les vues Chantiers et Compagnons pour une semaine.

    Implémente FDH-01: 2 onglets de vue [Chantiers] [Compagnons/Sous-traitants].
    """

    def __init__(self, pointage_repo: PointageRepository):
        """
        Initialise le use case.

        Args:
            pointage_repo: Repository des pointages.
        """
        self.pointage_repo = pointage_repo

    def get_vue_chantiers(
        self,
        semaine_debut: date,
        chantier_ids: List[int] = None,
    ) -> List[VueChantierDTO]:
        """
        Retourne la vue par chantiers pour une semaine (FDH-01 onglet Chantiers).

        Args:
            semaine_debut: Date du lundi de la semaine.
            chantier_ids: Liste des chantiers à inclure (None = tous).

        Returns:
            Liste des vues par chantier.
        """
        # Préparer la période et récupérer les pointages
        semaine_debut, semaine_fin = self._get_semaine_range(semaine_debut)
        pointages = self._fetch_pointages_chantiers(semaine_debut, semaine_fin, chantier_ids)

        # Grouper par chantier
        by_chantier = self._group_by_chantier(pointages)

        # Construire les DTOs
        return [
            self._build_vue_chantier_dto(chantier_id, chantier_pointages, semaine_debut)
            for chantier_id, chantier_pointages in by_chantier.items()
        ]

    def _fetch_pointages_chantiers(
        self,
        semaine_debut: date,
        semaine_fin: date,
        chantier_ids: List[int] = None
    ):
        """Récupère les pointages de la semaine filtrés par chantier."""
        pointages, _ = self.pointage_repo.search(
            date_debut=semaine_debut,
            date_fin=semaine_fin,
            chantier_id=chantier_ids[0] if chantier_ids and len(chantier_ids) == 1 else None,
            skip=0,
            limit=10000,
        )
        if chantier_ids:
            pointages = [p for p in pointages if p.chantier_id in chantier_ids]
        return pointages

    def _group_by_chantier(self, pointages) -> Dict[int, List]:
        """Groupe les pointages par chantier."""
        by_chantier: Dict[int, List] = defaultdict(list)
        for p in pointages:
            by_chantier[p.chantier_id].append(p)
        return by_chantier

    def _build_vue_chantier_dto(
        self,
        chantier_id: int,
        chantier_pointages: List,
        semaine_debut: date
    ) -> VueChantierDTO:
        """Construit le DTO pour un chantier."""
        first_p = chantier_pointages[0]
        chantier_nom = first_p.chantier_nom or f"Chantier {chantier_id}"
        chantier_couleur = first_p.chantier_couleur or "#808080"
        total_heures = Duree.from_minutes(sum(p.total_heures.total_minutes for p in chantier_pointages))

        # Pointages par jour
        pointages_par_jour, total_par_jour = self._build_pointages_chantier_par_jour(
            chantier_pointages, semaine_debut
        )

        return VueChantierDTO(
            chantier_id=chantier_id,
            chantier_nom=chantier_nom,
            chantier_couleur=chantier_couleur,
            total_heures=str(total_heures),
            total_heures_decimal=total_heures.decimal,
            pointages_par_jour=pointages_par_jour,
            total_par_jour=total_par_jour,
        )

    def _build_pointages_chantier_par_jour(
        self,
        chantier_pointages: List,
        semaine_debut: date
    ) -> tuple[Dict[str, List[PointageUtilisateurDTO]], Dict[str, str]]:
        """Construit les pointages et totaux par jour pour un chantier."""
        pointages_par_jour: Dict[str, List[PointageUtilisateurDTO]] = {}
        total_par_jour: Dict[str, str] = {}

        for i in range(7):
            jour_date = semaine_debut + timedelta(days=i)
            jour_nom = JOURS_SEMAINE[i]
            jour_pointages = [p for p in chantier_pointages if p.date_pointage == jour_date]

            pointages_par_jour[jour_nom] = [
                PointageUtilisateurDTO(
                    pointage_id=p.id,
                    utilisateur_id=p.utilisateur_id,
                    utilisateur_nom=p.utilisateur_nom or f"Utilisateur {p.utilisateur_id}",
                    heures_normales=str(p.heures_normales),
                    heures_supplementaires=str(p.heures_supplementaires),
                    total_heures=str(p.total_heures),
                    statut=p.statut.value,
                )
                for p in jour_pointages
            ]

            jour_total = sum(p.total_heures.total_minutes for p in jour_pointages)
            total_par_jour[jour_nom] = str(Duree.from_minutes(jour_total))

        return pointages_par_jour, total_par_jour

    def get_vue_compagnons(
        self,
        semaine_debut: date,
        utilisateur_ids: List[int] = None,
    ) -> List[VueCompagnonDTO]:
        """
        Retourne la vue par compagnons pour une semaine (FDH-01 onglet Compagnons).

        Args:
            semaine_debut: Date du lundi de la semaine.
            utilisateur_ids: Liste des utilisateurs à inclure (None = tous).

        Returns:
            Liste des vues par compagnon.
        """
        # Préparer la période et récupérer les pointages
        semaine_debut, semaine_fin = self._get_semaine_range(semaine_debut)
        pointages = self._fetch_pointages_semaine(semaine_debut, semaine_fin, utilisateur_ids)

        # Grouper par utilisateur
        by_utilisateur = self._group_by_utilisateur(pointages)

        # Construire les DTOs
        return [
            self._build_vue_compagnon_dto(utilisateur_id, user_pointages, semaine_debut)
            for utilisateur_id, user_pointages in by_utilisateur.items()
        ]

    def _get_semaine_range(self, semaine_debut: date) -> tuple[date, date]:
        """Retourne le lundi et dimanche de la semaine."""
        if semaine_debut.weekday() != 0:
            days_since_monday = semaine_debut.weekday()
            semaine_debut = semaine_debut - timedelta(days=days_since_monday)
        semaine_fin = semaine_debut + timedelta(days=6)
        return semaine_debut, semaine_fin

    def _fetch_pointages_semaine(
        self,
        semaine_debut: date,
        semaine_fin: date,
        utilisateur_ids: List[int] = None
    ):
        """Récupère les pointages de la semaine filtrés par utilisateur."""
        pointages, _ = self.pointage_repo.search(
            date_debut=semaine_debut,
            date_fin=semaine_fin,
            utilisateur_id=utilisateur_ids[0] if utilisateur_ids and len(utilisateur_ids) == 1 else None,
            skip=0,
            limit=10000,
        )
        if utilisateur_ids:
            pointages = [p for p in pointages if p.utilisateur_id in utilisateur_ids]
        return pointages

    def _group_by_utilisateur(self, pointages) -> Dict[int, List]:
        """Groupe les pointages par utilisateur."""
        by_utilisateur: Dict[int, List] = defaultdict(list)
        for p in pointages:
            by_utilisateur[p.utilisateur_id].append(p)
        return by_utilisateur

    def _build_vue_compagnon_dto(
        self,
        utilisateur_id: int,
        user_pointages: List,
        semaine_debut: date
    ) -> VueCompagnonDTO:
        """Construit le DTO pour un compagnon."""
        utilisateur_nom = user_pointages[0].utilisateur_nom or f"Utilisateur {utilisateur_id}"
        total_heures = Duree.from_minutes(sum(p.total_heures.total_minutes for p in user_pointages))

        # Construire les chantiers
        chantiers = self._build_chantiers_dto(user_pointages, semaine_debut)

        # Calculer les totaux par jour
        totaux_par_jour = self._calculate_totaux_par_jour(user_pointages, semaine_debut)

        return VueCompagnonDTO(
            utilisateur_id=utilisateur_id,
            utilisateur_nom=utilisateur_nom,
            total_heures=str(total_heures),
            total_heures_decimal=total_heures.decimal,
            chantiers=chantiers,
            totaux_par_jour=totaux_par_jour,
        )

    def _build_chantiers_dto(self, user_pointages: List, semaine_debut: date) -> List[ChantierPointageDTO]:
        """Construit la liste des DTOs chantier pour un utilisateur."""
        by_chantier: Dict[int, List] = defaultdict(list)
        for p in user_pointages:
            by_chantier[p.chantier_id].append(p)

        chantiers = []
        for chantier_id, chantier_pointages in by_chantier.items():
            first_cp = chantier_pointages[0]
            chantier_nom = first_cp.chantier_nom or f"Chantier {chantier_id}"
            chantier_couleur = first_cp.chantier_couleur or "#808080"
            chantier_total = sum(p.total_heures.total_minutes for p in chantier_pointages)

            pointages_par_jour = self._build_pointages_par_jour(chantier_pointages, semaine_debut)

            chantiers.append(
                ChantierPointageDTO(
                    chantier_id=chantier_id,
                    chantier_nom=chantier_nom,
                    chantier_couleur=chantier_couleur,
                    total_heures=str(Duree.from_minutes(chantier_total)),
                    pointages_par_jour=pointages_par_jour,
                )
            )
        return chantiers

    def _build_pointages_par_jour(
        self,
        chantier_pointages: List,
        semaine_debut: date
    ) -> Dict[str, List[PointageJourCompagnonDTO]]:
        """Construit le dictionnaire des pointages par jour pour un chantier."""
        pointages_par_jour: Dict[str, List[PointageJourCompagnonDTO]] = {}
        for i in range(7):
            jour_date = semaine_debut + timedelta(days=i)
            jour_nom = JOURS_SEMAINE[i]
            jour_pointages = [p for p in chantier_pointages if p.date_pointage == jour_date]
            pointages_par_jour[jour_nom] = [
                PointageJourCompagnonDTO(
                    id=p.id,
                    utilisateur_id=p.utilisateur_id,
                    chantier_id=p.chantier_id,
                    date_pointage=str(p.date_pointage),
                    heures_normales=str(p.heures_normales),
                    heures_supplementaires=str(p.heures_supplementaires),
                    total_heures=str(p.total_heures),
                    statut=p.statut.value,
                    is_editable=p.is_editable,
                    commentaire=p.commentaire,
                )
                for p in jour_pointages
            ]
        return pointages_par_jour

    def _calculate_totaux_par_jour(self, user_pointages: List, semaine_debut: date) -> Dict[str, str]:
        """Calcule les totaux d'heures par jour pour un utilisateur."""
        totaux_par_jour: Dict[str, str] = {}
        for i in range(7):
            jour_date = semaine_debut + timedelta(days=i)
            jour_nom = JOURS_SEMAINE[i]
            jour_total = sum(
                p.total_heures.total_minutes
                for p in user_pointages
                if p.date_pointage == jour_date
            )
            totaux_par_jour[jour_nom] = str(Duree.from_minutes(jour_total))
        return totaux_par_jour
