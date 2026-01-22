"""Interfaces des repositories du module Taches."""

from .tache_repository import TacheRepository
from .template_modele_repository import TemplateModeleRepository
from .feuille_tache_repository import FeuilleTacheRepository

__all__ = ["TacheRepository", "TemplateModeleRepository", "FeuilleTacheRepository"]
