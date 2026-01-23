"""Entite FormulaireRempli - Instance d'un formulaire rempli."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Any

from ..value_objects import StatutFormulaire, TypeChamp


@dataclass
class PhotoFormulaire:
    """
    Photo jointe a un formulaire.

    Selon CDC FOR-04 - Ajout photos horodatees.

    Attributes:
        id: Identifiant unique.
        url: URL de stockage de la photo.
        nom_fichier: Nom original du fichier.
        timestamp: Date/heure de prise de la photo.
        latitude: Latitude GPS (optionnel).
        longitude: Longitude GPS (optionnel).
        champ_nom: Nom du champ associe.
    """

    url: str
    nom_fichier: str
    champ_nom: str
    id: Optional[int] = None
    timestamp: datetime = field(default_factory=datetime.now)
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    @property
    def est_geolocalisee(self) -> bool:
        """Verifie si la photo est geolocalisee."""
        return self.latitude is not None and self.longitude is not None


@dataclass
class ChampRempli:
    """
    Valeur d'un champ rempli dans un formulaire.

    Attributes:
        nom: Nom du champ (reference au template).
        valeur: Valeur saisie.
        type_champ: Type de champ.
        timestamp: Horodatage de la saisie.
    """

    nom: str
    type_champ: TypeChamp
    valeur: Optional[Any] = None
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def est_rempli(self) -> bool:
        """Verifie si le champ a une valeur."""
        if self.valeur is None:
            return False
        if isinstance(self.valeur, str) and not self.valeur.strip():
            return False
        return True


@dataclass
class FormulaireRempli:
    """
    Entite representant un formulaire rempli.

    Selon CDC Section 8 - Formulaires Chantier.

    Attributes:
        id: Identifiant unique (None si non persiste).
        template_id: ID du template utilise (FOR-01).
        chantier_id: ID du chantier associe (FOR-06).
        user_id: ID de l'utilisateur qui remplit (FOR-03 - auto_intervenant).
        statut: Statut du formulaire.
        champs: Valeurs des champs remplis.
        photos: Photos jointes (FOR-04).
        signature_url: URL de la signature (FOR-05).
        signature_nom: Nom du signataire.
        signature_timestamp: Date/heure de signature.
        localisation_latitude: Latitude GPS (FOR-03).
        localisation_longitude: Longitude GPS (FOR-03).
        soumis_at: Date/heure de soumission (FOR-07).
        valide_by: ID du valideur.
        valide_at: Date/heure de validation.
        version: Version du formulaire (pour historique FOR-08).
        parent_id: ID de la version precedente (FOR-08).
        created_at: Date de creation.
        updated_at: Date de derniere modification.
    """

    template_id: int
    chantier_id: int
    user_id: int

    id: Optional[int] = None
    statut: StatutFormulaire = StatutFormulaire.BROUILLON
    champs: List[ChampRempli] = field(default_factory=list)
    photos: List[PhotoFormulaire] = field(default_factory=list)

    # Signature (FOR-05)
    signature_url: Optional[str] = None
    signature_nom: Optional[str] = None
    signature_timestamp: Optional[datetime] = None

    # Localisation (FOR-03)
    localisation_latitude: Optional[float] = None
    localisation_longitude: Optional[float] = None

    # Soumission (FOR-07)
    soumis_at: Optional[datetime] = None

    # Validation
    valide_by: Optional[int] = None
    valide_at: Optional[datetime] = None

    # Historique (FOR-08)
    version: int = 1
    parent_id: Optional[int] = None

    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    @property
    def est_brouillon(self) -> bool:
        """Verifie si le formulaire est en brouillon."""
        return self.statut == StatutFormulaire.BROUILLON

    @property
    def est_soumis(self) -> bool:
        """Verifie si le formulaire a ete soumis."""
        return self.statut.est_soumis

    @property
    def est_signe(self) -> bool:
        """Verifie si le formulaire est signe."""
        return self.signature_url is not None

    @property
    def est_geolocalise(self) -> bool:
        """Verifie si le formulaire est geolocalise."""
        return self.localisation_latitude is not None and self.localisation_longitude is not None

    @property
    def nombre_photos(self) -> int:
        """Retourne le nombre de photos jointes."""
        return len(self.photos)

    def set_champ(self, nom: str, valeur: Any, type_champ: TypeChamp) -> None:
        """
        Definit la valeur d'un champ.

        Args:
            nom: Nom du champ.
            valeur: Valeur a definir.
            type_champ: Type du champ.

        Raises:
            ValueError: Si le formulaire n'est pas modifiable.
        """
        if not self.statut.est_modifiable:
            raise ValueError("Le formulaire n'est plus modifiable")

        # Rechercher si le champ existe deja
        for champ in self.champs:
            if champ.nom == nom:
                champ.valeur = valeur
                champ.timestamp = datetime.now()
                self.updated_at = datetime.now()
                return

        # Ajouter le nouveau champ
        self.champs.append(ChampRempli(
            nom=nom,
            type_champ=type_champ,
            valeur=valeur,
        ))
        self.updated_at = datetime.now()

    def get_champ(self, nom: str) -> Optional[ChampRempli]:
        """
        Recupere un champ par son nom.

        Args:
            nom: Nom du champ.

        Returns:
            Le champ trouve ou None.
        """
        for champ in self.champs:
            if champ.nom == nom:
                return champ
        return None

    def get_valeur(self, nom: str) -> Optional[Any]:
        """
        Recupere la valeur d'un champ.

        Args:
            nom: Nom du champ.

        Returns:
            La valeur du champ ou None.
        """
        champ = self.get_champ(nom)
        return champ.valeur if champ else None

    def ajouter_photo(self, photo: PhotoFormulaire) -> None:
        """
        Ajoute une photo au formulaire (FOR-04).

        Args:
            photo: La photo a ajouter.

        Raises:
            ValueError: Si le formulaire n'est pas modifiable.
        """
        if not self.statut.est_modifiable:
            raise ValueError("Le formulaire n'est plus modifiable")

        self.photos.append(photo)
        self.updated_at = datetime.now()

    def retirer_photo(self, photo_id: int) -> bool:
        """
        Retire une photo du formulaire.

        Args:
            photo_id: ID de la photo a retirer.

        Returns:
            True si la photo a ete retiree.

        Raises:
            ValueError: Si le formulaire n'est pas modifiable.
        """
        if not self.statut.est_modifiable:
            raise ValueError("Le formulaire n'est plus modifiable")

        initial_count = len(self.photos)
        self.photos = [p for p in self.photos if p.id != photo_id]

        if len(self.photos) < initial_count:
            self.updated_at = datetime.now()
            return True
        return False

    def signer(self, signature_url: str, nom_signataire: str) -> None:
        """
        Ajoute une signature au formulaire (FOR-05).

        Args:
            signature_url: URL de la signature.
            nom_signataire: Nom du signataire.

        Raises:
            ValueError: Si le formulaire n'est pas modifiable.
        """
        if not self.statut.est_modifiable:
            raise ValueError("Le formulaire n'est plus modifiable")

        self.signature_url = signature_url
        self.signature_nom = nom_signataire
        self.signature_timestamp = datetime.now()
        self.updated_at = datetime.now()

    def set_localisation(self, latitude: float, longitude: float) -> None:
        """
        Definit la localisation du formulaire (FOR-03).

        Args:
            latitude: Latitude GPS.
            longitude: Longitude GPS.
        """
        self.localisation_latitude = latitude
        self.localisation_longitude = longitude
        self.updated_at = datetime.now()

    def soumettre(self) -> None:
        """
        Soumet le formulaire avec horodatage (FOR-07).

        Raises:
            ValueError: Si le formulaire n'est pas en brouillon.
        """
        if self.statut != StatutFormulaire.BROUILLON:
            raise ValueError("Seul un brouillon peut etre soumis")

        self.statut = StatutFormulaire.SOUMIS
        self.soumis_at = datetime.now()
        self.updated_at = datetime.now()

    def valider(self, valideur_id: int) -> None:
        """
        Valide le formulaire.

        Args:
            valideur_id: ID de l'utilisateur qui valide.

        Raises:
            ValueError: Si le formulaire n'est pas soumis.
        """
        if self.statut != StatutFormulaire.SOUMIS:
            raise ValueError("Seul un formulaire soumis peut etre valide")

        self.statut = StatutFormulaire.VALIDE
        self.valide_by = valideur_id
        self.valide_at = datetime.now()
        self.updated_at = datetime.now()

    def archiver(self) -> None:
        """
        Archive le formulaire (FOR-08).

        Raises:
            ValueError: Si le formulaire n'est pas valide.
        """
        if self.statut != StatutFormulaire.VALIDE:
            raise ValueError("Seul un formulaire valide peut etre archive")

        self.statut = StatutFormulaire.ARCHIVE
        self.updated_at = datetime.now()

    def __eq__(self, other: object) -> bool:
        """Egalite basee sur l'ID (entite)."""
        if not isinstance(other, FormulaireRempli):
            return False
        if self.id is None or other.id is None:
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash base sur l'ID."""
        return hash(self.id) if self.id else hash(id(self))
