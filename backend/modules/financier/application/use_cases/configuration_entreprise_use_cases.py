"""Use Cases pour la configuration entreprise.

Parametres financiers configurables par l'admin :
- Couts fixes annuels
- Coefficient frais generaux
- Coefficient charges patronales
- Coefficients heures supplementaires
"""

import logging
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Tuple

from ...domain.entities import ConfigurationEntreprise
from ...domain.repositories import ConfigurationEntrepriseRepository
from ..dtos import ConfigurationEntrepriseDTO, ConfigurationEntrepriseUpdateDTO

logger = logging.getLogger(__name__)


class ConfigurationNotFoundError(Exception):
    """Erreur levee quand aucune configuration n'existe pour l'annee."""

    def __init__(self, annee: int):
        self.annee = annee
        super().__init__(f"Aucune configuration trouvee pour l'annee {annee}")


def _build_dto(config: ConfigurationEntreprise) -> ConfigurationEntrepriseDTO:
    """Construit un DTO depuis une entite ConfigurationEntreprise."""
    return ConfigurationEntrepriseDTO(
        id=config.id or 0,
        couts_fixes_annuels=config.couts_fixes_annuels,
        annee=config.annee,
        coeff_frais_generaux=config.coeff_frais_generaux,
        coeff_charges_patronales=config.coeff_charges_patronales,
        coeff_heures_sup=config.coeff_heures_sup,
        coeff_heures_sup_2=config.coeff_heures_sup_2,
        notes=config.notes,
        updated_at=config.updated_at,
        updated_by=config.updated_by,
    )


def _check_warnings(config: ConfigurationEntreprise) -> List[str]:
    """Detecte les valeurs suspectes (VAL-002, EDGE-002).

    Returns:
        Liste de messages d'avertissement.
    """
    warnings: List[str] = []
    if config.couts_fixes_annuels == Decimal("0"):
        warnings.append(
            "Couts fixes annuels a 0 EUR : inhabituel pour une PME BTP. "
            "Verifiez que cette valeur est correcte."
        )
    if config.coeff_frais_generaux == Decimal("0"):
        warnings.append(
            "Coefficient frais generaux a 0% : aucun frais general ne sera "
            "impute aux chantiers. Verifiez que cette valeur est correcte."
        )
    return warnings


class GetConfigurationEntrepriseUseCase:
    """Use case pour lire la configuration entreprise d'une annee."""

    def __init__(self, config_repository: ConfigurationEntrepriseRepository):
        self._config_repository = config_repository

    def execute(self, annee: int) -> Tuple[ConfigurationEntrepriseDTO, bool]:
        """Retourne la configuration pour une annee donnee.

        EDGE-003: si aucune config n'existe, retourne les valeurs par defaut
        au lieu de lever une erreur 404.

        Args:
            annee: L'annee demandee.

        Returns:
            Tuple (DTO, is_default). is_default=True si aucune config en BDD.
        """
        config = self._config_repository.find_by_annee(annee)
        if not config:
            defaults = ConfigurationEntreprise(annee=annee)
            return _build_dto(defaults), True

        return _build_dto(config), False


class UpdateConfigurationEntrepriseUseCase:
    """Use case pour modifier la configuration entreprise (admin only)."""

    def __init__(self, config_repository: ConfigurationEntrepriseRepository):
        self._config_repository = config_repository

    def execute(
        self,
        annee: int,
        dto: ConfigurationEntrepriseUpdateDTO,
        updated_by: int,
    ) -> Tuple[ConfigurationEntrepriseDTO, bool, List[str]]:
        """Met a jour la configuration pour une annee.

        EDGE-001: si aucune config n'existe, en cree une et le signale
        via created=True.

        Args:
            annee: L'annee de la configuration.
            dto: Les champs a modifier.
            updated_by: L'ID de l'admin qui modifie.

        Returns:
            Tuple (DTO, created, warnings).
            - created: True si une nouvelle config a ete creee.
            - warnings: liste d'avertissements pour valeurs suspectes.
        """
        config = self._config_repository.find_by_annee(annee)
        created = config is None
        if created:
            config = ConfigurationEntreprise(annee=annee)
            logger.info("Creation config entreprise annee %d par user %d", annee, updated_by)

        # Appliquer uniquement les champs fournis
        if dto.couts_fixes_annuels is not None:
            config.couts_fixes_annuels = dto.couts_fixes_annuels
        if dto.coeff_frais_generaux is not None:
            config.coeff_frais_generaux = dto.coeff_frais_generaux
        if dto.coeff_charges_patronales is not None:
            config.coeff_charges_patronales = dto.coeff_charges_patronales
        if dto.coeff_heures_sup is not None:
            config.coeff_heures_sup = dto.coeff_heures_sup
        if dto.coeff_heures_sup_2 is not None:
            config.coeff_heures_sup_2 = dto.coeff_heures_sup_2
        if dto.notes is not None:
            config.notes = dto.notes

        config.updated_at = datetime.utcnow()
        config.updated_by = updated_by

        # Re-valider via __post_init__
        config.__post_init__()

        # VAL-002 + EDGE-002: detecter les valeurs suspectes
        warnings = _check_warnings(config)
        for w in warnings:
            logger.warning("Config entreprise %d: %s", annee, w)

        config = self._config_repository.save(config)

        return _build_dto(config), created, warnings
