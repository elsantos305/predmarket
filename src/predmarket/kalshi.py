from __future__ import annotations
from yarl import URL
from predmarket.model.rest import (
    Response,
    Price,
    Contract,
    BaseExchangeClient,
    Question,
    clean_params,
)


class KalshiExchange(BaseExchangeClient):
    """Kalshi-specific implementation."""

    BASE_URL = URL("https://api.elections.kalshi.com/trade-api/v2/")

    async def fetch_price(self, id: str) -> Response[Price]:
        data = await self._safe_get(self.BASE_URL / "markets" / id, {})
        return Response(data=Price.from_kalshi(data["market"]), metadata={})

    async def fetch_contract(self, id: str) -> Response[Contract]:
        data = await self._safe_get(self.BASE_URL / "markets" / id, {})
        return Response(data=Contract.from_kalshi(data["market"]), metadata={})

    async def fetch_contracts(self, **kwargs) -> Response[list[Contract]]:
        params = clean_params(**kwargs)
        data = await self._safe_get(self.BASE_URL / "markets", params)
        return Response(
            data=[Contract.from_kalshi(m) for m in data.get("markets", [])],
            metadata={"cursor": data.get("cursor")},
        )

    async def fetch_question(self, id: str) -> Response[Question]:
        data = await self._safe_get(self.BASE_URL / "events" / id, {})
        return Response(data=Question.from_kalshi(data["event"]), metadata={})

    async def fetch_questions(self, **kwargs) -> Response[list[Question]]:
        params = clean_params(**kwargs)
        data = await self._safe_get(self.BASE_URL / "events", params)
        return Response(
            data=[Question.from_kalshi(event) for event in data.get("events", [])],
            metadata={"cursor": data.get("cursor")},
        )
