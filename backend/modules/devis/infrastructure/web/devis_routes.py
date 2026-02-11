"""Routes FastAPI pour le module Devis.

DEV-03: CRUD devis
DEV-07: Pieces jointes (integration GED)
DEV-08: Variantes et revisions
DEV-11: Personnalisation presentation
DEV-14: Signature electronique client
DEV-15: Workflow statut
DEV-17: Dashboard
DEV-19: Recherche avancee
DEV-23: Attestation TVA reglementaire
DEV-24: Relances automatiques
DEV-25: Frais de chantier
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Literal, Optional, List

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request, status
from fastapi.responses import Response
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy.orm import Session

from shared.infrastructure.database import get_db
from shared.infrastructure.rate_limiter import limiter
from shared.infrastructure.web import (
    get_current_user_id,
    get_current_user_role,
    require_conducteur_or_admin,
)
from shared.domain.calcul_financier import COEFF_FRAIS_GENERAUX
from modules.financier.infrastructure.web.dependencies import get_configuration_entreprise_repository
from modules.financier.domain.repositories import ConfigurationEntrepriseRepository

from ...domain.entities.devis import TransitionStatutDevisInvalideError
from ...domain.value_objects import StatutDevis
from ...domain.entities.devis import DevisValidationError
from ...application.use_cases.devis_use_cases import (
    DevisNotFoundError,
    DevisNotModifiableError,
)
from ...application.use_cases.version_use_cases import (
    CreerRevisionUseCase,
    CreerVarianteUseCase,
    ListerVersionsUseCase,
    GenererComparatifUseCase,
    GetComparatifUseCase,
    FigerVersionUseCase,
    VersionFigeeError,
)
from ...application.dtos.devis_dtos import DevisCreateDTO, DevisUpdateDTO
from ...application.dtos.version_dtos import (
    CreerRevisionDTO,
    CreerVarianteDTO,
    FigerVersionDTO,
)
from ...application.dtos.lot_dtos import LotDevisCreateDTO, LotDevisUpdateDTO
from ...application.dtos.ligne_dtos import LigneDevisCreateDTO, LigneDevisUpdateDTO
from ...application.dtos.debourse_dtos import DebourseDetailCreateDTO
from ...application.dtos.article_dtos import ArticleCreateDTO
from ...application.use_cases.lot_use_cases import LotDevisNotFoundError
from ...application.use_cases.ligne_use_cases import LigneDevisNotFoundError
from ...application.use_cases.article_use_cases import ArticleNotFoundError
from ...application.use_cases.dashboard_use_cases import GetDashboardDevisUseCase
from ...application.use_cases.search_use_cases import SearchDevisUseCase
from ...application.use_cases.calcul_totaux_use_cases import CalculerTotauxDevisUseCase
from ...application.use_cases.journal_use_cases import GetJournalDevisUseCase
from ...application.use_cases.devis_use_cases import (
    CreateDevisUseCase,
    UpdateDevisUseCase,
    GetDevisUseCase,
    ListDevisUseCase,
    DeleteDevisUseCase,
)
from ...application.use_cases.workflow_use_cases import (
    SoumettreDevisUseCase,
    ValiderDevisUseCase,
    RetournerBrouillonUseCase,
    AccepterDevisUseCase,
    RefuserDevisUseCase,
    PerduDevisUseCase,
)
from ...application.use_cases.relance_use_cases import (
    PlanifierRelancesUseCase,
    ExecuterRelancesUseCase,
    AnnulerRelancesUseCase,
    GetRelancesDevisUseCase,
    UpdateConfigRelancesUseCase,
    RelanceDevisPlanificationError,
)
from ...domain.entities.relance_devis import RelanceDevisValidationError
from ...domain.value_objects.config_relances import ConfigRelancesInvalideError
from ...application.dtos.relance_dtos import PlanifierRelancesDTO, UpdateConfigRelancesDTO
from ...application.use_cases.conversion_use_cases import (
    ConvertirDevisUseCase,
    GetConversionInfoUseCase,
    DevisNonConvertibleError,
    DevisDejaConvertiError,
)
from ...application.use_cases.lot_use_cases import (
    CreateLotDevisUseCase,
    UpdateLotDevisUseCase,
    DeleteLotDevisUseCase,
)
from ...application.use_cases.ligne_use_cases import (
    CreateLigneDevisUseCase,
    UpdateLigneDevisUseCase,
    DeleteLigneDevisUseCase,
)
from ...application.use_cases.article_use_cases import (
    CreateArticleUseCase,
    UpdateArticleUseCase,
    ListArticlesUseCase,
    GetArticleUseCase,
    DeleteArticleUseCase,
    ArticleCodeExistsError,
)
from ...application.dtos.article_dtos import ArticleUpdateDTO
from ...application.use_cases.attestation_tva_use_cases import (
    GenererAttestationTVAUseCase,
    GetAttestationTVAUseCase,
    VerifierEligibiliteTVAUseCase,
    AttestationTVADejaExistanteError,
    AttestationTVANotFoundError,
    TVANonEligibleError,
)
from ...domain.entities.attestation_tva import AttestationTVAValidationError
from ...application.dtos.attestation_tva_dtos import AttestationTVACreateDTO
from ...application.use_cases.frais_chantier_use_cases import (
    CreateFraisChantierUseCase,
    UpdateFraisChantierUseCase,
    DeleteFraisChantierUseCase,
    ListFraisChantierUseCase,
    CalculerRepartitionFraisUseCase,
    FraisChantierNotFoundError,
    DevisNonModifiableError,
)
from ...domain.entities.frais_chantier_devis import FraisChantierValidationError
from ...application.dtos.frais_chantier_dtos import FraisChantierCreateDTO, FraisChantierUpdateDTO
from ...application.use_cases.presentation_use_cases import (
    UpdateOptionsPresentationUseCase,
    GetOptionsPresentationUseCase,
    ListTemplatesPresentationUseCase,
)
from ...domain.value_objects.options_presentation import OptionsPresentationInvalideError
from ...application.dtos.options_presentation_dtos import UpdateOptionsPresentationDTO
from ...application.use_cases.signature_use_cases import (
    SignerDevisUseCase,
    GetSignatureUseCase,
    RevoquerSignatureUseCase,
    VerifierSignatureUseCase,
    SignatureNotFoundError,
    DevisNonSignableError,
    DevisDejaSigneError,
)
from ...domain.entities.signature_devis import SignatureDevisValidationError
from ...application.dtos.signature_dtos import SignatureCreateDTO
from ...application.use_cases.piece_jointe_use_cases import (
    ListerPiecesJointesUseCase,
    AjouterPieceJointeUseCase,
    SupprimerPieceJointeUseCase,
    ToggleVisibiliteUseCase,
)
from ...application.dtos.piece_jointe_dtos import PieceJointeCreateDTO
from ...application.use_cases.convertir_devis_en_chantier_use_case import (
    ConvertirDevisEnChantierUseCase,
    DevisNonConvertibleError,
    DevisDejaConvertiError,
    ConversionError,
)
from ...application.dtos.convertir_devis_dto import ConvertirDevisOptionsDTO

from .dependencies import (
    get_create_devis_use_case,
    get_update_devis_use_case,
    get_get_devis_use_case,
    get_list_devis_use_case,
    get_delete_devis_use_case,
    get_soumettre_devis_use_case,
    get_valider_devis_use_case,
    get_retourner_brouillon_use_case,
    get_accepter_devis_use_case,
    get_refuser_devis_use_case,
    get_perdu_devis_use_case,
    get_search_devis_use_case,
    get_dashboard_devis_use_case,
    get_calculer_totaux_use_case,
    get_journal_devis_use_case,
    get_create_lot_use_case,
    get_update_lot_use_case,
    get_delete_lot_use_case,
    get_create_ligne_use_case,
    get_update_ligne_use_case,
    get_delete_ligne_use_case,
    get_create_article_use_case,
    get_update_article_use_case,
    get_list_articles_use_case,
    get_get_article_use_case,
    get_delete_article_use_case,
    # DEV-08: Versioning
    get_creer_revision_use_case,
    get_creer_variante_use_case,
    get_lister_versions_use_case,
    get_generer_comparatif_use_case,
    get_get_comparatif_use_case,
    get_figer_version_use_case,
    # DEV-23: Attestation TVA
    get_generer_attestation_tva_use_case,
    get_get_attestation_tva_use_case,
    get_verifier_eligibilite_tva_use_case,
    # DEV-25: Frais de chantier
    get_create_frais_chantier_use_case,
    get_update_frais_chantier_use_case,
    get_delete_frais_chantier_use_case,
    get_list_frais_chantier_use_case,
    get_calculer_repartition_frais_use_case,
    # DEV-11: Options de presentation
    get_update_options_presentation_use_case,
    get_get_options_presentation_use_case,
    get_list_templates_presentation_use_case,
    # DEV-14: Signature electronique
    get_signer_devis_use_case,
    get_get_signature_use_case,
    get_revoquer_signature_use_case,
    get_verifier_signature_use_case,
    # DEV-16: Conversion en chantier
    get_convertir_devis_use_case,
    get_get_conversion_info_use_case,
    # DEV-16: Conversion devis -> chantier (use case enrichi)
    get_convertir_devis_en_chantier_use_case,
    # DEV-07: Pieces jointes
    get_lister_pieces_jointes_use_case,
    get_ajouter_piece_jointe_use_case,
    get_supprimer_piece_jointe_use_case,
    get_toggle_visibilite_use_case,
    # DEV-24: Relances automatiques
    get_planifier_relances_use_case,
    get_executer_relances_use_case,
    get_annuler_relances_use_case,
    get_get_relances_devis_use_case,
    get_update_config_relances_use_case,
    # DEV-12: Generation PDF
    get_generate_pdf_use_case,
)
from ...application.use_cases.generate_pdf_use_case import (
    GenerateDevisPDFUseCase,
    GenerateDevisPDFError,
)


# ─────────────────────────────────────────────────────────────────────────────
# Pydantic request models
# ─────────────────────────────────────────────────────────────────────────────

class DevisCreateRequest(BaseModel):
    client_nom: str = Field(..., min_length=1, max_length=200)
    objet: str = Field(..., min_length=1, max_length=500)
    chantier_ref: Optional[str] = Field(None, max_length=50)
    client_adresse: Optional[str] = Field(None, max_length=500)
    client_email: Optional[str] = Field(None, max_length=255)
    client_telephone: Optional[str] = Field(None, max_length=30)
    date_validite: Optional[date] = None
    taux_tva_defaut: Decimal = Field(Decimal("20"), ge=0, le=100)
    taux_marge_global: Decimal = Field(Decimal("15"), ge=0, le=100)
    taux_marge_moe: Optional[Decimal] = Field(None, ge=0, le=100)
    taux_marge_materiaux: Optional[Decimal] = Field(None, ge=0, le=100)
    taux_marge_sous_traitance: Optional[Decimal] = Field(None, ge=0, le=100)
    taux_marge_materiel: Optional[Decimal] = Field(None, ge=0, le=100)
    taux_marge_deplacement: Optional[Decimal] = Field(None, ge=0, le=100)
    coefficient_frais_generaux: Optional[Decimal] = Field(None, ge=0, le=100, description="Si absent, lu depuis config entreprise (BDD)")
    retenue_garantie_pct: Decimal = Field(Decimal("0"), ge=0, le=5, description="Retenue de garantie: 0 ou 5% (Loi 71-584)")
    notes: Optional[str] = Field(None, max_length=2000)
    acompte_pct: Decimal = Field(Decimal("30"), ge=0, le=100)
    echeance: str = Field("30_jours_fin_mois", max_length=50)
    moyens_paiement: Optional[List[str]] = None
    date_visite: Optional[date] = None
    date_debut_travaux: Optional[date] = None
    duree_estimee_jours: Optional[int] = Field(None, ge=1)
    notes_bas_page: Optional[str] = Field(None, max_length=5000)
    nom_interne: Optional[str] = Field(None, max_length=255)
    commercial_id: Optional[int] = None
    conducteur_id: Optional[int] = None

    @field_validator("retenue_garantie_pct")
    @classmethod
    def valider_retenue_garantie(cls, v: Decimal) -> Decimal:
        """DEV-22 / Loi 71-584: retenue de garantie 0% ou 5% max."""
        if v not in (Decimal("0"), Decimal("5")):
            raise ValueError("La retenue de garantie doit etre 0% ou 5% (Loi 71-584 art. 1)")
        return v


class DevisUpdateRequest(BaseModel):
    client_nom: Optional[str] = Field(None, min_length=1, max_length=200)
    objet: Optional[str] = Field(None, min_length=1, max_length=500)
    chantier_ref: Optional[str] = Field(None, max_length=50)
    client_adresse: Optional[str] = Field(None, max_length=500)
    client_email: Optional[str] = Field(None, max_length=255)
    client_telephone: Optional[str] = Field(None, max_length=30)
    date_validite: Optional[date] = None
    taux_tva_defaut: Optional[Decimal] = Field(None, ge=0, le=100)
    taux_marge_global: Optional[Decimal] = Field(None, ge=0, le=100)
    taux_marge_moe: Optional[Decimal] = Field(None, ge=0, le=100)
    taux_marge_materiaux: Optional[Decimal] = Field(None, ge=0, le=100)
    taux_marge_sous_traitance: Optional[Decimal] = Field(None, ge=0, le=100)
    taux_marge_materiel: Optional[Decimal] = Field(None, ge=0, le=100)
    taux_marge_deplacement: Optional[Decimal] = Field(None, ge=0, le=100)
    coefficient_frais_generaux: Optional[Decimal] = Field(None, ge=0, le=100, description="Ignore - source unique COEFF_FRAIS_GENERAUX")
    retenue_garantie_pct: Optional[Decimal] = Field(None, ge=0, le=5, description="Retenue de garantie: 0 ou 5% (Loi 71-584)")
    notes: Optional[str] = Field(None, max_length=2000)
    acompte_pct: Optional[Decimal] = Field(None, ge=0, le=100)
    echeance: Optional[str] = Field(None, max_length=50)
    moyens_paiement: Optional[List[str]] = None
    date_visite: Optional[date] = None
    date_debut_travaux: Optional[date] = None
    duree_estimee_jours: Optional[int] = Field(None, ge=1)
    notes_bas_page: Optional[str] = Field(None, max_length=5000)
    nom_interne: Optional[str] = Field(None, max_length=255)
    commercial_id: Optional[int] = None
    conducteur_id: Optional[int] = None

    @field_validator("retenue_garantie_pct")
    @classmethod
    def valider_retenue_garantie(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """DEV-22 / Loi 71-584: retenue de garantie 0% ou 5% max."""
        if v is not None and v not in (Decimal("0"), Decimal("5")):
            raise ValueError("La retenue de garantie doit etre 0% ou 5% (Loi 71-584 art. 1)")
        return v


class MotifRequest(BaseModel):
    motif: str = Field(..., min_length=1, max_length=1000)


class ConvertirDevisRequest(BaseModel):
    """Options pour la conversion d'un devis en chantier."""
    notify_client: bool = False
    notify_team: bool = True


