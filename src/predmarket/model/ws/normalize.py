from typing import List, Literal, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class Exchange(str, Enum):
    POLYMARKET = "polymarket"
    KALSHI = "kalshi"


class Side(str, Enum):
    BUY = "buy"
    SELL = "sell"
    YES = "yes"
    NO = "no"


class PriceLevel(BaseModel):
    price: float = Field(..., description="Price in USD (or cents normalized to USD).")
    size: float = Field(..., description="Quantity available at this price level.")
    side: Optional[Side] = None


class BookSnapshot(BaseModel):
    exchange: Exchange
    market_id: str
    bids: List[PriceLevel]
    asks: List[PriceLevel]
    timestamp: Optional[datetime] = None


class BookDelta(BaseModel):
    exchange: Exchange
    market_id: str
    deltas: List[PriceLevel]
    timestamp: Optional[datetime] = None


class Trade(BaseModel):
    exchange: Exchange
    market_id: str
    price: float
    size: float
    side: Side
    taker_side: Optional[Side] = None
    timestamp: Optional[datetime] = None


class Ticker(BaseModel):
    exchange: Exchange
    market_id: str
    last_price: Optional[float] = None
    best_bid: Optional[float] = None
    best_ask: Optional[float] = None
    volume: Optional[float] = None
    open_interest: Optional[float] = None
    timestamp: Optional[datetime] = None


UnifiedModel = Union[BookSnapshot, BookDelta, Trade, Ticker]


class PolymarketParser:
    """Parses Polymarket WS messages into unified models."""

    @staticmethod
    def parse(msg: dict) -> Optional[UnifiedModel]:
        et = msg.get("event_type")
        ts = (
            datetime.fromtimestamp(int(msg.get("timestamp", 0)) / 1000)
            if msg.get("timestamp")
            else None
        )
        market_id = msg.get("market") or msg.get("condition_id") or msg.get("asset_id")

        if et == "book":
            bids = [
                PriceLevel(
                    price=float(x["price"]), size=float(x["size"]), side=Side.BUY
                )
                for x in msg.get("bids", [])
            ]
            asks = [
                PriceLevel(
                    price=float(x["price"]), size=float(x["size"]), side=Side.SELL
                )
                for x in msg.get("asks", [])
            ]
            return BookSnapshot(
                exchange=Exchange.POLYMARKET,
                market_id=market_id,
                bids=bids,
                asks=asks,
                timestamp=ts,
            )

        elif et == "price_change":
            deltas = []
            for pc in msg.get("price_changes", []):
                side = Side.BUY if pc.get("side") == "BUY" else Side.SELL
                deltas.append(
                    PriceLevel(
                        price=float(pc["price"]), size=float(pc["size"]), side=side
                    )
                )
            return BookDelta(
                exchange=Exchange.POLYMARKET,
                market_id=market_id,
                deltas=deltas,
                timestamp=ts,
            )

        elif et == "last_trade_price":
            return Trade(
                exchange=Exchange.POLYMARKET,
                market_id=market_id,
                price=float(msg.get("price")),
                size=float(msg.get("size", 0)),
                side=Side.BUY if msg.get("side") == "BUY" else Side.SELL,
                timestamp=ts,
            )

        return None


class KalshiParser:
    """Parses Kalshi WS messages into unified models."""

    @staticmethod
    def parse(msg: dict) -> Optional[UnifiedModel]:
        t = msg.get("type")
        data = msg.get("msg") or msg.get("data") or {}
        ts = None
        if "ts" in data:
            # Kalshi timestamps are typically ISO strings
            try:
                ts = datetime.fromisoformat(data["ts"].replace("Z", "+00:00"))
            except Exception:
                pass
        market_id = data.get("market_ticker")

        if t == "orderbook_snapshot":
            bids_yes = [
                PriceLevel(price=x[0] / 100.0, size=x[1], side=Side.YES)
                for x in data.get("yes", [])
            ]
            bids_no = [
                PriceLevel(price=x[0] / 100.0, size=x[1], side=Side.NO)
                for x in data.get("no", [])
            ]
            return BookSnapshot(
                exchange=Exchange.KALSHI,
                market_id=market_id,
                bids=bids_yes,
                asks=bids_no,
                timestamp=ts,
            )

        elif t == "orderbook_delta":
            deltas = []
            for side in ("yes", "no"):
                for d in data.get(side, []):
                    deltas.append(
                        PriceLevel(
                            price=d[0] / 100.0,
                            size=d[1],
                            side=Side.YES if side == "yes" else Side.NO,
                        )
                    )
            return BookDelta(
                exchange=Exchange.KALSHI,
                market_id=market_id,
                deltas=deltas,
                timestamp=ts,
            )

        elif t == "trade":
            return Trade(
                exchange=Exchange.KALSHI,
                market_id=market_id,
                price=float(data.get("yes_price", 0)) / 100.0,
                size=float(data.get("count", 0)),
                taker_side=Side.YES if data.get("taker_side") == "yes" else Side.NO,
                side=Side.YES if data.get("taker_side") == "yes" else Side.NO,
                timestamp=ts,
            )

        elif t == "ticker":
            return Ticker(
                exchange=Exchange.KALSHI,
                market_id=market_id,
                last_price=(data.get("price", 0) / 100.0)
                if data.get("price")
                else None,
                best_bid=(data.get("yes_bid", 0) / 100.0)
                if data.get("yes_bid")
                else None,
                best_ask=(data.get("yes_ask", 0) / 100.0)
                if data.get("yes_ask")
                else None,
                volume=float(data.get("volume", 0)) if data.get("volume") else None,
                open_interest=float(data.get("open_interest", 0))
                if data.get("open_interest")
                else None,
                timestamp=ts,
            )

        return None


def normalize_message(
    msg: dict, source: Literal["polymarket", "kalshi"]
) -> Optional[UnifiedModel]:
    """Normalize any raw message from either source into a unified Pydantic model."""
    if source == "polymarket":
        return PolymarketParser.parse(msg)
    elif source == "kalshi":
        return KalshiParser.parse(msg)
    else:
        raise ValueError(f"Unknown source: {source}")
