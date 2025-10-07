from predmarket.model.rest import (
    Response,
    Price,
    Contract,
    BaseExchangeClient,
    Question,
    clean_params,
)
from typing import Any
from yarl import URL


class PolymarketRest(BaseExchangeClient):
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
