"""Value Object pour le type de signature electronique.

DEV-14: Signature electronique client - Types de signature simple.
"""

from enum import Enum


class TypeSignature(str, Enum):
    """Types de signature electronique supportes.

    Conformite eIDAS (signature simple) :
    - Dessin tactile sur ecran (canvas/tablette)
    - Upload d'un scan de signature manuscrite
    - Saisie textuelle nom/prenom (validation identite)

    Values:
        DESSIN_TACTILE: Signature dessinee sur ecran tactile (base64 PNG).
        UPLOAD_SCAN: Upload d'un scan de signature manuscrite (base64 image).
        NOM_PRENOM: Saisie textuelle du nom et prenom du signataire.
    """

    DESSIN_TACTILE = "dessin_tactile"
    UPLOAD_SCAN = "upload_scan"
    NOM_PRENOM = "nom_prenom"

    @property
    def label(self) -> str:
        """Retourne le libelle affichable du type de signature."""
        labels = {
            self.DESSIN_TACTILE: "Dessin tactile",
            self.UPLOAD_SCAN: "Upload scan",
            self.NOM_PRENOM: "Nom / Prenom",
        }
        return labels[self]
