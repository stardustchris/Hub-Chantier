"""Use Cases pour le tableau de bord devis.

DEV-17: Tableau de bord devis - KPI pipeline commercial.
"""

from decimal import Decimal, ROUND_HALF_UP

from ...domain.value_objects import StatutDevis
from ...domain.repositories.devis_repository import DevisRepository
from ..dtos.dashboard_dtos import DashboardDevisDTO, KPIDevisDTO, DevisRecentDTO


class GetDashboardDevisUseCase:
    """Use case pour obtenir le tableau de bord des devis.

    DEV-17: Nb par statut, montant total pipeline, taux conversion.
    """

    def __init__(self, devis_repository: DevisRepository):
        self._devis_repository = devis_repository

    def execute(self) -> DashboardDevisDTO:
        """Calcule les KPI du pipeline commercial.

        Returns:
            Le DTO du dashboard avec KPI et devis recents.
        """
        # Compter par statut
        counts = self._devis_repository.count_by_statut()
        totaux = self._devis_repository.somme_montant_by_statut()

        nb_total = sum(counts.values())
        nb_accepte = counts.get(StatutDevis.ACCEPTE.value, 0)
        nb_refuse = counts.get(StatutDevis.REFUSE.value, 0)
        nb_perdu = counts.get(StatutDevis.PERDU.value, 0)

        # Pipeline = devis en cours (pas brouillon, pas final)
        statuts_pipeline = [
            StatutDevis.EN_VALIDATION.value,
            StatutDevis.ENVOYE.value,
            StatutDevis.VU.value,
            StatutDevis.EN_NEGOCIATION.value,
        ]
        total_pipeline = sum(
            Decimal(str(totaux.get(s, 0))) for s in statuts_pipeline
        )
        total_accepte = Decimal(str(totaux.get(StatutDevis.ACCEPTE.value, 0)))

        # Taux conversion = acceptes / (acceptes + refuses + perdus)
        nb_decides = nb_accepte + nb_refuse + nb_perdu
        taux_conversion = (
            Decimal(str(nb_accepte)) / Decimal(str(nb_decides)) * Decimal("100")
            if nb_decides > 0
            else Decimal("0")
        )

        kpi = KPIDevisDTO(
            nb_brouillon=counts.get(StatutDevis.BROUILLON.value, 0),
            nb_en_validation=counts.get(StatutDevis.EN_VALIDATION.value, 0),
            nb_envoye=counts.get(StatutDevis.ENVOYE.value, 0),
            nb_vu=counts.get(StatutDevis.VU.value, 0),
            nb_en_negociation=counts.get(StatutDevis.EN_NEGOCIATION.value, 0),
            nb_accepte=nb_accepte,
            nb_refuse=nb_refuse,
            nb_perdu=nb_perdu,
            nb_expire=counts.get(StatutDevis.EXPIRE.value, 0),
            total_pipeline_ht=str(total_pipeline),
            total_accepte_ht=str(total_accepte),
            taux_conversion=str(taux_conversion.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
            nb_total=nb_total,
        )

        # Devis recents
        recents = self._devis_repository.find_all(limit=10, offset=0)
        derniers_devis = [
            DevisRecentDTO(
                id=d.id,
                numero=d.numero,
                client_nom=d.client_nom,
                objet=d.objet,
                statut=d.statut.value,
                montant_total_ht=str(d.montant_total_ht),
                date_creation=d.date_creation.isoformat() if d.date_creation else "",
            )
            for d in recents
        ]

        return DashboardDevisDTO(kpi=kpi, derniers_devis=derniers_devis)
