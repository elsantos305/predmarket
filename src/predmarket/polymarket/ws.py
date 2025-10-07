from predmarket.model.ws import normalize_message
from predmarket.model.ws.exchange import BaseWebSocket
import websockets, json
from contextlib import asynccontextmanager


class PolymarketWS:
    URL = "wss://ws-subscriptions-clob.polymarket.com/ws/market"

    def __init__(self, websocket: websockets.ClientConnection):
        self.socket = websocket

    async def stream(self, ids: list[str]):
        await self.socket.send(json.dumps({"assets_ids": ids, "type": "market"}))

        async for msg in self.socket:
            data = json.loads(msg)
            if not isinstance(data, list):
                data = [data]

            for row in data:
                yield normalize_message(row, source="polymarket")

    @classmethod
    @asynccontextmanager
    async def connect(cls):
        async with websockets.connect(
            "wss://ws-subscriptions-clob.polymarket.com/ws/market"
        ) as socket:
            yield socket
