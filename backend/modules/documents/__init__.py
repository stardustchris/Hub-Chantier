"""Module Documents - Gestion Électronique des Documents (GED).

Ce module implémente les fonctionnalités GED-01 à GED-15 du CDC:
- GED-01: Onglet Documents intégré dans chaque fiche chantier
- GED-02: Arborescence par dossiers hiérarchique numérotée
- GED-03: Tableau de gestion avec métadonnées
- GED-04: Rôle minimum par dossier (Compagnon/Chef/Conducteur/Admin)
- GED-05: Autorisations nominatives spécifiques
- GED-06: Upload multiple (jusqu'à 10 fichiers)
- GED-07: Taille max 10 Go par fichier
- GED-08: Zone Drag & Drop
- GED-09: Barre de progression
- GED-10: Sélection droits à l'upload
- GED-11: Transfert auto depuis ERP (infra)
- GED-12: Formats supportés (PDF, Images, XLS, DOC, Vidéos)
- GED-13: Actions Éditer/Supprimer
- GED-14: Consultation mobile
- GED-15: Synchronisation Offline (infra)
"""

# Router importé directement depuis infrastructure.web dans main.py
# from .infrastructure.web import router

__all__: list = []
