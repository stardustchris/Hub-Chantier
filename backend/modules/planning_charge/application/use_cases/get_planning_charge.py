"""Use Case GetPlanningCharge - Recuperation du planning de charge."""

from typing import List, Dict, Optional, Tuple
from abc import ABC, abstractmethod

from ...domain.repositories import BesoinChargeRepository
from ...domain.value_objects import Semaine, TypeMetier, TauxOccupation, UniteCharge
from ..dtos import (
    PlanningChargeFiltersDTO,
    PlanningChargeDTO,
    ChantierChargeDTO,
    SemaineChargeDTO,
    CelluleChargeDTO,
    FooterChargeDTO,
)


class ChantierProvider(ABC):
    """Interface pour recuperer les informations des chantiers."""

    @abstractmethod
    def get_chantiers_actifs(self, search: Optional[str] = None) -> List[Dict]:
        """
        Recupere les chantiers actifs.

        Args:
            search: Terme de recherche optionnel.

        Returns:
            Liste de dicts avec id, code, nom, couleur, heures_estimees.
        """
        pass


class AffectationProvider(ABC):
    """Interface pour recuperer les heures planifiees."""

    @abstractmethod
    def get_heures_planifiees_par_chantier_et_semaine(
        self,
        chantier_ids: List[int],
        semaine_debut: Semaine,
        semaine_fin: Semaine,
    ) -> Dict[Tuple[int, str], float]:
        """
        Recupere les heures planifiees par chantier et semaine.

        Args:
            chantier_ids: Liste des IDs de chantiers.
            semaine_debut: Premiere semaine.
            semaine_fin: Derniere semaine.

        Returns:
            Dict {(chantier_id, semaine_code): heures_planifiees}.
        """
        pass

    @abstractmethod
    def get_capacite_par_semaine(
        self,
        semaine_debut: Semaine,
        semaine_fin: Semaine,
    ) -> Dict[str, float]:
        """
        Calcule la capacite disponible par semaine.

        La capacite = nombre_utilisateurs_actifs * heures_travail_semaine.

        Args:
            semaine_debut: Premiere semaine.
            semaine_fin: Derniere semaine.

        Returns:
            Dict {semaine_code: capacite_heures}.
        """
        pass

    @abstractmethod
    def get_utilisateurs_non_planifies_par_semaine(
        self,
        semaine_debut: Semaine,
        semaine_fin: Semaine,
    ) -> Dict[str, int]:
        """
        Compte les utilisateurs non planifies par semaine (PDC-15).

        Args:
            semaine_debut: Premiere semaine.
            semaine_fin: Derniere semaine.

        Returns:
            Dict {semaine_code: nombre_non_planifies}.
        """
        pass


