# A Unified SDK for Prediction Markets

### Check out [The Odds Company](https://github.com/orgs/the-odds-company/repositories) for similar projects

`predmarket` is an `asyncio`-native Python-based library that communicates directly with prediction markets (Kalshi and Polymarket).

Both Kalshi and Polymarket provide public-facing APIs with high rate limits. `predmarket` aims to unify these two APIs into one install, one format, and one library to learn. The goal to be abstract enough to be intuitive, but not lose **any** power of the individual APIs.

Currently, Websocket support is under development. A working implementation of Polymarket's CLOB WS API is available, while Kalshi's is still being developed.

## Install
```uv add predmarket ```
or
`pip install predmarket`

## Basic Usage

### REST
```python
from predmarket import KalshiRest, PolymarketRest
from httpx import AsyncClient

async def main()
    async with AsyncClient() as client:

        # Initialize fetchers. Each with exact same public-facing API.
        kalshi = KalshiRest(client)
        polymarket = PolymarketRest(client)

        # Fetch available Questions (e.g. "When will Elon Musk get to Mars?", known as events in native API)
        kalshi_questions = await kalshi.fetch_questions()
        polymarket_questions = await polymarket.fetch_questions(limit=10, asc=True) # Polymarket-specific query params

        # Fetch available Contracts  (e.g. "Will Elon Musk get to Mars before 2026?", these are individual "solutions" for a given question , Markets in native APIs)
        kalshi_contracts = await kalshi.fetch_contracts()
        polymarket_contracts = await polymarket.fetch_contracts() # Polymarket-specific query params
```
### WS
```python
from predmarket import PolymarktWS # Kalshi is NOT currently supported, but will be very solutions

async def main():
    async with PolymarketWS.connect() as socket:
        polymarket = PolymarketWS(socket)
        for row in polymarket.stream(["AB.....XYZ"]): # Example of fetching real markets later in docs
            print(row) # Row is a pydantic model. Autocomplete!


```
## More Information
`predmarket` is under rapid development. Expect breaking changes unless indiciated otherwise.
