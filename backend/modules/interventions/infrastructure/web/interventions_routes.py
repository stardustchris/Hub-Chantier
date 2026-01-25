"""Routes API pour le module Interventions.

INT-01 a INT-17: Endpoints REST pour la gestion des interventions.
"""

from datetime import date
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from shared.infrastructure.database import get_async_session
from modules.auth.infrastructure.web.dependencies import get_current_user
from modules.auth.domain.entities import User

from ...application.dtos import (
    CreateInterventionDTO,
    UpdateInterventionDTO,
    PlanifierInterventionDTO,
    DemarrerInterventionDTO,
    TerminerInterventionDTO,
    InterventionResponseDTO,
    InterventionListResponseDTO,
    InterventionFiltersDTO,
    TechnicienResponseDTO,
    AffecterTechnicienDTO,
    MessageResponseDTO,
    CreateMessageDTO,
    SignatureResponseDTO,
    CreateSignatureDTO,
)
from ...domain.value_objects import (
    StatutIntervention,
    PrioriteIntervention,
    TypeIntervention,
)
from .dependencies import (
    get_create_intervention_use_case,
    get_get_intervention_use_case,
    get_list_interventions_use_case,
    get_update_intervention_use_case,
    get_planifier_intervention_use_case,
    get_demarrer_intervention_use_case,
    get_terminer_intervention_use_case,
    get_annuler_intervention_use_case,
    get_delete_intervention_use_case,
    get_affecter_technicien_use_case,
    get_desaffecter_technicien_use_case,
    get_list_techniciens_use_case,
    get_add_message_use_case,
    get_list_messages_use_case,
    get_toggle_rapport_use_case,
    get_add_signature_use_case,
    get_list_signatures_use_case,
)

router = APIRouter(prefix="/interventions", tags=["interventions"])


# =============================================================================
# INTERVENTIONS CRUD
# =============================================================================


