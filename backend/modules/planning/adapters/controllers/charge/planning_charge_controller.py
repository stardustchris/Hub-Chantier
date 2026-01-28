"""Controller pour les endpoints planning de charge."""

from typing import List

from ...application.dtos import (
    CreateBesoinDTO,
    UpdateBesoinDTO,
    PlanningChargeFiltersDTO,
    BesoinChargeDTO,
    PlanningChargeDTO,
    OccupationDetailsDTO,
)
from ...application.use_cases import (
    CreateBesoinUseCase,
    UpdateBesoinUseCase,
    DeleteBesoinUseCase,
    GetPlanningChargeUseCase,
    GetBesoinsByChantierUseCase,
    GetOccupationDetailsUseCase,
)
from .planning_charge_schemas import (
    CreateBesoinRequest,
    UpdateBesoinRequest,
    PlanningChargeFiltersRequest,
    BesoinChargeResponse,
    PlanningChargeResponse,
    OccupationDetailsResponse,
    ChantierChargeResponse,
    SemaineChargeResponse,
    CelluleChargeResponse,
    FooterChargeResponse,
    TypeOccupationResponse,
    ListeBesoinResponse,
)


class PlanningChargeController:
    """
    Controller pour le module planning de charge.

    Convertit les requetes HTTP en appels use cases et les reponses
    use cases en schemas de reponse HTTP.
    """

    def __init__(
        self,
        create_besoin_uc: CreateBesoinUseCase,
        update_besoin_uc: UpdateBesoinUseCase,
        delete_besoin_uc: DeleteBesoinUseCase,
        get_planning_uc: GetPlanningChargeUseCase,
        get_besoins_uc: GetBesoinsByChantierUseCase,
        get_occupation_uc: GetOccupationDetailsUseCase,
    ):
        """
        Initialise le controller.

        Args:
            create_besoin_uc: Use case creation besoin.
            update_besoin_uc: Use case mise a jour besoin.
            delete_besoin_uc: Use case suppression besoin.
            get_planning_uc: Use case planning de charge.
            get_besoins_uc: Use case besoins par chantier.
            get_occupation_uc: Use case details occupation.
        """
        self.create_besoin_uc = create_besoin_uc
        self.update_besoin_uc = update_besoin_uc
        self.delete_besoin_uc = delete_besoin_uc
        self.get_planning_uc = get_planning_uc
        self.get_besoins_uc = get_besoins_uc
        self.get_occupation_uc = get_occupation_uc

    def create_besoin(
        self,
        request: CreateBesoinRequest,
        current_user_id: int,
    ) -> BesoinChargeResponse:
        """Cree un nouveau besoin de charge."""
        dto = CreateBesoinDTO(
            chantier_id=request.chantier_id,
            semaine_code=request.semaine_code,
            type_metier=request.type_metier,
            besoin_heures=request.besoin_heures,
            note=request.note,
        )

        result = self.create_besoin_uc.execute(dto, created_by=current_user_id)
        return self._to_besoin_response(result)

    def update_besoin(
        self,
        besoin_id: int,
        request: UpdateBesoinRequest,
        current_user_id: int,
    ) -> BesoinChargeResponse:
        """Met a jour un besoin existant."""
        dto = UpdateBesoinDTO(
            besoin_heures=request.besoin_heures,
            note=request.note,
            type_metier=request.type_metier,
        )

        result = self.update_besoin_uc.execute(
            besoin_id=besoin_id,
            dto=dto,
            updated_by=current_user_id,
        )
        return self._to_besoin_response(result)

    def delete_besoin(
        self,
        besoin_id: int,
        current_user_id: int,
    ) -> bool:
        """Supprime un besoin."""
        return self.delete_besoin_uc.execute(
            besoin_id=besoin_id,
            deleted_by=current_user_id,
        )

    def get_planning_charge(
        self,
        request: PlanningChargeFiltersRequest,
    ) -> PlanningChargeResponse:
        """Recupere le planning de charge complet."""
        filters = PlanningChargeFiltersDTO(
            semaine_debut=request.semaine_debut,
            semaine_fin=request.semaine_fin,
            recherche=request.recherche,
            mode_avance=request.mode_avance,
            unite=request.unite,
        )

        result = self.get_planning_uc.execute(filters)
        return self._to_planning_response(result)

    def get_besoins_by_chantier(
        self,
        chantier_id: int,
        semaine_debut: str,
        semaine_fin: str,
        page: int = 1,
        page_size: int = 50,
    ) -> ListeBesoinResponse:
        """Recupere les besoins d'un chantier avec pagination."""
        result = self.get_besoins_uc.execute(
            chantier_id=chantier_id,
            semaine_debut=semaine_debut,
            semaine_fin=semaine_fin,
        )

        # Pagination
        total = len(result)
        total_pages = (total + page_size - 1) // page_size if total > 0 else 1
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_result = result[start_idx:end_idx]

        items = [self._to_besoin_response(b) for b in paginated_result]
        return ListeBesoinResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    def get_occupation_details(
        self,
        semaine_code: str,
    ) -> OccupationDetailsResponse:
        """Recupere les details d'occupation pour une semaine."""
        result = self.get_occupation_uc.execute(semaine_code)
        return self._to_occupation_response(result)

    # --- Methodes de conversion ---

    def _to_besoin_response(self, dto: BesoinChargeDTO) -> BesoinChargeResponse:
        """Convertit un DTO en schema de reponse."""
        return BesoinChargeResponse(
            id=dto.id,
            chantier_id=dto.chantier_id,
            semaine_code=dto.semaine_code,
            semaine_label=dto.semaine_label,
            type_metier=dto.type_metier,
            type_metier_label=dto.type_metier_label,
            type_metier_couleur=dto.type_metier_couleur,
            besoin_heures=dto.besoin_heures,
            besoin_jours_homme=dto.besoin_jours_homme,
            note=dto.note,
            created_by=dto.created_by,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
        )

    def _to_planning_response(self, dto: PlanningChargeDTO) -> PlanningChargeResponse:
        """Convertit le DTO planning en schema de reponse."""
        chantiers = []
        for c in dto.chantiers:
            semaines = []
            for s in c.semaines:
                semaines.append(SemaineChargeResponse(
                    code=s.code,
                    label=s.label,
                    cellule=CelluleChargeResponse(
                        planifie_heures=s.cellule.planifie_heures,
                        besoin_heures=s.cellule.besoin_heures,
                        besoin_non_couvert=s.cellule.besoin_non_couvert,
                        has_besoin=s.cellule.has_besoin,
                        est_couvert=s.cellule.est_couvert,
                    ),
                ))

            chantiers.append(ChantierChargeResponse(
                id=c.id,
                code=c.code,
                nom=c.nom,
                couleur=c.couleur,
                charge_totale=c.charge_totale,
                semaines=semaines,
            ))

        footer = []
        for f in dto.footer:
            footer.append(FooterChargeResponse(
                semaine_code=f.semaine_code,
                taux_occupation=f.taux_occupation,
                taux_couleur=f.taux_couleur,
                taux_label=f.taux_label,
                alerte_surcharge=f.alerte_surcharge,
                a_recruter=f.a_recruter,
                a_placer=f.a_placer,
            ))

        return PlanningChargeResponse(
            total_chantiers=dto.total_chantiers,
            semaine_debut=dto.semaine_debut,
            semaine_fin=dto.semaine_fin,
            unite=dto.unite,
            semaines=dto.semaines,
            chantiers=chantiers,
            footer=footer,
            capacite_totale=dto.capacite_totale,
            planifie_total=dto.planifie_total,
            besoin_total=dto.besoin_total,
        )

    def _to_occupation_response(
        self,
        dto: OccupationDetailsDTO,
    ) -> OccupationDetailsResponse:
        """Convertit le DTO occupation en schema de reponse."""
        types = []
        for t in dto.types:
            types.append(TypeOccupationResponse(
                type_metier=t.type_metier,
                type_metier_label=t.type_metier_label,
                type_metier_couleur=t.type_metier_couleur,
                planifie_heures=t.planifie_heures,
                besoin_heures=t.besoin_heures,
                capacite_heures=t.capacite_heures,
                taux_occupation=t.taux_occupation,
                taux_couleur=t.taux_couleur,
                alerte=t.alerte,
            ))

        return OccupationDetailsResponse(
            semaine_code=dto.semaine_code,
            semaine_label=dto.semaine_label,
            taux_global=dto.taux_global,
            taux_global_couleur=dto.taux_global_couleur,
            alerte_globale=dto.alerte_globale,
            types=types,
            planifie_total=dto.planifie_total,
            besoin_total=dto.besoin_total,
            capacite_totale=dto.capacite_totale,
            a_recruter=dto.a_recruter,
            a_placer=dto.a_placer,
        )