class LotCreateRequest(BaseModel):
    devis_id: Optional[int] = None  # Optionnel car fourni par le path param
    titre: str = Field(..., min_length=1, max_length=300)
    numero: str = ""
    ordre: int = 0
    marge_lot_pct: Optional[Decimal] = None


class LotUpdateRequest(BaseModel):
    titre: Optional[str] = Field(None, min_length=1, max_length=300)
    numero: Optional[str] = None
    ordre: Optional[int] = None
    marge_lot_pct: Optional[Decimal] = None


class DebourseCreateRequest(BaseModel):
    type_debourse: str = Field(..., min_length=1, max_length=50, description="Type de debourse (moe, materiaux, sous_traitance, materiel, deplacement)")
    designation: str = Field(..., min_length=1, max_length=300)
    quantite: Decimal = Field(Decimal("0"), ge=0)
    prix_unitaire: Decimal = Field(Decimal("0"), ge=0)
    unite: str = "U"


class LigneCreateRequest(BaseModel):
    lot_devis_id: Optional[int] = None  # Optionnel car fourni par le path param
    designation: str = Field(..., min_length=1, max_length=500)
    unite: str = "U"
    quantite: Decimal = Field(Decimal("0"), ge=0)
    prix_unitaire_ht: Decimal = Field(Decimal("0"), ge=0)
    taux_tva: Decimal = Field(Decimal("20"), ge=0, le=100)
    ordre: int = 0
    marge_ligne_pct: Optional[Decimal] = Field(None, ge=0, le=100)
    article_id: Optional[int] = None
    debourses: list[DebourseCreateRequest] = []


class ArticleCreateRequest(BaseModel):
    designation: str = Field(..., min_length=1, max_length=300)
    unite: str = Field("U", max_length=20)
    prix_unitaire_ht: Decimal = Field(Decimal("0"), ge=0)
    code: Optional[str] = Field(None, max_length=50)
    categorie: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)
    taux_tva: Decimal = Field(Decimal("20"), ge=0, le=100)
    actif: bool = True


