"""Entité Achat - Représente un achat sur chantier.

FIN-05: Saisie achat - Formulaire de saisie des achats.
FIN-06: Suivi achat - Workflow de validation et suivi.
"""

from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal
from typing import Optional

from ..value_objects import TypeAchat, StatutAchat, UniteMesure
from ..value_objects.taux_tva import TAUX_VALIDES


class AchatValidationError(Exception):
    """Erreur levée lors d'une validation métier sur un achat."""

    pass


class TransitionStatutAchatInvalideError(Exception):
    """Erreur levée lors d'une transition de statut invalide."""

    def __init__(
        self, statut_actuel: StatutAchat, statut_cible: StatutAchat
    ):
        self.statut_actuel = statut_actuel
        self.statut_cible = statut_cible
        super().__init__(
            f"Transition invalide: {statut_actuel.label} → {statut_cible.label}"
        )


@dataclass
class Achat:
    """Représente un achat lié à un chantier.

    Un achat suit un workflow de validation :
    demande -> validé -> commandé -> livré -> facturé.
    """

    id: Optional[int] = None
    chantier_id: int = 0
    fournisseur_id: Optional[int] = None
    lot_budgetaire_id: Optional[int] = None
    type_achat: TypeAchat = TypeAchat.MATERIAU
    libelle: str = ""
    quantite: Decimal = Decimal("0")
    unite: UniteMesure = UniteMesure.U
    prix_unitaire_ht: Decimal = Decimal("0")
    taux_tva: Decimal = Decimal("20")
    date_commande: Optional[date] = None
    date_livraison_prevue: Optional[date] = None
    statut: StatutAchat = StatutAchat.DEMANDE
    numero_facture: Optional[str] = None
    motif_refus: Optional[str] = None
    commentaire: Optional[str] = None
    demandeur_id: Optional[int] = None
    valideur_id: Optional[int] = None
    validated_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    # H10: Soft delete fields
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[int] = None

    def __post_init__(self) -> None:
        """Validation à la création."""
        if not self.libelle or not self.libelle.strip():
            raise AchatValidationError("Le libellé de l'achat est obligatoire")
        if self.quantite <= Decimal("0"):
            raise AchatValidationError("La quantité doit être supérieure à 0")
        if self.prix_unitaire_ht < Decimal("0"):
            raise AchatValidationError(
                "Le prix unitaire HT ne peut pas être négatif"
            )
        if self.taux_tva not in TAUX_VALIDES:
            taux_str = ", ".join(str(t) for t in TAUX_VALIDES)
            raise AchatValidationError(
                f"Taux de TVA invalide : {self.taux_tva}%. "
                f"Taux autorisés : {taux_str}"
            )

    @property
    def total_ht(self) -> Decimal:
        """Montant total HT = quantité * prix unitaire."""
        return self.quantite * self.prix_unitaire_ht

    @property
    def montant_tva(self) -> Decimal:
        """Montant de la TVA."""
        return self.total_ht * self.taux_tva / Decimal("100")

    @property
    def total_ttc(self) -> Decimal:
        """Montant total TTC = HT + TVA."""
        return self.total_ht + self.montant_tva

    @property
    def est_supprime(self) -> bool:
        """Vérifie si l'achat a été supprimé (soft delete)."""
        return self.deleted_at is not None

    def _transitionner(self, nouveau_statut: StatutAchat) -> None:
        """Effectue une transition de statut avec validation.

        Args:
            nouveau_statut: Le statut cible.

        Raises:
            TransitionStatutAchatInvalideError: Si la transition est interdite.
        """
        if not self.statut.peut_transitionner_vers(nouveau_statut):
            raise TransitionStatutAchatInvalideError(
                self.statut, nouveau_statut
            )
        self.statut = nouveau_statut
        self.updated_at = datetime.utcnow()

    def valider(self, valideur_id: int) -> None:
        """Valide l'achat (demande -> validé).

        Args:
            valideur_id: ID de l'utilisateur qui valide.

        Raises:
            TransitionStatutAchatInvalideError: Si la transition est interdite.
        """
        self._transitionner(StatutAchat.VALIDE)
        self.valideur_id = valideur_id
        self.validated_at = datetime.utcnow()

    def refuser(self, valideur_id: int, motif: str) -> None:
        """Refuse l'achat (demande/validé -> refusé).

        Args:
            valideur_id: ID de l'utilisateur qui refuse.
            motif: Raison du refus.

        Raises:
            AchatValidationError: Si le motif est vide.
            TransitionStatutAchatInvalideError: Si la transition est interdite.
        """
        if not motif or not motif.strip():
            raise AchatValidationError(
                "Le motif de refus est obligatoire"
            )
        self._transitionner(StatutAchat.REFUSE)
        self.valideur_id = valideur_id
        self.motif_refus = motif
        self.validated_at = datetime.utcnow()

    def passer_commande(self) -> None:
        """Passe l'achat en commande (validé -> commandé).

        Raises:
            TransitionStatutAchatInvalideError: Si la transition est interdite.
        """
        self._transitionner(StatutAchat.COMMANDE)
        self.date_commande = date.today()

    def marquer_livre(self) -> None:
        """Marque l'achat comme livré (commandé -> livré).

        Raises:
            TransitionStatutAchatInvalideError: Si la transition est interdite.
        """
        self._transitionner(StatutAchat.LIVRE)

    def marquer_facture(self, numero_facture: str) -> None:
        """Marque l'achat comme facturé (livré -> facturé).

        Args:
            numero_facture: Numéro de la facture.

        Raises:
            AchatValidationError: Si le numéro de facture est vide.
            TransitionStatutAchatInvalideError: Si la transition est interdite.
        """
        if not numero_facture or not numero_facture.strip():
            raise AchatValidationError(
                "Le numéro de facture est obligatoire"
            )
        self._transitionner(StatutAchat.FACTURE)
        self.numero_facture = numero_facture

    def supprimer(self, deleted_by: int) -> None:
        """Marque l'achat comme supprimé (soft delete).

        Args:
            deleted_by: ID de l'utilisateur qui supprime.
        """
        self.deleted_at = datetime.utcnow()
        self.deleted_by = deleted_by

    def to_dict(self) -> dict:
        """Convertit l'entité en dictionnaire."""
        return {
            "id": self.id,
            "chantier_id": self.chantier_id,
            "fournisseur_id": self.fournisseur_id,
            "lot_budgetaire_id": self.lot_budgetaire_id,
            "type_achat": self.type_achat.value,
            "libelle": self.libelle,
            "quantite": str(self.quantite),
            "unite": self.unite.value,
            "prix_unitaire_ht": str(self.prix_unitaire_ht),
            "taux_tva": str(self.taux_tva),
            "total_ht": str(self.total_ht),
            "montant_tva": str(self.montant_tva),
            "total_ttc": str(self.total_ttc),
            "date_commande": self.date_commande.isoformat()
            if self.date_commande
            else None,
            "date_livraison_prevue": self.date_livraison_prevue.isoformat()
            if self.date_livraison_prevue
            else None,
            "statut": self.statut.value,
            "numero_facture": self.numero_facture,
            "motif_refus": self.motif_refus,
            "commentaire": self.commentaire,
            "demandeur_id": self.demandeur_id,
            "valideur_id": self.valideur_id,
            "validated_at": self.validated_at.isoformat()
            if self.validated_at
            else None,
            "created_at": self.created_at.isoformat()
            if self.created_at
            else None,
            "updated_at": self.updated_at.isoformat()
            if self.updated_at
            else None,
            "created_by": self.created_by,
        }
