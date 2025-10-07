from __future__ import annotations
from typing import Any
from httpx import AsyncClient
from yarl import URL
from predmarket.model.rest import (
    Response,
    Price,
    Contract,
    BaseExchangeClient,
    Question,
    ExchangeName,
)
from .kalshi import KalshiExchange
from .polymarket import PolymarketExchange
import structlog


log = structlog.get_logger()


class PredMarket:
    _CLIENTS: dict[ExchangeName, type[BaseExchangeClient]] = {
        "kalshi": KalshiExchange,
        "polymarket": PolymarketExchange,
    }

    def __init__(self, client: AsyncClient, exchange: ExchangeName):
        self.client = client
        self.exchange = exchange
        self._exchange_client = self._CLIENTS[exchange](client)
        self.log = log.bind(exchange=exchange)

    async def fetch_price(self, id: str) -> Response[Price]:
        self.log.debug(id=id, event="fetch_price")
        return await self._exchange_client.fetch_price(id)

    async def fetch_contract(self, id: str) -> Response[Contract]:
        self.log.debug(id=id, event="fetch_contract")
        return await self._exchange_client.fetch_contract(id)

    async def fetch_contracts(self, **query: Any) -> Response[list[Contract]]:
        self.log.debug(query=query, event="fetch_contracts")
        return await self._exchange_client.fetch_contracts(**(query or {}))

    async def fetch_question(self, id: str) -> Response[Question]:
        self.log.debug(id=id, event="fetch_question")
        return await self._exchange_client.fetch_question(id)

    async def fetch_questions(self, **query: Any) -> Response[list[Question]]:
        self.log.debug(query=query, event="fetch_questions")
        return await self._exchange_client.fetch_questions(**(query or {}))
