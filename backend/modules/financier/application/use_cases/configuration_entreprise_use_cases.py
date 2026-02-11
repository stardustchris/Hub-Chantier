"""Use Cases pour la configuration entreprise.

Parametres financiers configurables par l'admin :
- Couts fixes annuels
- Coefficient frais generaux
- Coefficient charges patronales
- Coefficients heures supplementaires
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from ...domain.entities import ConfigurationEntreprise
from ...domain.repositories import ConfigurationEntrepriseRepository
from ..dtos import ConfigurationEntrepriseDTO, ConfigurationEntrepriseUpdateDTO


class ConfigurationNotFoundError(Exception):
    """Erreur levee quand aucune configuration n'existe pour l'annee."""

    def __init__(self, annee: int):
        self.annee = annee
        super().__init__(f"Aucune configuration trouvee pour l'annee {annee}")


class GetConfigurationEntrepriseUseCase:
    """Use case pour lire la configuration entreprise d'une annee."""

    def __init__(self, config_repository: ConfigurationEntrepriseRepository):
        self._config_repository = config_repository

    def execute(self, annee: int) -> ConfigurationEntrepriseDTO:
        """Retourne la configuration pour une annee donnee.

        Args:
            annee: L'annee demandee.

        Returns:
            Le DTO de la configuration.

        Raises:
            ConfigurationNotFoundError: Si aucune config pour cette annee.
        """
        config = self._config_repository.find_by_annee(annee)
        if not config:
            raise ConfigurationNotFoundError(annee)

        return ConfigurationEntrepriseDTO(
            id=config.id,
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


class UpdateConfigurationEntrepriseUseCase:
    """Use case pour modifier la configuration entreprise (admin only)."""

    def __init__(self, config_repository: ConfigurationEntrepriseRepository):
        self._config_repository = config_repository

    def execute(
        self,
        annee: int,
        dto: ConfigurationEntrepriseUpdateDTO,
        updated_by: int,
    ) -> ConfigurationEntrepriseDTO:
        """Met a jour la configuration pour une annee.

        Si aucune config n'existe pour l'annee, en cree une avec les
        valeurs par defaut puis applique les modifications.

        Args:
            annee: L'annee de la configuration.
            dto: Les champs a modifier.
            updated_by: L'ID de l'admin qui modifie.

        Returns:
            Le DTO de la configuration mise a jour.
        """
        config = self._config_repository.find_by_annee(annee)
        if not config:
            config = ConfigurationEntreprise(annee=annee)

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

        config = self._config_repository.save(config)

        return ConfigurationEntrepriseDTO(
            id=config.id,
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
