"""
Zentra AI - Bank Transaction Scanner

Connects to Plaid API to fetch bank/card transactions
and identify recurring subscription payments.
"""
import logging
from datetime import date, timedelta
from typing import List, Dict, Optional
from app.config import settings

logger = logging.getLogger(__name__)


class BankScanner:
    """Scans bank transactions via Plaid for subscription payments."""

    def __init__(self, access_token: Optional[str] = None):
        self.plaid_access_token = access_token
        self.plaid_client = None
        self._init_plaid()

    def _init_plaid(self):
        """Initialize Plaid client."""
        if not (settings.PLAID_CLIENT_ID and settings.PLAID_SECRET):
            logger.info("Plaid credentials not configured")
            return

        try:
            from plaid.api import plaid_api
            from plaid.model.products import Products
            from plaid.model.country_code import CountryCode
            import plaid

            env_map = {
                "sandbox": plaid.Environment.Sandbox,
                "development": plaid.Environment.Development,
                "production": plaid.Environment.Production,
            }
            configuration = plaid.Configuration(
                host=env_map.get(settings.PLAID_ENV, plaid.Environment.Sandbox),
                api_key={
                    "clientId": settings.PLAID_CLIENT_ID,
                    "secret": settings.PLAID_SECRET,
                },
            )
            api_client = plaid.ApiClient(configuration)
            self.plaid_client = plaid_api.PlaidApi(api_client)
            logger.info("Plaid initialized")
        except Exception as e:
            logger.warning(f"Plaid not available: {e}")

    def get_transactions(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[Dict]:
        """Fetch bank transactions from Plaid."""
        if not start_date:
            start_date = date.today() - timedelta(days=90)
        if not end_date:
            end_date = date.today()

        if not self.plaid_client or not self.plaid_access_token:
            logger.info("Plaid not configured, returning mock transactions")
            return self._mock_transactions()

        try:
            from plaid.model.transactions_get_request import TransactionsGetRequest
            from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions

            request = TransactionsGetRequest(
                access_token=self.plaid_access_token,
                start_date=start_date,
                end_date=end_date,
            )
            response = self.plaid_client.transactions_get(request)
            transactions = response.transactions

            return [
                {
                    "id": txn.transaction_id,
                    "description": txn.name,
                    "amount": abs(txn.amount),
                    "date": txn.date,
                    "category": txn.category[0] if txn.category else "other",
                    "merchant_name": txn.merchant_name or txn.name,
                }
                for txn in transactions
                if txn.amount < 0  # negative = debit
            ]
        except Exception as e:
            logger.error(f"Plaid transaction fetch failed: {e}")
            return []

    def _mock_transactions(self) -> List[Dict]:
        """Return mock transactions for testing."""
        today = date.today()
        return [
            {
                "id": "txn_001",
                "description": "Netflix Monthly Subscription",
                "amount": 649.0,
                "date": today - timedelta(days=15),
                "category": "Entertainment",
                "merchant_name": "Netflix",
            },
            {
                "id": "txn_002",
                "description": "Spotify Premium",
                "amount": 119.0,
                "date": today - timedelta(days=15),
                "category": "Entertainment",
                "merchant_name": "Spotify",
            },
            {
                "id": "txn_003",
                "description": "Amazon Prime Membership",
                "amount": 1499.0,
                "date": today - timedelta(days=30),
                "category": "Entertainment",
                "merchant_name": "Amazon Prime",
            },
            {
                "id": "txn_004",
                "description": "Google One Storage",
                "amount": 130.0,
                "date": today - timedelta(days=15),
                "category": "Software",
                "merchant_name": "Google One",
            },
            {
                "id": "txn_005",
                "description": "Zomato Pro Membership",
                "amount": 149.0,
                "date": today - timedelta(days=20),
                "category": "Food",
                "merchant_name": "Zomato Pro",
            },
        ]

    def create_link_token(self, user_id: str) -> Optional[str]:
        """Create a Plaid Link token for OAuth flow."""
        if not self.plaid_client:
            return "mock_link_token_for_testing"

        try:
            from plaid.model.link_token_create_request import LinkTokenCreateRequest
            from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
            from plaid.model.products import Products
            from plaid.model.country_code import CountryCode

            request = LinkTokenCreateRequest(
                products=[Products("transactions")],
                client_name="Zentra AI",
                country_codes=[CountryCode("IN")],
                language="en",
                user=LinkTokenCreateRequestUser(client_user_id=user_id),
            )
            response = self.plaid_client.link_token_create(request)
            return response.link_token
        except Exception as e:
            logger.error(f"Failed to create Plaid link token: {e}")
            return None

    def exchange_public_token(self, public_token: str) -> Optional[str]:
        """Exchange Plaid public token for access token."""
        if not self.plaid_client:
            return "mock_plaid_access_token"

        try:
            from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
            request = ItemPublicTokenExchangeRequest(public_token=public_token)
            response = self.plaid_client.item_public_token_exchange(request)
            return response.access_token
        except Exception as e:
            logger.error(f"Failed to exchange public token: {e}")
            return None
