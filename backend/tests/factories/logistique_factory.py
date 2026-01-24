"""Factories pour générer des données de test du module Logistique.

Ces factories créent des données dynamiques, évitant les données en dur.
Chaque appel génère des données différentes.
"""

import random
import string
from datetime import date, time, datetime, timedelta
from typing import Optional, List

from modules.logistique.domain.entities import Ressource, Reservation
from modules.logistique.domain.value_objects import (
    CategorieRessource,
    StatutReservation,
    PlageHoraire,
)


class RessourceFactory:
    """Factory pour créer des instances de Ressource de test."""

    # Pools de données pour génération aléatoire
    NOMS_ENGIN_LEVAGE = [
        "Grue mobile {}T",
        "Grue à tour {}m",
        "Nacelle élévatrice {}m",
        "Chariot élévateur {}T",
        "Mini-grue araignée",
        "Palan électrique {}kg",
    ]

    NOMS_VEHICULE = [
        "Camion-benne {}T",
        "Camionnette utilitaire",
        "Fourgon {}m3",
        "Camion plateau",
        "Tracteur agricole",
        "4x4 chantier",
    ]

    NOMS_GROS_OUTILLAGE = [
        "Marteau-piqueur {}kg",
        "Groupe électrogène {}kW",
        "Compresseur {}L",
        "Bétonnière {}L",
        "Poste à souder MIG",
        "Disqueuse {}mm",
    ]

    NOMS_PETIT_OUTILLAGE = [
        "Perceuse visseuse {}V",
        "Meuleuse d'angle",
        "Scie sauteuse",
        "Niveau laser",
        "Décapeur thermique",
        "Rainureuse",
    ]

    NOMS_EPI = [
        "Casque de chantier",
        "Harnais antichute",
        "Gants de protection",
        "Lunettes de sécurité",
        "Chaussures de sécurité",
        "Gilet haute visibilité",
    ]

    COULEURS = [
        "#FF5733", "#3498DB", "#27AE60", "#9B59B6",
        "#E74C3C", "#1ABC9C", "#F39C12", "#2ECC71",
        "#E67E22", "#8E44AD", "#16A085", "#D35400",
    ]

    _counter = 0

    @classmethod
    def _get_next_id(cls) -> int:
        """Génère un ID unique incrémental."""
        cls._counter += 1
        return cls._counter

    @classmethod
    def _random_code(cls, prefix: str = "RES") -> str:
        """Génère un code unique aléatoire."""
        suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"{prefix}{suffix}"

    @classmethod
    def _random_name(cls, categorie: CategorieRessource) -> str:
        """Génère un nom aléatoire selon la catégorie."""
        noms_map = {
            CategorieRessource.ENGIN_LEVAGE: cls.NOMS_ENGIN_LEVAGE,
            CategorieRessource.VEHICULE: cls.NOMS_VEHICULE,
            CategorieRessource.GROS_OUTILLAGE: cls.NOMS_GROS_OUTILLAGE,
            CategorieRessource.PETIT_OUTILLAGE: cls.NOMS_PETIT_OUTILLAGE,
            CategorieRessource.EPI: cls.NOMS_EPI,
        }
        nom_template = random.choice(noms_map[categorie])
        # Remplacer {} par une valeur aléatoire
        valeurs = {
            "T": random.choice([5, 10, 25, 50, 100]),
            "m": random.choice([10, 15, 20, 25, 30, 40]),
            "m3": random.choice([5, 8, 12, 15, 20]),
            "kg": random.choice([5, 10, 15, 25, 30]),
            "kW": random.choice([3, 5, 10, 15, 20]),
            "L": random.choice([100, 150, 200, 350, 500]),
            "mm": random.choice([115, 125, 180, 230]),
            "V": random.choice([12, 18, 24, 36]),
        }
        for key, val in valeurs.items():
            if f"{{{key}}}" in nom_template:
                return nom_template.replace(f"{{{key}}}", str(val))
        return nom_template.replace("{}", str(random.randint(10, 100)))

    @classmethod
    def _random_plage_horaire(cls) -> PlageHoraire:
        """Génère une plage horaire aléatoire réaliste."""
        debuts = [time(6, 0), time(7, 0), time(7, 30), time(8, 0)]
        fins = [time(16, 0), time(17, 0), time(17, 30), time(18, 0), time(19, 0)]
        return PlageHoraire(
            heure_debut=random.choice(debuts),
            heure_fin=random.choice(fins),
        )

    @classmethod
    def create(
        cls,
        id: Optional[int] = None,
        code: Optional[str] = None,
        nom: Optional[str] = None,
        categorie: Optional[CategorieRessource] = None,
        couleur: Optional[str] = None,
        plage_horaire_defaut: Optional[PlageHoraire] = None,
        validation_requise: Optional[bool] = None,
        actif: bool = True,
        **kwargs,
    ) -> Ressource:
        """Crée une instance de Ressource avec des valeurs aléatoires par défaut.

        Args:
            id: ID optionnel (auto-généré si non fourni)
            code: Code unique (auto-généré si non fourni)
            nom: Nom de la ressource (auto-généré selon catégorie si non fourni)
            categorie: Catégorie de ressource (aléatoire si non fourni)
            couleur: Couleur hex (aléatoire si non fourni)
            plage_horaire_defaut: Plage par défaut (aléatoire si non fourni)
            validation_requise: Si validation requise (basé sur catégorie si non fourni)
            actif: Si la ressource est active
            **kwargs: Arguments supplémentaires pour Ressource

        Returns:
            Une instance Ressource avec des données générées
        """
        if categorie is None:
            categorie = random.choice(list(CategorieRessource))

        if nom is None:
            nom = cls._random_name(categorie)

        if validation_requise is None:
            validation_requise = categorie.validation_requise

        now = datetime.now()

        return Ressource(
            id=id or cls._get_next_id(),
            code=code or cls._random_code(categorie.value[:3].upper()),
            nom=nom,
            description=kwargs.get("description", f"Ressource de type {categorie.label}"),
            categorie=categorie,
            couleur=couleur or random.choice(cls.COULEURS),
            photo_url=kwargs.get("photo_url"),
            plage_horaire_defaut=plage_horaire_defaut or cls._random_plage_horaire(),
            validation_requise=validation_requise,
            actif=actif,
            created_at=kwargs.get("created_at", now),
            updated_at=kwargs.get("updated_at", now),
            created_by=kwargs.get("created_by"),
            updated_by=kwargs.get("updated_by"),
        )

    @classmethod
    def create_batch(cls, count: int = 5, **kwargs) -> List[Ressource]:
        """Crée plusieurs ressources.

        Args:
            count: Nombre de ressources à créer
            **kwargs: Arguments passés à create()

        Returns:
            Liste de ressources
        """
        return [cls.create(**kwargs) for _ in range(count)]

    @classmethod
    def create_one_per_category(cls) -> List[Ressource]:
        """Crée une ressource par catégorie.

        Returns:
            Liste de 5 ressources (une par catégorie)
        """
        return [cls.create(categorie=cat) for cat in CategorieRessource]