class ArticleUpdateRequest(BaseModel):
    """Requete de mise a jour d'un article (DEV-01)."""

    designation: Optional[str] = Field(None, min_length=1, max_length=300)
    unite: Optional[str] = Field(None, max_length=20)
    prix_unitaire_ht: Optional[Decimal] = Field(None, ge=0)
    code: Optional[str] = Field(None, max_length=50)
    categorie: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)
    taux_tva: Optional[Decimal] = Field(None, ge=0, le=100)
    actif: Optional[bool] = None


class LigneUpdateRequest(BaseModel):
    designation: Optional[str] = Field(None, min_length=1, max_length=500)
    unite: Optional[str] = None
    quantite: Optional[Decimal] = None
    prix_unitaire_ht: Optional[Decimal] = None
    taux_tva: Optional[Decimal] = None
    ordre: Optional[int] = None
    marge_ligne_pct: Optional[Decimal] = None
    article_id: Optional[int] = None
    debourses: Optional[list[DebourseCreateRequest]] = None


# DEV-08: Request models pour versioning
class RevisionCreateRequest(BaseModel):
    commentaire: Optional[str] = Field(None, max_length=2000)


class VarianteCreateRequest(BaseModel):
    label_variante: str = Field(..., min_length=1, max_length=50)
    commentaire: Optional[str] = Field(None, max_length=2000)


class FigerVersionRequest(BaseModel):
    commentaire: Optional[str] = Field(None, max_length=2000)


# DEV-23: Request model pour attestation TVA
class AttestationTVACreateRequest(BaseModel):
    """Donnees pour generer une attestation TVA reglementaire."""

    nom_client: Optional[str] = Field(None, max_length=200, description="Nom du client (defaut: client du devis)")
    adresse_client: Optional[str] = Field(None, max_length=500, description="Adresse du client (defaut: adresse du devis)")
    telephone_client: Optional[str] = Field(None, max_length=30)
    adresse_immeuble: str = Field(..., min_length=1, max_length=500, description="Adresse de l'immeuble concerne")
    nature_immeuble: Literal["maison", "appartement", "immeuble"] = Field(
        "maison", description="Type d'immeuble"
    )
    date_construction_plus_2ans: bool = Field(
        True, description="L'immeuble a plus de 2 ans (obligatoire pour TVA reduite)"
    )
    description_travaux: str = Field(
        ..., min_length=1, max_length=2000, description="Description des travaux"
    )
    nature_travaux: Literal["amelioration", "entretien", "transformation"] = Field(
        "amelioration", description="Nature des travaux"
    )
    atteste_par: str = Field(
        ..., min_length=1, max_length=200, description="Nom du signataire"
    )


# DEV-25: Request models pour frais de chantier
class FraisChantierCreateRequest(BaseModel):
    """Donnees pour creer un frais de chantier."""

    type_frais: Literal[
        "compte_prorata", "frais_generaux", "installation_chantier", "autre"
    ] = Field(..., description="Type de frais de chantier")
    libelle: str = Field(..., min_length=1, max_length=300)
    montant_ht: Decimal = Field(..., ge=0, description="Montant HT du frais")
    mode_repartition: Literal["global", "prorata_lots"] = Field(
        "global", description="Mode de repartition sur les lots"
    )
    taux_tva: Decimal = Field(Decimal("20"), ge=0, le=100)
    ordre: int = Field(0, ge=0)
    lot_devis_id: Optional[int] = Field(
        None, description="ID du lot associe (optionnel)"
    )


class FraisChantierUpdateRequest(BaseModel):
    """Donnees pour modifier un frais de chantier."""

    type_frais: Optional[
        Literal["compte_prorata", "frais_generaux", "installation_chantier", "autre"]
    ] = None
    libelle: Optional[str] = Field(None, min_length=1, max_length=300)
    montant_ht: Optional[Decimal] = Field(None, ge=0)
    mode_repartition: Optional[Literal["global", "prorata_lots"]] = None
    taux_tva: Optional[Decimal] = Field(None, ge=0, le=100)
    ordre: Optional[int] = Field(None, ge=0)
    lot_devis_id: Optional[int] = None


# DEV-11: Request model pour options de presentation
class OptionsPresentationUpdateRequest(BaseModel):
    """Donnees pour mettre a jour les options de presentation d'un devis."""

    afficher_debourses: Optional[bool] = Field(
        None, description="Afficher les debourses (toujours force a False)"
    )
    afficher_composants: Optional[bool] = Field(
        None, description="Afficher le detail des composants"
    )
    afficher_quantites: Optional[bool] = Field(
        None, description="Afficher les quantites par ligne"
    )
    afficher_prix_unitaires: Optional[bool] = Field(
        None, description="Afficher les prix unitaires par ligne"
    )
    afficher_tva_detaillee: Optional[bool] = Field(
        None, description="Afficher le detail TVA par taux"
    )
    afficher_conditions_generales: Optional[bool] = Field(
        None, description="Afficher les conditions generales"
    )
    afficher_logo: Optional[bool] = Field(
        None, description="Afficher le logo de l'entreprise"
    )
    afficher_coordonnees_entreprise: Optional[bool] = Field(
        None, description="Afficher les coordonnees de l'entreprise"
    )
    afficher_retenue_garantie: Optional[bool] = Field(
        None, description="Afficher la retenue de garantie"
    )
    afficher_frais_chantier_detail: Optional[bool] = Field(
        None, description="Afficher le detail des frais de chantier"
    )
    template_nom: Optional[
        Literal["standard", "simplifie", "detaille", "minimaliste"]
    ] = Field(None, description="Nom du template de presentation a appliquer")


# DEV-14: Request models pour signature electronique
class SignatureCreateRequest(BaseModel):
    """Donnees pour signer un devis electroniquement."""

    type_signature: Literal["dessin_tactile", "upload_scan", "nom_prenom"] = Field(
        ..., description="Type de signature electronique"
    )
    signataire_nom: str = Field(
        ..., min_length=1, max_length=200, description="Nom complet du signataire"
    )
    signataire_email: EmailStr = Field(
        ..., description="Email du signataire"
    )
    signature_data: str = Field(
        ..., min_length=1, max_length=2_000_000, description="Donnees de signature (base64 PNG, path scan, texte) - max ~1.5 Mo base64"
    )
    signataire_telephone: Optional[str] = Field(
        None, max_length=30, description="Telephone du signataire"
    )


class RevocationSignatureRequest(BaseModel):
    """Donnees pour revoquer une signature."""

    motif: str = Field(
        ..., min_length=1, max_length=1000, description="Motif de la revocation"
    )


# DEV-24: Request models pour relances automatiques
class PlanifierRelancesRequest(BaseModel):
    """Donnees pour planifier les relances d'un devis."""

    message_personnalise: Optional[str] = Field(
        None, max_length=2000, description="Message personnalise pour les relances"
    )


class ConfigRelancesUpdateRequest(BaseModel):
    """Donnees pour modifier la configuration des relances."""

    delais: Optional[List[int]] = Field(
        None, description="Delais en jours pour chaque relance (ex: [7, 15, 30])"
    )
    actif: Optional[bool] = Field(
        None, description="Activer/desactiver les relances"
    )
    type_relance_defaut: Optional[
        Literal["email", "push", "email_push"]
    ] = Field(
        None, description="Type de relance par defaut"
    )

    @field_validator("delais")
    @classmethod
    def valider_delais(cls, v: Optional[List[int]]) -> Optional[List[int]]:
        """Valide que les delais sont positifs et croissants."""
        if v is not None:
            if not v:
                raise ValueError("Au moins un delai est requis")
            for delai in v:
                if delai < 1:
                    raise ValueError(f"Chaque delai doit etre >= 1 jour (recu: {delai})")
            if v != sorted(v):
                raise ValueError("Les delais doivent etre en ordre croissant")
        return v


# ─────────────────────────────────────────────────────────────────────────────
# Router
# ─────────────────────────────────────────────────────────────────────────────

router = APIRouter(prefix="/devis", tags=["devis"])


# ─────────────────────────────────────────────────────────────────────────────
# Dashboard
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/dashboard")
async def get_dashboard(
    _role: str = Depends(require_conducteur_or_admin),
    use_case: GetDashboardDevisUseCase = Depends(get_dashboard_devis_use_case),
):
    """Tableau de bord devis - KPI pipeline commercial (DEV-17)."""
    result = use_case.execute()
    return result.to_dict()


# ─────────────────────────────────────────────────────────────────────────────
# Templates de presentation (DEV-11) - route statique avant /{devis_id}
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/templates-presentation")
async def list_templates_presentation(
    _role: str = Depends(require_conducteur_or_admin),
    use_case: ListTemplatesPresentationUseCase = Depends(
        get_list_templates_presentation_use_case
    ),
):
    """Liste les templates de presentation disponibles (DEV-11).

    Retourne tous les templates predefinis avec leur description
    et configuration d'options.
    """
    result = use_case.execute()
    return result.to_dict()


