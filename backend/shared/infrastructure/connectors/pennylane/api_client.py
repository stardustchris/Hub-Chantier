"""Client HTTP pour l'API Pennylane v2.

CONN-10: Sync factures fournisseurs Pennylane.
CONN-11: Sync encaissements clients Pennylane.
CONN-12: Import fournisseurs Pennylane.

Documentation API: https://pennylane.readme.io/
Rate limiting: 5 requetes/seconde.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)


class PennylaneApiError(Exception):
    """Erreur levee lors d'un appel API Pennylane."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(self.message)


class PennylaneRateLimitError(PennylaneApiError):
    """Erreur levee quand le rate limit est atteint (429)."""

    def __init__(self, retry_after: Optional[int] = None):
        self.retry_after = retry_after
        super().__init__(
            f"Rate limit atteint. Reessayez dans {retry_after or 'quelques'} secondes.",
            status_code=429,
        )


class PennylaneAuthenticationError(PennylaneApiError):
    """Erreur levee lors d'un probleme d'authentification (401)."""

    def __init__(self, message: str = "Token API invalide ou expire."):
        super().__init__(message, status_code=401)


@dataclass
class PennylaneSupplierInvoice:
    """Represente une facture fournisseur depuis Pennylane."""

    id: str
    invoice_number: Optional[str]
    supplier_id: str
    supplier_name: Optional[str]
    supplier_siret: Optional[str]
    amount_ht: Decimal
    amount_ttc: Decimal
    currency: str
    invoice_date: Optional[datetime]
    due_date: Optional[datetime]
    paid_date: Optional[datetime]
    is_paid: bool
    analytic_code: Optional[str]
    label: Optional[str]
    updated_at: datetime

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "PennylaneSupplierInvoice":
        """Cree une instance depuis la reponse API.

        Args:
            data: Dictionnaire de la reponse API.

        Returns:
            Instance PennylaneSupplierInvoice.
        """
        # Parser les montants
        amount_ht = Decimal(str(data.get("amount", 0) or 0))
        amount_ttc = Decimal(str(data.get("gross_amount", amount_ht) or amount_ht))

        # Parser les dates
        invoice_date = None
        if data.get("date"):
            try:
                invoice_date = datetime.fromisoformat(data["date"].replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass

        due_date = None
        if data.get("deadline"):
            try:
                due_date = datetime.fromisoformat(data["deadline"].replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass

        paid_date = None
        if data.get("paid_at"):
            try:
                paid_date = datetime.fromisoformat(data["paid_at"].replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass

        updated_at = datetime.utcnow()
        if data.get("updated_at"):
            try:
                updated_at = datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass

        # Extraire infos fournisseur
        supplier = data.get("supplier", {}) or {}
        supplier_id = str(data.get("supplier_id", "") or supplier.get("id", ""))
        supplier_name = supplier.get("name")
        supplier_siret = supplier.get("siret")

        # Extraire code analytique (peut etre dans plusieurs endroits)
        analytic_code = None
        if data.get("analytic_reference"):
            analytic_code = data["analytic_reference"]
        elif data.get("line_items"):
            for item in data["line_items"]:
                if item.get("analytic_reference"):
                    analytic_code = item["analytic_reference"]
                    break

        return cls(
            id=str(data.get("id", "")),
            invoice_number=data.get("invoice_number"),
            supplier_id=supplier_id,
            supplier_name=supplier_name,
            supplier_siret=supplier_siret,
            amount_ht=amount_ht,
            amount_ttc=amount_ttc,
            currency=data.get("currency", "EUR"),
            invoice_date=invoice_date,
            due_date=due_date,
            paid_date=paid_date,
            is_paid=data.get("paid", False) or data.get("is_paid", False),
            analytic_code=analytic_code,
            label=data.get("label") or data.get("filename"),
            updated_at=updated_at,
        )


@dataclass
class PennylaneCustomerInvoice:
    """Represente une facture client depuis Pennylane."""

    id: str
    invoice_number: Optional[str]
    customer_name: Optional[str]
    amount_ht: Decimal
    amount_ttc: Decimal
    currency: str
    invoice_date: Optional[datetime]
    due_date: Optional[datetime]
    paid_date: Optional[datetime]
    is_paid: bool
    amount_paid: Decimal
    updated_at: datetime

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "PennylaneCustomerInvoice":
        """Cree une instance depuis la reponse API."""
        amount_ht = Decimal(str(data.get("amount", 0) or 0))
        amount_ttc = Decimal(str(data.get("gross_amount", amount_ht) or amount_ht))
        amount_paid = Decimal(str(data.get("paid_amount", 0) or 0))

        invoice_date = None
        if data.get("date"):
            try:
                invoice_date = datetime.fromisoformat(data["date"].replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass

        due_date = None
        if data.get("deadline"):
            try:
                due_date = datetime.fromisoformat(data["deadline"].replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass

        paid_date = None
        if data.get("paid_at"):
            try:
                paid_date = datetime.fromisoformat(data["paid_at"].replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass

        updated_at = datetime.utcnow()
        if data.get("updated_at"):
            try:
                updated_at = datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass

        customer = data.get("customer", {}) or {}

        return cls(
            id=str(data.get("id", "")),
            invoice_number=data.get("invoice_number"),
            customer_name=customer.get("name"),
            amount_ht=amount_ht,
            amount_ttc=amount_ttc,
            currency=data.get("currency", "EUR"),
            invoice_date=invoice_date,
            due_date=due_date,
            paid_date=paid_date,
            is_paid=data.get("paid", False) or data.get("is_paid", False),
            amount_paid=amount_paid,
            updated_at=updated_at,
        )


@dataclass
class PennylaneSupplier:
    """Represente un fournisseur depuis Pennylane."""

    id: str
    name: str
    siret: Optional[str]
    address: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    payment_delay_days: int
    iban: Optional[str]
    bic: Optional[str]
    updated_at: datetime

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "PennylaneSupplier":
        """Cree une instance depuis la reponse API."""
        updated_at = datetime.utcnow()
        if data.get("updated_at"):
            try:
                updated_at = datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass

        # Extraire les coordonnees bancaires
        bank_info = data.get("bank_account", {}) or {}

        return cls(
            id=str(data.get("id", "")),
            name=data.get("name", ""),
            siret=data.get("siret") or data.get("registration_number"),
            address=data.get("address"),
            email=data.get("email"),
            phone=data.get("phone"),
            payment_delay_days=data.get("payment_delay", 30) or 30,
            iban=bank_info.get("iban"),
            bic=bank_info.get("bic") or bank_info.get("swift"),
            updated_at=updated_at,
        )


class PennylaneApiClient:
    """Client HTTP pour l'API Pennylane v2.

    Gere l'authentification, le rate limiting et les erreurs.
    Rate limit: 5 requetes/seconde.

    Example:
        >>> async with PennylaneApiClient(api_key="xxx") as client:
        ...     invoices = await client.get_supplier_invoices(
        ...         is_paid=True,
        ...         updated_since=datetime(2026, 1, 1)
        ...     )
        ...     for inv in invoices:
        ...         print(inv.supplier_name, inv.amount_ht)
    """

    BASE_URL = "https://app.pennylane.com/api/external/v2"
    DEFAULT_TIMEOUT = 30.0
    RATE_LIMIT_DELAY = 0.2  # 200ms entre requetes (5 req/sec)

    def __init__(
        self,
        api_key: str,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = 3,
    ):
        """Initialise le client API Pennylane.

        Args:
            api_key: Cle API Pennylane.
            timeout: Timeout en secondes pour les requetes.
            max_retries: Nombre max de tentatives en cas d'erreur.

        Raises:
            ValueError: Si la cle API est invalide ou manquante.
        """
        # Validation de la cle API (finding HIGH security-auditor)
        if not api_key or api_key.strip() == "":
            raise ValueError(
                "PENNYLANE_API_KEY est requise. "
                "Configurez-la dans les variables d'environnement."
            )

        import os
        environment = os.getenv("ENVIRONMENT", "development")
        if environment == "production":
            # En production, verifier que la cle a une longueur minimale
            if len(api_key.strip()) < 20:
                raise ValueError(
                    "PENNYLANE_API_KEY invalide pour la production. "
                    "Verifiez que vous utilisez une vraie cle API Pennylane."
                )
            # Verifier que ce n'est pas une cle de test/exemple
            test_patterns = ["test", "example", "demo", "xxx", "your_", "placeholder"]
            if any(pattern in api_key.lower() for pattern in test_patterns):
                raise ValueError(
                    "PENNYLANE_API_KEY semble etre une cle de test/exemple. "
                    "Utilisez une vraie cle API Pennylane en production."
                )

        self.api_key = api_key.strip()
        self.timeout = timeout
        self.max_retries = max_retries
        self._client: Optional[httpx.AsyncClient] = None
        self._last_request_time: float = 0

    async def __aenter__(self) -> "PennylaneApiClient":
        """Entre dans le context manager."""
        self._client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            timeout=self.timeout,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "HubChantier/1.0",
            },
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Sort du context manager."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _rate_limit(self) -> None:
        """Applique le rate limiting (5 req/sec)."""
        import time

        now = time.time()
        elapsed = now - self._last_request_time
        if elapsed < self.RATE_LIMIT_DELAY:
            await asyncio.sleep(self.RATE_LIMIT_DELAY - elapsed)
        self._last_request_time = time.time()

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute une requete HTTP avec retry et rate limiting.

        Args:
            method: Methode HTTP (GET, POST, etc.).
            endpoint: Endpoint API (ex: /supplier_invoices).
            params: Parametres de requete.
            json_data: Corps JSON de la requete.

        Returns:
            Reponse JSON parsee.

        Raises:
            PennylaneApiError: En cas d'erreur API.
            PennylaneRateLimitError: Si rate limit atteint.
            PennylaneAuthenticationError: Si authentification echouee.
        """
        if not self._client:
            raise PennylaneApiError("Client non initialise. Utilisez 'async with'.")

        last_error: Optional[Exception] = None

        for attempt in range(self.max_retries):
            try:
                await self._rate_limit()

                logger.debug(
                    f"Pennylane API {method} {endpoint} "
                    f"(attempt {attempt + 1}/{self.max_retries})"
                )

                response = await self._client.request(
                    method=method,
                    url=endpoint,
                    params=params,
                    json=json_data,
                )

                # Gestion des erreurs HTTP
                if response.status_code == 401:
                    raise PennylaneAuthenticationError()

                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 5))
                    logger.warning(f"Rate limit atteint, attente {retry_after}s")
                    await asyncio.sleep(retry_after)
                    continue

                if response.status_code >= 400:
                    raise PennylaneApiError(
                        f"Erreur API Pennylane: {response.status_code}",
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response.json()

            except httpx.TimeoutException as e:
                last_error = PennylaneApiError(f"Timeout: {e}")
                logger.warning(f"Timeout Pennylane (attempt {attempt + 1}): {e}")
                await asyncio.sleep(1 * (attempt + 1))  # Backoff exponentiel simple

            except httpx.RequestError as e:
                last_error = PennylaneApiError(f"Erreur reseau: {e}")
                logger.warning(f"Erreur reseau Pennylane (attempt {attempt + 1}): {e}")
                await asyncio.sleep(1 * (attempt + 1))

        raise last_error or PennylaneApiError("Erreur inconnue apres retries")

    async def get_supplier_invoices(
        self,
        is_paid: Optional[bool] = None,
        updated_since: Optional[datetime] = None,
        page: int = 1,
        per_page: int = 100,
    ) -> List[PennylaneSupplierInvoice]:
        """Recupere les factures fournisseurs.

        CONN-10: Synchronise les factures fournisseurs payees.

        Args:
            is_paid: Filtrer par statut de paiement.
            updated_since: Filtrer par date de mise a jour.
            page: Numero de page (pagination).
            per_page: Nombre de resultats par page (max 100).

        Returns:
            Liste des factures fournisseurs.
        """
        params: Dict[str, Any] = {
            "page": page,
            "per_page": min(per_page, 100),
        }

        if is_paid is not None:
            params["paid"] = str(is_paid).lower()

        if updated_since:
            params["updated_since"] = updated_since.isoformat()

        response = await self._request("GET", "/supplier_invoices", params=params)

        # La reponse peut etre une liste ou un objet avec une cle "invoices"
        invoices_data = response if isinstance(response, list) else response.get("invoices", [])

        return [
            PennylaneSupplierInvoice.from_api_response(inv)
            for inv in invoices_data
        ]

    async def get_all_supplier_invoices(
        self,
        is_paid: Optional[bool] = None,
        updated_since: Optional[datetime] = None,
    ) -> List[PennylaneSupplierInvoice]:
        """Recupere toutes les factures fournisseurs (pagination auto).

        Args:
            is_paid: Filtrer par statut de paiement.
            updated_since: Filtrer par date de mise a jour.

        Returns:
            Liste complete des factures fournisseurs.
        """
        all_invoices: List[PennylaneSupplierInvoice] = []
        page = 1
        per_page = 100

        while True:
            invoices = await self.get_supplier_invoices(
                is_paid=is_paid,
                updated_since=updated_since,
                page=page,
                per_page=per_page,
            )

            if not invoices:
                break

            all_invoices.extend(invoices)

            if len(invoices) < per_page:
                break

            page += 1

        logger.info(f"Recupere {len(all_invoices)} factures fournisseurs Pennylane")
        return all_invoices

    async def get_customer_invoices(
        self,
        updated_since: Optional[datetime] = None,
        page: int = 1,
        per_page: int = 100,
    ) -> List[PennylaneCustomerInvoice]:
        """Recupere les factures clients.

        CONN-11: Synchronise les encaissements clients.

        Args:
            updated_since: Filtrer par date de mise a jour.
            page: Numero de page (pagination).
            per_page: Nombre de resultats par page (max 100).

        Returns:
            Liste des factures clients.
        """
        params: Dict[str, Any] = {
            "page": page,
            "per_page": min(per_page, 100),
        }

        if updated_since:
            params["updated_since"] = updated_since.isoformat()

        response = await self._request("GET", "/customer_invoices", params=params)

        invoices_data = response if isinstance(response, list) else response.get("invoices", [])

        return [
            PennylaneCustomerInvoice.from_api_response(inv)
            for inv in invoices_data
        ]

    async def get_all_customer_invoices(
        self,
        updated_since: Optional[datetime] = None,
    ) -> List[PennylaneCustomerInvoice]:
        """Recupere toutes les factures clients (pagination auto).

        Args:
            updated_since: Filtrer par date de mise a jour.

        Returns:
            Liste complete des factures clients.
        """
        all_invoices: List[PennylaneCustomerInvoice] = []
        page = 1
        per_page = 100

        while True:
            invoices = await self.get_customer_invoices(
                updated_since=updated_since,
                page=page,
                per_page=per_page,
            )

            if not invoices:
                break

            all_invoices.extend(invoices)

            if len(invoices) < per_page:
                break

            page += 1

        logger.info(f"Recupere {len(all_invoices)} factures clients Pennylane")
        return all_invoices

    async def get_suppliers(
        self,
        page: int = 1,
        per_page: int = 100,
    ) -> List[PennylaneSupplier]:
        """Recupere les fournisseurs.

        CONN-12: Import fournisseurs Pennylane.

        Args:
            page: Numero de page (pagination).
            per_page: Nombre de resultats par page (max 100).

        Returns:
            Liste des fournisseurs.
        """
        params: Dict[str, Any] = {
            "page": page,
            "per_page": min(per_page, 100),
        }

        response = await self._request("GET", "/suppliers", params=params)

        suppliers_data = response if isinstance(response, list) else response.get("suppliers", [])

        return [
            PennylaneSupplier.from_api_response(sup)
            for sup in suppliers_data
        ]

    async def get_all_suppliers(self) -> List[PennylaneSupplier]:
        """Recupere tous les fournisseurs (pagination auto).

        Returns:
            Liste complete des fournisseurs.
        """
        all_suppliers: List[PennylaneSupplier] = []
        page = 1
        per_page = 100

        while True:
            suppliers = await self.get_suppliers(
                page=page,
                per_page=per_page,
            )

            if not suppliers:
                break

            all_suppliers.extend(suppliers)

            if len(suppliers) < per_page:
                break

            page += 1

        logger.info(f"Recupere {len(all_suppliers)} fournisseurs Pennylane")
        return all_suppliers

    async def get_supplier_invoice_by_id(
        self,
        invoice_id: str,
    ) -> Optional[PennylaneSupplierInvoice]:
        """Recupere une facture fournisseur par son ID.

        Args:
            invoice_id: ID de la facture Pennylane.

        Returns:
            La facture ou None si non trouvee.
        """
        try:
            response = await self._request("GET", f"/supplier_invoices/{invoice_id}")
            return PennylaneSupplierInvoice.from_api_response(response)
        except PennylaneApiError as e:
            if e.status_code == 404:
                return None
            raise
