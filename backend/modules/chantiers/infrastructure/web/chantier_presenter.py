"""Presenter pour transformer les entités Chantier en réponses API."""

from typing import Optional, List, Dict, Any

from .chantier_schemas import ChantierResponse, ContactResponse, UserPublicSummary


def chantier_dto_to_dict(dto: "ChantierDTO") -> Dict[str, Any]:
    """Convertit un ChantierDTO en dictionnaire pour le presenter."""
    contacts = []
    if hasattr(dto, "contacts") and dto.contacts:
        contacts = [
            {"nom": c.nom, "profession": c.profession, "telephone": c.telephone}
            for c in dto.contacts
        ]

    return {
        "id": dto.id,
        "code": dto.code,
        "nom": dto.nom,
        "adresse": dto.adresse,
        "statut": dto.statut,
        "couleur": dto.couleur,
        "coordonnees_gps": dto.coordonnees_gps,
        "contact": dto.contact,
        "contacts": contacts,
        "maitre_ouvrage": dto.maitre_ouvrage,
        "heures_estimees": dto.heures_estimees,
        "date_debut": dto.date_debut,
        "date_fin": dto.date_fin,
        "description": dto.description,
        "conducteur_ids": dto.conducteur_ids,
        "chef_chantier_ids": dto.chef_chantier_ids,
        "type_travaux": dto.type_travaux,
        "batiment_plus_2ans": dto.batiment_plus_2ans,
        "usage_habitation": dto.usage_habitation,
        "created_at": dto.created_at.isoformat() if dto.created_at else None,
        "updated_at": dto.updated_at.isoformat() if dto.updated_at else None,
    }


def get_user_summary(
    user_id: int,
    user_repo: "UserRepository",
    include_telephone: bool = False,
) -> Optional[UserPublicSummary]:
    """
    Récupère les infos publiques d'un utilisateur pour l'inclusion dans un chantier.

    RGPD: Le téléphone est inclus UNIQUEMENT si include_telephone=True (chefs de chantier).
    Besoin opérationnel légitime: permettre aux ouvriers d'appeler leur chef sur chantier.

    Args:
        user_id: ID de l'utilisateur à récupérer.
        user_repo: Repository pour accéder aux utilisateurs.
        include_telephone: Si True, inclut le numéro de téléphone (pour chefs uniquement).

    Returns:
        UserPublicSummary avec les données publiques, ou None si non trouvé.
    """
    try:
        user = user_repo.find_by_id(user_id)
        if user:
            return UserPublicSummary(
                id=str(user.id),
                nom=user.nom,
                prenom=user.prenom,
                role=user.role.value,
                type_utilisateur=user.type_utilisateur.value,
                metier=user.metier,
                couleur=str(user.couleur) if user.couleur else None,
                telephone=user.telephone if include_telephone else None,
                is_active=user.is_active,
            )
        return None
    except (AttributeError, ValueError, TypeError):
        # Erreurs de conversion de types ou attributs manquants
        return None


def transform_chantier_response(
    chantier_dict: dict,
    controller: "ChantierController",
    user_repo: Optional["UserRepository"] = None,
    chantier_repo=None,
) -> ChantierResponse:
    """
    Transforme un dictionnaire chantier du controller en ChantierResponse.

    Convertit les IDs des conducteurs/chefs/ouvriers en objets User complets.
    """
    # Récupérer les coordonnées GPS
    coords = chantier_dict.get("coordonnees_gps") or {}
    latitude = coords.get("latitude") if coords else None
    longitude = coords.get("longitude") if coords else None

    # Récupérer le contact legacy (premier contact)
    contact = chantier_dict.get("contact") or {}
    contact_nom = contact.get("nom") if contact else None
    contact_telephone = contact.get("telephone") if contact else None

    # Récupérer les contacts multiples
    contacts_data = chantier_dict.get("contacts", [])
    contacts = [
        ContactResponse(
            nom=c.get("nom", ""),
            profession=c.get("profession"),
            telephone=c.get("telephone"),
        )
        for c in contacts_data
    ] if contacts_data else []

    # Si pas de contacts mais contact legacy, créer un contact
    if not contacts and contact_nom:
        contacts = [ContactResponse(
            nom=contact_nom,
            profession=None,
            telephone=contact_telephone,
        )]

    # Récupérer les IDs des conducteurs et chefs
    conducteur_ids = chantier_dict.get("conducteur_ids", [])
    chef_chantier_ids = chantier_dict.get("chef_chantier_ids", [])

    # Récupérer les IDs des ouvriers via le repository
    ouvrier_ids = []
    if chantier_repo:
        ouvrier_ids = chantier_repo.list_ouvrier_ids(chantier_dict.get("id"))

    # Récupérer les objets User complets si le repo est disponible
    conducteurs = []
    chefs = []
    ouvriers = []

    if user_repo:
        for uid in conducteur_ids:
            user_summary = get_user_summary(uid, user_repo)
            if user_summary:
                conducteurs.append(user_summary)

        for uid in chef_chantier_ids:
            user_summary = get_user_summary(uid, user_repo, include_telephone=True)
            if user_summary:
                chefs.append(user_summary)

        for uid in ouvrier_ids:
            user_summary = get_user_summary(uid, user_repo)
            if user_summary:
                ouvriers.append(user_summary)

    return ChantierResponse(
        id=str(chantier_dict.get("id", "")),
        code=chantier_dict.get("code", ""),
        nom=chantier_dict.get("nom", ""),
        adresse=chantier_dict.get("adresse", ""),
        statut=chantier_dict.get("statut", "ouvert"),
        couleur=chantier_dict.get("couleur"),
        latitude=latitude,
        longitude=longitude,
        contact_nom=contact_nom,
        contact_telephone=contact_telephone,
        contacts=contacts,
        maitre_ouvrage=chantier_dict.get("maitre_ouvrage"),
        heures_estimees=chantier_dict.get("heures_estimees"),
        date_debut_prevue=chantier_dict.get("date_debut"),
        date_fin_prevue=chantier_dict.get("date_fin"),
        description=chantier_dict.get("description"),
        conducteurs=conducteurs,
        chefs=chefs,
        ouvriers=ouvriers,
        created_at=chantier_dict.get("created_at", ""),
        updated_at=chantier_dict.get("updated_at"),
        type_travaux=chantier_dict.get("type_travaux"),
        batiment_plus_2ans=chantier_dict.get("batiment_plus_2ans"),
        usage_habitation=chantier_dict.get("usage_habitation"),
    )
