import asyncio

from app.core.market_data_loader import IMarketDataLoader, MarketDataLoaderRequest
from app.core.market_data_adapter import IMarketDataAdapter

from app.core.date_time import Timestamp
from app.core.entities import Security, Candle, CandleSpan, Timeframe
from app.core.unit_of_work import IUnitOfWork
from app.core.repository.security_repository import ISecurityRepository
from app.core.repository.candle_repository import ICandleRepository
from app.core.repository.candle_span_repository import ICandleSpanRepository
from app.market_data_loader.rangediff import Range, rangediff


class MarketDataLoader(IMarketDataLoader):

    def __init__(
        self,
        market_data_adapter: IMarketDataAdapter,
        security_repository: ISecurityRepository,
        candle_repository: ICandleRepository,
        candle_span_repository: ICandleSpanRepository,
        unit_of_work: IUnitOfWork,
    ):
        self.market_data_adapter = market_data_adapter
        self.security_repository = security_repository
        self.candle_repository = candle_repository
        self.candle_span_repository = candle_span_repository
        self.unit_of_work = unit_of_work

    async def load_candles(self, request: MarketDataLoaderRequest) -> None:
        request_batches = self._construct_batches(request)
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
        repo = self.candle_span_repository.filter_by_security(
            security
        ).filter_by_timeframe(timeframe)
        span_records = [span_record async for span_record in repo]
        ranges = [
            Range(record.entity.date_from, record.entity.date_till)
            for record in span_records
        ] + [Range(b.time_from, b.time_till) for b in batches]
        ranges.sort(key=lambda x: x.left)
        prev = None
        updated_ranges = []
        for rng in ranges:
            if prev is None:
                updated_ranges += [rng]
                prev = rng
                continue
            if rng.left == prev.right or rng.left == prev.right + 1:
                updated_ranges[-1].right = rng.right
                continue
        updated_spans = [
            CandleSpan(
                security=security,
                timeframe=timeframe,
                date_from=rng.left,
                date_till=rng.right,
            )
            for rng in updated_ranges
        ]
        self.candle_span_repository.remove(span_records)
        self.candle_repository.add(updated_spans)

    async def _load_batch(self, request: MarketDataLoaderRequest) -> None:
        await self.market_data_adapter.load(request)
