"""Value Object UniteMesure - Unite de mesure selon CDC TAC-09."""

from enum import Enum


class UniteMesure(Enum):
    """
    Unite de mesure pour les quantites de taches.

    Selon CDC Section 13 - TAC-09:
    m2, litre, unite, ml, kg, m3...
    """

    M2 = "m2"          # Metres carres
    M3 = "m3"          # Metres cubes
    ML = "ml"          # Metres lineaires
    KG = "kg"          # Kilogrammes
    TONNE = "tonne"    # Tonnes
    LITRE = "litre"    # Litres
    UNITE = "unite"    # Unites
    HEURE = "heure"    # Heures
    JOUR = "jour"      # Jours

    @classmethod
    def from_string(cls, value: str) -> "UniteMesure":
        """
        Cree une UniteMesure depuis une chaine.

        Args:
            value: La valeur en chaine (ex: "m2", "kg").

        Returns:
            L'UniteMesure correspondante.

        Raises:
            ValueError: Si la valeur n'est pas valide.
        """
        value_lower = value.lower().strip()
        for unite in cls:
            if unite.value == value_lower:
                return unite
        raise ValueError(
            f"Unite invalide: {value}. Valeurs possibles: {[u.value for u in cls]}"
        )

    def __str__(self) -> str:
        """Retourne la valeur string de l'unite."""
        return self.value

    @property
    def display_name(self) -> str:
        """Retourne le nom d'affichage de l'unite."""
        mapping = {
            UniteMesure.M2: "m²",
            UniteMesure.M3: "m³",
            UniteMesure.ML: "ml",
            UniteMesure.KG: "kg",
            UniteMesure.TONNE: "tonne",
            UniteMesure.LITRE: "litre",
            UniteMesure.UNITE: "unité",
            UniteMesure.HEURE: "heure",
            UniteMesure.JOUR: "jour",
        }
        return mapping.get(self, self.value)

    @classmethod
    def list_all(cls) -> list[dict]:
        """Retourne la liste de toutes les unites avec leurs infos."""
        return [
            {"value": unite.value, "display": unite.display_name}
            for unite in cls
        ]
