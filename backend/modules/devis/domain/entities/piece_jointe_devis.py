"""Entite PieceJointeDevis - Liaison entre devis et documents GED.

DEV-07: Insertion multimedia - Ajout photos, fiches techniques ou documents
par ligne/lot pour enrichissement visuel du devis client.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class PieceJointeDevis:
    """Represente une piece jointe associee a un devis.

    Fait le lien entre un devis (et optionnellement un lot ou une ligne)
    et un document stocke dans le module GED.

    Attributes:
        id: Identifiant unique (None si non persiste).
        devis_id: ID du devis associe (FK).
        document_id: ID du document GED associe (FK).
        lot_devis_id: ID du lot associe (optionnel).
        ligne_devis_id: ID de la ligne associee (optionnel).
        visible_client: Si la piece jointe est visible par le client.
        ordre: Ordre d affichage dans le devis.
        created_at: Date de creation.
        created_by: ID de l utilisateur createur.
        nom_fichier: Nom du fichier (denormalise depuis GED).
        type_fichier: Type de fichier (denormalise depuis GED).
        taille_octets: Taille en octets (denormalise depuis GED).
        mime_type: Type MIME (denormalise depuis GED).
    """

    id: Optional[int] = None
    devis_id: Optional[int] = None
    document_id: Optional[int] = None  # FK vers documents.id (GED)
    lot_devis_id: Optional[int] = None  # Optionnel: attache a un lot specifique
    ligne_devis_id: Optional[int] = None  # Optionnel: attache a une ligne specifique
    visible_client: bool = True
    ordre: int = 0
    created_at: Optional[datetime] = None
    created_by: Optional[int] = None

    # Champs denormalises depuis le document GED (pour lecture rapide)
    nom_fichier: Optional[str] = None
    type_fichier: Optional[str] = None
    taille_octets: Optional[int] = None
    mime_type: Optional[str] = None
