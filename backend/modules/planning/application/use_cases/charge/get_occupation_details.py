"""Use Case GetOccupationDetails - Details d'occupation par type (PDC-17)."""

from typing import List, Dict, Optional
from abc import ABC, abstractmethod

from ....domain.repositories import BesoinChargeRepository
from ....domain.value_objects.charge import Semaine, TypeMetier, TauxOccupation
from ...dtos.charge import OccupationDetailsDTO, TypeOccupationDTO


class UtilisateurProvider(ABC):
    """Interface pour recuperer les informations des utilisateurs par metier."""

    @abstractmethod
    def get_capacite_par_type_metier(
        self,
        semaine: Semaine,
    ) -> Dict[str, float]:
        """
        Recupere la capacite disponible par type de metier.

        Args:
            semaine: La semaine concernee.

        Returns:
            Dict {type_metier: capacite_heures}.
        """
        pass

    @abstractmethod
    def get_count_par_type_metier(self) -> Dict[str, int]:
        """
        Compte les utilisateurs actifs par type de metier.

        Returns:
            Dict {type_metier: count}.
        """
        pass


class AffectationProviderForOccupation(ABC):
    """Interface pour les heures planifiees par type."""

    @abstractmethod
    def get_heures_planifiees_par_type_metier(
        self,
        semaine: Semaine,
    ) -> Dict[str, float]:
        """
        Recupere les heures planifiees par type de metier.

        Args:
            semaine: La semaine concernee.

        Returns:
            Dict {type_metier: heures_planifiees}.
        """
        pass


class GetOccupationDetailsUseCase:
    """
    Cas d'utilisation : Details d'occupation par type (PDC-17).

    Affiche le taux d'occupation par type/metier avec code couleur
    pour une semaine donnee.

    Attributes:
        besoin_repo: Repository pour acceder aux besoins.
        utilisateur_provider: Provider pour les utilisateurs.
        affectation_provider: Provider pour les affectations.
    """

    # Heures de travail par semaine
    HEURES_PAR_SEMAINE = 35.0

    def __init__(
        self,
        besoin_repo: BesoinChargeRepository,
        utilisateur_provider: Optional[UtilisateurProvider] = None,
        affectation_provider: Optional[AffectationProviderForOccupation] = None,
    ):
        """
        Initialise le use case.

        Args:
            besoin_repo: Repository besoins (interface).
            utilisateur_provider: Provider utilisateurs (optionnel).
            affectation_provider: Provider affectations (optionnel).
        """
        self.besoin_repo = besoin_repo
        self.utilisateur_provider = utilisateur_provider
        self.affectation_provider = affectation_provider

    def execute(self, semaine_code: str) -> OccupationDetailsDTO:
        """
        Recupere les details d'occupation pour une semaine.

        Args:
            semaine_code: Code de la semaine (SXX-YYYY).

        Returns:
            Le DTO des details d'occupation.
        """
        semaine = Semaine.from_code(semaine_code)

        # Recuperer les besoins par type pour cette semaine
        besoins = self.besoin_repo.find_by_semaine(semaine)
        besoins_par_type: Dict[str, float] = {}
        for besoin in besoins:
            type_key = besoin.type_metier.value
            besoins_par_type[type_key] = besoins_par_type.get(type_key, 0.0) + besoin.besoin_heures

        # Recuperer les capacites par type
        capacites_par_type: Dict[str, float] = {}
        if self.utilisateur_provider:
            capacites_par_type = self.utilisateur_provider.get_capacite_par_type_metier(semaine)
        else:
            # Mode degrade : capacite par defaut pour chaque type avec besoin
            for type_metier in TypeMetier.all_types():
                capacites_par_type[type_metier.value] = self.HEURES_PAR_SEMAINE * 5

        # Recuperer les heures planifiees par type
        planifie_par_type: Dict[str, float] = {}
        if self.affectation_provider:
            planifie_par_type = self.affectation_provider.get_heures_planifiees_par_type_metier(semaine)

        # Construire les DTOs par type
        types_dto = []
        planifie_total = 0.0
        besoin_total = 0.0
        capacite_totale = 0.0

        for type_metier in TypeMetier.all_types():
            type_key = type_metier.value
            planifie = planifie_par_type.get(type_key, 0.0)
            besoin = besoins_par_type.get(type_key, 0.0)
            capacite = capacites_par_type.get(type_key, 0.0)

            # Skip si aucune activite pour ce type
            if planifie == 0 and besoin == 0 and capacite == 0:
                continue

            # Calculer le taux
            taux = TauxOccupation.calculer(planifie, capacite)

            types_dto.append(TypeOccupationDTO(
                type_metier=type_key,
                type_metier_label=type_metier.label,
                type_metier_couleur=type_metier.couleur,
                planifie_heures=planifie,
                besoin_heures=besoin,
                capacite_heures=capacite,
                taux_occupation=taux.valeur,
                taux_couleur=taux.couleur,
                alerte=taux.alerte,
            ))

            planifie_total += planifie
            besoin_total += besoin
            capacite_totale += capacite

        # Calculer le taux global
        taux_global = TauxOccupation.calculer(planifie_total, capacite_totale)

        # Calculer a recruter et a placer
        deficit_heures = max(besoin_total - capacite_totale, 0.0)
        a_recruter = int(deficit_heures / self.HEURES_PAR_SEMAINE + 0.5)

        surplus_heures = max(capacite_totale - planifie_total, 0.0)
        a_placer = int(surplus_heures / self.HEURES_PAR_SEMAINE)

        return OccupationDetailsDTO(
            semaine_code=semaine_code,
            semaine_label=str(semaine),
            taux_global=taux_global.valeur,
            taux_global_couleur=taux_global.couleur,
            alerte_globale=taux_global.alerte,
            types=types_dto,
            planifie_total=planifie_total,
            besoin_total=besoin_total,
            capacite_totale=capacite_totale,
            a_recruter=a_recruter,
            a_placer=a_placer,
        )
