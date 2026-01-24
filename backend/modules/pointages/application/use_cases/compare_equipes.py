"""Use Case: Comparer les équipes (FDH-15)."""

from datetime import date, timedelta
from collections import defaultdict

from ...domain.repositories import PointageRepository
from ..dtos import ComparaisonEquipesDTO, EquipeStatsDTO, EcartDTO


class CompareEquipesUseCase:
    """
    Compare les équipes par chantier pour détecter les écarts.

    Implémente FDH-15: Comparaison inter-équipes (Détection automatique des écarts).
    """

    def __init__(self, pointage_repo: PointageRepository):
        """
        Initialise le use case.

        Args:
            pointage_repo: Repository des pointages.
        """
        self.pointage_repo = pointage_repo

    def execute(
        self,
        semaine_debut: date,
        heures_planifiees_par_chantier: dict = None,
        seuil_ecart_pourcentage: float = 15.0,
    ) -> ComparaisonEquipesDTO:
        """
        Compare les équipes pour une semaine donnée.

        Args:
            semaine_debut: Date du lundi de la semaine.
            heures_planifiees_par_chantier: Dict {chantier_id: heures_planifiees}.
            seuil_ecart_pourcentage: Seuil pour détecter un écart (défaut 15%).

        Returns:
            DTO avec les stats par équipe et les écarts détectés.
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
            skip=0,
            limit=100000,
        )

        # Groupe par chantier
        by_chantier = defaultdict(list)
        for p in pointages:
            by_chantier[p.chantier_id].append(p)

        # Calcule les stats par équipe (chantier)
        equipes = []
        ecarts = []

        for chantier_id, chantier_pointages in by_chantier.items():
            # Nom du chantier
            first_p = chantier_pointages[0]
            chantier_nom = first_p.chantier_nom or f"Chantier {chantier_id}"

            # Calcule les heures réalisées
            total_minutes = sum(p.total_heures.total_minutes for p in chantier_pointages)
            heures_realisees = total_minutes / 60.0

            # Heures planifiées (depuis paramètre ou estimation)
            heures_planifiees = 0.0
            if heures_planifiees_par_chantier and chantier_id in heures_planifiees_par_chantier:
                heures_planifiees = heures_planifiees_par_chantier[chantier_id]
            else:
                # Estimation: 35h * nombre d'utilisateurs uniques
                utilisateurs_uniques = len(set(p.utilisateur_id for p in chantier_pointages))
                heures_planifiees = 35.0 * utilisateurs_uniques

            # Taux de complétion
            taux_completion = 0.0
            if heures_planifiees > 0:
                taux_completion = (heures_realisees / heures_planifiees) * 100

            # Nombre d'utilisateurs
            nombre_utilisateurs = len(set(p.utilisateur_id for p in chantier_pointages))

            equipes.append(
                EquipeStatsDTO(
                    chantier_id=chantier_id,
                    chantier_nom=chantier_nom,
                    total_heures_planifiees=round(heures_planifiees, 2),
                    total_heures_realisees=round(heures_realisees, 2),
                    taux_completion=round(taux_completion, 1),
                    nombre_utilisateurs=nombre_utilisateurs,
                )
            )

            # Détecte les écarts
            if heures_planifiees > 0:
                ecart_pourcentage = abs(taux_completion - 100)
                if ecart_pourcentage > seuil_ecart_pourcentage:
                    ecart_heures = heures_realisees - heures_planifiees
                    type_ecart = "surplus" if ecart_heures > 0 else "deficit"

                    ecarts.append(
                        EcartDTO(
                            type_ecart=type_ecart,
                            chantier_id=chantier_id,
                            chantier_nom=chantier_nom,
                            heures_planifiees=round(heures_planifiees, 2),
                            heures_realisees=round(heures_realisees, 2),
                            ecart_heures=round(abs(ecart_heures), 2),
                            ecart_pourcentage=round(ecart_pourcentage, 1),
                        )
                    )

        iso_cal = semaine_debut.isocalendar()

        return ComparaisonEquipesDTO(
            semaine=f"Semaine {iso_cal[1]} - {iso_cal[0]}",
            equipes=equipes,
            ecarts_detectes=ecarts,
        )
