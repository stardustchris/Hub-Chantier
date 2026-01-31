"""Service Registry pour la communication cross-module.

Ce module fournit un registre centralisé de services permettant aux modules
d'accéder aux fonctionnalités d'autres modules sans imports directs,
respectant ainsi le principe d'isolation des modules de Clean Architecture.

Pattern: Service Locator
"""

from typing import Any, Callable, Dict, Optional
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


class ServiceRegistry:
    """
    Registre centralisé de services pour la communication cross-module.

    Permet d'obtenir des instances de repositories ou services d'autres modules
    sans imports directs, avec graceful degradation si le module n'est pas disponible.
    """

    _factories: Dict[str, Callable[[Session], Any]] = {}

    @classmethod
    def register(cls, name: str, factory: Callable[[Session], Any]) -> None:
        """
        Enregistre une factory de service.

        Args:
            name: Nom du service (ex: "formulaire_repository").
            factory: Fonction factory qui prend une Session DB et retourne le service.
        """
        cls._factories[name] = factory
        logger.debug(f"Service registered: {name}")

    @classmethod
    def get(cls, name: str, db: Session) -> Optional[Any]:
        """
        Récupère une instance de service.

        Args:
            name: Nom du service à récupérer.
            db: Session de base de données pour initialiser le service.

        Returns:
            Instance du service ou None si non disponible.
        """
        factory = cls._factories.get(name)
        if factory is None:
            logger.warning(f"Service not available: {name}")
            return None

        try:
            return factory(db)
        except Exception as e:
            logger.warning(f"Failed to instantiate service {name}: {e}")
            return None

    @classmethod
    def clear(cls) -> None:
        """Vide le registre (utile pour les tests)."""
        cls._factories.clear()


# Fonctions de convénience
def register_service(name: str, factory: Callable[[Session], Any]) -> None:
    """Enregistre un service dans le registre global."""
    ServiceRegistry.register(name, factory)


def get_service(name: str, db: Session) -> Optional[Any]:
    """Récupère un service depuis le registre global."""
    return ServiceRegistry.get(name, db)


# =============================================================================
# Enregistrement des services cross-module
# =============================================================================

def _register_core_services():
    """Enregistre les services des modules core (formulaires, signalements, pointages)."""

    # Formulaires repository
    def formulaire_repository_factory(db: Session):
        try:
            from modules.formulaires.infrastructure.persistence import (
                SQLAlchemyFormulaireRempliRepository
            )
            return SQLAlchemyFormulaireRempliRepository(db)
        except ImportError:
            return None

    register_service("formulaire_repository", formulaire_repository_factory)

    # Signalements repository
    def signalement_repository_factory(db: Session):
        try:
            from modules.signalements.infrastructure.persistence import (
                SQLAlchemySignalementRepository
            )
            return SQLAlchemySignalementRepository(db)
        except ImportError:
            return None

    register_service("signalement_repository", signalement_repository_factory)

    # Pointages repository
    def pointage_repository_factory(db: Session):
        try:
            from modules.pointages.infrastructure.persistence import (
                SQLAlchemyPointageRepository
            )
            return SQLAlchemyPointageRepository(db)
        except ImportError:
            return None

    register_service("pointage_repository", pointage_repository_factory)


# Initialiser au chargement du module
_register_core_services()
