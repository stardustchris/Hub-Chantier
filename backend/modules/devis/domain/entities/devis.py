"""Entite Devis - Document principal de devis.

DEV-03: Creation devis structure
DEV-06: Gestion marges et coefficients
DEV-08: Variantes et revisions
DEV-11: Personnalisation presentation
DEV-15: Workflow statut devis
DEV-16: Conversion en chantier
DEV-22: Retenue de garantie
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from ..value_objects import StatutDevis
from ..value_objects.type_version import TypeVersion
from ..value_objects.retenue_garantie import RetenueGarantie, RetenueGarantieInvalideError
from ..value_objects.options_presentation import OptionsPresentation
from ..value_objects.config_relances import ConfigRelances


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

    # DEV-08: Versioning fields
    devis_parent_id: Optional[int] = None
    numero_version: int = 1
    type_version: TypeVersion = TypeVersion.ORIGINALE
    label_variante: Optional[str] = None
    version_commentaire: Optional[str] = None
    version_figee: bool = False
    version_figee_at: Optional[datetime] = None
    version_figee_par: Optional[int] = None

    # DEV-11: Options de presentation
    options_presentation_json: Optional[Dict[str, Any]] = None

    # DEV-24: Configuration des relances automatiques
    config_relances_json: Optional[Dict[str, Any]] = None

    # DEV-16: Conversion en chantier
    converti_en_chantier_id: Optional[int] = None

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
        # DEV-22: Validation stricte - valeurs autorisees: 0, 5, 10
        try:
            RetenueGarantie(self.retenue_garantie_pct)
        except RetenueGarantieInvalideError:
            raise DevisValidationError(
                "La retenue de garantie doit etre 0%, 5% ou 10%"
            )
        if self.date_creation and self.date_validite:
            if self.date_validite < self.date_creation:
                raise DevisValidationError(
                    "La date de validite ne peut pas etre anterieure a la date de creation"
                )

    @property
    def est_modifiable(self) -> bool:
        """Verifie si le devis peut etre modifie.

        Un devis fige (version figee) ne peut jamais etre modifie,
        quel que soit son statut.
        """
        if self.version_figee:
            return False
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

    # ─────────────────────────────────────────────────────────────────
    # DEV-22: Retenue de garantie - Montants calcules
    # ─────────────────────────────────────────────────────────────────

    @property
    def retenue_garantie(self) -> RetenueGarantie:
        """Retourne le value object RetenueGarantie."""
        return RetenueGarantie(self.retenue_garantie_pct)

    @property
    def montant_retenue_garantie(self) -> Decimal:
        """Calcule le montant de la retenue de garantie.

        DEV-22: montant_ttc * retenue_garantie_pct / 100.
        """
        return self.retenue_garantie.calculer_montant(self.montant_total_ttc)

    @property
    def montant_net_a_payer(self) -> Decimal:
        """Calcule le montant net a payer apres retenue de garantie.

        DEV-22: montant_ttc - montant_retenue_garantie.
        """
        return self.retenue_garantie.montant_net_a_payer(self.montant_total_ttc)

    # ─────────────────────────────────────────────────────────────────
    # DEV-11: Options de presentation
    # ─────────────────────────────────────────────────────────────────

    @property
    def options_presentation(self) -> OptionsPresentation:
        """Retourne le value object OptionsPresentation.

        Si aucune option n'est definie, retourne les options par defaut.
        """
        return OptionsPresentation.from_dict(self.options_presentation_json)

    def set_options_presentation(self, options: OptionsPresentation) -> None:
        """Met a jour les options de presentation du devis.

        Args:
            options: Le value object OptionsPresentation a appliquer.
        """
        self.options_presentation_json = options.to_dict()

    # ─────────────────────────────────────────────────────────────────
    # DEV-24: Configuration des relances
    # ─────────────────────────────────────────────────────────────────

    @property
    def config_relances(self) -> ConfigRelances:
        """Retourne le value object ConfigRelances.

        Si aucune configuration n'est definie, retourne la config par defaut.
        """
        return ConfigRelances.from_dict(self.config_relances_json)

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

    def revoquer_acceptation(self) -> None:
        """Revoque l'acceptation du devis (accepte -> en_negociation).

        DEV-14: Lors de la revocation d'une signature, le devis repasse
        en negociation. Cette transition n'est pas dans le workflow standard
        car elle ne peut se produire que via une revocation admin.

        Raises:
            DevisValidationError: Si le devis n'est pas en statut 'accepte'.
        """
        if self.statut != StatutDevis.ACCEPTE:
            raise DevisValidationError(
                f"Le devis {self.numero} doit etre en statut 'accepte' "
                f"pour revoquer l'acceptation (statut actuel: {self.statut.label})"
            )
        self.statut = StatutDevis.EN_NEGOCIATION
        self.updated_at = datetime.utcnow()

    # ─────────────────────────────────────────────────────────────────
    # DEV-08: Methodes de versioning
    # ─────────────────────────────────────────────────────────────────

    @property
    def est_version_figee(self) -> bool:
        """Verifie si la version est figee (gelee)."""
        return self.version_figee

    @property
    def est_original(self) -> bool:
        """Verifie si le devis est l'original (pas une copie)."""
        return self.devis_parent_id is None and self.type_version == TypeVersion.ORIGINALE

    @property
    def est_revision(self) -> bool:
        """Verifie si le devis est une revision."""
        return self.type_version == TypeVersion.REVISION

    @property
    def est_variante(self) -> bool:
        """Verifie si le devis est une variante."""
        return self.type_version == TypeVersion.VARIANTE

    def figer(self, fige_par: int) -> None:
        """Fige (gele) la version du devis.

        Une version figee ne peut plus etre modifiee ni supprimee.

        Args:
            fige_par: ID de l'utilisateur qui fige la version.

        Raises:
            DevisValidationError: Si la version est deja figee.
        """
        if self.version_figee:
            raise DevisValidationError(
                f"Le devis {self.numero} est deja fige"
            )
        self.version_figee = True
        self.version_figee_at = datetime.utcnow()
        self.version_figee_par = fige_par
        self.updated_at = datetime.utcnow()

    # ─────────────────────────────────────────────────────────────────
    # DEV-16: Conversion en chantier
    # ─────────────────────────────────────────────────────────────────

    @property
    def est_converti(self) -> bool:
        """Verifie si le devis a deja ete converti en chantier."""
        return self.converti_en_chantier_id is not None

    def marquer_converti(self, chantier_id: int) -> None:
        """Marque le devis comme converti en chantier.

        Args:
            chantier_id: L'ID du chantier cree a partir de ce devis.

        Raises:
            DevisValidationError: Si le devis est deja converti.
            DevisValidationError: Si le devis n'est pas en statut 'accepte'.
        """
        if self.est_converti:
            raise DevisValidationError(
                f"Le devis {self.numero} a deja ete converti en chantier "
                f"(chantier_id={self.converti_en_chantier_id})"
            )
        if self.statut != StatutDevis.ACCEPTE:
            raise DevisValidationError(
                f"Le devis {self.numero} doit etre en statut 'accepte' "
                f"pour etre converti (statut actuel: {self.statut.label})"
            )
        self.converti_en_chantier_id = chantier_id
        self.updated_at = datetime.utcnow()

    def convertir(self, chantier_ref: str) -> None:
        """Convertit le devis en chantier (accepte -> converti).

        Marque le devis comme converti et le lie au chantier cree.
        Le devis devient immutable apres cette operation.

        Args:
            chantier_ref: L'identifiant du chantier cree (ID sous forme de string).

        Raises:
            TransitionStatutDevisInvalideError: Si le devis n'est pas en statut accepte.
            DevisValidationError: Si le chantier_ref est vide.
        """
        if not chantier_ref or not chantier_ref.strip():
            raise DevisValidationError("La reference chantier est obligatoire pour la conversion")
        self._transitionner(StatutDevis.CONVERTI)
        self.chantier_ref = chantier_ref.strip()

    def supprimer(self, deleted_by: int) -> None:
        """Marque le devis comme supprime (soft delete).

        Les versions figees ne peuvent PAS etre supprimees.

        Args:
            deleted_by: ID de l'utilisateur qui supprime.

        Raises:
            DevisValidationError: Si la version est figee.
        """
        if self.version_figee:
            raise DevisValidationError(
                f"Le devis {self.numero} est fige et ne peut pas etre supprime"
            )
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
            "montant_retenue_garantie": str(self.montant_retenue_garantie),
            "montant_net_a_payer": str(self.montant_net_a_payer),
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
            "devis_parent_id": self.devis_parent_id,
            "numero_version": self.numero_version,
            "type_version": self.type_version.value,
            "label_variante": self.label_variante,
            "version_commentaire": self.version_commentaire,
            "version_figee": self.version_figee,
            "version_figee_at": self.version_figee_at.isoformat() if self.version_figee_at else None,
            "version_figee_par": self.version_figee_par,
            "options_presentation": self.options_presentation.to_dict(),
            "config_relances": self.config_relances.to_dict(),
            "converti_en_chantier_id": self.converti_en_chantier_id,
        }
