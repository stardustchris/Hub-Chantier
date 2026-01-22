"""Module Chantiers - Gestion des chantiers de construction.

Selon CDC Section 4 - Gestion des Chantiers (CHT-01 à CHT-20).

Ce module fournit:
- CRUD complet des chantiers
- Gestion des statuts (Ouvert, En cours, Réceptionné, Fermé)
- Coordonnées GPS et navigation
- Gestion des responsables (conducteurs, chefs de chantier)
- Dates prévisionnelles et budget temps

Structure Clean Architecture:
- domain/: Entités, Value Objects, Repository interfaces
- application/: Use Cases, DTOs
- adapters/: Controllers
- infrastructure/: Persistence, Routes FastAPI
"""

from .infrastructure.web import router as chantiers_router

__all__ = ["chantiers_router"]
