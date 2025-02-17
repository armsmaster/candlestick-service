import asyncio
import aiohttp
from urllib.parse import urlencode

from app.core.date_time import Timestamp
from app.core.entities import Timeframe, Candle, Security
from app.core.market_data_adapter import (
    IMarketDataAdapter,
    MarketDataRequest,
    MarketDataAdapterException,
)


class MarketDataAdapter(IMarketDataAdapter):

    API = "https://iss.moex.com"
    ENGINE = "stock"
    MARKETS = {
        "TQBR": "shares",
        "TQOB": "bonds",
        "TQCB": "bonds",
    }
    INTERVALS = {
        Timeframe.M1: "1",
        Timeframe.M10: "10",
        Timeframe.H1: "60",
    }

    def __init__(self, request: MarketDataRequest):
        self.ticker = request.ticker
        self.board = request.board
        self.time_from = request.time_from
        self.time_till = request.time_till
        self.timeframe = request.timeframe
        self.init_market()
        self.init_interval()
        self.security = Security(ticker=self.ticker, board=self.board)

    def init_market(self):
        try:
            self.market = self.MARKETS[self.board]
        except KeyError:
            raise MarketDataAdapterException(f"Board '{self.board}' not supported.")

    def init_interval(self):
        try:
            self.interval = self.INTERVALS[self.timeframe]
        except KeyError:
            raise MarketDataAdapterException(
                f"Timeframe '{self.timeframe}' not supported."
            )

    def load(self) -> list[Candle]:
        x = asyncio.run(self.work())
        return x

    async def work(self) -> list[Candle]:
        i = 0
        out = {}
        while True:
            url = self.get_url(index=i)
            data = await self.request_get(url)
            columns = data["candles"]["columns"]
            rows = data["candles"]["data"]
            if not rows:
                break
            candles = self.process_rows(columns, rows)
            out.update({candle.timestamp: candle for candle in candles})
            i += 100
        return sorted(list(out.values()), key=lambda x: x.timestamp)

    async def request_get(self, url: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url) as resp:
                response_json = await resp.json()
                return response_json

    def get_url(self, index: int):
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

    def process_rows(self, columns: list[str], data: list[list]):
        mapping = {c: idx for idx, c in enumerate(columns)}
        return [self.process_row(mapping, item) for item in data]

    def process_row(self, mapping: dict[str, int], data: list):
        return Candle(
            security=self.security,
            timeframe=self.timeframe,
            timestamp=Timestamp(data[mapping["begin"]]),
            open=data[mapping["open"]],
            high=data[mapping["high"]],
            low=data[mapping["low"]],
            close=data[mapping["close"]],
        )
