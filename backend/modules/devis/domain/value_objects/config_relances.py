"""Value Object ConfigRelances - Configuration des relances automatiques.

DEV-24: Relances automatiques - Configuration des delais et types
de relance par devis.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


class ConfigRelancesInvalideError(Exception):
    """Erreur levee quand la configuration de relances est invalide."""

    def __init__(self, message: str = "Configuration de relances invalide"):
        self.message = message
        super().__init__(self.message)


DELAIS_DEFAUT = [7, 15, 30]
TYPE_RELANCE_DEFAUT = "email"
TYPES_RELANCE_VALIDES = ("email", "push", "email_push")


@dataclass(frozen=True)
class ConfigRelances:
    """Configuration des relances automatiques pour un devis.

    Value object immuable definissant les parametres de relance :
    - Delais en jours apres envoi du devis (par defaut 7, 15, 30 jours)
    - Activation/desactivation des relances
    - Type de relance par defaut (email, push, email_push)

    Attributes:
        delais: Liste des delais en jours pour chaque relance.
        actif: Si les relances sont actives pour ce devis.
        type_relance_defaut: Type de relance par defaut.
    """

    delais: tuple = (7, 15, 30)
    actif: bool = True
    type_relance_defaut: str = "email"

    def __post_init__(self) -> None:
        """Valide les donnees a la creation."""
        if not self.delais:
            raise ConfigRelancesInvalideError(
                "Au moins un delai de relance est requis"
            )
        for delai in self.delais:
            if not isinstance(delai, int) or delai < 1:
                raise ConfigRelancesInvalideError(
                    f"Chaque delai doit etre un entier >= 1 jour (recu: {delai})"
                )
        # Verifier que les delais sont croissants
        delais_list = list(self.delais)
        if delais_list != sorted(delais_list):
            raise ConfigRelancesInvalideError(
                "Les delais doivent etre en ordre croissant"
            )
        if self.type_relance_defaut not in TYPES_RELANCE_VALIDES:
            raise ConfigRelancesInvalideError(
                f"Type de relance invalide: {self.type_relance_defaut}. "
                f"Valeurs autorisees: {', '.join(TYPES_RELANCE_VALIDES)}"
            )

    @property
    def nombre_relances(self) -> int:
        """Retourne le nombre total de relances configurees."""
        return len(self.delais)

    def prochaine_relance(
        self,
        date_envoi: datetime,
        nb_relances_effectuees: int,
    ) -> Optional[datetime]:
        """Calcule la date de la prochaine relance.

        Args:
            date_envoi: Date d'envoi du devis au client.
            nb_relances_effectuees: Nombre de relances deja envoyees/planifiees.

        Returns:
            La date de la prochaine relance, ou None si toutes les relances
            ont ete effectuees ou si les relances sont desactivees.
        """
        if not self.actif:
            return None
        if nb_relances_effectuees >= len(self.delais):
            return None
        delai_jours = self.delais[nb_relances_effectuees]
        return date_envoi + timedelta(days=delai_jours)

    def toutes_les_dates(self, date_envoi: datetime) -> List[datetime]:
        """Calcule toutes les dates de relance prevues.

        Args:
            date_envoi: Date d'envoi du devis au client.

        Returns:
            Liste des dates de relance prevues.
        """
        if not self.actif:
            return []
        return [
            date_envoi + timedelta(days=delai)
            for delai in self.delais
        ]

    def to_dict(self) -> Dict[str, Any]:
        """Convertit le value object en dictionnaire (pour JSON)."""
        return {
            "delais": list(self.delais),
            "actif": self.actif,
            "type_relance_defaut": self.type_relance_defaut,
        }

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "ConfigRelances":
        """Cree un ConfigRelances depuis un dictionnaire.

        Args:
            data: Dictionnaire de configuration. Si None, retourne les valeurs par defaut.

        Returns:
            Le ConfigRelances correspondant.
        """
        if not data:
            return cls()
        return cls(
            delais=tuple(data.get("delais", DELAIS_DEFAUT)),
            actif=data.get("actif", True),
            type_relance_defaut=data.get("type_relance_defaut", TYPE_RELANCE_DEFAUT),
        )

    @classmethod
    def defaut(cls) -> "ConfigRelances":
        """Retourne la configuration par defaut (7, 15, 30 jours, email)."""
        return cls()
