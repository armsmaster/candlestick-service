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
    adapter = MarketDataAdapter(request=request)
    candles = await adapter.load()
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
    adapters = [MarketDataAdapter(request=request) for request in requests]
    candles_lists = await asyncio.gather(*[adapter.load() for adapter in adapters])
    assert isinstance(candles_lists, list)
    assert len(candles_lists) == len(requests)
    assert isinstance(candles_lists[0], list)
    assert isinstance(candles_lists[0][0], Candle)
    assert isinstance(candles_lists[1][0], Candle)
    assert len(candles_lists[0]) == 674
    assert len(candles_lists[1]) == 674
