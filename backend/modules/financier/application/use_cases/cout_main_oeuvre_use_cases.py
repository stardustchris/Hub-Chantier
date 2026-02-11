"""Use Cases pour le suivi des couts main-d'oeuvre.

FIN-09: Suivi couts main-d'oeuvre - calculs a partir des pointages valides.
"""

from datetime import date
from decimal import Decimal
from typing import Optional

from ...domain.repositories.cout_main_oeuvre_repository import (
    CoutMainOeuvreRepository,
)
from ..dtos.cout_dtos import CoutEmployeDTO, CoutMainOeuvreSummaryDTO


class GetCoutMainOeuvreUseCase:
    """Use case pour recuperer les couts main-d'oeuvre d'un chantier.

    FIN-09: Aggrege les pointages valides par employe et calcule les couts.
    """

    def __init__(self, cout_mo_repository: CoutMainOeuvreRepository):
        self._cout_mo_repository = cout_mo_repository

    def execute(
        self,
        chantier_id: int,
        date_debut: Optional[date] = None,
        date_fin: Optional[date] = None,
    ) -> CoutMainOeuvreSummaryDTO:
        """Calcule les couts main-d'oeuvre d'un chantier.

        Args:
            chantier_id: L'ID du chantier.
            date_debut: Date de debut de la periode (optionnel).
            date_fin: Date de fin de la periode (optionnel).

        Returns:
            Le resume des couts main-d'oeuvre.
        """
        # Obtenir le detail par employe (domain VOs)
        employes = self._cout_mo_repository.calculer_cout_par_employe(
            chantier_id, date_debut, date_fin
        )

        # Calculer le cout total
        cout_total = self._cout_mo_repository.calculer_cout_chantier(
            chantier_id, date_debut, date_fin
        )

        # Mapper domain VOs -> application DTOs
        total_heures = Decimal("0")
        details = []
        for emp in employes:
            total_heures += emp.heures_validees
            details.append(
                CoutEmployeDTO(
                    user_id=emp.user_id,
                    nom=emp.nom,
                    prenom=emp.prenom,
                    heures_validees=str(emp.heures_validees),
                    taux_horaire=str(emp.taux_horaire),
                    taux_horaire_charge=str(emp.taux_horaire_charge),
                    cout_total=str(emp.cout_total),
                )
            )

        return CoutMainOeuvreSummaryDTO(
            chantier_id=chantier_id,
            total_heures=str(total_heures),
            cout_total=str(cout_total),
            details=details,
        )
