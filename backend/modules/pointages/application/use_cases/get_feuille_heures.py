"""Use Case: Récupérer une feuille d'heures."""

from datetime import date, timedelta
from typing import Optional, List, Dict

from ...domain.entities import FeuilleHeures, Pointage
from ...domain.repositories import FeuilleHeuresRepository, PointageRepository
from ...domain.value_objects import TypeVariablePaie
from ..dtos import (
    FeuilleHeuresDTO,
    PointageJourDTO,
    VariablePaieSemaineDTO,
    NavigationSemaineDTO,
)


JOURS_SEMAINE = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]


class GetFeuilleHeuresUseCase:
    """
    Récupère une feuille d'heures avec tous ses détails.

    Implémente FDH-02 (navigation semaine), FDH-05 (vue tabulaire),
    FDH-08 (total par ligne), FDH-09 (total groupe).
    """

    def __init__(
        self,
        feuille_repo: FeuilleHeuresRepository,
        pointage_repo: PointageRepository,
    ):
        """
        Initialise le use case.

        Args:
            feuille_repo: Repository des feuilles d'heures.
            pointage_repo: Repository des pointages.
        """
        self.feuille_repo = feuille_repo
        self.pointage_repo = pointage_repo

    def execute(self, feuille_id: int) -> Optional[FeuilleHeuresDTO]:
        """
        Récupère une feuille d'heures par son ID.

        Args:
            feuille_id: ID de la feuille.

        Returns:
            Le DTO de la feuille ou None si non trouvée.
        """
        feuille = self.feuille_repo.find_by_id(feuille_id)
        if not feuille:
            return None

        # Charge les pointages de la semaine
        pointages = self.pointage_repo.find_by_utilisateur_and_semaine(
            utilisateur_id=feuille.utilisateur_id,
            semaine_debut=feuille.semaine_debut,
        )
        feuille.pointages = pointages

        return self._to_dto(feuille)

    def execute_by_utilisateur_semaine(
        self, utilisateur_id: int, semaine_debut: date
    ) -> Optional[FeuilleHeuresDTO]:
        """
        Récupère une feuille par utilisateur et semaine.

        Args:
            utilisateur_id: ID de l'utilisateur.
            semaine_debut: Date du lundi de la semaine.

        Returns:
            Le DTO de la feuille ou None.
        """
        # Assure que c'est un lundi
        if semaine_debut.weekday() != 0:
            days_since_monday = semaine_debut.weekday()
            semaine_debut = semaine_debut - timedelta(days=days_since_monday)

        feuille = self.feuille_repo.find_by_utilisateur_and_semaine(
            utilisateur_id=utilisateur_id,
            semaine_debut=semaine_debut,
        )

        if not feuille:
            # Crée une feuille vide pour la réponse
            feuille, _ = self.feuille_repo.get_or_create(
                utilisateur_id=utilisateur_id,
                semaine_debut=semaine_debut,
            )

        # Charge les pointages
        pointages = self.pointage_repo.find_by_utilisateur_and_semaine(
            utilisateur_id=utilisateur_id,
            semaine_debut=semaine_debut,
        )
        feuille.pointages = pointages

        return self._to_dto(feuille)

    def get_navigation(self, semaine_debut: date) -> NavigationSemaineDTO:
        """
        Retourne les informations de navigation (FDH-02).

        Args:
            semaine_debut: Date du lundi de la semaine courante.

        Returns:
            DTO avec les informations de navigation.
        """
        # Assure que c'est un lundi
        if semaine_debut.weekday() != 0:
            days_since_monday = semaine_debut.weekday()
            semaine_debut = semaine_debut - timedelta(days=days_since_monday)

        iso_calendar = semaine_debut.isocalendar()

        return NavigationSemaineDTO(
            semaine_courante=semaine_debut,
            semaine_precedente=semaine_debut - timedelta(weeks=1),
            semaine_suivante=semaine_debut + timedelta(weeks=1),
            numero_semaine=iso_calendar[1],
            annee=iso_calendar[0],
            label=f"Semaine {iso_calendar[1]} - {iso_calendar[0]}",
        )

    def _to_dto(self, feuille: FeuilleHeures) -> FeuilleHeuresDTO:
        """Convertit l'entité en DTO."""
        # Pointages par jour
        pointages_dto = []
        for p in feuille.pointages:
            jour_idx = p.date_pointage.weekday()
            jour_nom = JOURS_SEMAINE[jour_idx] if jour_idx < 7 else "inconnu"

            pointages_dto.append(
                PointageJourDTO(
                    id=p.id,
                    chantier_id=p.chantier_id,
                    chantier_nom=p.chantier_nom or f"Chantier {p.chantier_id}",
                    chantier_couleur=p.chantier_couleur or "#808080",
                    date_pointage=p.date_pointage,
                    jour_semaine=jour_nom,
                    heures_normales=str(p.heures_normales),
                    heures_supplementaires=str(p.heures_supplementaires),
                    total_heures=str(p.total_heures),
                    statut=p.statut.value,
                    is_editable=p.is_editable,
                )
            )

        # Variables de paie par type
        variables_dto = []
        variables_par_type = feuille.get_variables_par_type()
        for type_var, total in variables_par_type.items():
            variables_dto.append(
                VariablePaieSemaineDTO(
                    type_variable=type_var.value,
                    type_variable_libelle=type_var.libelle,
                    total=str(total),
                )
            )

        # Totaux par jour
        totaux_par_jour: Dict[str, str] = {}
        for jour in feuille.jours_semaine:
            jour_nom = JOURS_SEMAINE[jour.weekday()]
            total_jour = sum(
                (p.total_heures.total_minutes for p in feuille.pointages if p.date_pointage == jour),
                0,
            )
            from ...domain.value_objects import Duree
            totaux_par_jour[jour_nom] = str(Duree.from_minutes(total_jour))

        # Totaux par chantier
        totaux_par_chantier: Dict[int, str] = {}
        for chantier_id, duree in feuille.total_heures_par_chantier().items():
            totaux_par_chantier[chantier_id] = str(duree)

        return FeuilleHeuresDTO(
            id=feuille.id,
            utilisateur_id=feuille.utilisateur_id,
            semaine_debut=feuille.semaine_debut,
            semaine_fin=feuille.semaine_fin,
            annee=feuille.annee,
            numero_semaine=feuille.numero_semaine,
            label_semaine=feuille.label_semaine,
            statut_global=feuille.statut_global.value,
            total_heures_normales=str(feuille.total_heures_normales),
            total_heures_supplementaires=str(feuille.total_heures_supplementaires),
            total_heures=str(feuille.total_heures),
            total_heures_decimal=feuille.total_heures_decimal,
            commentaire_global=feuille.commentaire_global,
            is_complete=feuille.is_complete,
            is_all_validated=feuille.is_all_validated,
            created_at=feuille.created_at,
            updated_at=feuille.updated_at,
            utilisateur_nom=feuille.utilisateur_nom,
            pointages=pointages_dto,
            variables_paie=variables_dto,
            totaux_par_jour=totaux_par_jour,
            totaux_par_chantier=totaux_par_chantier,
        )
