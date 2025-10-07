from pydantic import BaseModel, ConfigDict
from typing import Any


class Question(BaseModel):
    """Normalized event/question across exchanges."""

    id: str
    platform: str
    title: str | None = None
    raw: dict[str, Any]
    model_config = ConfigDict(extra="allow")

    @classmethod
    def from_polymarket(cls, event: dict[str, Any]) -> "Question":
        overrides = {
            "id": event.get("id"),
            "platform": "polymarket",
            "title": event.get("title") or event.get("question"),
            "raw": event,
        }
        return cls(**{**event, **overrides})  # pyright: ignore

    @classmethod
    def from_kalshi(cls, event: dict[str, Any]) -> "Question":
        overrides = {
            "id": event.get("event_ticker"),
            "platform": "kalshi",
            "title": event.get("title"),
            "raw": event,
        }
        return cls(**{**event, **overrides})  # pyright: ignore
