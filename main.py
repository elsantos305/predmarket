from predmarket.polymarket.ws import PolymarketWS
from predmarket.polymarket.rest import PolymarketRest
import asyncio, httpx, json


async def main():
    async with httpx.AsyncClient() as h:
        polymarket = PolymarketRest(h)
        markets = await polymarket.fetch_contracts(offset=113000)
        markets = [json.loads(d.raw["clobTokenIds"])[0] for d in markets.data][:10]
        async with PolymarketWS.connect() as c:
            pm = PolymarketWS(c)
            async for d in pm.stream(markets):
                print(d)


asyncio.run(main())
