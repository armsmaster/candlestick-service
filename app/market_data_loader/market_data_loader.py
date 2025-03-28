"""Market Data Loader implementation."""

import asyncio

from app.core.entities import CandleSpan, Security, Timeframe
from app.core.market_data_adapter import IMarketDataAdapter, MarketDataRequest
from app.core.market_data_loader import IMarketDataLoader, MarketDataLoaderRequest
from app.core.repository.candle_repository import ICandleRepository
from app.core.repository.candle_span_repository import ICandleSpanRepository
from app.core.repository.security_repository import ISecurityRepository
from app.core.unit_of_work import IUnitOfWork
from app.dependency import get_logger
from app.market_data_loader.range_operations import Range, rangediff, rangemerge

logger = get_logger()


class MarketDataLoader(IMarketDataLoader):
    """Market Data Loader."""

    def __init__(
        self,
        market_data_adapter: IMarketDataAdapter,
        security_repository: ISecurityRepository,
        candle_repository: ICandleRepository,
        candle_span_repository: ICandleSpanRepository,
        unit_of_work: IUnitOfWork,
    ):
        """Initialize."""
        self.market_data_adapter = market_data_adapter
        self.security_repository = security_repository
        self.candle_repository = candle_repository
        self.candle_span_repository = candle_span_repository
        self.unit_of_work = unit_of_work

    async def load_candles(self, request: MarketDataLoaderRequest) -> None:
        """Load candles."""
        request_batches = await self._construct_batches(request)
        logger.debug("MarketDataLoader.load_candles", n_batches=len(request_batches))
        if not request_batches:
            return
        await asyncio.gather(*[self._load_batch(rb) for rb in request_batches])
        candles = self.market_data_adapter.candles
        async with self.unit_of_work:
            await self.candle_repository.add(candles)
            await self._update_candle_spans(
                request.security,
                request.timeframe,
                request_batches,
            )

    async def _construct_batches(
        self,
        request: MarketDataLoaderRequest,
    ) -> list[MarketDataLoaderRequest]:
        """Split request into batches to exclude loading data already present in DB."""
        repo = self.candle_span_repository.filter_by_security(
            request.security
        ).filter_by_timeframe(request.timeframe)
        candle_spans: list[CandleSpan] = [
            span_record.entity async for span_record in repo
        ]
        range_batches = rangediff(
            remove_from=Range(request.time_from, request.time_till),
            remove_what=[Range(cs.date_from, cs.date_till) for cs in candle_spans],
        )
        request_batches = [
            MarketDataLoaderRequest(
                security=request.security,
                timeframe=request.timeframe,
                time_from=rng.left,
                time_till=rng.right,
            )
            for rng in range_batches
        ]
        return request_batches

    async def _update_candle_spans(
        self,
        security: Security,
        timeframe: Timeframe,
        batches: list[MarketDataLoaderRequest],
    ):
        """
        Update stored time spans.

        Time spans represent periods, for which candles are stored in DB.
        """
        repo = self.candle_span_repository
        repo = repo.filter_by_security(security).filter_by_timeframe(timeframe)
        span_records = [span_record async for span_record in repo]

        ranges = [
            *[Range(sr.entity.date_from, sr.entity.date_till) for sr in span_records],
            *[Range(b.time_from, b.time_till) for b in batches],
        ]
        merged_ranges = rangemerge(ranges)
        updated_spans = [
            CandleSpan(
                security=security,
                timeframe=timeframe,
                date_from=rng.left,
                date_till=rng.right,
            )
            for rng in merged_ranges
        ]
        await self.candle_span_repository.remove(span_records)
        await self.candle_span_repository.add(updated_spans)

    async def _load_batch(self, request: MarketDataLoaderRequest) -> None:
        """Load market data."""
        logger.debug("MarketDataLoader._load_batch", request=str(request))
        md_request = MarketDataRequest(
            board=request.security.board,
            ticker=request.security.ticker,
            timeframe=request.timeframe,
            time_from=request.time_from,
            time_till=request.time_till,
        )
        await self.market_data_adapter.load(md_request)
        logger.debug("MarketDataLoader._load_batch finished")