# ─────────────────────────────────────────────────────────────────────────────
# Devis CRUD
# ─────────────────────────────────────────────────────────────────────────────

@router.get("")
async def list_devis(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    _role: str = Depends(require_conducteur_or_admin),
    use_case: ListDevisUseCase = Depends(get_list_devis_use_case),
):
    """Liste les devis avec pagination (DEV-03)."""
    result = use_case.execute(limit=limit, offset=offset)
    return {
        "items": [d.to_dict() for d in result.items],
        "total": result.total,
        "limit": result.limit,
        "offset": result.offset,
    }


@router.get("/search")
async def search_devis(
    client_nom: Optional[str] = None,
    statut: Optional[str] = None,
    date_min: Optional[date] = None,
    date_max: Optional[date] = None,
    montant_min: Optional[Decimal] = None,
    montant_max: Optional[Decimal] = None,
    commercial_id: Optional[int] = None,
    search: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    _role: str = Depends(require_conducteur_or_admin),
    use_case: SearchDevisUseCase = Depends(get_search_devis_use_case),
):
    """Recherche avancee de devis (DEV-19)."""
    statut_enum = None
    if statut:
        try:
            statut_enum = StatutDevis(statut)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Statut invalide: {statut}",
            )

    result = use_case.execute(
        client_nom=client_nom,
        statut=statut_enum,
        date_creation_min=date_min,
        date_creation_max=date_max,
        montant_min=montant_min,
        montant_max=montant_max,
        commercial_id=commercial_id,
        search=search,
        limit=limit,
        offset=offset,
    )
    return {
        "items": [d.to_dict() for d in result.items],
        "total": result.total,
        "limit": result.limit,
        "offset": result.offset,
    }


# DEV-08: Comparatif par ID (doit etre avant /{devis_id} pour eviter conflit de path)
@router.get("/comparatifs/{comparatif_id}")
async def get_comparatif(
    comparatif_id: int,
    _role: str = Depends(require_conducteur_or_admin),
    use_case: GetComparatifUseCase = Depends(get_get_comparatif_use_case),
):
    """Recupere un comparatif existant par son ID (DEV-08)."""
    try:
        result = use_case.execute(comparatif_id)
        return result.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{devis_id}")
async def get_devis(
    devis_id: int,
    _role: str = Depends(require_conducteur_or_admin),
    use_case: GetDevisUseCase = Depends(get_get_devis_use_case),
):
    """Recupere un devis avec ses details complets (DEV-03)."""
    try:
        result = use_case.execute(devis_id)
        return result.to_dict()
    except DevisNotFoundError:
        raise HTTPException(status_code=404, detail=f"Devis {devis_id} non trouve")


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_devis(
    request: DevisCreateRequest,
    db: Session = Depends(get_db),
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case: CreateDevisUseCase = Depends(get_create_devis_use_case),
    config_repository: ConfigurationEntrepriseRepository = Depends(get_configuration_entreprise_repository),
):
    """Cree un nouveau devis (DEV-03)."""
    # Resoudre coefficient_frais_generaux depuis config entreprise (SSOT)
    coeff_fg = request.coefficient_frais_generaux
    if coeff_fg is None:
        coeff_fg = COEFF_FRAIS_GENERAUX  # fallback
        config = config_repository.find_by_annee(datetime.now().year)
        if config:
            coeff_fg = config.coeff_frais_generaux

    dto = DevisCreateDTO(
        client_nom=request.client_nom,
        objet=request.objet,
        chantier_ref=request.chantier_ref,
        client_adresse=request.client_adresse,
        client_email=request.client_email,
        client_telephone=request.client_telephone,
        date_validite=request.date_validite,
        taux_tva_defaut=request.taux_tva_defaut,
        taux_marge_global=request.taux_marge_global,
        taux_marge_moe=request.taux_marge_moe,
        taux_marge_materiaux=request.taux_marge_materiaux,
        taux_marge_sous_traitance=request.taux_marge_sous_traitance,
        taux_marge_materiel=request.taux_marge_materiel,
        taux_marge_deplacement=request.taux_marge_deplacement,
        coefficient_frais_generaux=coeff_fg,
        retenue_garantie_pct=request.retenue_garantie_pct,
        notes=request.notes,
        acompte_pct=request.acompte_pct,
        echeance=request.echeance,
        moyens_paiement=request.moyens_paiement,
        date_visite=request.date_visite,
        date_debut_travaux=request.date_debut_travaux,
        duree_estimee_jours=request.duree_estimee_jours,
        notes_bas_page=request.notes_bas_page,
        nom_interne=request.nom_interne,
        commercial_id=request.commercial_id,
        conducteur_id=request.conducteur_id,
    )
    result = use_case.execute(dto, current_user_id)
    db.commit()
    return result.to_dict()


