"""Constantes partagées pour les statuts financiers."""

from .statut_achat import StatutAchat

# Statuts considérés comme "engagé" (somme des achats validés/commandés/livrés/facturés)
STATUTS_ENGAGES = [
    StatutAchat.VALIDE,
    StatutAchat.COMMANDE,
    StatutAchat.LIVRE,
    StatutAchat.FACTURE,
]

# Statuts considérés comme "réalisé" (somme des achats facturés uniquement)
STATUTS_REALISES = [
    StatutAchat.FACTURE,
]
