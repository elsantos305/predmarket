from predmarket.model.ws.book import Book, Element
from predmarket.model.ws.exchange import BaseWebSocket
import websockets, json


class PolymarketWS:
    URL = "wss://ws-subscriptions-clob.polymarket.com/ws/market"

    def __init__(self, websocket: websockets.ClientConnection):
        self.socket = websocket

    async def stream_book(self, ids: list[str]):
        await self.socket.send(json.dumps({"assets_ids": ids, "type": "market"}))

        async for msg in self.socket:
            data = json.loads(msg)
            yield Book.from_polymarket(data)
