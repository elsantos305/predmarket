from predmarket import PredMarket
import asyncio, httpx


async def main():
    async with httpx.AsyncClient() as c:
        kalshi = PredMarket(c, exchange="kalshi")
        data = await kalshi.fetch_questions()
        print(data.data[0])


asyncio.run(main())
