"""Schemas Pydantic (request models) pour le module Devis.

Extraits de devis_routes.py pour une meilleure separation des responsabilites.
"""

from datetime import date
from decimal import Decimal
from typing import List, Literal, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


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
    coefficient_frais_generaux: Optional[Decimal] = Field(None, ge=0, le=100, description="Si fourni, remplace le coefficient existant du devis")
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


# DEV-21: Request model pour import DPGF
class DPGFMappingRequest(BaseModel):
    """Options de mapping des colonnes pour l'import DPGF (DEV-21).

    Permet de specifier quelles colonnes du fichier correspondent
    a quels champs DPGF. Par defaut: lot(0), description(1), unite(2),
    quantite(3), prix_unitaire(4).
    """

    col_lot: int = Field(0, ge=0, description="Index colonne lot")
    col_description: int = Field(1, ge=0, description="Index colonne description")
    col_unite: int = Field(2, ge=0, description="Index colonne unite")
    col_quantite: int = Field(3, ge=0, description="Index colonne quantite")
    col_prix_unitaire: int = Field(4, ge=0, description="Index colonne prix unitaire")
    ligne_debut: int = Field(1, ge=0, description="Premiere ligne de donnees (0=header)")
    feuille: int = Field(0, ge=0, description="Index de la feuille Excel")
