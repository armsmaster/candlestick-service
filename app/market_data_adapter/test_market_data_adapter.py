import pytest
import asyncio

from app.core.date_time import Timestamp
from app.core.entities import Timeframe, Candle
from app.market_data_adapter.market_data_adapter import (
    MarketDataAdapter,
    MarketDataRequest,
    MarketDataAdapterException,
)

pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_market_data_adapter_mono():
    request = MarketDataRequest(
        ticker="SBER",
        board="TQBR",
        timeframe=Timeframe.H1,
        time_from=Timestamp("2024-12-17"),
        time_till=Timestamp("2025-02-17"),
    )
    adapter = MarketDataAdapter()
    await adapter.load(request=request)
    candles = adapter.candles
    assert isinstance(candles, list)
    assert len(candles) == 674
    assert isinstance(candles[0], Candle)


@pytest.mark.asyncio
async def test_market_data_adapter_concurrent():
    requests = [
        MarketDataRequest(
            ticker="SBER",
            board="TQBR",
            timeframe=Timeframe.H1,
            time_from=Timestamp("2024-12-17"),
            time_till=Timestamp("2025-02-17"),
        ),
        MarketDataRequest(
            ticker="GAZP",
            board="TQBR",
            timeframe=Timeframe.H1,
            time_from=Timestamp("2024-12-17"),
            time_till=Timestamp("2025-02-17"),
        ),
        MarketDataRequest(
            ticker="LKOH",
            board="TQBR",
            timeframe=Timeframe.H1,
            time_from=Timestamp("2024-12-17"),
            time_till=Timestamp("2025-02-17"),
        ),
    ]
    adapters = [MarketDataAdapter() for _ in requests]
    await asyncio.gather(
        *[adapter.load(request) for adapter, request in zip(adapters, requests)]
    )
    assert isinstance(adapters[0].candles[0], Candle)
    assert isinstance(adapters[1].candles[0], Candle)
    assert isinstance(adapters[2].candles[0], Candle)
    assert len(adapters[0].candles) == 674
    assert len(adapters[1].candles) == 674
