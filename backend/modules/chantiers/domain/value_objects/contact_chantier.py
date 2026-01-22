"""Value Object ContactChantier - Contact sur place d'un chantier."""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ContactChantier:
    """
    Value Object représentant le contact sur place d'un chantier.

    Selon CDC CHT-07: Nom et téléphone du contact sur place.

    Attributes:
        nom: Nom du contact.
        telephone: Numéro de téléphone du contact.
    """

    nom: str
    telephone: str

    # Pattern pour validation du téléphone (français ou international)
    PHONE_PATTERN = r"^(\+\d{1,3})?[\s.-]?\d{1,4}[\s.-]?\d{1,4}[\s.-]?\d{1,4}[\s.-]?\d{0,4}$"

    def __post_init__(self) -> None:
        """Valide les données à la création."""
        # Valider le nom
        if not self.nom or not self.nom.strip():
            raise ValueError("Le nom du contact ne peut pas être vide")

        # Normaliser le nom
        normalized_nom = self.nom.strip().title()
        object.__setattr__(self, "nom", normalized_nom)

        # Valider le téléphone
        if not self.telephone or not self.telephone.strip():
            raise ValueError("Le téléphone du contact ne peut pas être vide")

        # Nettoyer le téléphone (garder + et chiffres)
        cleaned_phone = re.sub(r"[^\d+]", "", self.telephone)

        if len(cleaned_phone) < 8:
            raise ValueError(
                f"Numéro de téléphone trop court: {self.telephone}. "
                f"Minimum 8 chiffres requis."
            )

        if len(cleaned_phone) > 15:
            raise ValueError(
                f"Numéro de téléphone trop long: {self.telephone}. "
                f"Maximum 15 chiffres autorisés."
            )

        object.__setattr__(self, "telephone", cleaned_phone)

    def __str__(self) -> str:
        """Retourne le contact formaté."""
        return f"{self.nom} ({self.formatted_phone})"

    @property
    def formatted_phone(self) -> str:
        """
        Retourne le téléphone formaté pour affichage.

        Returns:
            Téléphone au format lisible.
        """
        phone = self.telephone

        # Format français (10 chiffres commençant par 0)
        if len(phone) == 10 and phone.startswith("0"):
            return f"{phone[0:2]} {phone[2:4]} {phone[4:6]} {phone[6:8]} {phone[8:10]}"

        # Format international français (+33...)
        if phone.startswith("+33") and len(phone) == 12:
            return f"+33 {phone[3]} {phone[4:6]} {phone[6:8]} {phone[8:10]} {phone[10:12]}"

        # Autre format international
        if phone.startswith("+"):
            return phone

        return phone

    @property
    def callable_phone(self) -> str:
        """
        Retourne le numéro au format appelable (tel:).

        Returns:
            URL tel: pour click-to-call.
        """
        return f"tel:{self.telephone}"

    def to_dict(self) -> dict[str, str]:
        """
        Convertit en dictionnaire pour sérialisation.

        Returns:
            Dictionnaire avec nom et telephone.
        """
        return {
            "nom": self.nom,
            "telephone": self.telephone,
        }

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "ContactChantier":
        """
        Crée un contact à partir d'un dictionnaire.

        Args:
            data: Dictionnaire avec 'nom' et 'telephone'.

        Returns:
            Instance ContactChantier.

        Raises:
            ValueError: Si les clés sont manquantes.
        """
        if "nom" not in data or "telephone" not in data:
            raise ValueError("Dictionnaire doit contenir 'nom' et 'telephone'")
        return cls(nom=data["nom"], telephone=data["telephone"])
