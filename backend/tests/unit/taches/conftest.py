"""Fixtures pour les tests du module Taches."""

import pytest
from datetime import datetime, date
from typing import Optional, List

from backend.modules.taches.domain.entities import Tache, TemplateModele, FeuilleTache
from backend.modules.taches.domain.entities.template_modele import SousTacheModele
from backend.modules.taches.domain.entities.feuille_tache import StatutValidation
from backend.modules.taches.domain.value_objects import StatutTache, UniteMesure
from backend.modules.taches.domain.repositories import (
    TacheRepository,
    TemplateModeleRepository,
    FeuilleTacheRepository,
)


class InMemoryTacheRepository(TacheRepository):
    """Repository en memoire pour les tests."""

    def __init__(self):
        self.taches: dict[int, Tache] = {}
        self._next_id = 1

    def find_by_id(self, tache_id: int) -> Optional[Tache]:
        return self.taches.get(tache_id)

    def find_by_chantier(
        self,
        chantier_id: int,
        include_sous_taches: bool = True,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Tache]:
        taches = [
            t for t in self.taches.values()
            if t.chantier_id == chantier_id and t.parent_id is None
        ]
        return sorted(taches, key=lambda x: x.ordre)[skip:skip + limit]

    def find_children(self, parent_id: int) -> List[Tache]:
        children = [t for t in self.taches.values() if t.parent_id == parent_id]
        return sorted(children, key=lambda x: x.ordre)

    def save(self, tache: Tache) -> Tache:
        if tache.id is None:
            tache.id = self._next_id
            self._next_id += 1
        self.taches[tache.id] = tache
        return tache

    def delete(self, tache_id: int) -> bool:
        if tache_id in self.taches:
            # Supprimer les sous-taches
            for t in list(self.taches.values()):
                if t.parent_id == tache_id:
                    self.delete(t.id)
            del self.taches[tache_id]
            return True
        return False

    def count_by_chantier(self, chantier_id: int) -> int:
        return len([t for t in self.taches.values() if t.chantier_id == chantier_id])

    def search(
        self,
        chantier_id: int,
        query: Optional[str] = None,
        statut: Optional[StatutTache] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[Tache], int]:
        taches = [t for t in self.taches.values() if t.chantier_id == chantier_id]
        if query:
            taches = [t for t in taches if query.lower() in t.titre.lower()]
        if statut:
            taches = [t for t in taches if t.statut == statut]
        total = len(taches)
        return taches[skip:skip + limit], total

    def reorder(self, tache_id: int, nouvel_ordre: int) -> None:
        if tache_id in self.taches:
            self.taches[tache_id].ordre = nouvel_ordre

    def find_by_template(self, template_id: int) -> List[Tache]:
        return [t for t in self.taches.values() if t.template_id == template_id]

    def get_stats_chantier(self, chantier_id: int) -> dict:
        taches = [t for t in self.taches.values() if t.chantier_id == chantier_id]
        terminees = len([t for t in taches if t.statut == StatutTache.TERMINE])
        en_retard = len([
            t for t in taches
            if t.statut == StatutTache.A_FAIRE and t.date_echeance and t.date_echeance < date.today()
        ])
        return {
            "total": len(taches),
            "terminees": terminees,
            "en_cours": len(taches) - terminees,
            "en_retard": en_retard,
            "heures_estimees_total": sum(t.heures_estimees or 0 for t in taches),
            "heures_realisees_total": sum(t.heures_realisees for t in taches),
        }


class InMemoryTemplateModeleRepository(TemplateModeleRepository):
    """Repository en memoire pour les templates."""

    def __init__(self):
        self.templates: dict[int, TemplateModele] = {}
        self._next_id = 1

    def find_by_id(self, template_id: int) -> Optional[TemplateModele]:
        return self.templates.get(template_id)

    def find_all(
        self,
        active_only: bool = True,
        skip: int = 0,
        limit: int = 100,
    ) -> List[TemplateModele]:
        templates = list(self.templates.values())
        if active_only:
            templates = [t for t in templates if t.is_active]
        return templates[skip:skip + limit]

    def find_by_categorie(
        self,
        categorie: str,
        active_only: bool = True,
        skip: int = 0,
        limit: int = 100,
    ) -> List[TemplateModele]:
        templates = [t for t in self.templates.values() if t.categorie == categorie]
        if active_only:
            templates = [t for t in templates if t.is_active]
        return templates[skip:skip + limit]

    def save(self, template: TemplateModele) -> TemplateModele:
        if template.id is None:
            template.id = self._next_id
            self._next_id += 1
        self.templates[template.id] = template
        return template

    def delete(self, template_id: int) -> bool:
        if template_id in self.templates:
            del self.templates[template_id]
            return True
        return False

    def count(self, active_only: bool = True) -> int:
        if active_only:
            return len([t for t in self.templates.values() if t.is_active])
        return len(self.templates)

    def search(
        self,
        query: Optional[str] = None,
        categorie: Optional[str] = None,
        active_only: bool = True,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[TemplateModele], int]:
        templates = list(self.templates.values())
        if active_only:
            templates = [t for t in templates if t.is_active]
        if query:
            templates = [t for t in templates if query.lower() in t.nom.lower()]
        if categorie:
            templates = [t for t in templates if t.categorie == categorie]
        total = len(templates)
        return templates[skip:skip + limit], total

    def get_categories(self) -> List[str]:
        categories = set(t.categorie for t in self.templates.values() if t.categorie and t.is_active)
        return list(categories)

    def exists_by_nom(self, nom: str) -> bool:
        return any(t.nom == nom for t in self.templates.values())


