"""Utilitaires de calcul financier BTP.

Module partage pour garantir la coherence des calculs financiers
dans tout le systeme Hub Chantier.

Formule de marge BTP unifiee (FFB/FNTP) :
    Marge (%) = (CA HT - Cout de revient total) / CA HT x 100

Regle d'arrondi : ROUND_HALF_UP (standard comptable francais PCG art. 120-2).
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Optional


# -- Constantes entreprise ---------------------------------------------------

# Valeur par defaut. En production, utiliser ConfigurationEntreprise
# pour configurer ce montant via l'interface admin.
# Frais generaux BTP typiques : 10-15% du CA -> ~600k EUR pour CA de 4.3M EUR
COUTS_FIXES_ANNUELS = Decimal("600000")


# -- Main-d'oeuvre -----------------------------------------------------------

# Coefficient de majoration heures supplementaires (Convention Collective BTP).
# Art. L3121-36 Code du travail : +25% pour les 8 premieres heures sup/semaine.
COEFF_HEURES_SUP = Decimal("1.25")

# Art. L3121-36 Code du travail : au-dela de 43h/semaine (+50%).
COEFF_HEURES_SUP_2 = Decimal("1.50")

# Coefficient de charges patronales BTP (salaire brut → coût employeur).
# Charges sociales employeur BTP typiques : ~45% du brut.
# Inclut : URSSAF, retraite PROBTP, prévoyance, congés payés caisse BTP.
# Configurable par l'admin à terme via ConfigurationEntreprise.
COEFF_CHARGES_PATRONALES = Decimal("1.45")


# -- Arrondi comptable -------------------------------------------------------

def arrondir_montant(montant: Decimal, decimales: str = "0.01") -> Decimal:
    """Arrondit un montant selon le standard comptable francais (ROUND_HALF_UP).

    2.5 -> 3, 3.5 -> 4 (contrairement a ROUND_HALF_EVEN qui donne 2 et 4).

    Args:
        montant: Le montant a arrondir.
        decimales: La precision souhaitee (defaut: 2 decimales).

    Returns:
        Le montant arrondi.
    """
    return montant.quantize(Decimal(decimales), rounding=ROUND_HALF_UP)


def arrondir_pct(pct: Decimal) -> Decimal:
    """Arrondit un pourcentage a 2 decimales (ROUND_HALF_UP).

    Args:
        pct: Le pourcentage a arrondir.

    Returns:
        Le pourcentage arrondi.
    """
    return arrondir_montant(pct, "0.01")


# -- TVA ---------------------------------------------------------------------

def calculer_tva(montant_ht: Decimal, taux_tva: Decimal) -> Decimal:
    """Calcule le montant de TVA avec arrondi comptable.

    La TVA est arrondie a 2 decimales AVANT addition au TTC,
    conformement aux regles fiscales francaises.

    Args:
        montant_ht: Montant hors taxes.
        taux_tva: Taux de TVA en pourcentage (ex: Decimal("20")).

    Returns:
        Montant de la TVA arrondi a 2 decimales.
    """
    tva = montant_ht * taux_tva / Decimal("100")
    return arrondir_montant(tva)


def calculer_ttc(montant_ht: Decimal, taux_tva: Decimal) -> Decimal:
    """Calcule le montant TTC = HT + TVA arrondie.

    Args:
        montant_ht: Montant hors taxes.
        taux_tva: Taux de TVA en pourcentage.

    Returns:
        Montant TTC.
    """
    return montant_ht + calculer_tva(montant_ht, taux_tva)


# -- Marge BTP ----------------------------------------------------------------

def calculer_marge_chantier(
    ca_ht: Decimal,
    cout_achats: Decimal,
    cout_mo: Decimal,
    cout_materiel: Decimal,
    quote_part_frais_generaux: Decimal = Decimal("0"),
) -> Optional[Decimal]:
    """Calcule la marge chantier BTP (formule unifiee FFB/FNTP).

    Formule : (CA HT - Cout de revient) / CA HT x 100

    Ou :
        CA HT = situations de travaux facturees / factures client emises
        Cout de revient = achats realises + cout MO + cout materiel + frais generaux

    Cette fonction est LA source de verite pour le calcul de marge
    dans tout Hub Chantier. Dashboard, P&L, bilan de cloture et consolidation
    doivent tous utiliser cette fonction.

    IMPORTANT - Frontiere achats / cout_materiel :
        - cout_achats = achats externes fournisseurs (AchatRepository, statut FACTURE)
        - cout_materiel = couts materiel INTERNE : amortissement/location du
          parc materiel de l'entreprise (CoutMaterielRepository)
        Ces deux sources NE doivent PAS se chevaucher. Un achat de materiel
        chez un fournisseur est dans cout_achats, PAS dans cout_materiel.
        Le cout_materiel ne concerne que l'usage du parc propre.

    Args:
        ca_ht: Chiffre d'affaires HT (factures client / situations).
        cout_achats: Somme des achats realises (statut FACTURE) - achats fournisseurs.
        cout_mo: Cout main-d'oeuvre (pointages valides x taux horaire).
        cout_materiel: Cout materiel INTERNE (parc propre, pas achats fournisseurs).
        quote_part_frais_generaux: Quote-part des frais generaux de l'entreprise.

    Returns:
        La marge en pourcentage arrondie a 2 decimales, ou None si CA = 0.
    """
    if ca_ht <= Decimal("0"):
        return None

    cout_revient = cout_achats + cout_mo + cout_materiel + quote_part_frais_generaux
    marge = ((ca_ht - cout_revient) / ca_ht) * Decimal("100")
    return arrondir_pct(marge)


def calculer_quote_part_frais_generaux(
    ca_chantier_ht: Decimal,
    ca_total_annee: Decimal,
    couts_fixes_annuels: Decimal,
) -> Decimal:
    """Calcule la quote-part des frais generaux pour un chantier.

    Repartition au prorata du CA facture du chantier par rapport au CA total.

    Args:
        ca_chantier_ht: CA HT du chantier.
        ca_total_annee: CA total annuel de l'entreprise.
        couts_fixes_annuels: Frais generaux annuels de l'entreprise.

    Returns:
        La quote-part des frais generaux pour ce chantier.
    """
    if ca_total_annee <= Decimal("0") or ca_chantier_ht <= Decimal("0"):
        return Decimal("0")

    return arrondir_montant(
        (ca_chantier_ht / ca_total_annee) * couts_fixes_annuels
    )