@router.put("/{devis_id}")
async def update_devis(
    devis_id: int,
    request: DevisUpdateRequest,
    db: Session = Depends(get_db),
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case: UpdateDevisUseCase = Depends(get_update_devis_use_case),
):
    """Met a jour un devis (DEV-03)."""
    dto = DevisUpdateDTO(**request.model_dump(exclude_unset=True))
    try:
        result = use_case.execute(devis_id, dto, current_user_id)
        db.commit()
        return result.to_dict()
    except DevisNotFoundError:
        raise HTTPException(status_code=404, detail=f"Devis {devis_id} non trouve")
    except DevisNotModifiableError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.delete("/{devis_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_devis(
    devis_id: int,
    db: Session = Depends(get_db),
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case: DeleteDevisUseCase = Depends(get_delete_devis_use_case),
):
    """Supprime un devis en brouillon (DEV-03)."""
    try:
        use_case.execute(devis_id, current_user_id)
        db.commit()
    except DevisNotFoundError:
        raise HTTPException(status_code=404, detail=f"Devis {devis_id} non trouve")
    except DevisNotModifiableError as e:
        raise HTTPException(status_code=409, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# Workflow transitions (DEV-15)
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/{devis_id}/soumettre")
async def soumettre_devis(
    devis_id: int,
    db: Session = Depends(get_db),
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case: SoumettreDevisUseCase = Depends(get_soumettre_devis_use_case),
):
    """Soumet un devis pour validation (brouillon -> en_validation)."""
    try:
        result = use_case.execute(devis_id, current_user_id)
        db.commit()
        return result.to_dict()
    except DevisNotFoundError:
        raise HTTPException(status_code=404, detail=f"Devis {devis_id} non trouve")
    except TransitionStatutDevisInvalideError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/{devis_id}/valider")
async def valider_devis(
    devis_id: int,
    db: Session = Depends(get_db),
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case: ValiderDevisUseCase = Depends(get_valider_devis_use_case),
):
    """Valide et envoie un devis (en_validation -> envoye)."""
    try:
        result = use_case.execute(devis_id, current_user_id)
        db.commit()
        return result.to_dict()
    except DevisNotFoundError:
        raise HTTPException(status_code=404, detail=f"Devis {devis_id} non trouve")
    except TransitionStatutDevisInvalideError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/{devis_id}/retourner-brouillon")
async def retourner_brouillon(
    devis_id: int,
    db: Session = Depends(get_db),
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case: RetournerBrouillonUseCase = Depends(get_retourner_brouillon_use_case),
):
    """Retourne un devis en brouillon (en_validation -> brouillon)."""
    try:
        result = use_case.execute(devis_id, current_user_id)
        db.commit()
        return result.to_dict()
    except DevisNotFoundError:
        raise HTTPException(status_code=404, detail=f"Devis {devis_id} non trouve")
    except TransitionStatutDevisInvalideError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/{devis_id}/accepter")
async def accepter_devis(
    devis_id: int,
    db: Session = Depends(get_db),
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case: AccepterDevisUseCase = Depends(get_accepter_devis_use_case),
):
    """Accepte un devis (envoye/vu/en_negociation -> accepte)."""
    try:
        result = use_case.execute(devis_id, current_user_id)
        db.commit()
        return result.to_dict()
    except DevisNotFoundError:
        raise HTTPException(status_code=404, detail=f"Devis {devis_id} non trouve")
    except TransitionStatutDevisInvalideError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/{devis_id}/refuser")
async def refuser_devis(
    devis_id: int,
    body: MotifRequest,
    db: Session = Depends(get_db),
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case: RefuserDevisUseCase = Depends(get_refuser_devis_use_case),
):
    """Refuse un devis avec motif (envoye/vu/en_negociation -> refuse)."""
    try:
        result = use_case.execute(devis_id, current_user_id, body.motif)
        db.commit()
        return result.to_dict()
    except DevisNotFoundError:
        raise HTTPException(status_code=404, detail=f"Devis {devis_id} non trouve")
    except TransitionStatutDevisInvalideError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/{devis_id}/perdu")
async def marquer_perdu(
    devis_id: int,
    body: MotifRequest,
    db: Session = Depends(get_db),
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case: PerduDevisUseCase = Depends(get_perdu_devis_use_case),
):
    """Marque un devis comme perdu avec motif (en_negociation -> perdu)."""
    try:
        result = use_case.execute(devis_id, current_user_id, body.motif)
        db.commit()
        return result.to_dict()
    except DevisNotFoundError:
        raise HTTPException(status_code=404, detail=f"Devis {devis_id} non trouve")
    except TransitionStatutDevisInvalideError as e:
        raise HTTPException(status_code=409, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# Conversion en chantier (DEV-16)
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/{devis_id}/conversion-info")
async def get_conversion_info(
    devis_id: int,
    _role: str = Depends(require_conducteur_or_admin),
    use_case: GetConversionInfoUseCase = Depends(get_get_conversion_info_use_case),
):
    """Verifie les pre-requis de conversion d'un devis en chantier (DEV-16).

    Retourne si la conversion est possible et les pre-requis manquants :
    - Statut 'accepte'
    - Signature client valide
    - Non deja converti
    """
    try:
        result = use_case.execute(devis_id)
        return result.to_dict()
    except DevisNotFoundError:
        raise HTTPException(status_code=404, detail=f"Devis {devis_id} non trouve")


@router.post("/{devis_id}/convertir", status_code=status.HTTP_201_CREATED)
async def convertir_devis(
    devis_id: int,
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case: ConvertirDevisUseCase = Depends(get_convertir_devis_use_case),
):
    """Convertit un devis accepte et signe en chantier (DEV-16).

    Pre-requis :
    - Devis en statut 'accepte'
    - Signature client valide
    - Pas deja converti

    La conversion emet un DevisConvertEvent pour que les modules
    chantier et financier puissent creer leurs entites.

    Retourne les donnees de conversion (client, budget, lots, retenue garantie).
    """
    try:
        result = use_case.execute(devis_id, current_user_id)
        return result.to_dict()
    except DevisNotFoundError:
        raise HTTPException(status_code=404, detail=f"Devis {devis_id} non trouve")
    except DevisDejaConvertiError as e:
        raise HTTPException(status_code=409, detail=e.message)
    except DevisNonConvertibleError as e:
        raise HTTPException(status_code=422, detail=e.message)
    except DevisValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# Versioning - Revisions et Variantes (DEV-08)
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/{devis_id}/revisions", status_code=status.HTTP_201_CREATED)
async def creer_revision(
    devis_id: int,
    request: RevisionCreateRequest,
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case: CreerRevisionUseCase = Depends(get_creer_revision_use_case),
):
    """Cree une revision d'un devis (copie profonde + gel automatique) (DEV-08)."""
    dto = CreerRevisionDTO(commentaire=request.commentaire)
    try:
        result = use_case.execute(devis_id, dto, current_user_id)
        return result.to_dict()
    except DevisNotFoundError:
        raise HTTPException(status_code=404, detail=f"Devis {devis_id} non trouve")
    except VersionFigeeError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except DevisValidationError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/{devis_id}/variantes", status_code=status.HTTP_201_CREATED)
async def creer_variante(
    devis_id: int,
    request: VarianteCreateRequest,
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case: CreerVarianteUseCase = Depends(get_creer_variante_use_case),
):
    """Cree une variante d'un devis (economique/standard/premium) (DEV-08)."""
    dto = CreerVarianteDTO(
        label_variante=request.label_variante,
        commentaire=request.commentaire,
    )
    try:
        result = use_case.execute(devis_id, dto, current_user_id)
        return result.to_dict()
    except DevisNotFoundError:
        raise HTTPException(status_code=404, detail=f"Devis {devis_id} non trouve")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{devis_id}/versions")
async def lister_versions(
    devis_id: int,
    _role: str = Depends(require_conducteur_or_admin),
    use_case: ListerVersionsUseCase = Depends(get_lister_versions_use_case),
):
    """Liste toutes les versions/variantes d'un devis (DEV-08)."""
    try:
        result = use_case.execute(devis_id)
        return {"versions": [v.to_dict() for v in result]}
    except DevisNotFoundError:
        raise HTTPException(status_code=404, detail=f"Devis {devis_id} non trouve")


@router.post("/{devis_id}/comparer/{cible_id}", status_code=status.HTTP_201_CREATED)
async def generer_comparatif(
    devis_id: int,
    cible_id: int,
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case: GenererComparatifUseCase = Depends(get_generer_comparatif_use_case),
):
    """Genere un comparatif detaille entre deux versions de devis (DEV-08)."""
    try:
        result = use_case.execute(devis_id, cible_id, current_user_id)
        return result.to_dict()
    except DevisNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{devis_id}/figer")
async def figer_version(
    devis_id: int,
    request: FigerVersionRequest,
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case: FigerVersionUseCase = Depends(get_figer_version_use_case),
):
    """Fige (gele) manuellement une version de devis (DEV-08)."""
    dto = FigerVersionDTO(commentaire=request.commentaire)
    try:
        result = use_case.execute(devis_id, dto, current_user_id)
        return result.to_dict()
    except DevisNotFoundError:
        raise HTTPException(status_code=404, detail=f"Devis {devis_id} non trouve")
    except DevisValidationError as e:
        raise HTTPException(status_code=409, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# Conversion Devis -> Chantier (DEV-16)
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/{devis_id}/convertir-en-chantier", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def convertir_devis_en_chantier(
    request: Request,
    devis_id: int,
    body: ConvertirDevisRequest = ConvertirDevisRequest(),
    db: Session = Depends(get_db),
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case: ConvertirDevisEnChantierUseCase = Depends(get_convertir_devis_en_chantier_use_case),
):
    """Convertit un devis accepte en chantier operationnel (DEV-16).

    Cree un chantier, un budget et des lots budgetaires a partir du devis.
    Le devis passe en statut 'converti' et devient immutable.
    """
    try:
        options = ConvertirDevisOptionsDTO(
            notify_client=body.notify_client,
            notify_team=body.notify_team,
        )
        result = use_case.execute(devis_id, current_user_id, options)
        db.commit()
        return {
            "success": True,
            "message": "Devis converti en chantier avec succes",
            "data": result.to_dict(),
        }
    except DevisNonConvertibleError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )
    except DevisDejaConvertiError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "DEVIS_ALREADY_CONVERTED",
                "message": e.message,
                "chantier_ref": e.chantier_ref,
            },
        )
    except ConversionError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur technique lors de la conversion. Veuillez reessayer ou contacter l'administrateur.",
        )


# ─────────────────────────────────────────────────────────────────────────────
# Calcul totaux (DEV-06)
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/{devis_id}/calculer")
async def calculer_totaux(
    devis_id: int,
    db: Session = Depends(get_db),
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case: CalculerTotauxDevisUseCase = Depends(get_calculer_totaux_use_case),
):
    """Recalcule les totaux et marges du devis (DEV-06)."""
    try:
        result = use_case.execute(devis_id, current_user_id)
        db.commit()
        return result
    except DevisNotFoundError:
        raise HTTPException(status_code=404, detail=f"Devis {devis_id} non trouve")


