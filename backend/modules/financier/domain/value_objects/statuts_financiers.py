"""Constantes partagées pour les statuts financiers."""

from .statut_achat import StatutAchat

# Statuts considérés comme "engagé" (somme des achats validés/commandés/livrés/facturés)
STATUTS_ENGAGES = [
    StatutAchat.VALIDE,
    StatutAchat.COMMANDE,
    StatutAchat.LIVRE,
    StatutAchat.FACTURE,
]

# Statuts considérés comme "réalisé" (achats livrés + facturés = coûts réels engagés)
# DM-1: En pilotage chantier BTP, un achat livré est un coût réel même sans facture
STATUTS_REALISES = [
    StatutAchat.LIVRE,
    StatutAchat.FACTURE,
]
