from __future__ import annotations

import asyncio
import json
from abc import ABC, abstractmethod
from typing import Any, Generic, Literal, TypeVar

from httpx import AsyncClient, HTTPStatusError
from pydantic import BaseModel, ConfigDict
from yarl import URL

T = TypeVar("T")
Param = T | None
KalshiStatus = Literal["unopened", "open", "closed", "settled"]
ExchangeName = Literal["polymarket", "kalshi"]


def clean_params(**kwargs: Any) -> dict[str, Any]:
    """Remove None values from kwargs before sending as query params."""
    return {k: v for k, v in kwargs.items() if v is not None}


class Response(BaseModel, Generic[T]):
    """Generic API response wrapper."""

    data: T
    metadata: dict[str, Any] = {}

    def merge(self, other: Response[list[Any]]) -> Response[list[Any]]:
        """Merge two list-based responses."""
        if not isinstance(self.data, list) or not isinstance(other.data, list):
            raise TypeError("Both responses must have list data to merge.")
        return Response(
            data=self.data + other.data,
            metadata={**self.metadata, **other.metadata},
        )


class Price(BaseModel):
    """Normalized price of a contract."""

    bid: float
    ask: float
    price: float
    volume: float
    liquidity: float

    @classmethod
    def from_kalshi(cls, market: dict[str, Any]) -> Price:
        override = {
            "price": market.get("last_price"),
            "ask": market.get("yes_ask"),
            "bid": market.get("yes_bid"),
            "volume": market.get("volume"),
            "liquidity": market.get("liquidity"),
        }
        return cls(**override)  # pyright: ignore

    @classmethod
    def from_polymarket(cls, market: dict[str, Any]) -> Price:
        override = {
            "price": market.get("lastTradePrice"),
            "ask": market.get("bestAsk"),
            "bid": market.get("bestBid"),
            "volume": market.get("volume"),
            "liquidity": market.get("liquidity"),
        }

        return cls(**override)  # pyright: ignore


class Contract(BaseModel):
    """Normalized market contract."""

    id: str
    platform: str
    question: str
    raw: dict[str, Any]
    outcomes: list[str]
    model_config = ConfigDict(extra="allow")

    @classmethod
    def from_polymarket(cls, market: dict[str, Any]) -> Contract:
        """Convert a Polymarket event into a standardized Contract."""
        overrides = {
            "id": market.get("id"),
            "platform": "polymarket",
            "question": market.get("question"),
            "outcomes": json.loads(market.get("outcomes", "[]")),
            "raw": market,
        }
        return cls(**{**market, **overrides})  # pyright: ignore

    @classmethod
    def from_kalshi(cls, market: dict[str, Any]) -> Contract:
        """Convert a Kalshi market into a standardized Contract."""
        overrides = {
            "id": market.get("ticker"),
            "platform": "kalshi",
            "question": market.get("title"),
            "outcomes": ["Yes", "No"],
            "raw": market,
        }
        return cls(**{**market, **overrides})  # pyright: ignore


class Question(BaseModel):
    """Normalized event/question across exchanges."""

    id: str
    platform: str
    title: str | None = None
    raw: dict[str, Any]
    model_config = ConfigDict(extra="allow")

    @classmethod
    def from_polymarket(cls, event: dict[str, Any]) -> Question:
        overrides = {
            "id": event.get("id"),
            "platform": "polymarket",
            "title": event.get("title") or event.get("question"),
            "raw": event,
        }
        return cls(**{**event, **overrides})  # pyright: ignore

    @classmethod
    def from_kalshi(cls, event: dict[str, Any]) -> Question:
        overrides = {
            "id": event.get("event_ticker"),
            "platform": "kalshi",
            "title": event.get("title"),
            "raw": event,
        }
        return cls(**{**event, **overrides})  # pyright: ignore


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


class KalshiExchange(BaseExchangeClient):
    """Kalshi-specific implementation."""

    BASE_URL = URL("https://api.elections.kalshi.com/trade-api/v2/")

    async def fetch_price(self, id: str) -> Response[Price]:
        data = await self._safe_get(self.BASE_URL / "markets" / id, {})
        return Response(data=Price.from_kalshi(data["market"]), metadata={})

    async def fetch_contract(self, id: str) -> Response[Contract]:
        data = await self._safe_get(self.BASE_URL / "markets" / id, {})
        return Response(data=Contract.from_kalshi(data["market"]), metadata={})

    async def fetch_contracts(  # pyright: ignore
        self,
        *,
        limit: Param[int] = None,
        cursor: Param[str] = None,
        event_ticker: Param[str] = None,
        series_ticker: Param[str] = None,
        max_close_ts: Param[int] = None,
        min_close_ts: Param[int] = None,
        status: Param[KalshiStatus] = None,
        tickers: Param[str] = None,
    ) -> Response[list[Contract]]:
        params = clean_params(
            limit=limit,
            cursor=cursor,
            event_ticker=event_ticker,
            series_ticker=series_ticker,
            max_close_ts=max_close_ts,
            min_close_ts=min_close_ts,
            status=status,
            tickers=tickers,
        )
        data = await self._safe_get(self.BASE_URL / "markets", params)
        return Response(
            data=[Contract.from_kalshi(m) for m in data.get("markets", [])],
            metadata={"cursor": data.get("cursor")},
        )

    async def fetch_question(self, id: str) -> Response[Question]:
        data = await self._safe_get(self.BASE_URL / "events" / id, {})
        return Response(data=Question.from_kalshi(data["event"]), metadata={})

    async def fetch_questions(  # pyright: ignore
        self,
        *,
        series_ticker: Param[str] = None,
        status: Param[KalshiStatus] = None,
    ) -> Response[list[Question]]:
        params = clean_params(series_ticker=series_ticker, status=status)
        data = await self._safe_get(self.BASE_URL / "events", params)
        return Response(
            data=[Question.from_kalshi(event) for event in data.get("events", [])],
            metadata={"cursor": data.get("cursor")},
        )


class PolymarketExchange(BaseExchangeClient):
    """Polymarket-specific implementation."""

    BASE_URL = URL("https://gamma-api.polymarket.com/")

    async def fetch_price(self, id: str) -> Response[Price]:
        data = await self._safe_get(self.BASE_URL / "markets" / id, {})
        return Response(data=Price.from_polymarket(data), metadata={})

    async def fetch_contract(self, id: str) -> Response[Contract]:
        data = await self._safe_get(self.BASE_URL / "markets" / id, {})
        return Response(data=Contract.from_polymarket(data), metadata={})

    async def fetch_contracts(self, **kwargs: Any) -> Response[list[Contract]]:
        params = clean_params(**kwargs)
        data = await self._safe_get(self.BASE_URL / "markets", params)
        return Response(
            data=[Contract.from_polymarket(m) for m in data],
            metadata={},
        )

    async def fetch_question(self, id: str) -> Response[Question]:
        data = await self._safe_get(self.BASE_URL / "events" / id, {})
        return Response(data=Question.from_polymarket(data), metadata={})

    async def fetch_questions(self, **kwargs: Any) -> Response[list[Question]]:
        params = clean_params(**kwargs)
        data = await self._safe_get(self.BASE_URL / "events", params)
        return Response(
            data=[Question.from_polymarket(event) for event in data],
            metadata={},
        )


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
