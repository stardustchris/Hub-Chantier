"""Service de validation des prérequis de réception d'un chantier.

Ce service vérifie que toutes les conditions sont remplies avant de permettre
la réception d'un chantier.

Gap: GAP-CHT-001 - Validation prérequis réception
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional


@dataclass
class PrerequisResult:
    """Résultat de validation des prérequis de réception."""

    est_valide: bool
    prerequis_manquants: List[str]
    details: Dict[str, Any]  # Comptages détaillés pour debugging


class PrerequisReceptionService:
    """Service vérifiant les prérequis de réception d'un chantier.

    Ce service suit le pattern Domain Service (Clean Architecture).
    Il ne contient PAS de logique infrastructure (pas de session DB).
    Les repositories sont injectés depuis la couche application.
    """

    def verifier_prerequis(
        self,
        chantier_id: int,
        formulaire_repo=None,
        signalement_repo=None,
        pointage_repo=None,
    ) -> PrerequisResult:
        """
        Vérifie tous les prérequis de réception.

        Args:
            chantier_id: ID du chantier à vérifier
            formulaire_repo: Repository formulaires (optionnel)
            signalement_repo: Repository signalements (optionnel)
            pointage_repo: Repository pointages (optionnel)

        Returns:
            PrerequisResult avec détails des validations
        """
        manquants = []
        details = {}

        # 1. Vérifier formulaires obligatoires (si repo fourni)
        if formulaire_repo:
            # TODO: Définir liste formulaires obligatoires (config ou DB)
            # Pour l'instant, vérifier qu'il y a au moins 3 formulaires
            count = formulaire_repo.count_by_chantier(chantier_id)
            if count < 3:  # Placeholder: 3 formulaires minimum
                manquants.append(
                    f"Formulaires manquants ({count}/3 minimum requis)"
                )
            details['formulaires_count'] = count

        # 2. Vérifier signalements critiques ouverts
        if signalement_repo:
            try:
                # Récupérer TOUS les signalements puis filtrer localement (Clean Architecture)
                all_signalements = signalement_repo.find_by_chantier(chantier_id)

                # Filtrer localement pour éviter import cross-module
                critiques_ouverts = sum(
                    1 for s in all_signalements
                    if s.statut.value == "ouvert" and s.priorite.value == "critique"
                )

                if critiques_ouverts > 0:
                    manquants.append(
                        f"{critiques_ouverts} signalement(s) critique(s) ouvert(s)"
                    )
                details['signalements_critiques'] = critiques_ouverts
            except (AttributeError, ImportError):
                # Module signalements pas disponible ou attributs manquants
                details['signalements_critiques'] = 'non_verifie'

        # 3. Vérifier heures validées
        if pointage_repo:
            try:
                # Utilise search existante (Clean Architecture)
                pointages, total = pointage_repo.search(chantier_id=chantier_id)

                # Filtrer localement avec .value pour éviter import StatutPointage
                non_valides = sum(
                    1 for p in pointages
                    if p.statut.value != "valide"  # Compare .value (lowercase)
                )

                if non_valides > 0:
                    manquants.append(f"{non_valides} pointage(s) non validé(s)")
                details['pointages_non_valides'] = non_valides
            except (AttributeError, ImportError):
                # Module pointages pas disponible ou méthode/attribut manquant
                details['pointages_non_valides'] = 'non_verifie'

        return PrerequisResult(
            est_valide=len(manquants) == 0,
            prerequis_manquants=manquants,
            details=details
        )