# ─────────────────────────────────────────────────────────────────────────────
# Journal (DEV-18)
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/{devis_id}/journal")
async def get_journal(
    devis_id: int,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    _role: str = Depends(require_conducteur_or_admin),
    use_case: GetJournalDevisUseCase = Depends(get_journal_devis_use_case),
):
    """Consulte le journal d'audit d'un devis (DEV-18)."""
    result = use_case.execute(devis_id, limit=limit, offset=offset)
    return {
        "items": [e.to_dict() for e in result["items"]],
        "total": result["total"],
        "limit": result["limit"],
        "offset": result["offset"],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Attestation TVA (DEV-23)
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/{devis_id}/eligibilite-tva")
async def verifier_eligibilite_tva(
    devis_id: int,
    _role: str = Depends(require_conducteur_or_admin),
    use_case: VerifierEligibiliteTVAUseCase = Depends(get_verifier_eligibilite_tva_use_case),
):
    """Verifie si un devis est eligible a la TVA reduite (DEV-23)."""
    try:
        result = use_case.execute(devis_id)
        return result.to_dict()
    except DevisNotFoundError:
        raise HTTPException(status_code=404, detail=f"Devis {devis_id} non trouve")


@router.post("/{devis_id}/attestation-tva", status_code=status.HTTP_201_CREATED)
async def generer_attestation_tva(
    devis_id: int,
    request: AttestationTVACreateRequest,
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case: GenererAttestationTVAUseCase = Depends(get_generer_attestation_tva_use_case),
):
    """Genere une attestation TVA pour un devis avec TVA reduite (DEV-23).

    L'attestation CERFA est determinee automatiquement selon le taux TVA du devis:
    - Taux 5.5% -> CERFA 1301-SD (travaux lourds / renovation energetique)
    - Taux 10% -> CERFA 1300-SD (travaux simples / renovation standard)
    """
    dto = AttestationTVACreateDTO(
        nom_client=request.nom_client,
        adresse_client=request.adresse_client,
        telephone_client=request.telephone_client,
        adresse_immeuble=request.adresse_immeuble,
        nature_immeuble=request.nature_immeuble,
        date_construction_plus_2ans=request.date_construction_plus_2ans,
        description_travaux=request.description_travaux,
        nature_travaux=request.nature_travaux,
        atteste_par=request.atteste_par,
    )
    try:
        result = use_case.execute(devis_id, dto, current_user_id)
        return result.to_dict()
    except DevisNotFoundError:
        raise HTTPException(status_code=404, detail=f"Devis {devis_id} non trouve")
    except TVANonEligibleError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except AttestationTVADejaExistanteError as e:
        raise HTTPException(status_code=409, detail=e.message)
    except AttestationTVAValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/{devis_id}/attestation-tva")
async def get_attestation_tva(
    devis_id: int,
    _role: str = Depends(require_conducteur_or_admin),
    use_case: GetAttestationTVAUseCase = Depends(get_get_attestation_tva_use_case),
):
    """Recupere l'attestation TVA d'un devis (DEV-23)."""
    try:
        result = use_case.execute(devis_id)
        return result.to_dict()
    except DevisNotFoundError:
        raise HTTPException(status_code=404, detail=f"Devis {devis_id} non trouve")
    except AttestationTVANotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)


# ─────────────────────────────────────────────────────────────────────────────
# Frais de chantier (DEV-25)
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/{devis_id}/frais-chantier/repartition")
async def calculer_repartition_frais(
    devis_id: int,
    _role: str = Depends(require_conducteur_or_admin),
    use_case: CalculerRepartitionFraisUseCase = Depends(
        get_calculer_repartition_frais_use_case
    ),
):
    """Calcule la repartition des frais de chantier par lot (DEV-25)."""
    try:
        result = use_case.execute(devis_id)
        return result
    except DevisNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Devis {devis_id} non trouve"
        )


@router.get("/{devis_id}/frais-chantier")
async def list_frais_chantier(
    devis_id: int,
    _role: str = Depends(require_conducteur_or_admin),
    use_case: ListFraisChantierUseCase = Depends(
        get_list_frais_chantier_use_case
    ),
):
    """Liste les frais de chantier d'un devis (DEV-25)."""
    try:
        result = use_case.execute(devis_id)
        return {"items": [f.to_dict() for f in result]}
    except DevisNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Devis {devis_id} non trouve"
        )


@router.post("/{devis_id}/frais-chantier", status_code=status.HTTP_201_CREATED)
async def create_frais_chantier(
    devis_id: int,
    request: FraisChantierCreateRequest,
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case: CreateFraisChantierUseCase = Depends(
        get_create_frais_chantier_use_case
    ),
):
    """Cree un frais de chantier pour un devis (DEV-25)."""
    dto = FraisChantierCreateDTO(
        devis_id=devis_id,
        type_frais=request.type_frais,
        libelle=request.libelle,
        montant_ht=request.montant_ht,
        mode_repartition=request.mode_repartition,
        taux_tva=request.taux_tva,
        ordre=request.ordre,
        lot_devis_id=request.lot_devis_id,
    )
    try:
        result = use_case.execute(dto, current_user_id)
        return result.to_dict()
    except DevisNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Devis {devis_id} non trouve"
        )
    except DevisNonModifiableError as e:
        raise HTTPException(status_code=409, detail=e.message)
    except FraisChantierValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/frais-chantier/{frais_id}")
async def update_frais_chantier(
    frais_id: int,
    request: FraisChantierUpdateRequest,
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case: UpdateFraisChantierUseCase = Depends(
        get_update_frais_chantier_use_case
    ),
):
    """Modifie un frais de chantier (DEV-25)."""
    dto = FraisChantierUpdateDTO(**request.model_dump(exclude_unset=True))
    try:
        result = use_case.execute(frais_id, dto, current_user_id)
        return result.to_dict()
    except FraisChantierNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Frais de chantier {frais_id} non trouve"
        )
    except DevisNonModifiableError as e:
        raise HTTPException(status_code=409, detail=e.message)
    except FraisChantierValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/frais-chantier/{frais_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_frais_chantier(
    frais_id: int,
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case: DeleteFraisChantierUseCase = Depends(
        get_delete_frais_chantier_use_case
    ),
):
    """Supprime un frais de chantier (DEV-25)."""
    try:
        use_case.execute(frais_id, current_user_id)
    except FraisChantierNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Frais de chantier {frais_id} non trouve"
        )
    except DevisNonModifiableError as e:
        raise HTTPException(status_code=409, detail=e.message)


# ─────────────────────────────────────────────────────────────────────────────
# Options de presentation (DEV-11)
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/{devis_id}/options-presentation")
async def get_options_presentation(
    devis_id: int,
    _role: str = Depends(require_conducteur_or_admin),
    use_case: GetOptionsPresentationUseCase = Depends(
        get_get_options_presentation_use_case
    ),
):
    """Recupere les options de presentation d'un devis (DEV-11).

    Retourne les options configurees ou les options par defaut
    (template standard) si aucune configuration n'a ete sauvegardee.
    """
    try:
        result = use_case.execute(devis_id)
        return result.to_dict()
    except DevisNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Devis {devis_id} non trouve"
        )


@router.put("/{devis_id}/options-presentation")
async def update_options_presentation(
    devis_id: int,
    request: OptionsPresentationUpdateRequest,
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case: UpdateOptionsPresentationUseCase = Depends(
        get_update_options_presentation_use_case
    ),
):
    """Met a jour les options de presentation d'un devis (DEV-11).

    Permet de configurer quels elements sont visibles dans le rendu
    du devis. Si un template_nom est fourni, ses options sont appliquees
    en premier, puis les options individuelles surchargent.

    REGLE METIER: Les debourses ne sont JAMAIS montres au client.
    """
    dto = UpdateOptionsPresentationDTO(
        afficher_debourses=request.afficher_debourses,
        afficher_composants=request.afficher_composants,
        afficher_quantites=request.afficher_quantites,
        afficher_prix_unitaires=request.afficher_prix_unitaires,
        afficher_tva_detaillee=request.afficher_tva_detaillee,
        afficher_conditions_generales=request.afficher_conditions_generales,
        afficher_logo=request.afficher_logo,
        afficher_coordonnees_entreprise=request.afficher_coordonnees_entreprise,
        afficher_retenue_garantie=request.afficher_retenue_garantie,
        afficher_frais_chantier_detail=request.afficher_frais_chantier_detail,
        template_nom=request.template_nom,
    )
    try:
        result = use_case.execute(devis_id, dto, current_user_id)
        return result.to_dict()
    except DevisNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Devis {devis_id} non trouve"
        )
    except OptionsPresentationInvalideError as e:
        raise HTTPException(status_code=400, detail=e.message)


# ─────────────────────────────────────────────────────────────────────────────
# Signature electronique (DEV-14)
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/{devis_id}/signature", status_code=status.HTTP_201_CREATED)
async def signer_devis(
    devis_id: int,
    request: SignatureCreateRequest,
    http_request: Request,
    _role: str = Depends(require_conducteur_or_admin),
    use_case: SignerDevisUseCase = Depends(get_signer_devis_use_case),
):
    """Signe un devis electroniquement (DEV-14).

    Signature simple conforme eIDAS :
    - Tracabilite : IP, user-agent, horodatage
    - Integrite : hash SHA-512 du document
    - Statuts autorises : envoye, vu, en_negociation

    Le devis passe automatiquement en statut 'accepte' apres signature.
    """
    # Extraction IP et user-agent depuis la requete HTTP (tracabilite eIDAS)
    ip_adresse = http_request.client.host if http_request.client else "0.0.0.0"
    user_agent = http_request.headers.get("user-agent", "inconnu")

    dto = SignatureCreateDTO(
        type_signature=request.type_signature,
        signataire_nom=request.signataire_nom,
        signataire_email=request.signataire_email,
        signature_data=request.signature_data,
        signataire_telephone=request.signataire_telephone,
        ip_adresse=ip_adresse,
        user_agent=user_agent,
    )
    try:
        result = use_case.execute(devis_id, dto)
        return result.to_dict()
    except DevisNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Devis {devis_id} non trouve"
        )
    except DevisNonSignableError as e:
        raise HTTPException(status_code=409, detail=e.message)
    except DevisDejaSigneError as e:
        raise HTTPException(status_code=409, detail=e.message)
    except SignatureDevisValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/{devis_id}/signature")
