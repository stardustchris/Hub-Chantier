"""Entite SituationTravaux - Etat d'avancement periodique d'un chantier.

FIN-07: Situations de travaux - suivi de l'avancement des travaux
avec workflow de validation et facturation.
"""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from shared.domain.calcul_financier import calculer_tva as _calculer_tva, arrondir_montant


@dataclass
class SituationTravaux:
    """Represente une situation de travaux (etat d'avancement periodique).

    Une situation de travaux est un document periodique qui constate
    l'avancement des travaux sur un chantier. Elle suit un workflow:
    brouillon -> en_validation -> emise -> validee -> facturee.

    Attributes:
        id: Identifiant unique (None si non persiste).
        chantier_id: ID du chantier concerne.
        budget_id: ID du budget associe.
        numero: Numero de la situation (SIT-YYYY-NN).
        periode_debut: Date de debut de la periode.
        periode_fin: Date de fin de la periode.
        montant_cumule_precedent_ht: Montant cumule des situations precedentes HT.
        montant_periode_ht: Montant de la periode courante HT.
        montant_cumule_ht: Montant cumule total HT.
        retenue_garantie_pct: Pourcentage de retenue de garantie.
        taux_tva: Taux de TVA applicable.
        statut: Statut du workflow.
        notes: Notes optionnelles.
        created_by: ID de l'utilisateur createur.
        validated_by: ID de l'utilisateur valideur.
        validated_at: Date de validation.
        emise_at: Date d'emission.
        facturee_at: Date de facturation.
        created_at: Date de creation.
        updated_at: Date de derniere modification.
        deleted_at: Date de suppression (soft delete).
        deleted_by: ID de l'utilisateur qui a supprime.
    """

    id: Optional[int] = None
    chantier_id: int = 0
    budget_id: int = 0
    numero: str = ""
    periode_debut: Optional[date] = None
    periode_fin: Optional[date] = None
    montant_cumule_precedent_ht: Decimal = Decimal("0")
    montant_periode_ht: Decimal = Decimal("0")
    montant_cumule_ht: Decimal = Decimal("0")
    retenue_garantie_pct: Decimal = Decimal("5.00")
    taux_tva: Decimal = Decimal("20.00")
    statut: str = "brouillon"
    notes: Optional[str] = None
    created_by: Optional[int] = None
    validated_by: Optional[int] = None
    validated_at: Optional[datetime] = None
    emise_at: Optional[datetime] = None
    facturee_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    # H10: Soft delete fields
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[int] = None
    # A5: Lock optimiste
    version: int = 1

    def __post_init__(self) -> None:
        """Validation a la creation.

        Raises:
            ValueError: Si chantier_id <= 0, budget_id <= 0, numero vide,
                        periode_fin < periode_debut, retenue_garantie_pct
                        hors [0, 100] ou taux_tva hors [0, 100].
        """
        if self.chantier_id <= 0:
            raise ValueError("L'ID du chantier est obligatoire")
        if self.budget_id <= 0:
            raise ValueError("L'ID du budget est obligatoire")
        if not self.numero or not self.numero.strip():
            raise ValueError("Le numero de la situation est obligatoire")
        if (
            self.periode_debut is not None
            and self.periode_fin is not None
            and self.periode_fin < self.periode_debut
        ):
            raise ValueError(
                "La date de fin de periode doit etre posterieure ou egale "
                "a la date de debut"
            )
        if self.retenue_garantie_pct < Decimal("0") or self.retenue_garantie_pct > Decimal("100"):
            raise ValueError("Le taux de retenue de garantie doit etre entre 0% et 100%")
        if self.taux_tva < Decimal("0") or self.taux_tva > Decimal("100"):
            raise ValueError("Le taux de TVA doit etre entre 0% et 100%")

    # ── Workflow methods ──────────────────────────────────────────────────

    def soumettre_validation(self) -> None:
        """Soumet la situation pour validation.

        Transition: brouillon -> en_validation.

        Raises:
            ValueError: Si le statut n'est pas 'brouillon'.
        """
        if self.statut != "brouillon":
            raise ValueError(
                f"Impossible de soumettre une situation en statut '{self.statut}'. "
                "Seul le statut 'brouillon' est accepte."
            )
        self.statut = "en_validation"
        self.updated_at = datetime.utcnow()

    def valider(self, validated_by: int) -> None:
        """Valide la situation et l'emet.

        Transition: en_validation -> emise.

        Args:
            validated_by: ID de l'utilisateur qui valide.

        Raises:
            ValueError: Si le statut n'est pas 'en_validation'.
        """
        if self.statut != "en_validation":
            raise ValueError(
                f"Impossible de valider une situation en statut '{self.statut}'. "
                "Seul le statut 'en_validation' est accepte."
            )
        self.statut = "emise"
        self.validated_by = validated_by
        self.validated_at = datetime.utcnow()
        self.emise_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def marquer_validee_client(self) -> None:
        """Marque la situation comme validee par le client.

        Transition: emise -> validee.

        Raises:
            ValueError: Si le statut n'est pas 'emise'.
        """
        if self.statut != "emise":
            raise ValueError(
                f"Impossible de marquer comme validee une situation en statut "
                f"'{self.statut}'. Seul le statut 'emise' est accepte."
            )
        self.statut = "validee"
        self.updated_at = datetime.utcnow()

    def marquer_facturee(self, facturee_at: Optional[datetime] = None) -> None:
        """Marque la situation comme facturee.

        Transition: validee -> facturee.

        Args:
            facturee_at: Date de facturation (defaut: maintenant).

        Raises:
            ValueError: Si le statut n'est pas 'validee'.
        """
        if self.statut != "validee":
            raise ValueError(
                f"Impossible de marquer comme facturee une situation en statut "
                f"'{self.statut}'. Seul le statut 'validee' est accepte."
            )
        self.statut = "facturee"
        self.facturee_at = facturee_at or datetime.utcnow()
        self.updated_at = datetime.utcnow()

    # ── Properties calculees ─────────────────────────────────────────────

    @property
    def montant_retenue_garantie(self) -> Decimal:
        """Montant de la retenue de garantie HT (arrondi ROUND_HALF_UP)."""
        return arrondir_montant(
            self.montant_cumule_ht * self.retenue_garantie_pct / Decimal("100")
        )

    @property
    def montant_tva(self) -> Decimal:
        """Montant de la TVA (arrondi ROUND_HALF_UP, PCG art. 120-2)."""
        return _calculer_tva(self.montant_cumule_ht, self.taux_tva)

    @property
    def montant_ttc(self) -> Decimal:
        """Montant TTC = HT + TVA."""
        return self.montant_cumule_ht + self.montant_tva

    @property
    def montant_net(self) -> Decimal:
        """Montant net = TTC - retenue de garantie."""
        return self.montant_ttc - self.montant_retenue_garantie

    @property
    def est_supprime(self) -> bool:
        """Verifie si la situation a ete supprimee (soft delete)."""
        return self.deleted_at is not None

    def to_dict(self) -> dict:
        """Convertit l'entite en dictionnaire."""
        return {
            "id": self.id,
            "chantier_id": self.chantier_id,
            "budget_id": self.budget_id,
            "numero": self.numero,
            "periode_debut": (
                self.periode_debut.isoformat() if self.periode_debut else None
            ),
            "periode_fin": (
                self.periode_fin.isoformat() if self.periode_fin else None
            ),
            "montant_cumule_precedent_ht": str(self.montant_cumule_precedent_ht),
            "montant_periode_ht": str(self.montant_periode_ht),
            "montant_cumule_ht": str(self.montant_cumule_ht),
            "retenue_garantie_pct": str(self.retenue_garantie_pct),
            "taux_tva": str(self.taux_tva),
            "montant_retenue_garantie": str(self.montant_retenue_garantie),
            "montant_tva": str(self.montant_tva),
            "montant_ttc": str(self.montant_ttc),
            "montant_net": str(self.montant_net),
            "statut": self.statut,
            "notes": self.notes,
            "created_by": self.created_by,
            "validated_by": self.validated_by,
            "validated_at": (
                self.validated_at.isoformat() if self.validated_at else None
            ),
            "emise_at": self.emise_at.isoformat() if self.emise_at else None,
            "facturee_at": (
                self.facturee_at.isoformat() if self.facturee_at else None
            ),
            "created_at": (
                self.created_at.isoformat() if self.created_at else None
            ),
            "updated_at": (
                self.updated_at.isoformat() if self.updated_at else None
            ),
        }
