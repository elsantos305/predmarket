from predmarket import PredMarket
import asyncio, httpx


async def main():
    async with httpx.AsyncClient() as c:
        kalshi = PredMarket(c, exchange="kalshi")
        await kalshi.fetch_questions()


asyncio.run(main())
