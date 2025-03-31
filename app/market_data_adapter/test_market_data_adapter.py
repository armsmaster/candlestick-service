import asyncio

import pytest

from app.core.date_time import Timestamp
from app.core.entities import CandleData, Security, Timeframe
from app.market_data_adapter.market_data_adapter import (
    MarketDataAdapter,
    MarketDataRequest,
)

pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_market_data_adapter_mono():
    request = MarketDataRequest(
        security=Security(ticker="SBER", board="TQBR"),
        timeframe=Timeframe.H1,
        time_from=Timestamp("2024-12-17"),
        time_till=Timestamp("2025-02-17"),
    )
    adapter = MarketDataAdapter()
    candles = await adapter.load(request=request)
    assert isinstance(candles, list)
    assert len(candles) == 674
    assert isinstance(candles[0], CandleData)


@pytest.mark.asyncio
async def test_market_data_adapter_concurrent():
    requests = [
        MarketDataRequest(
            security=Security(ticker="SBER", board="TQBR"),
            timeframe=Timeframe.H1,
            time_from=Timestamp("2024-12-17"),
            time_till=Timestamp("2025-02-17"),
        ),
        MarketDataRequest(
            security=Security(ticker="GAZP", board="TQBR"),
            timeframe=Timeframe.H1,
            time_from=Timestamp("2024-12-17"),
            time_till=Timestamp("2025-02-17"),
        ),
        MarketDataRequest(
            security=Security(ticker="LKOH", board="TQBR"),
            timeframe=Timeframe.H1,
            time_from=Timestamp("2024-12-17"),
            time_till=Timestamp("2025-02-17"),
        ),
    ]
    adapters = [MarketDataAdapter() for _ in requests]
    candles = await asyncio.gather(
        *[adapter.load(request) for adapter, request in zip(adapters, requests)]
    )
    assert isinstance(candles[0][0], CandleData)
    assert isinstance(candles[1][0], CandleData)
    assert isinstance(candles[2][0], CandleData)
    assert len(candles[0]) == 674
    assert len(candles[1]) == 674
