from __future__ import annotations
from yarl import URL
from .models import (
    BaseExchangeClient,
    Response,
    Price,
    Contract,
    Question,
    KalshiStatus,
    Param,
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
