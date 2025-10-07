from pydantic import BaseModel
import datetime
from typing import Any


class Element(BaseModel):
    price: float
    size: float

    @classmethod
    def from_polymarket(cls, data: dict[str, Any]):
        return cls(price=data["price"], size=data["size"])


class Book(BaseModel):
    asks: list[Element]
    bids: list[Element]
    timestamp: datetime.datetime

    @classmethod
    def from_polymarket(cls, data: dict[str, Any]):
        return cls(
            asks=[Element.from_polymarket(e) for e in data["asks"]],
            bids=[Element.from_polymarket(e) for e in data["bids"]],
            timestamp=data["timestamp"],
        )