class InMemoryFeuilleTacheRepository(FeuilleTacheRepository):
    """Repository en memoire pour les feuilles de taches."""

    def __init__(self):
        self.feuilles: dict[int, FeuilleTache] = {}
        self._next_id = 1

    def find_by_id(self, feuille_id: int) -> Optional[FeuilleTache]:
        return self.feuilles.get(feuille_id)

    def find_by_tache(
        self,
        tache_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[FeuilleTache]:
        feuilles = [f for f in self.feuilles.values() if f.tache_id == tache_id]
        return feuilles[skip:skip + limit]

    def find_by_utilisateur(
        self,
        utilisateur_id: int,
        date_debut: Optional[date] = None,
        date_fin: Optional[date] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[FeuilleTache]:
        feuilles = [f for f in self.feuilles.values() if f.utilisateur_id == utilisateur_id]
        if date_debut:
            feuilles = [f for f in feuilles if f.date_travail >= date_debut]
        if date_fin:
            feuilles = [f for f in feuilles if f.date_travail <= date_fin]
        return feuilles[skip:skip + limit]

    def find_by_chantier(
        self,
        chantier_id: int,
        date_debut: Optional[date] = None,
        date_fin: Optional[date] = None,
        statut: Optional[StatutValidation] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[FeuilleTache]:
        feuilles = [f for f in self.feuilles.values() if f.chantier_id == chantier_id]
        if date_debut:
            feuilles = [f for f in feuilles if f.date_travail >= date_debut]
        if date_fin:
            feuilles = [f for f in feuilles if f.date_travail <= date_fin]
        if statut:
            feuilles = [f for f in feuilles if f.statut_validation == statut]
        return feuilles[skip:skip + limit]

    def find_en_attente_validation(
        self,
        chantier_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[FeuilleTache]:
        feuilles = [f for f in self.feuilles.values() if f.statut_validation == StatutValidation.EN_ATTENTE]
        if chantier_id:
            feuilles = [f for f in feuilles if f.chantier_id == chantier_id]
        return feuilles[skip:skip + limit]

    def save(self, feuille: FeuilleTache) -> FeuilleTache:
        if feuille.id is None:
            feuille.id = self._next_id
            self._next_id += 1
        self.feuilles[feuille.id] = feuille
        return feuille

    def delete(self, feuille_id: int) -> bool:
        if feuille_id in self.feuilles:
            del self.feuilles[feuille_id]
            return True
        return False

    def count_by_tache(self, tache_id: int) -> int:
        return len([f for f in self.feuilles.values() if f.tache_id == tache_id])

    def get_total_heures_tache(self, tache_id: int, validees_only: bool = True) -> float:
        feuilles = [f for f in self.feuilles.values() if f.tache_id == tache_id]
        if validees_only:
            feuilles = [f for f in feuilles if f.statut_validation == StatutValidation.VALIDEE]
        return sum(f.heures_travaillees for f in feuilles)

    def get_total_quantite_tache(self, tache_id: int, validees_only: bool = True) -> float:
        feuilles = [f for f in self.feuilles.values() if f.tache_id == tache_id]
        if validees_only:
            feuilles = [f for f in feuilles if f.statut_validation == StatutValidation.VALIDEE]
        return sum(f.quantite_realisee for f in feuilles)

    def exists_for_date(
        self,
        tache_id: int,
        utilisateur_id: int,
        date_travail: date,
    ) -> bool:
        return any(
            f.tache_id == tache_id and f.utilisateur_id == utilisateur_id and f.date_travail == date_travail
            for f in self.feuilles.values()
        )


@pytest.fixture
def tache_repo():
    """Fixture pour le repository de taches."""
    return InMemoryTacheRepository()


@pytest.fixture
def template_repo():
    """Fixture pour le repository de templates."""
    return InMemoryTemplateModeleRepository()


@pytest.fixture
def feuille_repo():
    """Fixture pour le repository de feuilles."""
    return InMemoryFeuilleTacheRepository()


@pytest.fixture
def sample_tache():
    """Fixture pour une tache de test."""
    return Tache(
        chantier_id=1,
        titre="Test Tache",
        description="Description test",
        heures_estimees=8.0,
    )


@pytest.fixture
def sample_template():
    """Fixture pour un template de test."""
    template = TemplateModele(
        nom="Coffrage voiles",
        description="Mise en place des banches",
        categorie="Gros Oeuvre",
        unite_mesure=UniteMesure.M2,
    )
    template.ajouter_sous_tache("Preparation banches", ordre=0)
    template.ajouter_sous_tache("Positionnement", ordre=1)
    return template
