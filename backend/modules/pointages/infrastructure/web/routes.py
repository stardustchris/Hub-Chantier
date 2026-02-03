"""Routes FastAPI pour le module pointages (feuilles d'heures)."""

from datetime import date
from typing import Optional, List
import re

from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session

from sqlalchemy import text as sql_text

from shared.infrastructure.database import get_db
from shared.infrastructure.web.dependencies import (
    get_current_user_id,
    get_current_user_role,
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
from ...domain.services.permission_service import PointagePermissionService
from ...domain.value_objects.periode_paie import PeriodePaie


router = APIRouter(prefix="/pointages", tags=["Feuilles d'heures"])


# ===== Permission Helpers =====


def _get_chef_chantier_ids(user_id: int, user_role: str, db: Session) -> set[int] | None:
    """Recupere les IDs des chantiers d'un chef de chantier.

    Pour les conducteurs/admins, retourne None (acces total).
    Pour les compagnons, retourne None (pas utilise).
    Pour les chefs, requete la table chantier_chefs.

    Args:
        user_id: ID de l'utilisateur.
        user_role: Role de l'utilisateur.
        db: Session SQLAlchemy.

    Returns:
        Set d'IDs de chantiers pour un chef, None pour les autres roles.
    """
    if user_role != "chef_chantier":
        return None

    result = db.execute(
        sql_text("SELECT chantier_id FROM chantier_chefs WHERE user_id = :uid"),
        {"uid": user_id},
    )
    return {row[0] for row in result.fetchall()}


# ===== Validation Helpers =====


def validate_time_format(time_str: str) -> str:
    """
    Valide le format HH:MM strictement.

    Args:
        time_str: Chaîne au format HH:MM.

    Returns:
        La chaîne validée.

    Raises:
        ValueError: Si le format est invalide.

    Examples:
        >>> validate_time_format("08:30")
        '08:30'
        >>> validate_time_format("23:59")
        '23:59'
        >>> validate_time_format("00:00")
        '00:00'
        >>> validate_time_format("24:00")
        ValueError: Heures invalides (doit être entre 00 et 23)
        >>> validate_time_format("12:60")
        ValueError: Minutes invalides (doit être entre 00 et 59)
        >>> validate_time_format("-1:30")
        ValueError: Format d'heure invalide. Format attendu: HH:MM
        >>> validate_time_format("99:99")
        ValueError: Heures invalides (doit être entre 00 et 23)
    """
    # Vérification du format de base
    if not time_str or not isinstance(time_str, str):
        raise ValueError("Format d'heure invalide. Format attendu: HH:MM")

    # Regex stricte: exactement 2 chiffres pour les heures, 2 pour les minutes
    pattern = r"^(\d{1,2}):(\d{2})$"
    match = re.match(pattern, time_str)

    if not match:
        raise ValueError("Format d'heure invalide. Format attendu: HH:MM")

    hours_str, minutes_str = match.groups()

    # Convertir en entiers
    try:
        hours = int(hours_str)
        minutes = int(minutes_str)
    except ValueError:
        raise ValueError("Format d'heure invalide. Format attendu: HH:MM")

    # Validation des plages
    if hours < 0 or hours > 23:
        raise ValueError("Heures invalides (doit être entre 00 et 23)")

    if minutes < 0 or minutes > 59:
        raise ValueError("Minutes invalides (doit être entre 00 et 59)")

    # Normaliser le format (pad avec des zéros si nécessaire)
    return f"{hours:02d}:{minutes:02d}"


# ===== Pydantic Schemas =====


class CreatePointageRequest(BaseModel):
    """Requête de création de pointage."""

    utilisateur_id: int
    chantier_id: int
    date_pointage: date
    heures_normales: str
    heures_supplementaires: str = "00:00"
    commentaire: Optional[str] = None
    affectation_id: Optional[int] = None

    @validator("heures_normales", "heures_supplementaires")
    def validate_time(cls, v):
        """Valide le format HH:MM strictement."""
        if v:
            return validate_time_format(v)
        return v


class UpdatePointageRequest(BaseModel):
    """Requête de mise à jour de pointage."""

    heures_normales: Optional[str] = None
    heures_supplementaires: Optional[str] = None
    commentaire: Optional[str] = None

    @validator("heures_normales", "heures_supplementaires")
    def validate_time(cls, v):
        """Valide le format HH:MM strictement."""
        if v:
            return validate_time_format(v)
        return v


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
    current_user_role: str = Depends(get_current_user_role),
    controller: PointageController = Depends(get_controller),
    db: Session = Depends(get_db),
):
    """
    Crée un nouveau pointage.

    - **utilisateur_id**: ID de l'utilisateur pointé
    - **chantier_id**: ID du chantier
    - **date_pointage**: Date du pointage
    - **heures_normales**: Heures normales (format HH:MM)
    - **heures_supplementaires**: Heures sup (format HH:MM, défaut 00:00)

    Permissions:
    - Compagnon: Peut créer uniquement pour lui-même
    - Chef de chantier: Peut créer pour les compagnons de SES chantiers
    - Conducteur/Admin: Peut créer pour n'importe qui
    """
    # Vérification des permissions (SEC-PTG-002)
    chef_chantier_ids = _get_chef_chantier_ids(current_user_id, current_user_role, db)
    if not PointagePermissionService.can_create_for_user(
        current_user_id=current_user_id,
        target_user_id=request.utilisateur_id,
        user_role=current_user_role,
        pointage_chantier_id=request.chantier_id,
        user_chantier_ids=chef_chantier_ids,
    ):
        raise HTTPException(
            status_code=403,
            detail="Vous n'avez pas la permission de créer un pointage pour cet utilisateur",
        )

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
            created_by_role=current_user_role,
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
    current_user_role: str = Depends(get_current_user_role),
    controller: PointageController = Depends(get_controller),
):
    """Exporte les feuilles d'heures (FDH-03, FDH-17)."""
    # Vérification des permissions (SEC-PTG-004)
    if not PointagePermissionService.can_export(current_user_role):
        raise HTTPException(
            status_code=403,
            detail="Vous n'avez pas la permission d'exporter les feuilles d'heures"
        )

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
    current_user_role: str = Depends(get_current_user_role),
    controller: PointageController = Depends(get_controller),
    db: Session = Depends(get_db),
):
    """
    Met à jour un pointage (si en brouillon ou rejeté).

    Permissions:
    - Compagnon: Peut modifier uniquement ses propres pointages
    - Chef de chantier: Peut modifier les pointages de SES chantiers
    - Conducteur/Admin: Peut modifier n'importe quel pointage
    """
    # Récupérer le pointage pour vérifier le propriétaire (SEC-PTG-002)
    pointage = controller.get_pointage(pointage_id)
    if not pointage:
        raise HTTPException(status_code=404, detail="Pointage non trouvé")

    # Vérification des permissions avec restriction par chantier pour les chefs
    chef_chantier_ids = _get_chef_chantier_ids(current_user_id, current_user_role, db)
    if not PointagePermissionService.can_modify(
        current_user_id=current_user_id,
        pointage_owner_id=pointage.get("utilisateur_id"),
        user_role=current_user_role,
        pointage_chantier_id=pointage.get("chantier_id"),
        user_chantier_ids=chef_chantier_ids,
    ):
        raise HTTPException(
            status_code=403,
            detail="Vous n'avez pas la permission de modifier ce pointage",
        )

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
    current_user_role: str = Depends(get_current_user_role),
    event_bus = Depends(get_event_bus),
    controller: PointageController = Depends(get_controller),
    db: Session = Depends(get_db),
):
    """Valide un pointage soumis. ⚡ CRITIQUE: Déclenche la synchronisation avec la paie."""
    # Récupérer le pointage pour vérifier le chantier
    pointage = controller.get_pointage(pointage_id)
    if not pointage:
        raise HTTPException(status_code=404, detail="Pointage non trouvé")

    # Vérification des permissions avec restriction par chantier pour les chefs
    chef_chantier_ids = _get_chef_chantier_ids(validateur_id, current_user_role, db)
    if not PointagePermissionService.can_validate(
        current_user_role,
        pointage_chantier_id=pointage.get("chantier_id"),
        user_chantier_ids=chef_chantier_ids,
    ):
        raise HTTPException(
            status_code=403,
            detail="Vous n'avez pas la permission de valider des pointages"
        )

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
    current_user_role: str = Depends(get_current_user_role),
    controller: PointageController = Depends(get_controller),
    db: Session = Depends(get_db),
):
    """Rejette un pointage soumis."""
    # Récupérer le pointage pour vérifier le chantier
    pointage = controller.get_pointage(pointage_id)
    if not pointage:
        raise HTTPException(status_code=404, detail="Pointage non trouvé")

    # Vérification des permissions avec restriction par chantier pour les chefs
    chef_chantier_ids = _get_chef_chantier_ids(validateur_id, current_user_role, db)
    if not PointagePermissionService.can_reject(
        current_user_role,
        pointage_chantier_id=pointage.get("chantier_id"),
        user_chantier_ids=chef_chantier_ids,
    ):
        raise HTTPException(
            status_code=403,
            detail="Vous n'avez pas la permission de rejeter des pointages"
        )

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


