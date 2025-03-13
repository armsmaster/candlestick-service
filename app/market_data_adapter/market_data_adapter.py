import asyncio
import aiohttp
from urllib.parse import urlencode
from pytz import timezone


from app.core.date_time import Timestamp
from app.core.entities import Candle, Security
from app.core.market_data_adapter import (
    IMarketDataAdapter,
    MarketDataRequest,
    MarketDataAdapterException,
)
import app.market_data_adapter.constants as constants


class MarketDataAdapter(IMarketDataAdapter):

    API = constants.API
    ENGINE = constants.ENGINE
    MARKETS = constants.MARKETS
    INTERVALS = constants.INTERVALS

    def __init__(self):
        pass

    def _init(self, request: MarketDataRequest) -> None:
        self.ticker = request.ticker
        self.board = request.board
        self.time_from = request.time_from
        self.time_till = request.time_till
        self.timeframe = request.timeframe
        self._candles: list[Candle] = []
        self._init_market()
        self._init_interval()
        self._init_security()

    @property
    def candles(self) -> list[Candle]:
        return self._candles

    @candles.setter
    def candles(self, values: list[Candle]) -> None:
        self._candles = values
        self._candles.sort(key=lambda x: x.timestamp)

    def _init_market(self):
        try:
            self.market = self.MARKETS[self.board]
        except KeyError:
            raise MarketDataAdapterException(f"Board '{self.board}' not supported.")

    def _init_interval(self):
        try:
            self.interval = self.INTERVALS[self.timeframe]
        except KeyError:
            raise MarketDataAdapterException(
                f"Timeframe '{self.timeframe}' not supported."
            )

    def _init_security(self):
        self.security = Security(ticker=self.ticker, board=self.board)

    async def load(self, request: MarketDataRequest):
        self._init(request)
        self.candles_set = set()
        queue = asyncio.Queue()
        n_consumers = constants.N_CONSUMERS
        consumers = [
            asyncio.create_task(self._consume(queue)) for _ in range(n_consumers)
        ]
        await self._produce(queue)
        await queue.join()
        for consumer in consumers:
            consumer.cancel()

        candles = list(self.candles_set)
        self.candles += candles

    async def _produce(self, queue: asyncio.Queue):
        i = 0
        while True:
            url = self._generate_url(index=i)
            data = await self._request_get(url)
            columns, rows = data["candles"]["columns"], data["candles"]["data"]
            if not rows:
                break
            await queue.put((columns, rows))
            i += 100

    async def _consume(self, queue: asyncio.Queue):
        while True:
            columns, rows = await queue.get()
            candles = self._process_rows(columns, rows)
            self.candles_set.update(candles)
            queue.task_done()

    async def _request_get(self, url: str) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url) as resp:
                response_json = await resp.json()
                return response_json

    def _generate_url(self, index: int) -> str:
        url = "{a}/iss/{e}/{m}/{b}/{t}/candles.json".format(
            a=self.API,
            e=f"engines/{self.ENGINE}",
            m=f"markets/{self.market}",
            b=f"boards/{self.board}",
            t=f"securities/{self.ticker}",
        )
        params = {
            "from": self.time_from,
            "till": self.time_till,
            "iss.reverse": "true",
            "interval": self.interval,
            "start": index,
        }
        url += "?" + urlencode(params)
        return url

    def _process_rows(self, columns: list[str], data: list[list]) -> list[Candle]:
        mapping = {c: idx for idx, c in enumerate(columns)}
        return [self._process_row(mapping, item) for item in data]

    def _process_row(self, mapping: dict[str, int], data: list) -> Candle:
        timestamp_str: str = data[mapping["begin"]]
        return Candle(
            security=self.security,
            timeframe=self.timeframe,
            timestamp=Timestamp(timestamp=timestamp_str, tz="Europe/Moscow"),
            open=data[mapping["open"]],
            high=data[mapping["high"]],
            low=data[mapping["low"]],
            close=data[mapping["close"]],
        )
