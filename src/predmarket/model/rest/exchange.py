from abc import ABC, abstractmethod
from typing import Any
from .response import *
from httpx import AsyncClient, HTTPStatusError
from yarl import URL
from .price import Price
from .question import Question
from .contract import Contract


class BaseExchangeClient(ABC):
    """Shared helpers for exchange-specific clients."""

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def _safe_get(self, url: URL, params: dict[str, Any]) -> Any:
        """Perform a GET request with simple error handling."""
        try:
            response = await self._client.get(str(url), params=params)
            response.raise_for_status()
            return response.json()
        except HTTPStatusError as exc:
            raise RuntimeError(f"Request failed ({url}): {exc.response.text}") from exc

    @abstractmethod
    async def fetch_price(self, id: str) -> Response[Price]:
        """Fetch a single contract price."""

    @abstractmethod
    async def fetch_contract(self, id: str) -> Response[Contract]:
        """Fetch metadata for a single contract."""

    @abstractmethod
    async def fetch_contracts(self, **kwargs: Any) -> Response[list[Contract]]:
        """Fetch a batch of contracts."""

    @abstractmethod
    async def fetch_question(self, id: str) -> Response[Question]:
        """Fetch metadata for a single question/event."""

    @abstractmethod
    async def fetch_questions(self, **kwargs: Any) -> Response[list[Question]]:
        """Fetch a batch of questions/events."""
