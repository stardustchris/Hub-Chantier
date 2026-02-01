"""Entite Devis - Document principal de devis.

DEV-03: Creation devis structure
DEV-06: Gestion marges et coefficients
DEV-15: Workflow statut devis
DEV-22: Retenue de garantie
"""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from ..value_objects import StatutDevis


class DevisValidationError(Exception):
    """Erreur levee lors d'une validation metier sur un devis."""

    pass


class TransitionStatutDevisInvalideError(Exception):
    """Erreur levee lors d'une transition de statut invalide."""

    def __init__(
        self, statut_actuel: StatutDevis, statut_cible: StatutDevis
    ):
        self.statut_actuel = statut_actuel
        self.statut_cible = statut_cible
        super().__init__(
            f"Transition invalide: {statut_actuel.label} -> {statut_cible.label}"
        )


@dataclass
class Devis:
    """Represente un devis client.

    Un devis est le document commercial principal. Il contient les informations
    client, les montants calcules, les parametres de marge et le workflow de statut.
    La structure detaillee (lots/lignes) est dans les entites LotDevis et LigneDevis.
    """

    id: Optional[int] = None
    numero: str = ""
    client_nom: str = ""
    client_adresse: Optional[str] = None
    client_telephone: Optional[str] = None
    client_email: Optional[str] = None
    chantier_ref: Optional[str] = None
    objet: Optional[str] = None
    date_creation: Optional[date] = None
    date_validite: Optional[date] = None
    statut: StatutDevis = StatutDevis.BROUILLON

    # Montants calcules (mis a jour par le service de calcul)
    montant_total_ht: Decimal = Decimal("0")
    montant_total_ttc: Decimal = Decimal("0")

    # Parametres de marge (DEV-06)
    taux_marge_global: Decimal = Decimal("15")
    coefficient_frais_generaux: Decimal = Decimal("12")
    taux_tva_defaut: Decimal = Decimal("20")

    # Retenue de garantie (DEV-22)
    retenue_garantie_pct: Decimal = Decimal("0")

    # Marges par type de debourse (priorite 3 dans la hierarchie)
    taux_marge_moe: Optional[Decimal] = None
    taux_marge_materiaux: Optional[Decimal] = None
    taux_marge_sous_traitance: Optional[Decimal] = None
    taux_marge_materiel: Optional[Decimal] = None
    taux_marge_deplacement: Optional[Decimal] = None

    notes: Optional[str] = None
    conditions_generales: Optional[str] = None

    # References utilisateurs
    commercial_id: Optional[int] = None
    conducteur_id: Optional[int] = None
    created_by: Optional[int] = None

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # H10: Soft delete fields
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[int] = None

    def __post_init__(self) -> None:
        """Validation a la creation."""
        if not self.numero or not self.numero.strip():
            raise DevisValidationError("Le numero du devis est obligatoire")
        if not self.client_nom or not self.client_nom.strip():
            raise DevisValidationError("Le nom du client est obligatoire")
        if self.taux_marge_global < Decimal("0"):
            raise DevisValidationError("Le taux de marge global ne peut pas etre negatif")
        if self.coefficient_frais_generaux < Decimal("0"):
            raise DevisValidationError(
                "Le coefficient de frais generaux ne peut pas etre negatif"
            )
        if self.taux_tva_defaut < Decimal("0") or self.taux_tva_defaut > Decimal("100"):
            raise DevisValidationError(
                "Le taux de TVA par defaut doit etre entre 0 et 100%"
            )
        if self.retenue_garantie_pct < Decimal("0") or self.retenue_garantie_pct > Decimal("100"):
            raise DevisValidationError(
                "La retenue de garantie doit etre entre 0 et 100%"
            )
        if self.date_creation and self.date_validite:
            if self.date_validite < self.date_creation:
                raise DevisValidationError(
                    "La date de validite ne peut pas etre anterieure a la date de creation"
                )

    @property
    def est_modifiable(self) -> bool:
        """Verifie si le devis peut etre modifie."""
        return self.statut.est_modifiable

    @property
    def est_supprime(self) -> bool:
        """Verifie si le devis a ete supprime (soft delete)."""
        return self.deleted_at is not None

    @property
    def est_expire(self) -> bool:
        """Verifie si le devis a depasse sa date de validite."""
        if self.date_validite is None:
            return False
        return date.today() > self.date_validite

    def _transitionner(self, nouveau_statut: StatutDevis) -> None:
        """Effectue une transition de statut avec validation.

        Args:
            nouveau_statut: Le statut cible.

        Raises:
            TransitionStatutDevisInvalideError: Si la transition est interdite.
        """
        if not self.statut.peut_transitionner_vers(nouveau_statut):
            raise TransitionStatutDevisInvalideError(
                self.statut, nouveau_statut
            )
        self.statut = nouveau_statut
        self.updated_at = datetime.utcnow()

    def soumettre_validation(self) -> None:
        """Soumet le devis en validation (brouillon -> en_validation).

        Raises:
            TransitionStatutDevisInvalideError: Si la transition est interdite.
        """
        self._transitionner(StatutDevis.EN_VALIDATION)

    def retourner_brouillon(self) -> None:
        """Retourne le devis en brouillon (en_validation -> brouillon).

        Raises:
            TransitionStatutDevisInvalideError: Si la transition est interdite.
        """
        self._transitionner(StatutDevis.BROUILLON)

    def envoyer(self) -> None:
        """Envoie le devis au client (en_validation -> envoye).

        Raises:
            TransitionStatutDevisInvalideError: Si la transition est interdite.
        """
        self._transitionner(StatutDevis.ENVOYE)

    def marquer_vu(self) -> None:
        """Marque le devis comme vu par le client (envoye -> vu).

        Raises:
            TransitionStatutDevisInvalideError: Si la transition est interdite.
        """
        self._transitionner(StatutDevis.VU)

    def passer_en_negociation(self) -> None:
        """Passe le devis en negociation (envoye/vu/expire -> en_negociation).

        Raises:
            TransitionStatutDevisInvalideError: Si la transition est interdite.
        """
        self._transitionner(StatutDevis.EN_NEGOCIATION)

    def accepter(self) -> None:
        """Accepte le devis (envoye/vu/en_negociation -> accepte).

        Raises:
            TransitionStatutDevisInvalideError: Si la transition est interdite.
        """
        self._transitionner(StatutDevis.ACCEPTE)

    def refuser(self) -> None:
        """Refuse le devis (envoye/vu/en_negociation -> refuse).

        Raises:
            TransitionStatutDevisInvalideError: Si la transition est interdite.
        """
        self._transitionner(StatutDevis.REFUSE)

    def marquer_perdu(self) -> None:
        """Marque le devis comme perdu (en_negociation -> perdu).

        Raises:
            TransitionStatutDevisInvalideError: Si la transition est interdite.
        """
        self._transitionner(StatutDevis.PERDU)

    def marquer_expire(self) -> None:
        """Marque le devis comme expire (envoye/vu -> expire).

        Raises:
            TransitionStatutDevisInvalideError: Si la transition est interdite.
        """
        self._transitionner(StatutDevis.EXPIRE)

    def supprimer(self, deleted_by: int) -> None:
        """Marque le devis comme supprime (soft delete).

        Args:
            deleted_by: ID de l'utilisateur qui supprime.
        """
        self.deleted_at = datetime.utcnow()
        self.deleted_by = deleted_by

    def to_dict(self) -> dict:
        """Convertit l'entite en dictionnaire."""
        return {
            "id": self.id,
            "numero": self.numero,
            "client_nom": self.client_nom,
            "client_adresse": self.client_adresse,
            "client_telephone": self.client_telephone,
            "client_email": self.client_email,
            "chantier_ref": self.chantier_ref,
            "objet": self.objet,
            "date_creation": self.date_creation.isoformat() if self.date_creation else None,
            "date_validite": self.date_validite.isoformat() if self.date_validite else None,
            "statut": self.statut.value,
            "montant_total_ht": str(self.montant_total_ht),
            "montant_total_ttc": str(self.montant_total_ttc),
            "taux_marge_global": str(self.taux_marge_global),
            "coefficient_frais_generaux": str(self.coefficient_frais_generaux),
            "taux_tva_defaut": str(self.taux_tva_defaut),
            "retenue_garantie_pct": str(self.retenue_garantie_pct),
            "taux_marge_moe": str(self.taux_marge_moe) if self.taux_marge_moe is not None else None,
            "taux_marge_materiaux": str(self.taux_marge_materiaux) if self.taux_marge_materiaux is not None else None,
            "taux_marge_sous_traitance": str(self.taux_marge_sous_traitance) if self.taux_marge_sous_traitance is not None else None,
            "taux_marge_materiel": str(self.taux_marge_materiel) if self.taux_marge_materiel is not None else None,
            "taux_marge_deplacement": str(self.taux_marge_deplacement) if self.taux_marge_deplacement is not None else None,
            "notes": self.notes,
            "conditions_generales": self.conditions_generales,
            "commercial_id": self.commercial_id,
            "conducteur_id": self.conducteur_id,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