# ===== Phase 2 GAPs =====


class BulkValidateRequest(BaseModel):
    """Requête de validation par lot (GAP-FDH-004)."""

    pointage_ids: List[int] = Field(..., min_items=1, description="IDs des pointages à valider")


@router.post("/bulk-validate")
def bulk_validate_pointages(
    request: BulkValidateRequest,
    validateur_id: int = Depends(get_current_user_id),
    current_user_role: str = Depends(get_current_user_role),
    controller: PointageController = Depends(get_controller),
    db: Session = Depends(get_db),
):
    """
    Valide plusieurs pointages en une seule opération (GAP-FDH-004).

    Permet au chef de chantier ou conducteur de valider tous les pointages
    d'une feuille d'heures en un seul clic.

    Retourne un résultat détaillé avec les succès et les échecs.

    Permissions:
    - Chef de chantier: Peut valider uniquement les pointages de SES chantiers
    - Conducteur/Admin: Peut valider n'importe quel pointage
    """
    # SEC-PTG-P2-001: Vérification des permissions avant validation en masse
    chef_chantier_ids = _get_chef_chantier_ids(validateur_id, current_user_role, db)

    # Vérification de base : est-ce un manager ?
    if not PointagePermissionService.can_validate(current_user_role):
        raise HTTPException(
            status_code=403,
            detail="Seuls les chefs de chantier, conducteurs et admins peuvent valider des pointages"
        )

    # Pour les chefs : vérifier que tous les pointages sont dans leurs chantiers
    if current_user_role == "chef_chantier" and chef_chantier_ids is not None:
        for pid in request.pointage_ids:
            pointage = controller.get_pointage(pid)
            if not pointage:
                continue  # sera géré par le controller
            if not PointagePermissionService.can_validate(
                current_user_role,
                pointage_chantier_id=pointage.get("chantier_id"),
                user_chantier_ids=chef_chantier_ids,
            ):
                raise HTTPException(
                    status_code=403,
                    detail=f"Vous n'avez pas la permission de valider le pointage #{pid} (chantier non assigné)",
                )

    try:
        return controller.bulk_validate_pointages(request.pointage_ids, validateur_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/recap/{utilisateur_id}/{year}/{month}")
def get_monthly_recap(
    utilisateur_id: int,
    year: int,
    month: int,
    export_pdf: bool = Query(False, description="Générer un export PDF"),
    current_user_id: int = Depends(get_current_user_id),
    current_user_role: str = Depends(get_current_user_role),
    controller: PointageController = Depends(get_controller),
):
    """
    Récapitulatif mensuel des heures (GAP-FDH-008).

    Retourne un récapitulatif complet pour un compagnon sur un mois donné:
    - Totaux hebdomadaires (heures normales, heures sup)
    - Totaux mensuels
    - Variables de paie (paniers, indemnités, primes)
    - Absences
    - Statut de validation

    Optionnel: Génération d'un export PDF.
    """
    # SEC-PTG-P2-002: Un compagnon ne peut consulter que son propre récapitulatif
    if current_user_role == "compagnon" and current_user_id != utilisateur_id:
        raise HTTPException(
            status_code=403,
            detail="Vous ne pouvez consulter que votre propre récapitulatif mensuel"
        )

    try:
        return controller.generate_monthly_recap(utilisateur_id, year, month, export_pdf)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


class LockPeriodRequest(BaseModel):
    """Requête de verrouillage de période (GAP-FDH-009)."""

    year: int = Field(..., ge=2000, le=2100, description="Année")
    month: int = Field(..., ge=1, le=12, description="Mois (1-12)")


@router.post("/lock-period")
def lock_monthly_period(
    request: LockPeriodRequest,
    current_user_id: int = Depends(get_current_user_id),
    current_user_role: str = Depends(get_current_user_role),
    controller: PointageController = Depends(get_controller),
):
    """
    Verrouille manuellement une période de paie (GAP-FDH-009).

    Réservé aux administrateurs et conducteurs de travaux.
    Après le verrouillage, aucun pointage du mois ne peut plus être modifié.

    Note: Le verrouillage automatique est déclenché par le scheduler
    le dernier vendredi avant la dernière semaine du mois à 23:59.
    """
    # Vérification des permissions (admin ou conducteur uniquement)
    if current_user_role not in ["admin", "conducteur"]:
        raise HTTPException(
            status_code=403,
            detail="Seuls les administrateurs et conducteurs peuvent verrouiller une période",
        )

    # SEC-PTG-P2-006: Validations de sécurité sur la période de verrouillage
    today = date.today()
    period_date = date(request.year, request.month, 1)

    # 1. Interdire le verrouillage de périodes futures
    if request.year > today.year or (request.year == today.year and request.month > today.month):
        raise HTTPException(
            status_code=400,
            detail="Impossible de verrouiller une période future"
        )

    # 2. Interdire le verrouillage de périodes trop anciennes (> 12 mois)
    # Calculer la date limite = 12 mois en arrière (1er du mois)
    twelve_months_ago = today - relativedelta(months=12)
    twelve_months_ago_first = date(twelve_months_ago.year, twelve_months_ago.month, 1)

    if period_date < twelve_months_ago_first:
        raise HTTPException(
            status_code=400,
            detail="Impossible de verrouiller une période de plus de 12 mois"
        )

    # 3. Vérifier que la période n'est pas déjà verrouillée
    # Utiliser le 15 du mois comme date de référence pour vérifier le statut de verrouillage
    if PeriodePaie.is_locked(date(request.year, request.month, 15), today=today):
        raise HTTPException(
            status_code=409,
            detail="Cette période est déjà verrouillée"
        )

    try:
        return controller.lock_monthly_period(
            request.year, request.month, locked_by=current_user_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
