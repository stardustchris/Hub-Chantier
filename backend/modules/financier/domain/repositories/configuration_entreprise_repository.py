"""Interface du repository pour la configuration entreprise."""

from abc import ABC, abstractmethod
from typing import Optional

from ..entities import ConfigurationEntreprise


class ConfigurationEntrepriseRepository(ABC):
    """Interface abstraite pour la persistence de la configuration entreprise."""

    @abstractmethod
    def find_by_annee(self, annee: int) -> Optional[ConfigurationEntreprise]:
        """Recherche la configuration pour une annee donnee.

        Args:
            annee: L'annee de la configuration.

        Returns:
            La configuration ou None si non trouvee.
        """
        pass

    @abstractmethod
    def save(self, config: ConfigurationEntreprise) -> ConfigurationEntreprise:
        """Persiste une configuration (creation ou mise a jour).

        Args:
            config: La configuration a persister.

        Returns:
            La configuration avec son ID attribue.
        """
        pass