class ReservationFactory:
    """Factory pour créer des instances de Reservation de test."""

    COMMENTAIRES = [
        "Besoin pour travaux de fondation",
        "Utilisation prévue toute la journée",
        "Chantier prioritaire - livraison béton",
        "Installation échafaudage prévu",
        "Travaux de finition intérieure",
        "Démontage structure métallique",
        "Coulage dalle niveau {}",
        "Pose menuiseries extérieures",
        "Travaux toiture - étanchéité",
        "Installation réseau électrique",
    ]

    _counter = 0

    @classmethod
    def _get_next_id(cls) -> int:
        """Génère un ID unique incrémental."""
        cls._counter += 1
        return cls._counter

    @classmethod
    def _random_commentaire(cls) -> str:
        """Génère un commentaire aléatoire."""
        commentaire = random.choice(cls.COMMENTAIRES)
        return commentaire.replace("{}", str(random.randint(1, 5)))

    @classmethod
    def _random_plage(cls, date_base: date) -> tuple:
        """Génère une plage horaire aléatoire pour une réservation."""
        heures_debut = [7, 8, 9, 10, 13, 14]
        heure_debut = random.choice(heures_debut)
        duree = random.choice([2, 3, 4, 5, 8])  # heures
        heure_fin = min(heure_debut + duree, 19)

        return (
            time(heure_debut, 0),
            time(heure_fin, 0),
        )

    @classmethod
    def create(
        cls,
        id: Optional[int] = None,
        ressource_id: int = 1,
        chantier_id: int = 1,
        demandeur_id: int = 1,
        date_reservation: Optional[date] = None,
        heure_debut: Optional[time] = None,
        heure_fin: Optional[time] = None,
        statut: Optional[StatutReservation] = None,
        commentaire: Optional[str] = None,
        **kwargs,
    ) -> Reservation:
        """Crée une instance de Reservation avec des valeurs aléatoires par défaut.

        Args:
            id: ID optionnel (auto-généré si non fourni)
            ressource_id: ID de la ressource
            chantier_id: ID du chantier
            demandeur_id: ID du demandeur
            date_reservation: Date de réservation (aléatoire dans les 30 jours si non fourni)
            heure_debut: Heure de début (aléatoire si non fourni)
            heure_fin: Heure de fin (aléatoire si non fourni)
            statut: Statut de la réservation (EN_ATTENTE par défaut)
            commentaire: Commentaire (aléatoire si non fourni)
            **kwargs: Arguments supplémentaires

        Returns:
            Une instance Reservation avec des données générées
        """
        if date_reservation is None:
            # Date aléatoire dans les 30 prochains jours
            days_offset = random.randint(1, 30)
            date_reservation = date.today() + timedelta(days=days_offset)

        if heure_debut is None or heure_fin is None:
            h_debut, h_fin = cls._random_plage(date_reservation)
            heure_debut = heure_debut or h_debut
            heure_fin = heure_fin or h_fin

        if statut is None:
            statut = StatutReservation.EN_ATTENTE

        now = datetime.now()

        reservation = Reservation(
            id=id or cls._get_next_id(),
            ressource_id=ressource_id,
            chantier_id=chantier_id,
            demandeur_id=demandeur_id,
            date_reservation=date_reservation,
            heure_debut=heure_debut,
            heure_fin=heure_fin,
            statut=statut,
            commentaire=commentaire or cls._random_commentaire(),
            valideur_id=kwargs.get("valideur_id"),
            motif_refus=kwargs.get("motif_refus"),
            validated_at=kwargs.get("validated_at"),
            created_at=kwargs.get("created_at", now),
            updated_at=kwargs.get("updated_at", now),
        )

        return reservation

    @classmethod
    def create_en_attente(cls, **kwargs) -> Reservation:
        """Crée une réservation en attente."""
        return cls.create(statut=StatutReservation.EN_ATTENTE, **kwargs)

    @classmethod
    def create_validee(cls, valideur_id: int = 5, **kwargs) -> Reservation:
        """Crée une réservation validée."""
        return cls.create(
            statut=StatutReservation.VALIDEE,
            valideur_id=valideur_id,
            validated_at=datetime.now(),
            **kwargs,
        )

    @classmethod
    def create_refusee(
        cls, valideur_id: int = 5, motif: str = "Ressource indisponible", **kwargs
    ) -> Reservation:
        """Crée une réservation refusée."""
        return cls.create(
            statut=StatutReservation.REFUSEE,
            valideur_id=valideur_id,
            motif_refus=motif,
            validated_at=datetime.now(),
            **kwargs,
        )

    @classmethod
    def create_annulee(cls, **kwargs) -> Reservation:
        """Crée une réservation annulée."""
        return cls.create(statut=StatutReservation.ANNULEE, **kwargs)

    @classmethod
    def create_batch(cls, count: int = 5, **kwargs) -> List[Reservation]:
        """Crée plusieurs réservations.

        Args:
            count: Nombre de réservations à créer
            **kwargs: Arguments passés à create()

        Returns:
            Liste de réservations
        """
        return [cls.create(**kwargs) for _ in range(count)]

    @classmethod
    def create_week_planning(
        cls,
        ressource_id: int,
        start_date: Optional[date] = None,
        reservations_per_day: int = 2,
    ) -> List[Reservation]:
        """Crée un planning de réservations sur une semaine.

        Args:
            ressource_id: ID de la ressource
            start_date: Date de début (lundi de cette semaine par défaut)
            reservations_per_day: Nombre de réservations par jour

        Returns:
            Liste de réservations pour la semaine
        """
        if start_date is None:
            today = date.today()
            start_date = today - timedelta(days=today.weekday())  # Lundi

        reservations = []
        chantier_ids = [1, 2, 3, 4, 5]
        demandeur_ids = [10, 11, 12, 13, 14]

        for day in range(5):  # Lundi à vendredi
            current_date = start_date + timedelta(days=day)

            for slot in range(reservations_per_day):
                # Matin ou après-midi
                if slot == 0:
                    heure_debut = time(8, 0)
                    heure_fin = time(12, 0)
                else:
                    heure_debut = time(14, 0)
                    heure_fin = time(17, 0)

                # Statut varié
                statuts_poids = [
                    (StatutReservation.VALIDEE, 50),
                    (StatutReservation.EN_ATTENTE, 30),
                    (StatutReservation.REFUSEE, 10),
                    (StatutReservation.ANNULEE, 10),
                ]
                statut = random.choices(
                    [s[0] for s in statuts_poids],
                    weights=[s[1] for s in statuts_poids],
                )[0]

                reservation = cls.create(
                    ressource_id=ressource_id,
                    chantier_id=random.choice(chantier_ids),
                    demandeur_id=random.choice(demandeur_ids),
                    date_reservation=current_date,
                    heure_debut=heure_debut,
                    heure_fin=heure_fin,
                    statut=statut,
                    valideur_id=5 if statut in [StatutReservation.VALIDEE, StatutReservation.REFUSEE] else None,
                    validated_at=datetime.now() if statut in [StatutReservation.VALIDEE, StatutReservation.REFUSEE] else None,
                    motif_refus="Planning complet" if statut == StatutReservation.REFUSEE else None,
                )
                reservations.append(reservation)

        return reservations


