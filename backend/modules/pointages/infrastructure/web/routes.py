"""Routes FastAPI pour le module pointages (feuilles d'heures)."""

from datetime import date
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from shared.infrastructure.database import get_db
from shared.infrastructure.web.dependencies import (
    get_current_user_id,
)
from shared.infrastructure.entity_info_impl import SQLAlchemyEntityInfoService
from ..persistence import (
    SQLAlchemyPointageRepository,
    SQLAlchemyFeuilleHeuresRepository,
    SQLAlchemyVariablePaieRepository,
)
from ..event_bus_impl import get_event_bus
from ...adapters.controllers import PointageController
from ...domain.events.heures_validated import HeuresValidatedEvent


router = APIRouter(prefix="/pointages", tags=["Feuilles d'heures"])


# ===== Pydantic Schemas =====


class CreatePointageRequest(BaseModel):
    """Requête de création de pointage."""

    utilisateur_id: int
    chantier_id: int
    date_pointage: date
    heures_normales: str = Field(..., pattern=r"^\d{1,2}:\d{2}$")
    heures_supplementaires: str = Field(default="00:00", pattern=r"^\d{1,2}:\d{2}$")
    commentaire: Optional[str] = None
    affectation_id: Optional[int] = None


class UpdatePointageRequest(BaseModel):
    """Requête de mise à jour de pointage."""

    heures_normales: Optional[str] = Field(None, pattern=r"^\d{1,2}:\d{2}$")
    heures_supplementaires: Optional[str] = Field(None, pattern=r"^\d{1,2}:\d{2}$")
    commentaire: Optional[str] = None


class SignPointageRequest(BaseModel):
    """Requête de signature de pointage."""

    signature: str


class RejectPointageRequest(BaseModel):
    """Requête de rejet de pointage."""

    motif: str


class CreateVariablePaieRequest(BaseModel):
    """Requête de création de variable de paie."""

    pointage_id: int
    type_variable: str
    valeur: float
    date_application: date
    commentaire: Optional[str] = None


class BulkCreateRequest(BaseModel):
    """Requête de création en masse depuis le planning."""

    utilisateur_id: int
    semaine_debut: date
    affectations: List[dict]


class ExportRequest(BaseModel):
    """Requête d'export."""

    format_export: str = Field(..., pattern=r"^(csv|xlsx|pdf|erp)$")
    date_debut: date
    date_fin: date
    utilisateur_ids: Optional[List[int]] = None
    chantier_ids: Optional[List[int]] = None
    inclure_variables_paie: bool = True
    inclure_signatures: bool = False


# ===== Dependencies =====


def get_controller(db: Session = Depends(get_db)) -> PointageController:
    """Factory pour le controller avec injection de dépendances."""
    pointage_repo = SQLAlchemyPointageRepository(db)
    feuille_repo = SQLAlchemyFeuilleHeuresRepository(db)
    variable_repo = SQLAlchemyVariablePaieRepository(db)
    event_bus = get_event_bus()
    entity_info_service = SQLAlchemyEntityInfoService(db)

    return PointageController(
        pointage_repo=pointage_repo,
        feuille_repo=feuille_repo,
        variable_repo=variable_repo,
        event_bus=event_bus,
        entity_info_service=entity_info_service,
    )


# ===== Routes Pointages =====


