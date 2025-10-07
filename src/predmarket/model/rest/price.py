from pydantic import BaseModel
from typing import Any


class Price(BaseModel):
    """Normalized price of a contract."""

    bid: float
    ask: float
    price: float
    volume: float
    liquidity: float

    @classmethod
    def from_kalshi(cls, market: dict[str, Any]) -> "Price":
        override = {
            "price": market.get("last_price"),
            "ask": market.get("yes_ask"),
            "bid": market.get("yes_bid"),
            "volume": market.get("volume"),
            "liquidity": market.get("liquidity"),
        }
        return cls(**override)  # pyright: ignore

    @classmethod
    def from_polymarket(cls, market: dict[str, Any]) -> "Price":
        override = {
            "price": market.get("lastTradePrice"),
            "ask": market.get("bestAsk"),
            "bid": market.get("bestBid"),
            "volume": market.get("volume"),
            "liquidity": market.get("liquidity"),
        }

        return cls(**override)  # pyright: ignore