async def get_signature(
    devis_id: int,
    _role: str = Depends(require_conducteur_or_admin),
    use_case: GetSignatureUseCase = Depends(get_get_signature_use_case),
):
    """Recupere la signature electronique d'un devis (DEV-14)."""
    try:
        result = use_case.execute(devis_id)
        return result.to_dict()
    except DevisNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Devis {devis_id} non trouve"
        )
    except SignatureNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)


@router.post("/{devis_id}/signature/revoquer")
async def revoquer_signature(
    devis_id: int,
    request: RevocationSignatureRequest,
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case: RevoquerSignatureUseCase = Depends(get_revoquer_signature_use_case),
):
    """Revoque la signature d'un devis (admin only) (DEV-14).

    La revocation invalide la signature et remet le devis
    en statut 'en_negociation'.
    """
    try:
        result = use_case.execute(devis_id, request.motif, current_user_id)
        return result.to_dict()
    except DevisNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Devis {devis_id} non trouve"
        )
    except SignatureNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except SignatureDevisValidationError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("/{devis_id}/signature/verifier")
async def verifier_signature(
    devis_id: int,
    _role: str = Depends(require_conducteur_or_admin),
    use_case: VerifierSignatureUseCase = Depends(get_verifier_signature_use_case),
):
    """Verifie la validite de la signature d'un devis (DEV-14).

    Compare le hash SHA-512 du document actuel avec celui enregistre
    lors de la signature pour detecter toute modification.
    """
    try:
        result = use_case.execute(devis_id)
        return result.to_dict()
    except DevisNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Devis {devis_id} non trouve"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Relances automatiques (DEV-24)
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/{devis_id}/relances")
async def get_relances(
    devis_id: int,
    _role: str = Depends(require_conducteur_or_admin),
    use_case: GetRelancesDevisUseCase = Depends(get_get_relances_devis_use_case),
):
    """Historique des relances d'un devis (DEV-24).

    Retourne la configuration des relances, la liste des relances
    (planifiees, envoyees, annulees) et les compteurs.
    """
    try:
        result = use_case.execute(devis_id)
        return result.to_dict()
    except DevisNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Devis {devis_id} non trouve"
        )


@router.post("/{devis_id}/relances/planifier", status_code=status.HTTP_201_CREATED)
async def planifier_relances(
    devis_id: int,
    request: PlanifierRelancesRequest,
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case: PlanifierRelancesUseCase = Depends(get_planifier_relances_use_case),
):
    """Planifie les relances automatiques pour un devis envoye (DEV-24).

    Les relances sont planifiees selon la configuration du devis
    (delais 7j, 15j, 30j par defaut). Le devis doit etre en statut
    'envoye', 'vu' ou 'en_negociation'.
    """
    dto = PlanifierRelancesDTO(
        message_personnalise=request.message_personnalise,
    )
    try:
        result = use_case.execute(devis_id, dto, current_user_id)
        return {"relances": [r.to_dict() for r in result]}
    except DevisNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Devis {devis_id} non trouve"
        )
    except RelanceDevisPlanificationError as e:
        raise HTTPException(status_code=409, detail=e.message)


@router.post("/{devis_id}/relances/annuler")
async def annuler_relances(
    devis_id: int,
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case: AnnulerRelancesUseCase = Depends(get_annuler_relances_use_case),
):
    """Annule les relances en attente d'un devis (DEV-24).

    Annule toutes les relances planifiees (non envoyees).
    Utile quand le devis change de statut (accepte, refuse, perdu).
    """
    try:
        result = use_case.execute(devis_id, current_user_id)
        return {
            "relances_annulees": [r.to_dict() for r in result],
            "nb_annulees": len(result),
        }
    except DevisNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Devis {devis_id} non trouve"
        )


@router.get("/{devis_id}/config-relances")
async def get_config_relances(
    devis_id: int,
    _role: str = Depends(require_conducteur_or_admin),
    use_case: GetRelancesDevisUseCase = Depends(get_get_relances_devis_use_case),
):
    """Recupere la configuration des relances d'un devis (DEV-24).

    Retourne les delais configures, le type de relance par defaut
    et l'etat d'activation.
    """
    try:
        result = use_case.execute(devis_id)
        return result.config.to_dict()
    except DevisNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Devis {devis_id} non trouve"
        )


@router.put("/{devis_id}/config-relances")
async def update_config_relances(
    devis_id: int,
    request: ConfigRelancesUpdateRequest,
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case: UpdateConfigRelancesUseCase = Depends(get_update_config_relances_use_case),
):
    """Modifie la configuration des relances d'un devis (DEV-24).

    Permet de personnaliser les delais (ex: [10, 20, 40]),
    le type de relance par defaut et l'activation.
    """
    dto = UpdateConfigRelancesDTO(
        delais=request.delais,
        actif=request.actif,
        type_relance_defaut=request.type_relance_defaut,
    )
    try:
        result = use_case.execute(devis_id, dto, current_user_id)
        return result.to_dict()
    except DevisNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Devis {devis_id} non trouve"
        )
    except ConfigRelancesInvalideError as e:
        raise HTTPException(status_code=400, detail=e.message)


# ─────────────────────────────────────────────────────────────────────────────
# Articles (DEV-01) - sous-routeur
# ─────────────────────────────────────────────────────────────────────────────

articles_router = APIRouter(prefix="/articles-devis", tags=["articles-devis"])


@articles_router.get("")
async def list_articles(
    categorie: Optional[str] = None,
    search: Optional[str] = None,
    actif: bool = True,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    _role: str = Depends(require_conducteur_or_admin),
    use_case: ListArticlesUseCase = Depends(get_list_articles_use_case),
):
    """Liste les articles de la bibliotheque (DEV-01)."""
    result = use_case.execute(
        categorie=categorie,
        actif_seulement=actif,
        search=search,
        limit=limit,
        offset=offset,
    )
    return {
        "items": [a.to_dict() for a in result.items],
        "total": result.total,
        "limit": result.limit,
        "offset": result.offset,
    }


@articles_router.get("/{article_id}")
async def get_article(
    article_id: int,
    _role: str = Depends(require_conducteur_or_admin),
    use_case: GetArticleUseCase = Depends(get_get_article_use_case),
):
    """Recupere un article (DEV-01)."""
    try:
        result = use_case.execute(article_id)
        return result.to_dict()
    except ArticleNotFoundError:
        raise HTTPException(status_code=404, detail=f"Article {article_id} non trouve")


@articles_router.post("", status_code=status.HTTP_201_CREATED)
async def create_article(
    request: ArticleCreateRequest,
    db: Session = Depends(get_db),
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case: CreateArticleUseCase = Depends(get_create_article_use_case),
):
    """Cree un nouvel article (DEV-01)."""
    dto = ArticleCreateDTO(**request.model_dump())
    result = use_case.execute(dto, current_user_id)
    db.commit()
    return result.to_dict()


@articles_router.put("/{article_id}")
async def update_article(
    article_id: int,
    request: ArticleUpdateRequest,
    db: Session = Depends(get_db),
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case: UpdateArticleUseCase = Depends(get_update_article_use_case),
):
    """Met a jour un article (DEV-01)."""
    try:
        dto = ArticleUpdateDTO(**request.model_dump(exclude_unset=True))
        result = use_case.execute(article_id, dto, current_user_id)
        db.commit()
        return result.to_dict()
    except ArticleNotFoundError:
        raise HTTPException(status_code=404, detail=f"Article {article_id} non trouve")
    except ArticleCodeExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))


@articles_router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(
    article_id: int,
    db: Session = Depends(get_db),
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case: DeleteArticleUseCase = Depends(get_delete_article_use_case),
):
    """Supprime un article (DEV-01)."""
    try:
        use_case.execute(article_id, current_user_id)
        db.commit()
    except ArticleNotFoundError:
        raise HTTPException(status_code=404, detail=f"Article {article_id} non trouve")


# ─────────────────────────────────────────────────────────────────────────────
# Lots (DEV-03)
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/{devis_id}/lots", status_code=status.HTTP_201_CREATED)
async def create_lot(
    devis_id: int,
    request: LotCreateRequest,
    db: Session = Depends(get_db),
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case: CreateLotDevisUseCase = Depends(get_create_lot_use_case),
):
    """Cree un lot dans un devis (DEV-03)."""
    dto = LotDevisCreateDTO(
        devis_id=devis_id,
        titre=request.titre,
        numero=request.numero,
        ordre=request.ordre,
        marge_lot_pct=request.marge_lot_pct,
    )
    try:
        result = use_case.execute(dto, current_user_id)
        db.commit()
        return result.to_dict()
    except DevisNotFoundError:
        raise HTTPException(status_code=404, detail=f"Devis {devis_id} non trouve")


