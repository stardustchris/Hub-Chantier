"""Use Cases pour le calcul des totaux et marges.

DEV-06: Gestion marges et coefficients.
Regle de priorite: ligne > lot > type debours > global.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from ...domain.entities.journal_devis import JournalDevis
from ...domain.repositories.devis_repository import DevisRepository
from ...domain.repositories.lot_devis_repository import LotDevisRepository
from ...domain.repositories.ligne_devis_repository import LigneDevisRepository
from ...domain.repositories.debourse_detail_repository import DebourseDetailRepository
from ...domain.repositories.journal_devis_repository import JournalDevisRepository


class CalculerTotauxDevisUseCase:
    """Use case pour recalculer tous les totaux d'un devis.

    DEV-06: Application des marges multi-niveaux.
    Formules:
        Debourse sec = Somme(quantite composant * prix unitaire composant)
        Prix de revient = Debourse sec * (1 + coeff frais generaux)
        Prix de vente HT = Prix de revient * (1 + taux de marge)
        Prix de vente TTC = Prix de vente HT * (1 + taux TVA)

    Priorite des marges: ligne > lot > type debours > global.
    """

    def __init__(
        self,
        devis_repository: DevisRepository,
        lot_repository: LotDevisRepository,
        ligne_repository: LigneDevisRepository,
        debourse_repository: DebourseDetailRepository,
        journal_repository: JournalDevisRepository,
    ):
        self._devis_repository = devis_repository
        self._lot_repository = lot_repository
        self._ligne_repository = ligne_repository
        self._debourse_repository = debourse_repository
        self._journal_repository = journal_repository

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

        total_debourse_sec = Decimal("0")
        total_ht = Decimal("0")
        total_ttc = Decimal("0")

        lots = self._lot_repository.find_by_devis_id(devis_id)

        for lot in lots:
            lot_debourse_sec = Decimal("0")
            lot_total_ht = Decimal("0")
            lot_total_ttc = Decimal("0")

            lignes = self._ligne_repository.find_by_lot_id(lot.id)

            for ligne in lignes:
                debourses = self._debourse_repository.find_by_ligne_id(ligne.id)

                # Calculer le debourse sec de la ligne
                ligne_debourse_sec = Decimal("0")
                for deb in debourses:
                    ligne_debourse_sec += deb.quantite * deb.prix_unitaire

                ligne.debourse_sec = ligne_debourse_sec

                # Prix de revient = Debourse sec * (1 + coeff frais generaux)
                ligne.prix_revient = ligne_debourse_sec * (
                    Decimal("1") + devis.coeff_frais_generaux
                )

                # Determiner la marge applicable (priorite)
                marge = self._resolve_marge(
                    ligne_marge=ligne.marge_ligne_pct,
                    lot_marge=lot.marge_lot_pct,
                    devis=devis,
                    debourses=debourses,
                )

                # Prix de vente HT
                if ligne_debourse_sec > 0:
                    ligne.prix_unitaire_ht = (
                        ligne.prix_revient * (Decimal("1") + marge / Decimal("100"))
                    ) / ligne.quantite if ligne.quantite > 0 else Decimal("0")
                    ligne_montant_ht = ligne.prix_unitaire_ht * ligne.quantite
                else:
                    ligne_montant_ht = ligne.prix_unitaire_ht * ligne.quantite

                ligne.montant_ht = ligne_montant_ht
                ligne.montant_ttc = ligne_montant_ht * (
                    Decimal("1") + ligne.taux_tva / Decimal("100")
                )

                self._ligne_repository.save(ligne)

                lot_debourse_sec += ligne_debourse_sec
                lot_total_ht += ligne.montant_ht
                lot_total_ttc += ligne.montant_ttc

            # Mettre a jour les totaux du lot
            lot.debourse_sec = lot_debourse_sec
            lot.total_ht = lot_total_ht
            lot.total_ttc = lot_total_ttc
            self._lot_repository.save(lot)

            total_debourse_sec += lot_debourse_sec
            total_ht += lot_total_ht
            total_ttc += lot_total_ttc

        # Mettre a jour les totaux du devis
        devis.debourse_sec_total = total_debourse_sec
        devis.total_ht = total_ht
        devis.total_ttc = total_ttc
        devis.updated_at = datetime.utcnow()
        self._devis_repository.save(devis)

        # Journal
        self._journal_repository.save(
            JournalDevis(
                devis_id=devis_id,
                action="recalcul_totaux",
                details=(
                    f"Recalcul des totaux - Debourse sec: {total_debourse_sec}, "
                    f"Total HT: {total_ht}, Total TTC: {total_ttc}"
                ),
                auteur_id=updated_by,
                created_at=datetime.utcnow(),
            )
        )

        return {
            "debourse_sec_total": str(total_debourse_sec),
            "total_ht": str(total_ht),
            "total_ttc": str(total_ttc),
        }

    def _resolve_marge(
        self,
        ligne_marge: Optional[Decimal],
        lot_marge: Optional[Decimal],
        devis,
        debourses: list,
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
        return devis.marge_globale_pct

    def _get_type_principal(self, debourses: list) -> Optional[str]:
        """Determine le type de debourse principal (le plus cher)."""
        if not debourses:
            return None
        type_totaux: dict = {}
        for d in debourses:
            montant = d.quantite * d.prix_unitaire
            type_totaux[d.type_debourse] = type_totaux.get(d.type_debourse, Decimal("0")) + montant
        if type_totaux:
            return max(type_totaux, key=type_totaux.get)
        return None

    def _get_marge_by_type(self, devis, type_debourse: Optional[str]) -> Optional[Decimal]:
        """Recupere la marge configuree pour un type de debourse."""
        if type_debourse is None:
            return None
        mapping = {
            "main_oeuvre": devis.marge_moe_pct,
            "materiaux": devis.marge_materiaux_pct,
            "sous_traitance": devis.marge_sous_traitance_pct,
        }
        return mapping.get(type_debourse)