@router.post("", status_code=201)
def create_pointage(
    request: CreatePointageRequest,
    current_user_id: int = Depends(get_current_user_id),
    controller: PointageController = Depends(get_controller),
):
    """
    Crée un nouveau pointage.

    - **utilisateur_id**: ID de l'utilisateur pointé
    - **chantier_id**: ID du chantier
    - **date_pointage**: Date du pointage
    - **heures_normales**: Heures normales (format HH:MM)
    - **heures_supplementaires**: Heures sup (format HH:MM, défaut 00:00)
    """
    try:
        return controller.create_pointage(
            utilisateur_id=request.utilisateur_id,
            chantier_id=request.chantier_id,
            date_pointage=request.date_pointage,
            heures_normales=request.heures_normales,
            heures_supplementaires=request.heures_supplementaires,
            commentaire=request.commentaire,
            affectation_id=request.affectation_id,
            created_by=current_user_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("")
def list_pointages(
    utilisateur_id: Optional[int] = None,
    chantier_id: Optional[int] = None,
    date_debut: Optional[date] = None,
    date_fin: Optional[date] = None,
    statut: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user_id: int = Depends(get_current_user_id),
    controller: PointageController = Depends(get_controller),
):
    """
    Liste les pointages avec filtres (FDH-04).

    Filtres disponibles:
    - **utilisateur_id**: Filtrer par utilisateur
    - **chantier_id**: Filtrer par chantier
    - **date_debut/date_fin**: Période
    - **statut**: brouillon, soumis, valide, rejete
    """
    return controller.list_pointages(
        utilisateur_id=utilisateur_id,
        chantier_id=chantier_id,
        date_debut=date_debut,
        date_fin=date_fin,
        statut=statut,
        page=page,
        page_size=page_size,
    )


# ===== Routes spécifiques (AVANT les routes paramétrées) =====


@router.get("/feuilles")
def list_feuilles_heures(
    utilisateur_id: Optional[int] = None,
    annee: Optional[int] = None,
    numero_semaine: Optional[int] = None,
    statut: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    current_user_id: int = Depends(get_current_user_id),
    controller: PointageController = Depends(get_controller),
):
    """Liste les feuilles d'heures avec filtres."""
    return controller.list_feuilles_heures(
        utilisateur_id=utilisateur_id,
        annee=annee,
        numero_semaine=numero_semaine,
        statut=statut,
        page=page,
        page_size=page_size,
    )


@router.get("/navigation")
def get_navigation_semaine(
    semaine_debut: date = Query(..., description="Date du lundi de la semaine"),
    current_user_id: int = Depends(get_current_user_id),
    controller: PointageController = Depends(get_controller),
):
    """Retourne les infos de navigation par semaine (FDH-02)."""
    return controller.get_navigation_semaine(semaine_debut)


@router.get("/vues/chantiers")
def get_vue_chantiers(
    semaine_debut: date = Query(..., description="Date du lundi de la semaine"),
    chantier_ids: Optional[str] = Query(None, description="IDs chantiers separes par virgule"),
    current_user_id: int = Depends(get_current_user_id),
    controller: PointageController = Depends(get_controller),
):
    """Vue par chantiers pour une semaine (FDH-01 onglet Chantiers)."""
    chantier_ids_list = None
    if chantier_ids:
        chantier_ids_list = [int(x) for x in chantier_ids.split(",")]
    return controller.get_vue_chantiers(semaine_debut, chantier_ids_list)


@router.get("/vues/compagnons")
def get_vue_compagnons(
    semaine_debut: date = Query(..., description="Date du lundi de la semaine"),
    utilisateur_ids: Optional[str] = Query(None, description="IDs utilisateurs separes par virgule"),
    current_user_id: int = Depends(get_current_user_id),
    controller: PointageController = Depends(get_controller),
):
    """Vue par compagnons pour une semaine (FDH-01 onglet Compagnons)."""
    utilisateur_ids_list = None
    if utilisateur_ids:
        utilisateur_ids_list = [int(x) for x in utilisateur_ids.split(",")]
    return controller.get_vue_compagnons(semaine_debut, utilisateur_ids_list)


@router.post("/variables-paie", status_code=201)
def create_variable_paie(
    request: CreateVariablePaieRequest,
    current_user_id: int = Depends(get_current_user_id),
    controller: PointageController = Depends(get_controller),
):
    """Crée une variable de paie (FDH-13)."""
    try:
        return controller.create_variable_paie(
            pointage_id=request.pointage_id,
            type_variable=request.type_variable,
            valeur=request.valeur,
            date_application=request.date_application,
            commentaire=request.commentaire,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/export")
def export_feuilles_heures(
    request: ExportRequest,
    current_user_id: int = Depends(get_current_user_id),
    controller: PointageController = Depends(get_controller),
):
    """Exporte les feuilles d'heures (FDH-03, FDH-17)."""
    result = controller.export_feuilles_heures(
        format_export=request.format_export,
        date_debut=request.date_debut,
        date_fin=request.date_fin,
        utilisateur_ids=request.utilisateur_ids,
        chantier_ids=request.chantier_ids,
        inclure_variables_paie=request.inclure_variables_paie,
        inclure_signatures=request.inclure_signatures,
        exported_by=current_user_id,
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error_message"])

    # Retourne le fichier si content disponible
    if result.get("file_content"):
        media_type = "text/csv" if request.format_export == "csv" else "application/octet-stream"
        return Response(
            content=result["file_content"],
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={result['filename']}"},
        )

    return result


@router.get("/feuilles/{feuille_id}")
def get_feuille_heures(
    feuille_id: int,
    current_user_id: int = Depends(get_current_user_id),
    controller: PointageController = Depends(get_controller),
):
    """Récupère une feuille d'heures par son ID."""
    result = controller.get_feuille_heures(feuille_id)
    if not result:
        raise HTTPException(status_code=404, detail="Feuille d'heures non trouvée")
    return result


@router.get("/feuilles/utilisateur/{utilisateur_id}/semaine")
def get_feuille_heures_semaine(
    utilisateur_id: int,
    semaine_debut: date = Query(..., description="Date du lundi de la semaine"),
    current_user_id: int = Depends(get_current_user_id),
    controller: PointageController = Depends(get_controller),
):
    """Récupère la feuille d'heures d'un utilisateur pour une semaine (FDH-05)."""
    return controller.get_feuille_heures_semaine(utilisateur_id, semaine_debut)


@router.get("/feuille-route/{utilisateur_id}")
def get_feuille_route(
    utilisateur_id: int,
    semaine_debut: date = Query(..., description="Date du lundi de la semaine"),
    current_user_id: int = Depends(get_current_user_id),
    controller: PointageController = Depends(get_controller),
):
    """Génère une feuille de route (FDH-19)."""
    return controller.generate_feuille_route(utilisateur_id, semaine_debut)


@router.get("/stats/jauge-avancement/{utilisateur_id}")
def get_jauge_avancement(
    utilisateur_id: int,
    semaine_debut: date = Query(..., description="Date du lundi de la semaine"),
    heures_planifiees: Optional[float] = Query(None, description="Heures planifiees (defaut 35h)"),
    current_user_id: int = Depends(get_current_user_id),
    controller: PointageController = Depends(get_controller),
):
    """Jauge d'avancement planifié vs réalisé (FDH-14)."""
    return controller.get_jauge_avancement(utilisateur_id, semaine_debut, heures_planifiees)


@router.get("/stats/comparaison-equipes")
def compare_equipes(
    semaine_debut: date = Query(..., description="Date du lundi de la semaine"),
    current_user_id: int = Depends(get_current_user_id),
    controller: PointageController = Depends(get_controller),
):
    """Comparaison inter-équipes (FDH-15)."""
    return controller.compare_equipes(semaine_debut)


@router.post("/bulk-from-planning", status_code=201)
def bulk_create_from_planning(
    request: BulkCreateRequest,
    current_user_id: int = Depends(get_current_user_id),
    controller: PointageController = Depends(get_controller),
):
    """Crée des pointages en masse depuis le planning (FDH-10)."""
    try:
        return controller.bulk_create_from_planning(
            utilisateur_id=request.utilisateur_id,
            semaine_debut=request.semaine_debut,
            affectations=request.affectations,
            created_by=current_user_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ===== Routes paramétrées (APRES les routes spécifiques) =====


@router.get("/{pointage_id}")
def get_pointage(
    pointage_id: int,
    current_user_id: int = Depends(get_current_user_id),
    controller: PointageController = Depends(get_controller),
):
    """Récupère un pointage par son ID."""
    result = controller.get_pointage(pointage_id)
    if not result:
        raise HTTPException(status_code=404, detail="Pointage non trouvé")
    return result


@router.put("/{pointage_id}")
def update_pointage(
    pointage_id: int,
    request: UpdatePointageRequest,
    current_user_id: int = Depends(get_current_user_id),
    controller: PointageController = Depends(get_controller),
):
    """Met à jour un pointage (si en brouillon ou rejeté)."""
    try:
        return controller.update_pointage(
            pointage_id=pointage_id,
            heures_normales=request.heures_normales,
            heures_supplementaires=request.heures_supplementaires,
            commentaire=request.commentaire,
            updated_by=current_user_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{pointage_id}", status_code=204)
def delete_pointage(
    pointage_id: int,
    current_user_id: int = Depends(get_current_user_id),
    controller: PointageController = Depends(get_controller),
):
    """Supprime un pointage (si en brouillon ou rejeté)."""
    try:
        controller.delete_pointage(pointage_id, current_user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ===== Routes Workflow Validation =====


@router.post("/{pointage_id}/sign")
def sign_pointage(
    pointage_id: int,
    request: SignPointageRequest,
    current_user_id: int = Depends(get_current_user_id),
    controller: PointageController = Depends(get_controller),
):
    """Signe électroniquement un pointage (FDH-12)."""
    try:
        return controller.sign_pointage(pointage_id, request.signature)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{pointage_id}/submit")
def submit_pointage(
    pointage_id: int,
    current_user_id: int = Depends(get_current_user_id),
    controller: PointageController = Depends(get_controller),
):
    """Soumet un pointage pour validation."""
    try:
        return controller.submit_pointage(pointage_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{pointage_id}/validate")
async def validate_pointage(
    pointage_id: int,
    validateur_id: int = Depends(get_current_user_id),
    event_bus = Depends(get_event_bus),
    controller: PointageController = Depends(get_controller),
):
    """Valide un pointage soumis. ⚡ CRITIQUE: Déclenche la synchronisation avec la paie."""
    try:
        result = controller.validate_pointage(pointage_id, validateur_id)

        # Publish event after database commit (CRITICAL for payroll sync)
        from datetime import datetime
        await event_bus.publish(HeuresValidatedEvent(
            heures_id=result.get("id", pointage_id),
            user_id=result.get("utilisateur_id"),
            chantier_id=result.get("chantier_id"),
            date=result.get("date_pointage") if isinstance(result.get("date_pointage"), date) else date.today(),
            heures_travaillees=float(result.get("heures_normales", "0:0").split(":")[0]) if isinstance(result.get("heures_normales"), str) else float(result.get("heures_normales", 0)),
            heures_supplementaires=float(result.get("heures_supplementaires", "0:0").split(":")[0]) if isinstance(result.get("heures_supplementaires"), str) else float(result.get("heures_supplementaires", 0)),
            validated_by=validateur_id,
            validated_at=datetime.now(),
            metadata={
                'user_id': validateur_id,
                'pointage_id': pointage_id,
            }
        ))

        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{pointage_id}/reject")
def reject_pointage(
    pointage_id: int,
    request: RejectPointageRequest,
    validateur_id: int = Depends(get_current_user_id),
    controller: PointageController = Depends(get_controller),
):
    """Rejette un pointage soumis."""
    try:
        return controller.reject_pointage(pointage_id, validateur_id, request.motif)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{pointage_id}/correct")
def correct_pointage(
    pointage_id: int,
    current_user_id: int = Depends(get_current_user_id),
    controller: PointageController = Depends(get_controller),
):
    """
    Repasse un pointage rejeté en brouillon pour correction.

    Le compagnon peut ensuite modifier les heures et re-soumettre.
    Workflow § 5.5 (Rejet et correction).
    """
    try:
        return controller.correct_pointage(pointage_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
