# A Unified SDK for Prediction Markets

`predmarket` is an asyncio-native python-based SDK that communicates directly with prediction markets (Kalshi and Polymarket).

Both Kalshi and Polymarket provide public-facing APIs with high rate limits. `predmarket` aims to unify these two APIs into one install, one format, and one library to learn. It aims to be abstract enough to be intuitive, but not lose **any** power of the individual APIs. So, any parameter in one of polymarket's API endpoints can be used as-is in `predmarket`.

## Install
```uv add predmarket ```


## Basic Usage

```python
from predmarket import PredMarket
from httpx import AsyncClient

async def main()
    async with AsyncClient() as client:

        # Initialize fetchers
        kalshi = PredMarket(client, exchange="kalshi")
        polymarket = PredMarket(client, exchange="polymarket")

        # Fetch available Questions (e.g. "When will Elon Musk get to Mars?", events in native APIs)
        kalshi_questions = await kalshi.fetch_questions()
        polymarket_questions = await polymarket.fetch_questions(limit=10, asc=True) # Polymarket-specific query params

        # Fetch available Contracts  (e.g. "Will Elon Musk get to Mars before 2026?", these are individual "solutions" for a given question , Markets in native APIs)
        kalshi_contracts = await kalshi.fetch_contracts()
        polymarket_contracts = await polymarket.fetch_contracts() # Polymarket-specific query params
```

## More Information
`predmarket` is under rapid development. Expect breaking changes unless indiciated otherwise.
