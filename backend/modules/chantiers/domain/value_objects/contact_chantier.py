"""Value Object ContactChantier - Contact sur place d'un chantier."""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ContactChantier:
    """
    Value Object représentant le contact sur place d'un chantier.

    Selon CDC CHT-07: Nom, profession et téléphone du contact sur place.

    Attributes:
        nom: Nom du contact.
        profession: Profession/rôle du contact (optionnel).
        telephone: Numéro de téléphone du contact (optionnel).
    """

    nom: str
    profession: Optional[str] = None
    telephone: Optional[str] = None

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

        # Normaliser la profession si présente
        if self.profession:
            normalized_profession = self.profession.strip()
            object.__setattr__(self, "profession", normalized_profession if normalized_profession else None)

        # Valider et nettoyer le téléphone si présent
        if self.telephone and self.telephone.strip():
            # Nettoyer le téléphone (garder + et chiffres)
            cleaned_phone = re.sub(r"[^\d+]", "", self.telephone)

            if len(cleaned_phone) >= 8 and len(cleaned_phone) <= 15:
                object.__setattr__(self, "telephone", cleaned_phone)
            else:
                # Si format invalide, garder tel quel
                object.__setattr__(self, "telephone", self.telephone.strip())
        else:
            object.__setattr__(self, "telephone", None)

    def __str__(self) -> str:
        """Retourne le contact formaté."""
        parts = [self.nom]
        if self.profession:
            parts.append(f"({self.profession})")
        if self.telephone:
            parts.append(f"- {self.formatted_phone}")
        return " ".join(parts)

    @property
    def formatted_phone(self) -> Optional[str]:
        """
        Retourne le téléphone formaté pour affichage.

        Returns:
            Téléphone au format lisible, ou None si pas de téléphone.
        """
        if not self.telephone:
            return None

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
    def callable_phone(self) -> Optional[str]:
        """
        Retourne le numéro au format appelable (tel:).

        Returns:
            URL tel: pour click-to-call, ou None si pas de téléphone.
        """
        if not self.telephone:
            return None
        return f"tel:{self.telephone}"

    def to_dict(self) -> dict[str, Optional[str]]:
        """
        Convertit en dictionnaire pour sérialisation.

        Returns:
            Dictionnaire avec nom, profession et telephone.
        """
        return {
            "nom": self.nom,
            "profession": self.profession,
            "telephone": self.telephone,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Optional[str]]) -> "ContactChantier":
        """
        Crée un contact à partir d'un dictionnaire.

        Args:
            data: Dictionnaire avec 'nom', 'profession' (optionnel) et 'telephone' (optionnel).

        Returns:
            Instance ContactChantier.

        Raises:
            ValueError: Si la clé 'nom' est manquante.
        """
        if "nom" not in data:
            raise ValueError("Dictionnaire doit contenir 'nom'")
        return cls(
            nom=data["nom"],
            profession=data.get("profession"),
            telephone=data.get("telephone"),
        )
