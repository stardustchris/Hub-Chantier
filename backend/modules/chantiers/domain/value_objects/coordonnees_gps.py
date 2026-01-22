"""Value Object CoordonneesGPS - Coordonnées géographiques d'un chantier."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CoordonneesGPS:
    """
    Value Object représentant les coordonnées GPS d'un chantier.

    Selon CDC CHT-04: Latitude + Longitude pour géolocalisation.
    Permet la navigation GPS (CHT-08) et l'affichage sur mini carte (CHT-09).

    Attributes:
        latitude: Latitude en degrés décimaux (-90 à 90).
        longitude: Longitude en degrés décimaux (-180 à 180).
    """

    latitude: float
    longitude: float

    def __post_init__(self) -> None:
        """Valide les coordonnées à la création."""
        if not -90 <= self.latitude <= 90:
            raise ValueError(
                f"Latitude invalide: {self.latitude}. "
                f"Doit être entre -90 et 90 degrés."
            )
        if not -180 <= self.longitude <= 180:
            raise ValueError(
                f"Longitude invalide: {self.longitude}. "
                f"Doit être entre -180 et 180 degrés."
            )

    def __str__(self) -> str:
        """Retourne les coordonnées formatées."""
        return f"{self.latitude:.6f}, {self.longitude:.6f}"

    @property
    def google_maps_url(self) -> str:
        """
        Retourne l'URL Google Maps pour navigation (CHT-08).

        Returns:
            URL vers Google Maps avec les coordonnées.
        """
        return f"https://www.google.com/maps?q={self.latitude},{self.longitude}"

    @property
    def waze_url(self) -> str:
        """
        Retourne l'URL Waze pour navigation (CHT-08).

        Returns:
            URL vers Waze avec les coordonnées.
        """
        return f"https://waze.com/ul?ll={self.latitude},{self.longitude}&navigate=yes"

    @property
    def apple_maps_url(self) -> str:
        """
        Retourne l'URL Apple Maps pour navigation.

        Returns:
            URL vers Apple Maps avec les coordonnées.
        """
        return f"https://maps.apple.com/?ll={self.latitude},{self.longitude}"

    def to_dict(self) -> dict[str, float]:
        """
        Convertit en dictionnaire pour sérialisation.

        Returns:
            Dictionnaire avec latitude et longitude.
        """
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
        }

    @classmethod
    def from_dict(cls, data: dict[str, float]) -> "CoordonneesGPS":
        """
        Crée des coordonnées à partir d'un dictionnaire.

        Args:
            data: Dictionnaire avec 'latitude' et 'longitude'.

        Returns:
            Instance CoordonneesGPS.

        Raises:
            ValueError: Si les clés sont manquantes.
        """
        if "latitude" not in data or "longitude" not in data:
            raise ValueError("Dictionnaire doit contenir 'latitude' et 'longitude'")
        return cls(latitude=data["latitude"], longitude=data["longitude"])

    @classmethod
    def from_string(cls, value: str) -> "CoordonneesGPS":
        """
        Parse des coordonnées depuis une chaîne "lat,lon".

        Args:
            value: Coordonnées au format "latitude,longitude".

        Returns:
            Instance CoordonneesGPS.

        Raises:
            ValueError: Si le format est invalide.
        """
        try:
            parts = value.split(",")
            if len(parts) != 2:
                raise ValueError("Format attendu: 'latitude,longitude'")
            lat = float(parts[0].strip())
            lon = float(parts[1].strip())
            return cls(latitude=lat, longitude=lon)
        except (ValueError, IndexError) as e:
            raise ValueError(f"Format de coordonnées invalide: {value}. {e}")

    def distance_to(self, other: "CoordonneesGPS") -> float:
        """
        Calcule la distance approximative vers d'autres coordonnées (en km).

        Utilise la formule de Haversine simplifiée.

        Args:
            other: Les coordonnées de destination.

        Returns:
            Distance approximative en kilomètres.
        """
        import math

        R = 6371  # Rayon de la Terre en km

        lat1 = math.radians(self.latitude)
        lat2 = math.radians(other.latitude)
        dlat = math.radians(other.latitude - self.latitude)
        dlon = math.radians(other.longitude - self.longitude)

        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    @classmethod
    def france_metropolitaine(cls) -> tuple[tuple[float, float], tuple[float, float]]:
        """
        Retourne les limites de la France métropolitaine.

        Returns:
            Tuple (min, max) avec (lat, lon) pour chaque.
        """
        return ((41.0, -5.5), (51.5, 10.0))

    def is_in_france(self) -> bool:
        """
        Vérifie si les coordonnées sont en France métropolitaine.

        Returns:
            True si les coordonnées sont en France.
        """
        bounds = self.france_metropolitaine()
        return (
            bounds[0][0] <= self.latitude <= bounds[1][0]
            and bounds[0][1] <= self.longitude <= bounds[1][1]
        )
