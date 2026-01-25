"""Value Object TypeUtilisateur - Type d'utilisateur (Employé ou Sous-traitant)."""

from enum import Enum


class TypeUtilisateur(str, Enum):
    """
    Énumération des types d'utilisateur.

    Selon CDC USR-05:
    - EMPLOYE: Salarié de l'entreprise Greg Constructions
    - INTERIMAIRE: Travailleur temporaire via agence d'intérim
    - SOUS_TRAITANT: Prestataire externe intervenant sur chantier
    """

    EMPLOYE = "employe"
    INTERIMAIRE = "interimaire"
    SOUS_TRAITANT = "sous_traitant"

    def __str__(self) -> str:
        """Retourne la valeur du type."""
        return self.value

    @classmethod
    def from_string(cls, value: str) -> "TypeUtilisateur":
        """
        Crée un TypeUtilisateur à partir d'une string.

        Args:
            value: La valeur string du type.

        Returns:
            L'instance TypeUtilisateur correspondante.

        Raises:
            ValueError: Si la valeur ne correspond à aucun type.
        """
        # Mapping des anciens types vers les nouveaux
        legacy_mapping = {
            "conducteur": "employe",
            "chef_chantier": "employe",
            "ouvrier": "employe",
            "admin": "employe",
            "siege": "employe",
        }

        normalized = value.lower()
        if normalized in legacy_mapping:
            normalized = legacy_mapping[normalized]

        try:
            return cls(normalized)
        except ValueError:
            valid_types = [t.value for t in cls]
            raise ValueError(
                f"Type utilisateur invalide: {value}. Types valides: {valid_types}"
            )

    def is_internal(self) -> bool:
        """Vérifie si l'utilisateur est interne à l'entreprise."""
        return self == TypeUtilisateur.EMPLOYE

    def is_interimaire(self) -> bool:
        """Vérifie si l'utilisateur est intérimaire."""
        return self == TypeUtilisateur.INTERIMAIRE

    def is_external(self) -> bool:
        """Vérifie si l'utilisateur est externe (sous-traitant)."""
        return self == TypeUtilisateur.SOUS_TRAITANT
