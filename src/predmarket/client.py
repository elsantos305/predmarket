from __future__ import annotations
from typing import Any
from httpx import AsyncClient
from yarl import URL
from .models import (
    BaseExchangeClient,
    Response,
    Price,
    Contract,
    Question,
    ExchangeName,
)
from .kalshi import KalshiExchange
from .polymarket import PolymarketExchange


class PredMarket:
    """Async interface for fetching prediction market data from Polymarket and Kalshi."""

    _CLIENTS: dict[ExchangeName, type[BaseExchangeClient]] = {
        "kalshi": KalshiExchange,
        "polymarket": PolymarketExchange,
    }

    def __init__(self, client: AsyncClient, exchange: ExchangeName):
        self.client = client
        self.exchange = exchange
        self._exchange_client = self._CLIENTS[exchange](client)

    async def fetch_price(self, id: str) -> Response[Price]:
        return await self._exchange_client.fetch_price(id)

    async def fetch_contract(self, id: str) -> Response[Contract]:
        return await self._exchange_client.fetch_contract(id)

    async def fetch_contracts(self, **query: Any) -> Response[list[Contract]]:
        """Fetch contracts from one or both exchanges."""
        return await self._exchange_client.fetch_contracts(**(query or {}))

    async def fetch_question(self, id: str) -> Response[Question]:
        return await self._exchange_client.fetch_question(id)

    async def fetch_questions(self, **query: Any) -> Response[list[Question]]:
        return await self._exchange_client.fetch_questions(**(query or {}))