class GetPlanningChargeUseCase:
    """
    Cas d'utilisation : Recuperation du planning de charge.

    Construit la vue tabulaire complete du planning de charge
    avec les chantiers en lignes et les semaines en colonnes (PDC-01).

    Calcule egalement les indicateurs du footer (PDC-11 a PDC-15).

    Attributes:
        besoin_repo: Repository pour acceder aux besoins.
        chantier_provider: Provider pour les chantiers.
        affectation_provider: Provider pour les affectations.
    """

    # Heures de travail par semaine (base 35h)
    HEURES_PAR_SEMAINE = 35.0

    def __init__(
        self,
        besoin_repo: BesoinChargeRepository,
        chantier_provider: Optional[ChantierProvider] = None,
        affectation_provider: Optional[AffectationProvider] = None,
    ):
        """
        Initialise le use case.

        Args:
            besoin_repo: Repository besoins (interface).
            chantier_provider: Provider chantiers (optionnel).
            affectation_provider: Provider affectations (optionnel).
        """
        self.besoin_repo = besoin_repo
        self.chantier_provider = chantier_provider
        self.affectation_provider = affectation_provider

    def execute(self, filters: PlanningChargeFiltersDTO) -> PlanningChargeDTO:
        """
        Execute la recuperation du planning de charge.

        Args:
            filters: Les filtres a appliquer.

        Returns:
            Le DTO complet du planning de charge.
        """
        # Parser les semaines
        semaine_debut = Semaine.from_code(filters.semaine_debut)
        semaine_fin = Semaine.from_code(filters.semaine_fin)

        # Generer la liste des semaines
        semaines = self._generate_semaines(semaine_debut, semaine_fin)
        semaines_codes = [s.code for s in semaines]

        # Recuperer les chantiers
        chantiers_data = []
        if self.chantier_provider:
            chantiers_data = self.chantier_provider.get_chantiers_actifs(
                search=filters.recherche
            )
        else:
            # Mode degradé : utiliser les chantiers ayant des besoins
            chantier_ids = self.besoin_repo.get_chantiers_with_besoins(
                semaine_debut, semaine_fin
            )
            chantiers_data = [
                {"id": cid, "code": f"C{cid}", "nom": f"Chantier {cid}",
                 "couleur": "#3498DB", "heures_estimees": 0.0}
                for cid in chantier_ids
            ]

        # Recuperer les besoins
        besoins = self.besoin_repo.find_all_in_range(semaine_debut, semaine_fin)

        # Indexer les besoins par chantier et semaine
        besoins_index: Dict[Tuple[int, str], float] = {}
        for besoin in besoins:
            key = (besoin.chantier_id, besoin.semaine.code)
            besoins_index[key] = besoins_index.get(key, 0.0) + besoin.besoin_heures

        # Recuperer les heures planifiees
        planifie_index: Dict[Tuple[int, str], float] = {}
        if self.affectation_provider and chantiers_data:
            chantier_ids = [c["id"] for c in chantiers_data]
            planifie_index = self.affectation_provider.get_heures_planifiees_par_chantier_et_semaine(
                chantier_ids, semaine_debut, semaine_fin
            )

        # Recuperer les capacites et non planifies
        capacites: Dict[str, float] = {}
        non_planifies: Dict[str, int] = {}
        if self.affectation_provider:
            capacites = self.affectation_provider.get_capacite_par_semaine(
                semaine_debut, semaine_fin
            )
            non_planifies = self.affectation_provider.get_utilisateurs_non_planifies_par_semaine(
                semaine_debut, semaine_fin
            )

        # Unite pour conversion
        unite = UniteCharge.from_string(filters.unite)

        # Construire les lignes chantiers
        chantiers_dto = []
        for chantier in chantiers_data:
            chantier_dto = self._build_chantier_dto(
                chantier=chantier,
                semaines=semaines,
                besoins_index=besoins_index,
                planifie_index=planifie_index,
                unite=unite,
            )
            chantiers_dto.append(chantier_dto)

        # Construire le footer
        footer = self._build_footer(
            semaines=semaines,
            besoins_index=besoins_index,
            planifie_index=planifie_index,
            capacites=capacites,
            non_planifies=non_planifies,
            chantier_ids=[c["id"] for c in chantiers_data],
        )

        # Calculer les totaux
        planifie_total = sum(planifie_index.values())
        besoin_total = sum(besoins_index.values())
        capacite_totale = sum(capacites.values())

        return PlanningChargeDTO(
            total_chantiers=len(chantiers_data),
            semaine_debut=filters.semaine_debut,
            semaine_fin=filters.semaine_fin,
            unite=filters.unite,
            semaines=semaines_codes,
            chantiers=chantiers_dto,
            footer=footer,
            capacite_totale=capacite_totale,
            planifie_total=planifie_total,
            besoin_total=besoin_total,
        )

    def _generate_semaines(
        self,
        debut: Semaine,
        fin: Semaine,
    ) -> List[Semaine]:
        """Genere la liste des semaines entre debut et fin."""
        semaines = []
        current = debut
        while current <= fin:
            semaines.append(current)
            current = current.next()
        return semaines

    def _build_chantier_dto(
        self,
        chantier: Dict,
        semaines: List[Semaine],
        besoins_index: Dict[Tuple[int, str], float],
        planifie_index: Dict[Tuple[int, str], float],
        unite: UniteCharge,
    ) -> ChantierChargeDTO:
        """Construit le DTO d'un chantier."""
        chantier_id = chantier["id"]
        semaines_dto = []

        for semaine in semaines:
            key = (chantier_id, semaine.code)
            planifie = planifie_index.get(key, 0.0)
            besoin = besoins_index.get(key, 0.0)
            non_couvert = max(besoin - planifie, 0.0)

            cellule = CelluleChargeDTO(
                planifie_heures=planifie,
                besoin_heures=besoin,
                besoin_non_couvert=non_couvert,
                has_besoin=besoin > 0,
            )

            semaines_dto.append(SemaineChargeDTO(
                code=semaine.code,
                label=str(semaine),
                cellule=cellule,
            ))

        return ChantierChargeDTO(
            id=chantier_id,
            code=chantier.get("code", ""),
            nom=chantier.get("nom", ""),
            couleur=chantier.get("couleur", "#3498DB"),
            charge_totale=chantier.get("heures_estimees", 0.0),
            semaines=semaines_dto,
        )

    def _build_footer(
        self,
        semaines: List[Semaine],
        besoins_index: Dict[Tuple[int, str], float],
        planifie_index: Dict[Tuple[int, str], float],
        capacites: Dict[str, float],
        non_planifies: Dict[str, int],
        chantier_ids: List[int],
    ) -> List[FooterChargeDTO]:
        """Construit le footer avec les indicateurs agreges."""
        footer = []

        for semaine in semaines:
            # Calculer totaux pour cette semaine
            planifie_semaine = sum(
                planifie_index.get((cid, semaine.code), 0.0)
                for cid in chantier_ids
            )
            besoin_semaine = sum(
                besoins_index.get((cid, semaine.code), 0.0)
                for cid in chantier_ids
            )

            capacite = capacites.get(semaine.code, self.HEURES_PAR_SEMAINE * 20)

            # Calculer le taux d'occupation
            taux = TauxOccupation.calculer(planifie_semaine, capacite)

            # Calculer a recruter (PDC-14)
            # Si besoin > capacite, il faut recruter
            deficit_heures = max(besoin_semaine - capacite, 0.0)
            a_recruter = int(deficit_heures / self.HEURES_PAR_SEMAINE + 0.5)

            # A placer (PDC-15)
            a_placer = non_planifies.get(semaine.code, 0)

            footer.append(FooterChargeDTO(
                semaine_code=semaine.code,
                taux_occupation=taux.valeur,
                taux_couleur=taux.couleur,
                taux_label=taux.label,
                alerte_surcharge=taux.alerte,
                a_recruter=a_recruter,
                a_placer=a_placer,
            ))

        return footer
