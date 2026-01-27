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
        # Assure que c'est un lundi
        if semaine_debut.weekday() != 0:
            days_since_monday = semaine_debut.weekday()
            semaine_debut = semaine_debut - timedelta(days=days_since_monday)

        semaine_fin = semaine_debut + timedelta(days=6)

        # Récupère tous les pointages de la semaine
        pointages, _ = self.pointage_repo.search(
            date_debut=semaine_debut,
            date_fin=semaine_fin,
            chantier_id=chantier_ids[0] if chantier_ids and len(chantier_ids) == 1 else None,
            skip=0,
            limit=10000,  # Pas de limite pour la vue
        )

        # Filtre par chantiers si spécifié
        if chantier_ids:
            pointages = [p for p in pointages if p.chantier_id in chantier_ids]

        # Groupe par chantier
        by_chantier: Dict[int, List] = defaultdict(list)
        for p in pointages:
            by_chantier[p.chantier_id].append(p)

        # Construit les DTOs
        result = []
        for chantier_id, chantier_pointages in by_chantier.items():
            # Info chantier du premier pointage
            first_p = chantier_pointages[0]
            chantier_nom = first_p.chantier_nom or f"Chantier {chantier_id}"
            chantier_couleur = first_p.chantier_couleur or "#808080"

            # Total heures
            total_minutes = sum(p.total_heures.total_minutes for p in chantier_pointages)
            total_heures = Duree.from_minutes(total_minutes)

            # Pointages par jour
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

            result.append(
                VueChantierDTO(
                    chantier_id=chantier_id,
                    chantier_nom=chantier_nom,
                    chantier_couleur=chantier_couleur,
                    total_heures=str(total_heures),
                    total_heures_decimal=total_heures.decimal,
                    pointages_par_jour=pointages_par_jour,
                    total_par_jour=total_par_jour,
                )
            )

        return result

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
        # Assure que c'est un lundi
        if semaine_debut.weekday() != 0:
            days_since_monday = semaine_debut.weekday()
            semaine_debut = semaine_debut - timedelta(days=days_since_monday)

        semaine_fin = semaine_debut + timedelta(days=6)

        # Récupère tous les pointages de la semaine
        pointages, _ = self.pointage_repo.search(
            date_debut=semaine_debut,
            date_fin=semaine_fin,
            utilisateur_id=utilisateur_ids[0] if utilisateur_ids and len(utilisateur_ids) == 1 else None,
            skip=0,
            limit=10000,
        )

        # Filtre par utilisateurs si spécifié
        if utilisateur_ids:
            pointages = [p for p in pointages if p.utilisateur_id in utilisateur_ids]

        # Groupe par utilisateur
        by_utilisateur: Dict[int, List] = defaultdict(list)
        for p in pointages:
            by_utilisateur[p.utilisateur_id].append(p)

        # Construit les DTOs
        result = []
        for utilisateur_id, user_pointages in by_utilisateur.items():
            # Info utilisateur du premier pointage
            first_p = user_pointages[0]
            utilisateur_nom = first_p.utilisateur_nom or f"Utilisateur {utilisateur_id}"

            # Total heures
            total_minutes = sum(p.total_heures.total_minutes for p in user_pointages)
            total_heures = Duree.from_minutes(total_minutes)

            # Groupe par chantier
            by_chantier: Dict[int, List] = defaultdict(list)
            for p in user_pointages:
                by_chantier[p.chantier_id].append(p)

            # Chantiers
            chantiers = []
            for chantier_id, chantier_pointages in by_chantier.items():
                first_cp = chantier_pointages[0]
                chantier_nom = first_cp.chantier_nom or f"Chantier {chantier_id}"
                chantier_couleur = first_cp.chantier_couleur or "#808080"

                chantier_total = sum(p.total_heures.total_minutes for p in chantier_pointages)

                # Pointages par jour (objets complets pour le frontend)
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

                chantiers.append(
                    ChantierPointageDTO(
                        chantier_id=chantier_id,
                        chantier_nom=chantier_nom,
                        chantier_couleur=chantier_couleur,
                        total_heures=str(Duree.from_minutes(chantier_total)),
                        pointages_par_jour=pointages_par_jour,
                    )
                )

            # Totaux par jour (FDH-09)
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

            result.append(
                VueCompagnonDTO(
                    utilisateur_id=utilisateur_id,
                    utilisateur_nom=utilisateur_nom,
                    total_heures=str(total_heures),
                    total_heures_decimal=total_heures.decimal,
                    chantiers=chantiers,
                    totaux_par_jour=totaux_par_jour,
                )
            )

        return result
