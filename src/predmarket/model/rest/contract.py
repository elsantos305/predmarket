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

    @staticmethod
    def _normalize_outcomes(value: Any) -> list[str]:
        """Polymarket sometimes delivers outcomes as JSON strings."""
        if isinstance(value, list):
            return [str(item) for item in value]
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
            except json.JSONDecodeError:
                return [value]
            if isinstance(parsed, list):
                return [str(item) for item in parsed]
            return [value]
        return []

    @classmethod
    def from_polymarket(cls, market: dict[str, Any]) -> "Contract":
        overrides = {
            "id": market.get("id"),
            "platform": "polymarket",
            "question": market.get("question"),
            "outcomes": cls._normalize_outcomes(market.get("outcomes")),
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
