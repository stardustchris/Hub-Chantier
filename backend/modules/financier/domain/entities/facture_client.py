"""Entite FactureClient - Represente une facture emise au client.

FIN-08: Facturation client - generee a partir des situations de travaux
ou en acompte.
CONN-11: Sync encaissements clients Pennylane.
"""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from shared.domain.calcul_financier import calculer_tva as _calculer_tva, arrondir_montant


@dataclass
class FactureClient:
    """Represente une facture client.

    Une facture peut etre generee a partir d'une situation de travaux validee
    (type situation) ou creee manuellement (type acompte/solde).
    Workflow: brouillon -> emise -> envoyee -> payee (ou annulee).

    Attributes:
        id: Identifiant unique (None si non persiste).
        chantier_id: ID du chantier concerne.
        situation_id: ID de la situation de travaux associee (optionnel).
        numero_facture: Numero unique de la facture (FAC-YYYY-NN).
        type_facture: Type (acompte, situation, solde).
        montant_ht: Montant hors taxes.
        taux_tva: Taux de TVA applicable.
        montant_tva: Montant de la TVA.
        montant_ttc: Montant toutes taxes comprises.
        retenue_garantie_montant: Montant de la retenue de garantie.
        montant_net: Montant net a payer.
        date_emission: Date d'emission de la facture.
        date_echeance: Date d'echeance de paiement.
        statut: Statut du workflow.
        notes: Notes optionnelles.
        created_by: ID de l'utilisateur createur.
        created_at: Date de creation.
        updated_at: Date de derniere modification.
        deleted_at: Date de suppression (soft delete).
        deleted_by: ID de l'utilisateur qui a supprime.
    """

    id: Optional[int] = None
    chantier_id: int = 0
    situation_id: Optional[int] = None
    numero_facture: str = ""
    type_facture: str = "situation"
    montant_ht: Decimal = Decimal("0")
    taux_tva: Decimal = Decimal("20.00")
    montant_tva: Decimal = Decimal("0")
    montant_ttc: Decimal = Decimal("0")
    retenue_garantie_montant: Decimal = Decimal("0")
    montant_net: Decimal = Decimal("0")
    date_emission: Optional[date] = None
    date_echeance: Optional[date] = None
    statut: str = "brouillon"
    notes: Optional[str] = None
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    # H10: Soft delete fields
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[int] = None
    # CONN-11: Champs Pennylane encaissements
    date_paiement_reel: Optional[date] = None
    montant_encaisse: Decimal = Decimal("0")
    pennylane_invoice_id: Optional[str] = None

    def __post_init__(self) -> None:
        """Validation a la creation.

        Raises:
            ValueError: Si chantier_id <= 0 ou montant_ht < 0.
        """
        if self.chantier_id <= 0:
            raise ValueError("L'ID du chantier est obligatoire")
        if self.montant_ht < Decimal("0"):
            raise ValueError("Le montant HT ne peut pas etre negatif")

    # -- Workflow methods -------------------------------------------------------

    def emettre(self) -> None:
        """Emet la facture.

        Transition: brouillon -> emise. Fixe la date d'emission.

        Raises:
            ValueError: Si le statut n'est pas 'brouillon'.
        """
        if self.statut != "brouillon":
            raise ValueError(
                f"Impossible d'emettre une facture en statut '{self.statut}'. "
                "Seul le statut 'brouillon' est accepte."
            )
        self.statut = "emise"
        self.date_emission = date.today()
        self.updated_at = datetime.utcnow()

    def envoyer(self) -> None:
        """Marque la facture comme envoyee au client.

        Transition: emise -> envoyee.

        Raises:
            ValueError: Si le statut n'est pas 'emise'.
        """
        if self.statut != "emise":
            raise ValueError(
                f"Impossible d'envoyer une facture en statut '{self.statut}'. "
                "Seul le statut 'emise' est accepte."
            )
        self.statut = "envoyee"
        self.updated_at = datetime.utcnow()

    def marquer_payee(self) -> None:
        """Marque la facture comme payee.

        Transition: envoyee -> payee.

        Raises:
            ValueError: Si le statut n'est pas 'envoyee'.
        """
        if self.statut != "envoyee":
            raise ValueError(
                f"Impossible de marquer comme payee une facture en statut "
                f"'{self.statut}'. Seul le statut 'envoyee' est accepte."
            )
        self.statut = "payee"
        self.updated_at = datetime.utcnow()

    def annuler(self) -> None:
        """Annule la facture.

        Transition: brouillon/emise -> annulee.

        Raises:
            ValueError: Si le statut ne permet pas l'annulation.
        """
        if self.statut not in ("brouillon", "emise"):
            raise ValueError(
                f"Impossible d'annuler une facture en statut '{self.statut}'. "
                "Seuls les statuts 'brouillon' et 'emise' sont acceptes."
            )
        self.statut = "annulee"
        self.updated_at = datetime.utcnow()

    # -- Calculs statiques -------------------------------------------------------

    @staticmethod
    def calculer_montants(
        montant_ht: Decimal,
        taux_tva: Decimal,
        retenue_garantie_pct: Decimal,
    ) -> tuple:
        """Calcule les montants derives d'une facture.

        Args:
            montant_ht: Montant hors taxes.
            taux_tva: Taux de TVA (ex: 20.00).
            retenue_garantie_pct: Pourcentage de retenue de garantie.

        Returns:
            Tuple (montant_tva, montant_ttc, retenue_montant, montant_net).
        """
        montant_tva = _calculer_tva(montant_ht, taux_tva)
        montant_ttc = montant_ht + montant_tva
        retenue_montant = arrondir_montant(
            montant_ttc * retenue_garantie_pct / Decimal("100")
        )
        montant_net = montant_ttc - retenue_montant
        return montant_tva, montant_ttc, retenue_montant, montant_net

    # -- Properties -------------------------------------------------------

    @property
    def est_supprime(self) -> bool:
        """Verifie si la facture a ete supprimee (soft delete)."""
        return self.deleted_at is not None

    @property
    def est_encaissee(self) -> bool:
        """Indique si la facture a ete entierement encaissee.

        CONN-11: Une facture est consideree encaissee si le montant
        encaisse est >= au montant net.

        Returns:
            True si entierement encaissee, False sinon.
        """
        return self.montant_encaisse >= self.montant_net

    @property
    def reste_a_encaisser(self) -> Decimal:
        """Calcule le montant restant a encaisser.

        CONN-11: Permet le suivi des creances clients.

        Returns:
            Le montant net moins le montant deja encaisse.
        """
        reste = self.montant_net - self.montant_encaisse
        return max(Decimal("0"), reste)

    def enregistrer_encaissement(
        self,
        montant: Decimal,
        date_paiement: date,
    ) -> None:
        """Enregistre un encaissement sur la facture.

        CONN-11: Permet de mettre a jour le montant encaisse depuis Pennylane.

        Args:
            montant: Montant encaisse.
            date_paiement: Date du paiement.

        Raises:
            ValueError: Si le montant est negatif ou si la facture est annulee.
        """
        if montant < Decimal("0"):
            raise ValueError("Le montant encaisse ne peut pas etre negatif")
        if self.statut == "annulee":
            raise ValueError("Impossible d'enregistrer un encaissement sur une facture annulee")

        self.montant_encaisse = montant
        self.date_paiement_reel = date_paiement
        self.updated_at = datetime.utcnow()

        # Si entierement encaissee et en statut envoyee, passer en payee
        if self.est_encaissee and self.statut == "envoyee":
            self.statut = "payee"

    def to_dict(self) -> dict:
        """Convertit l'entite en dictionnaire."""
        return {
            "id": self.id,
            "chantier_id": self.chantier_id,
            "situation_id": self.situation_id,
            "numero_facture": self.numero_facture,
            "type_facture": self.type_facture,
            "montant_ht": str(self.montant_ht),
            "taux_tva": str(self.taux_tva),
            "montant_tva": str(self.montant_tva),
            "montant_ttc": str(self.montant_ttc),
            "retenue_garantie_montant": str(self.retenue_garantie_montant),
            "montant_net": str(self.montant_net),
            "date_emission": (
                self.date_emission.isoformat() if self.date_emission else None
            ),
            "date_echeance": (
                self.date_echeance.isoformat() if self.date_echeance else None
            ),
            "statut": self.statut,
            "notes": self.notes,
            "created_by": self.created_by,
            "created_at": (
                self.created_at.isoformat() if self.created_at else None
            ),
            "updated_at": (
                self.updated_at.isoformat() if self.updated_at else None
            ),
            # CONN-11: Champs Pennylane encaissements
            "date_paiement_reel": (
                self.date_paiement_reel.isoformat() if self.date_paiement_reel else None
            ),
            "montant_encaisse": str(self.montant_encaisse),
            "pennylane_invoice_id": self.pennylane_invoice_id,
            "est_encaissee": self.est_encaissee,
            "reste_a_encaisser": str(self.reste_a_encaisser),
        }
