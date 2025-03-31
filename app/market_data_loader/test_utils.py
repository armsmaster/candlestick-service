from datetime import timedelta

from app.core.date_time import Timestamp
from app.core.entities import Candle, Timeframe
from app.core.market_data_adapter import IMarketDataAdapter, MarketDataRequest
from app.core.repository.candle_repository import ICandleRepository
from app.core.repository.candle_span_repository import ICandleSpanRepository
from app.core.repository.security_repository import ISecurityRepository
from app.core.unit_of_work import IUnitOfWork
from app.repository.json_repository.candle_repo import CandleRepository
from app.repository.json_repository.candle_span_repo import CandleSpanRepository
from app.repository.json_repository.security_repo import SecurityRepository


class FakeMarketDataAdapter(IMarketDataAdapter):

    n_minutes = 60 * 9
    n_hours = 9

    def __init__(self):
        pass

    async def load(self, request: MarketDataRequest):
        self.request = request
        return self._generate_candles()

    @property
    def candles(self) -> list[Candle]:
        return self._candles

    def _generate_candles(self) -> list[Candle]:
        t = Timestamp(f"{str(self.request.time_from.date())} 10:00:00+03:00")
        out: list[Candle] = []
        while Timestamp(t.date()) < self.request.time_till + 1:

            candle = Candle(
                security=self.request.security,
                timeframe=self.request.timeframe,
                timestamp=t,
                open=100,
                high=100,
                low=100,
                close=100,
            )
            out.append(candle)

            match self.request.timeframe:
                case Timeframe.M1:
                    t = Timestamp(t.dt + timedelta(minutes=1))
                case Timeframe.M10:
                    t = Timestamp(t.dt + timedelta(minutes=10))
                case Timeframe.H1:
                    t = Timestamp(t.dt + timedelta(minutes=60))

            tmax = Timestamp(f"{str(t.date())} 18:00:00+03:00")
            if t > tmax:
                t = Timestamp(f"{str((t + 1).date())} 10:00:00+03:00")

        return out


class UOW(IUnitOfWork):

    def __init__(self):
        pass

    async def __aenter__(self):
        pass

    async def __aexit__(self, exc_type, exc_val, traceback) -> bool:
        pass

    async def commit(self):
        pass

    async def rollback(self):
        pass


def security_repository_factory() -> ISecurityRepository:
    return SecurityRepository()


def candle_repository_factory() -> ICandleRepository:
    return CandleRepository()


def candle_span_repository_factory() -> ICandleSpanRepository:
    return CandleSpanRepository()
