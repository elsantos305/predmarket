# pip install websocket-client
import websockets
import json, asyncio

URL = "wss://ws-subscriptions-clob.polymarket.com"
ASSET_IDS = [
    "54088820318860171325228999484169921733046853829074459287504241672407038712534"
]


async def main():
    async with websockets.connect(f"{URL}/ws/market") as socket:
        await socket.send(json.dumps({"assets_ids": ASSET_IDS, "type": "market"}))

        async for msg in socket:
            print(msg)


asyncio.run(main())
