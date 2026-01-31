"""Use Cases pour le suivi des couts materiel.

FIN-10: Suivi couts materiel - calculs a partir des reservations validees.
"""

from datetime import date
from typing import Optional

from ...domain.repositories.cout_materiel_repository import (
    CoutMaterielRepository,
)
from ..dtos.cout_dtos import CoutMaterielDTO, CoutMaterielSummaryDTO


class GetCoutMaterielUseCase:
    """Use case pour recuperer les couts materiel d'un chantier.

    FIN-10: Aggrege les reservations validees par ressource et calcule les couts.
    """

    def __init__(self, cout_materiel_repository: CoutMaterielRepository):
        self._cout_materiel_repository = cout_materiel_repository

    def execute(
        self,
        chantier_id: int,
        date_debut: Optional[date] = None,
        date_fin: Optional[date] = None,
    ) -> CoutMaterielSummaryDTO:
        """Calcule les couts materiel d'un chantier.

        Args:
            chantier_id: L'ID du chantier.
            date_debut: Date de debut de la periode (optionnel).
            date_fin: Date de fin de la periode (optionnel).

        Returns:
            Le resume des couts materiel.
        """
        # Obtenir le detail par ressource (domain VOs)
        ressources = self._cout_materiel_repository.calculer_cout_par_ressource(
            chantier_id, date_debut, date_fin
        )

        # Calculer le cout total
        cout_total = self._cout_materiel_repository.calculer_cout_chantier(
            chantier_id, date_debut, date_fin
        )

        # Mapper domain VOs -> application DTOs
        details = []
        for res in ressources:
            details.append(
                CoutMaterielDTO(
                    ressource_id=res.ressource_id,
                    nom=res.nom,
                    code=res.code,
                    jours_reservation=res.jours_reservation,
                    tarif_journalier=str(res.tarif_journalier),
                    cout_total=str(res.cout_total),
                )
            )

        return CoutMaterielSummaryDTO(
            chantier_id=chantier_id,
            cout_total=str(cout_total),
            details=details,
        )
