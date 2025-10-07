from pydantic import BaseModel
from typing import Any


class Price(BaseModel):
    """Normalized price of a contract."""

    bid: float | None = None
    ask: float | None = None
    price: float | None = None
    volume: float | None = None
    liquidity: float | None = None

    @staticmethod
    def _coerce(value: Any) -> float | None:
        """Best-effort float conversion that tolerates missing values."""
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @classmethod
    def from_kalshi(cls, market: dict[str, Any]) -> "Price":
        return cls(
            price=cls._coerce(market.get("last_price")),
            ask=cls._coerce(market.get("yes_ask")),
            bid=cls._coerce(market.get("yes_bid")),
            volume=cls._coerce(market.get("volume")),
            liquidity=cls._coerce(market.get("liquidity")),
        )

    @classmethod
    def from_polymarket(cls, market: dict[str, Any]) -> "Price":
        return cls(
            price=cls._coerce(market.get("lastTradePrice")),
            ask=cls._coerce(market.get("bestAsk")),
            bid=cls._coerce(market.get("bestBid")),
            volume=cls._coerce(market.get("volume")),
            liquidity=cls._coerce(market.get("liquidity")),
        )