class LogistiqueDataFactory:
    """Factory principale pour générer un jeu de données complet."""

    @classmethod
    def create_full_dataset(
        cls,
        ressources_count: int = 10,
        reservations_per_ressource: int = 5,
    ) -> dict:
        """Crée un jeu de données complet pour les tests.

        Args:
            ressources_count: Nombre de ressources à créer
            reservations_per_ressource: Nombre de réservations par ressource

        Returns:
            Dict avec 'ressources' et 'reservations'
        """
        ressources = RessourceFactory.create_batch(ressources_count)
        reservations = []

        for ressource in ressources:
            ressource_reservations = ReservationFactory.create_batch(
                count=reservations_per_ressource,
                ressource_id=ressource.id,
            )
            reservations.extend(ressource_reservations)

        return {
            "ressources": ressources,
            "reservations": reservations,
        }

    @classmethod
    def create_demo_dataset(cls) -> dict:
        """Crée un jeu de données de démonstration réaliste.

        Returns:
            Dict avec ressources et réservations de démo
        """
        # Une ressource par catégorie
        ressources = RessourceFactory.create_one_per_category()

        # Réservations variées
        reservations = []
        for ressource in ressources:
            # Planning pour une semaine
            week_reservations = ReservationFactory.create_week_planning(
                ressource_id=ressource.id,
                reservations_per_day=1,
            )
            reservations.extend(week_reservations)

        return {
            "ressources": ressources,
            "reservations": reservations,
        }

    @classmethod
    def reset_counters(cls):
        """Remet à zéro les compteurs d'ID (utile entre les tests)."""
        RessourceFactory._counter = 0
        ReservationFactory._counter = 0
