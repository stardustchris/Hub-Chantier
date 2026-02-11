"""Use Cases pour le calcul des totaux et marges.

DEV-06: Gestion marges et coefficients.
DEV-25: Integration des frais de chantier dans les totaux.
Regle de priorite: ligne > lot > type debours > global.
"""

from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, TYPE_CHECKING

from shared.domain.calcul_financier import arrondir_montant, calculer_ttc, calculer_tva

if TYPE_CHECKING:
    from ...domain.entities.devis import Devis
    from ...domain.entities.debourse_detail import DebourseDetail

from ...domain.entities.journal_devis import JournalDevis
from ...domain.value_objects import TypeDebourse
from ...domain.repositories.devis_repository import DevisRepository
from ...domain.repositories.lot_devis_repository import LotDevisRepository
from ...domain.repositories.ligne_devis_repository import LigneDevisRepository
from ...domain.repositories.debourse_detail_repository import DebourseDetailRepository
from ...domain.repositories.journal_devis_repository import JournalDevisRepository
from ...domain.repositories.frais_chantier_repository import FraisChantierRepository


class CalculerTotauxDevisUseCase:
    """Use case pour recalculer tous les totaux d'un devis.

    DEV-06: Application des marges multi-niveaux.
    Formules:
        Debourse sec = Somme(quantite composant * prix unitaire composant)
        Prix de revient = Debourse sec * (1 + coeff frais generaux / 100)
        Prix de vente HT = Prix de revient * (1 + taux de marge / 100)
        Prix de vente TTC = Prix de vente HT * (1 + taux TVA / 100)

    Priorite des marges: ligne > lot > type debours > global.
    """

    def __init__(
        self,
        devis_repository: DevisRepository,
        lot_repository: LotDevisRepository,
        ligne_repository: LigneDevisRepository,
        debourse_repository: DebourseDetailRepository,
        journal_repository: JournalDevisRepository,
        frais_chantier_repository: Optional["FraisChantierRepository"] = None,
    ):
        self._devis_repository = devis_repository
        self._lot_repository = lot_repository
        self._ligne_repository = ligne_repository
        self._debourse_repository = debourse_repository
        self._journal_repository = journal_repository
        self._frais_chantier_repository = frais_chantier_repository

    def execute(self, devis_id: int, updated_by: int) -> dict:
        """Recalcule tous les totaux du devis.

        Parcourt toutes les lignes et applique les marges selon la priorite:
        1. Marge ligne (si definie)
        2. Marge lot (si definie)
        3. Marge par type de debours (si definie sur le devis)
        4. Marge globale du devis

        Args:
            devis_id: L'ID du devis a recalculer.
            updated_by: L'ID de l'utilisateur.

        Returns:
            Dictionnaire avec les totaux recalcules.
        """
        from .devis_use_cases import DevisNotFoundError

        devis = self._devis_repository.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        total_ht = Decimal("0")
        total_ttc = Decimal("0")
        ventilation_tva: Dict[str, Decimal] = {}  # taux -> base_ht

        lots = self._lot_repository.find_by_devis(devis_id)

        for lot in lots:
            lot_debourse_sec = Decimal("0")
            lot_total_ht = Decimal("0")
            lot_total_ttc = Decimal("0")

            lignes = self._ligne_repository.find_by_lot(lot.id)

            for ligne in lignes:
                debourses = self._debourse_repository.find_by_ligne(ligne.id)

                # Calculer le debourse sec de la ligne
                ligne_debourse_sec = Decimal("0")
                for deb in debourses:
                    ligne_debourse_sec += deb.quantite * deb.prix_unitaire

                ligne.debourse_sec = ligne_debourse_sec

                # Prix de revient = Debourse sec * (1 + coeff frais generaux / 100)
                ligne.prix_revient = ligne_debourse_sec * (
                    Decimal("1") + devis.coefficient_frais_generaux / Decimal("100")
                )

                # Determiner la marge applicable (priorite)
                marge = self._resolve_marge(
                    ligne_marge=ligne.taux_marge_ligne,
                    lot_marge=lot.taux_marge_lot,
                    devis=devis,
                    debourses=debourses,
                )

                # Prix de vente HT (arrondi PCG art. 120-2 ROUND_HALF_UP)
                # Guard: quantite = 0 avec debourses = impossible de calculer un prix unitaire
                if ligne_debourse_sec > 0 and ligne.quantite <= 0:
                    raise ValueError(
                        f"Ligne devis {ligne.id} (lot {lot.id}): quantite = {ligne.quantite} "
                        f"avec debourse sec = {ligne_debourse_sec} EUR. "
                        f"Impossible de calculer un prix unitaire. Corrigez la quantite."
                    )

                if ligne_debourse_sec > 0:
                    ligne.prix_unitaire_ht = arrondir_montant(
                        (ligne.prix_revient * (Decimal("1") + marge / Decimal("100"))
                        ) / ligne.quantite if ligne.quantite > 0 else Decimal("0")
                    )
                    ligne_montant_ht = arrondir_montant(ligne.prix_unitaire_ht * ligne.quantite)
                else:
                    ligne_montant_ht = arrondir_montant(ligne.prix_unitaire_ht * ligne.quantite)

                ligne.total_ht = ligne_montant_ht
                ligne.montant_ttc = calculer_ttc(ligne_montant_ht, ligne.taux_tva)

                self._ligne_repository.save(ligne)

                # Ventilation TVA: accumuler base HT par taux
                taux_key = str(ligne.taux_tva)
                ventilation_tva[taux_key] = ventilation_tva.get(taux_key, Decimal("0")) + ligne.total_ht

                lot_debourse_sec += ligne_debourse_sec
                lot_total_ht += ligne.total_ht
                lot_total_ttc += ligne.montant_ttc

            # Mettre a jour les totaux du lot
            lot.montant_debourse_ht = lot_debourse_sec
            lot.montant_vente_ht = lot_total_ht
            lot.montant_vente_ttc = lot_total_ttc
            self._lot_repository.save(lot)

            total_ht += lot_total_ht
            total_ttc += lot_total_ttc

        # DEV-25: Ajouter les frais de chantier aux totaux
        total_frais_ht = Decimal("0")
        total_frais_ttc = Decimal("0")
        if self._frais_chantier_repository:
            frais_list = self._frais_chantier_repository.find_by_devis(devis_id)
            for frais in frais_list:
                total_frais_ht += frais.montant_ht
                total_frais_ttc += frais.montant_ttc
                # Ventilation TVA: inclure les frais de chantier
                taux_key = str(frais.taux_tva)
                ventilation_tva[taux_key] = ventilation_tva.get(taux_key, Decimal("0")) + frais.montant_ht

        # Mettre a jour les totaux du devis (lots + frais de chantier)
        devis.montant_total_ht = total_ht + total_frais_ht
        devis.montant_total_ttc = total_ttc + total_frais_ttc
        devis.updated_at = datetime.utcnow()
        self._devis_repository.save(devis)

        # DEV-22: Calcul retenue de garantie
        montant_retenue_garantie = devis.montant_retenue_garantie
        montant_net_a_payer = devis.montant_net_a_payer

        # Journal
        self._journal_repository.save(
            JournalDevis(
                devis_id=devis_id,
                action="recalcul_totaux",
                details_json={
                    "message": (
                        f"Recalcul des totaux - Total HT: {devis.montant_total_ht}, "
                        f"Total TTC: {devis.montant_total_ttc}, "
                        f"Frais chantier HT: {total_frais_ht}, "
                        f"Retenue garantie: {montant_retenue_garantie}, "
                        f"Net a payer: {montant_net_a_payer}"
                    ),
                },
                auteur_id=updated_by,
                created_at=datetime.utcnow(),
            )
        )

        # Construire la ventilation TVA triee par taux
        ventilation_tva_list = sorted(
            [
                {
                    "taux": taux,
                    "base_ht": str(arrondir_montant(base_ht)),
                    "montant_tva": str(
                        calculer_tva(base_ht, Decimal(taux))
                    ),
                }
                for taux, base_ht in ventilation_tva.items()
            ],
            key=lambda x: Decimal(x["taux"]),
        )

        return {
            "montant_total_ht": str(devis.montant_total_ht),
            "montant_total_ttc": str(devis.montant_total_ttc),
            "total_lots_ht": str(total_ht),
            "total_lots_ttc": str(total_ttc),
            "total_frais_chantier_ht": str(total_frais_ht),
            "total_frais_chantier_ttc": str(total_frais_ttc),
            "retenue_garantie_pct": str(devis.retenue_garantie_pct),
            "montant_retenue_garantie": str(montant_retenue_garantie),
            "montant_net_a_payer": str(montant_net_a_payer),
            "ventilation_tva": ventilation_tva_list,
        }

    def _resolve_marge(
        self,
        ligne_marge: Optional[Decimal],
        lot_marge: Optional[Decimal],
        devis: "Devis",
        debourses: List["DebourseDetail"],
    ) -> Decimal:
        """Resout la marge applicable selon la priorite.

        Priorite: ligne > lot > type debours > global.
        """
        # 1. Marge ligne
        if ligne_marge is not None:
            return ligne_marge

        # 2. Marge lot
        if lot_marge is not None:
            return lot_marge

        # 3. Marge par type de debours (si la ligne n'a qu'un type principal)
        if debourses:
            type_principal = self._get_type_principal(debourses)
            marge_type = self._get_marge_by_type(devis, type_principal)
            if marge_type is not None:
                return marge_type

        # 4. Marge globale
        return devis.taux_marge_global

    def _get_type_principal(self, debourses: List["DebourseDetail"]) -> Optional[TypeDebourse]:
        """Determine le type de debourse principal (le plus cher)."""
        if not debourses:
            return None
        type_totaux: Dict[TypeDebourse, Decimal] = {}
        for d in debourses:
            montant = d.quantite * d.prix_unitaire
            type_totaux[d.type_debourse] = type_totaux.get(d.type_debourse, Decimal("0")) + montant
        if type_totaux:
            return max(type_totaux, key=type_totaux.get)
        return None

    def _get_marge_by_type(self, devis: "Devis", type_debourse: Optional[TypeDebourse]) -> Optional[Decimal]:
        """Recupere la marge configuree pour un type de debourse."""
        if type_debourse is None:
            return None
        mapping = {
            TypeDebourse.MOE: devis.taux_marge_moe,
            TypeDebourse.MATERIAUX: devis.taux_marge_materiaux,
            TypeDebourse.SOUS_TRAITANCE: devis.taux_marge_sous_traitance,
            TypeDebourse.MATERIEL: devis.taux_marge_materiel,
            TypeDebourse.DEPLACEMENT: devis.taux_marge_deplacement,
        }
        return mapping.get(type_debourse)
