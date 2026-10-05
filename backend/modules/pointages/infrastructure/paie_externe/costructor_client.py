"""Adaptateur HTTP vers l'API externe de Costructor (saisies de temps)."""

import logging
import time as horloge
from collections.abc import Callable
from datetime import date, time

import httpx

from ...application.ports import ClientPaieExternePort, ErreurPaieExterne

logger = logging.getLogger(__name__)

URL_API_COSTRUCTOR = "https://api.costructor.co/external/v1"

# Limitation de debit (429) : attentes successives avant d'abandonner, en secondes
ATTENTES_LIMITE_DEBIT = (2, 4, 8, 16)


class CostructorClient(ClientPaieExternePort):
    """Cree et supprime des saisies de temps via POST/DELETE /timesheet_entries.

    Comportements de l'API constates sur un compte reel :
    - debut et fin obligatoires pour une saisie de travail (une duree seule est refusee) ;
    - aucune protection contre les doublons : chaque POST cree une saisie ;
    - modification impossible (PATCH/PUT refuses) : on supprime puis on recree ;
    - debit limite : 429 apres une dizaine d'appels rapproches, leve en quelques
      secondes. Le client patiente puis reessaie, sans quoi une validation en lot
      tomberait en erreur au-dela des premiers pointages.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = URL_API_COSTRUCTOR,
        timeout: float = 15.0,
        transport: httpx.BaseTransport | None = None,
        attendre: Callable[[float], None] = horloge.sleep,
    ):
        """
        Initialise le client.

        Args:
            api_key: Cle d'API Costructor (Reglages > API).
            base_url: URL de base de l'API externe.
            timeout: Delai maximal par requete, en secondes.
            transport: Transport HTTP de substitution (tests).
            attendre: Fonction de pause, substituable dans les tests.

        Raises:
            ValueError: Si la cle d'API est absente.
        """
        if not api_key or not api_key.strip():
            raise ValueError("Cle d'API Costructor manquante (COSTRUCTOR_API_KEY).")
        self._attendre = attendre
        self._http = httpx.Client(
            base_url=base_url,
            timeout=timeout,
            transport=transport,
            headers={
                "Authorization": f"Bearer {api_key.strip()}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )

    def creer_saisie_travail(
        self,
        utilisateur_externe_id: str,
        chantier_externe_id: str,
        jour: date,
        debut: time,
        fin: time,
        notes: str,
    ) -> str:
        """Cree une saisie de travail et renvoie son identifiant Costructor."""
        reponse = self._requete("POST", "/timesheet_entries", json={
            "user": utilisateur_externe_id,
            "type": "work",
            "day": jour.isoformat(),
            "project": chantier_externe_id,
            "startTime": debut.strftime("%H:%M"),
            "endTime": fin.strftime("%H:%M"),
            "notes": notes,
        })
        try:
            return reponse.json()["data"]["id"]
        except (ValueError, KeyError, TypeError) as exc:
            raise ErreurPaieExterne(
                "Reponse de Costructor inattendue : identifiant de saisie absent."
            ) from exc

    def supprimer_saisie(self, saisie_id: str) -> None:
        """Supprime une saisie ; une saisie deja absente (404) n'est pas une erreur."""
        self._requete("DELETE", f"/timesheet_entries/{saisie_id}", accepter_absence=True)

    def fermer(self) -> None:
        """Libere la connexion HTTP."""
        self._http.close()

    def _requete(self, methode: str, chemin: str, accepter_absence: bool = False, **kwargs):
        for attente in (*ATTENTES_LIMITE_DEBIT, None):
            try:
                reponse = self._http.request(methode, chemin, **kwargs)
            except httpx.HTTPError as exc:
                raise ErreurPaieExterne(
                    f"Costructor injoignable : {exc.__class__.__name__}"
                ) from exc

            if reponse.status_code != 429 or attente is None:
                break
            # 429 : la requete a ete refusee sans etre traitee, la rejouer ne
            # cree donc pas de doublon.
            delai = self._delai_demande(reponse) or attente
            logger.info("Costructor limite le debit : nouvel essai dans %ss", delai)
            self._attendre(delai)

        if reponse.status_code == 404 and accepter_absence:
            return reponse
        if reponse.status_code >= 400:
            raise ErreurPaieExterne(
                f"Costructor a refuse la requete ({reponse.status_code}) : "
                f"{self._message_erreur(reponse)}"
            )
        return reponse

    @staticmethod
    def _delai_demande(reponse: httpx.Response) -> float | None:
        """Delai indique par l'en-tete Retry-After (en secondes), borne a 60 s."""
        try:
            return min(float(reponse.headers["Retry-After"]), 60.0)
        except (KeyError, ValueError):
            return None

    @staticmethod
    def _message_erreur(reponse: httpx.Response) -> str:
        try:
            return reponse.json().get("message") or reponse.reason_phrase
        except ValueError:
            # L'API renvoie parfois une page HTML (500, 405) : on n'en garde pas le contenu
            return reponse.reason_phrase or "erreur inconnue"