@router.post(
    "",
    response_model=InterventionResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Creer une intervention",
    description="INT-03: Creation d'une nouvelle intervention",
)
async def create_intervention(
    dto: CreateInterventionDTO,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Cree une nouvelle intervention."""
    use_case = await get_create_intervention_use_case(session)
    intervention = await use_case.execute(dto, current_user.id)
    await session.commit()

    return _intervention_to_response(intervention)


@router.get(
    "",
    response_model=InterventionListResponseDTO,
    summary="Lister les interventions",
    description="INT-02: Liste des interventions avec filtres et pagination",
)
async def list_interventions(
    statut: Optional[StatutIntervention] = None,
    priorite: Optional[PrioriteIntervention] = None,
    type_intervention: Optional[TypeIntervention] = None,
    date_debut: Optional[date] = None,
    date_fin: Optional[date] = None,
    chantier_origine_id: Optional[int] = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Liste les interventions."""
    filters = InterventionFiltersDTO(
        statut=statut,
        priorite=priorite,
        type_intervention=type_intervention,
        date_debut=date_debut,
        date_fin=date_fin,
        chantier_origine_id=chantier_origine_id,
        limit=limit,
        offset=offset,
    )

    use_case = await get_list_interventions_use_case(session)
    interventions, total = await use_case.execute(filters)

    return InterventionListResponseDTO(
        items=[_intervention_to_response(i) for i in interventions],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{intervention_id}",
    response_model=InterventionResponseDTO,
    summary="Recuperer une intervention",
)
async def get_intervention(
    intervention_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Recupere une intervention par son ID."""
    use_case = await get_get_intervention_use_case(session)
    intervention = await use_case.execute(intervention_id)

    if not intervention:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intervention non trouvee",
        )

    return _intervention_to_response(intervention)


@router.patch(
    "/{intervention_id}",
    response_model=InterventionResponseDTO,
    summary="Modifier une intervention",
)
async def update_intervention(
    intervention_id: int,
    dto: UpdateInterventionDTO,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Modifie une intervention."""
    use_case = await get_update_intervention_use_case(session)

    try:
        intervention = await use_case.execute(intervention_id, dto)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    if not intervention:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intervention non trouvee",
        )

    await session.commit()
    return _intervention_to_response(intervention)


@router.delete(
    "/{intervention_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer une intervention",
)
async def delete_intervention(
    intervention_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Supprime une intervention (soft delete)."""
    use_case = await get_delete_intervention_use_case(session)
    deleted = await use_case.execute(intervention_id, current_user.id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intervention non trouvee",
        )

    await session.commit()


# =============================================================================
# ACTIONS SUR LES INTERVENTIONS
# =============================================================================


@router.post(
    "/{intervention_id}/planifier",
    response_model=InterventionResponseDTO,
    summary="Planifier une intervention",
    description="INT-05, INT-06: Planifie l'intervention avec date et techniciens",
)
async def planifier_intervention(
    intervention_id: int,
    dto: PlanifierInterventionDTO,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Planifie une intervention."""
    use_case = await get_planifier_intervention_use_case(session)
    intervention = await use_case.execute(intervention_id, dto, current_user.id)

    if not intervention:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intervention non trouvee",
        )

    await session.commit()
    return _intervention_to_response(intervention)


@router.post(
    "/{intervention_id}/demarrer",
    response_model=InterventionResponseDTO,
    summary="Demarrer une intervention",
)
async def demarrer_intervention(
    intervention_id: int,
    dto: DemarrerInterventionDTO = DemarrerInterventionDTO(),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Demarre une intervention."""
    use_case = await get_demarrer_intervention_use_case(session)

    try:
        intervention = await use_case.execute(intervention_id, dto)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    if not intervention:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intervention non trouvee",
        )

    await session.commit()
    return _intervention_to_response(intervention)


@router.post(
    "/{intervention_id}/terminer",
    response_model=InterventionResponseDTO,
    summary="Terminer une intervention",
)
async def terminer_intervention(
    intervention_id: int,
    dto: TerminerInterventionDTO = TerminerInterventionDTO(),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Termine une intervention."""
    use_case = await get_terminer_intervention_use_case(session)

    try:
        intervention = await use_case.execute(intervention_id, dto)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    if not intervention:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intervention non trouvee",
        )

    await session.commit()
    return _intervention_to_response(intervention)


@router.post(
    "/{intervention_id}/annuler",
    response_model=InterventionResponseDTO,
    summary="Annuler une intervention",
)
async def annuler_intervention(
    intervention_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Annule une intervention."""
    use_case = await get_annuler_intervention_use_case(session)

    try:
        intervention = await use_case.execute(intervention_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    if not intervention:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intervention non trouvee",
        )

    await session.commit()
    return _intervention_to_response(intervention)


# =============================================================================
# TECHNICIENS
# =============================================================================


@router.post(
    "/{intervention_id}/techniciens",
    response_model=TechnicienResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Affecter un technicien",
    description="INT-10, INT-17: Affecte un technicien ou sous-traitant",
)
async def affecter_technicien(
    intervention_id: int,
    dto: AffecterTechnicienDTO,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Affecte un technicien a l'intervention."""
    use_case = await get_affecter_technicien_use_case(session)

    try:
        affectation = await use_case.execute(intervention_id, dto, current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    await session.commit()

    return TechnicienResponseDTO(
        id=affectation.id,
        utilisateur_id=affectation.utilisateur_id,
        est_principal=affectation.est_principal,
        commentaire=affectation.commentaire,
    )


@router.get(
    "/{intervention_id}/techniciens",
    response_model=List[TechnicienResponseDTO],
    summary="Lister les techniciens",
)
async def list_techniciens(
    intervention_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Liste les techniciens affectes a l'intervention."""
    use_case = await get_list_techniciens_use_case(session)
    affectations = await use_case.execute(intervention_id)

    return [
        TechnicienResponseDTO(
            id=a.id,
            utilisateur_id=a.utilisateur_id,
            est_principal=a.est_principal,
            commentaire=a.commentaire,
        )
        for a in affectations
    ]


@router.delete(
    "/{intervention_id}/techniciens/{affectation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Desaffecter un technicien",
)
async def desaffecter_technicien(
    intervention_id: int,
    affectation_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Desaffecte un technicien de l'intervention."""
    use_case = await get_desaffecter_technicien_use_case(session)
    deleted = await use_case.execute(affectation_id, current_user.id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Affectation non trouvee",
        )

    await session.commit()


# =============================================================================
# MESSAGES (Fil d'activite / Chat)
# =============================================================================


@router.post(
    "/{intervention_id}/messages",
    response_model=MessageResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Ajouter un message",
    description="INT-11, INT-12: Ajoute un message au fil d'activite",
)
async def add_message(
    intervention_id: int,
    dto: CreateMessageDTO,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Ajoute un message a l'intervention."""
    use_case = await get_add_message_use_case(session)
    message = await use_case.execute(intervention_id, dto, current_user.id)
    await session.commit()

    return MessageResponseDTO(
        id=message.id,
        intervention_id=message.intervention_id,
        auteur_id=message.auteur_id,
        type_message=message.type_message.value,
        contenu=message.contenu,
        photos_urls=message.photos_urls,
        inclure_rapport=message.inclure_rapport,
        created_at=message.created_at,
    )


@router.get(
    "/{intervention_id}/messages",
    response_model=List[MessageResponseDTO],
    summary="Lister les messages",
)
async def list_messages(
    intervention_id: int,
    type_message: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Liste les messages de l'intervention."""
    use_case = await get_list_messages_use_case(session)
    messages, _ = await use_case.execute(
        intervention_id, type_message, limit, offset
    )

    return [
        MessageResponseDTO(
            id=m.id,
            intervention_id=m.intervention_id,
            auteur_id=m.auteur_id,
            type_message=m.type_message.value,
            contenu=m.contenu,
            photos_urls=m.photos_urls,
            inclure_rapport=m.inclure_rapport,
            created_at=m.created_at,
        )
        for m in messages
    ]


@router.patch(
    "/{intervention_id}/messages/{message_id}/rapport",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Inclure/exclure du rapport",
    description="INT-15: Selection des posts pour le rapport PDF",
)
async def toggle_rapport_inclusion(
    intervention_id: int,
    message_id: int,
    inclure: bool = Query(...),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Active/desactive l'inclusion d'un message dans le rapport."""
    use_case = await get_toggle_rapport_use_case(session)
    updated = await use_case.execute(message_id, inclure)

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message non trouve",
        )

    await session.commit()


# =============================================================================
# SIGNATURES
# =============================================================================


@router.post(
    "/{intervention_id}/signatures",
    response_model=SignatureResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Ajouter une signature",
    description="INT-13: Signature client ou technicien",
)
async def add_signature(
    intervention_id: int,
    dto: CreateSignatureDTO,
    request: Request,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Ajoute une signature a l'intervention."""
    use_case = await get_add_signature_use_case(session)

    # Recuperer l'IP pour la tracabilite
    ip_address = request.client.host if request.client else None

    try:
        signature = await use_case.execute(
            intervention_id,
            dto,
            utilisateur_id=current_user.id if dto.type_signataire == "technicien" else None,
            ip_address=ip_address,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    await session.commit()

    return SignatureResponseDTO(
        id=signature.id,
        intervention_id=signature.intervention_id,
        type_signataire=signature.type_signataire.value,
        nom_signataire=signature.nom_signataire,
        utilisateur_id=signature.utilisateur_id,
        signed_at=signature.signed_at,
        horodatage_str=signature.horodatage_str,
    )


@router.get(
    "/{intervention_id}/signatures",
    response_model=List[SignatureResponseDTO],
    summary="Lister les signatures",
)
async def list_signatures(
    intervention_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Liste les signatures de l'intervention."""
    use_case = await get_list_signatures_use_case(session)
    signatures = await use_case.execute(intervention_id)

    return [
        SignatureResponseDTO(
            id=s.id,
            intervention_id=s.intervention_id,
            type_signataire=s.type_signataire.value,
            nom_signataire=s.nom_signataire,
            utilisateur_id=s.utilisateur_id,
            signed_at=s.signed_at,
            horodatage_str=s.horodatage_str,
        )
        for s in signatures
    ]


# =============================================================================
# HELPERS
# =============================================================================


def _intervention_to_response(intervention) -> InterventionResponseDTO:
    """Convertit une entite Intervention en DTO de reponse."""
    return InterventionResponseDTO(
        id=intervention.id,
        code=intervention.code,
        type_intervention=intervention.type_intervention,
        statut=intervention.statut,
        priorite=intervention.priorite,
        client_nom=intervention.client_nom,
        client_adresse=intervention.client_adresse,
        client_telephone=intervention.client_telephone,
        client_email=intervention.client_email,
        description=intervention.description,
        travaux_realises=intervention.travaux_realises,
        anomalies=intervention.anomalies,
        date_souhaitee=intervention.date_souhaitee,
        date_planifiee=intervention.date_planifiee,
        heure_debut=intervention.heure_debut,
        heure_fin=intervention.heure_fin,
        heure_debut_reelle=intervention.heure_debut_reelle,
        heure_fin_reelle=intervention.heure_fin_reelle,
        chantier_origine_id=intervention.chantier_origine_id,
        rapport_genere=intervention.rapport_genere,
        rapport_url=intervention.rapport_url,
        created_by=intervention.created_by,
        created_at=intervention.created_at,
        updated_at=intervention.updated_at,
    )
