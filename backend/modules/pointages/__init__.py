"""Module Pointages (Feuilles d'heures).

Ce module gère la saisie, le suivi et l'export des heures travaillées.
Selon CDC Section 7 - Feuilles d'heures (FDH-01 à FDH-20).

Fonctionnalités principales:
- FDH-01: 2 onglets de vue (Chantiers / Compagnons)
- FDH-02: Navigation par semaine
- FDH-03: Export des données
- FDH-04: Filtre utilisateurs multi-critères
- FDH-05: Vue tabulaire hebdomadaire
- FDH-06: Multi-chantiers par utilisateur
- FDH-07: Badges colorés par chantier
- FDH-08: Total par ligne
- FDH-09: Total groupe
- FDH-10: Création auto depuis le planning
- FDH-11: Saisie mobile HH:MM
- FDH-12: Signature électronique
- FDH-13: Variables de paie
- FDH-14: Jauge d'avancement
- FDH-15: Comparaison inter-équipes
- FDH-16: Import ERP auto
- FDH-17: Export ERP manuel
- FDH-18: Macros de paie
- FDH-19: Feuilles de route PDF
- FDH-20: Mode Offline
"""

from .infrastructure.web import router

__all__ = ["router"]
