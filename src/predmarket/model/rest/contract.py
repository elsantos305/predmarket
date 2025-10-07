from pydantic import BaseModel, ConfigDict
from typing import Any
import json


class Contract(BaseModel):
    """Normalized market contract."""

    id: str
    platform: str
    question: str
    raw: dict[str, Any]
    outcomes: list[str]
    model_config = ConfigDict(extra="allow")

    @classmethod
    def from_polymarket(cls, market: dict[str, Any]) -> "Contract":
        overrides = {
            "id": market.get("id"),
            "platform": "polymarket",
            "question": market.get("question"),
            "outcomes": json.loads(market.get("outcomes", "[]")),
            "raw": market,
        }
        return cls(**{**market, **overrides})  # pyright: ignore

    @classmethod
    def from_kalshi(cls, market: dict[str, Any]) -> "Contract":
        overrides = {
            "id": market.get("ticker"),
            "platform": "kalshi",
            "question": market.get("title"),
            "outcomes": ["Yes", "No"],
            "raw": market,
        }
        return cls(**{**market, **overrides})  # pyright: ignore