@router.put("/lots/{lot_id}")
async def update_lot(
    lot_id: int,
    request: LotUpdateRequest,
    db: Session = Depends(get_db),
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case: UpdateLotDevisUseCase = Depends(get_update_lot_use_case),
):
    """Met a jour un lot (DEV-03)."""
    dto = LotDevisUpdateDTO(**request.model_dump(exclude_unset=True))
    try:
        result = use_case.execute(lot_id, dto, current_user_id)
        db.commit()
        return result.to_dict()
    except LotDevisNotFoundError:
        raise HTTPException(status_code=404, detail=f"Lot {lot_id} non trouve")


@router.delete("/lots/{lot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lot(
    lot_id: int,
    db: Session = Depends(get_db),
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case: DeleteLotDevisUseCase = Depends(get_delete_lot_use_case),
):
    """Supprime un lot (DEV-03)."""
    try:
        use_case.execute(lot_id, current_user_id)
        db.commit()
    except LotDevisNotFoundError:
        raise HTTPException(status_code=404, detail=f"Lot {lot_id} non trouve")


# ─────────────────────────────────────────────────────────────────────────────
# Lignes (DEV-03 + DEV-05)
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/lots/{lot_id}/lignes", status_code=status.HTTP_201_CREATED)
async def create_ligne(
    lot_id: int,
    request: LigneCreateRequest,
    db: Session = Depends(get_db),
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case: CreateLigneDevisUseCase = Depends(get_create_ligne_use_case),
):
    """Cree une ligne dans un lot (DEV-03 + DEV-05)."""
    debourses_dto = [
        DebourseDetailCreateDTO(
            type_debourse=d.type_debourse,
            designation=d.designation,
            quantite=d.quantite,
            prix_unitaire=d.prix_unitaire,
        )
        for d in request.debourses
    ]

    dto = LigneDevisCreateDTO(
        lot_devis_id=lot_id,
        designation=request.designation,
        unite=request.unite,
        quantite=request.quantite,
        prix_unitaire_ht=request.prix_unitaire_ht,
        taux_tva=request.taux_tva,
        ordre=request.ordre,
        marge_ligne_pct=request.marge_ligne_pct,
        article_id=request.article_id,
        debourses=debourses_dto,
    )
    try:
        result = use_case.execute(dto, current_user_id)
        db.commit()
        return result.to_dict()
    except LotDevisNotFoundError:
        raise HTTPException(status_code=404, detail=f"Lot {lot_id} non trouve")


@router.put("/lignes/{ligne_id}")
async def update_ligne(
    ligne_id: int,
    request: LigneUpdateRequest,
    db: Session = Depends(get_db),
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case: UpdateLigneDevisUseCase = Depends(get_update_ligne_use_case),
):
    """Met a jour une ligne (DEV-03)."""
    update_data = request.model_dump(exclude_unset=True)
    debourses_dto = None
    if "debourses" in update_data and update_data["debourses"] is not None:
        debourses_dto = [
            DebourseDetailCreateDTO(
                type_debourse=d.type_debourse,
                designation=d.designation,
                quantite=d.quantite,
                prix_unitaire=d.prix_unitaire,
            )
            for d in request.debourses
        ]
        del update_data["debourses"]

    dto = LigneDevisUpdateDTO(**update_data, debourses=debourses_dto)
    try:
        result = use_case.execute(ligne_id, dto, current_user_id)
        db.commit()
        return result.to_dict()
    except LigneDevisNotFoundError:
        raise HTTPException(status_code=404, detail=f"Ligne {ligne_id} non trouvee")


@router.delete("/lignes/{ligne_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ligne(
    ligne_id: int,
    db: Session = Depends(get_db),
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case: DeleteLigneDevisUseCase = Depends(get_delete_ligne_use_case),
):
    """Supprime une ligne et ses debourses (DEV-03)."""
    try:
        use_case.execute(ligne_id, current_user_id)
        db.commit()
    except LigneDevisNotFoundError:
        raise HTTPException(status_code=404, detail=f"Ligne {ligne_id} non trouvee")

# ─────────────────────────────────────────────────────────────────────────────
# Pieces jointes (DEV-07)
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/{devis_id}/pieces-jointes")
async def list_pieces_jointes(
    devis_id: int,
    _role: str = Depends(require_conducteur_or_admin),
    use_case: ListerPiecesJointesUseCase = Depends(get_lister_pieces_jointes_use_case),
):
    """Liste les pieces jointes d'un devis (DEV-07)."""
    pieces = use_case.execute(devis_id)
    return {"items": [p.to_dict() for p in pieces]}


@router.post("/{devis_id}/pieces-jointes", status_code=status.HTTP_201_CREATED)
async def add_piece_jointe(
    devis_id: int,
    body: dict = Body(...),
    db: Session = Depends(get_db),
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case: AjouterPieceJointeUseCase = Depends(get_ajouter_piece_jointe_use_case),
):
    """Ajoute une piece jointe a un devis (DEV-07).

    Le document doit deja exister dans le module GED.
    Les metadonnees du fichier sont denormalisees pour lecture rapide.
    """
    dto = PieceJointeCreateDTO(
        devis_id=devis_id,
        document_id=body.get("document_id"),
        visible_client=body.get("visible_client", True),
        lot_devis_id=body.get("lot_devis_id"),
        ligne_devis_id=body.get("ligne_devis_id"),
    )
    result = use_case.execute(
        dto=dto,
        nom_fichier=body.get("nom_fichier", ""),
        type_fichier=body.get("type_fichier", ""),
        taille_octets=body.get("taille_octets", 0),
        mime_type=body.get("mime_type", ""),
        created_by=current_user_id,
    )
    db.commit()
    return result.to_dict()


@router.delete("/pieces-jointes/{piece_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_piece_jointe(
    piece_id: int,
    db: Session = Depends(get_db),
    _role: str = Depends(require_conducteur_or_admin),
    use_case: SupprimerPieceJointeUseCase = Depends(get_supprimer_piece_jointe_use_case),
):
    """Supprime une piece jointe (ne supprime PAS le document GED) (DEV-07)."""
    success = use_case.execute(piece_id)
    if not success:
        raise HTTPException(status_code=404, detail="Piece jointe non trouvee")
    db.commit()


@router.patch("/pieces-jointes/{piece_id}/visibilite")
async def toggle_visibilite_piece(
    piece_id: int,
    body: dict = Body(...),
    db: Session = Depends(get_db),
    _role: str = Depends(require_conducteur_or_admin),
    use_case: ToggleVisibiliteUseCase = Depends(get_toggle_visibilite_use_case),
):
    """Bascule la visibilite client d'une piece jointe (DEV-07)."""
    result = use_case.execute(piece_id, body.get("visible_client", True))
    if not result:
        raise HTTPException(status_code=404, detail="Piece jointe non trouvee")
    db.commit()
    return result.to_dict()


# ─────────────────────────────────────────────────────────────────────────────
# DEV-12: Generation PDF devis client
# ─────────────────────────────────────────────────────────────────────────────


@router.get("/{devis_id}/pdf")
async def generate_devis_pdf(
    devis_id: int,
    _role: str = Depends(require_conducteur_or_admin),
    use_case: GenerateDevisPDFUseCase = Depends(get_generate_pdf_use_case),
):
    """Genere et retourne le PDF du devis au format client (DEV-12).

    Le PDF contient les informations visibles par le client :
    lots, lignes, montants HT/TTC, ventilation TVA, conditions.
    Les debourses et marges internes ne sont PAS inclus.

    Args:
        devis_id: L'ID du devis a generer en PDF.

    Returns:
        Le fichier PDF en reponse binaire (application/pdf).

    Raises:
        HTTPException 404: Si le devis n'existe pas.
        HTTPException 500: Si la generation du PDF echoue.
    """
    import asyncio
    import re
    import logging

    logger = logging.getLogger(__name__)

    try:
        # Generation PDF synchrone → run_in_executor pour ne pas bloquer l'event loop
        loop = asyncio.get_event_loop()
        pdf_bytes, filename = await loop.run_in_executor(
            None, use_case.execute, devis_id
        )
    except DevisNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Devis {devis_id} non trouve",
        )
    except GenerateDevisPDFError as e:
        logger.error("Erreur generation PDF devis %s: %s", devis_id, e.message)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la generation du PDF. Veuillez reessayer.",
        )

    # Sanitiser le filename (protection Content-Disposition header injection)
    safe_filename = re.sub(r'[^A-Za-z0-9_\-.]', '_', filename)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{safe_filename}"',
        },
    )
