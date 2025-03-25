"""CLI commands."""

from app.io.cli.dependency import (
    candle_repository_factory,
    candle_span_repository_factory,
    connection_factory,
    market_data_adapter_factory,
    security_repository_factory,
    unit_of_work_factory,
)
from app.market_data_loader.market_data_loader import MarketDataLoader
from app.use_cases.create_security import CreateSecurity, CreateSecurityRequest
from app.use_cases.load_candles import LoadCandles
from app.use_cases.update_candles import UpdateCandles, UpdateCandlesRequest


async def create_security_command(ticker: str, board: str):
    """Create Security Command."""
    async with connection_factory() as conn:
        uow = unit_of_work_factory(conn)
        repo = security_repository_factory(conn)
        request = CreateSecurityRequest(ticker=ticker, board=board)
        use_case = CreateSecurity(uow=uow, security_repo=repo)
        result = await use_case.execute(request)
        print(result)


async def update_candles_command():
    """Update Candles Command."""
    async with connection_factory() as conn:
        market_data_adapter = market_data_adapter_factory()
        uow = unit_of_work_factory(conn)
        security_repo = security_repository_factory(conn)
        candle_repository = candle_repository_factory(conn)
        candle_span_repository = candle_span_repository_factory(conn)

        market_data_loader = MarketDataLoader(
            market_data_adapter=market_data_adapter,
            security_repository=security_repo,
            candle_repository=candle_repository,
            candle_span_repository=candle_span_repository,
            unit_of_work=uow,
        )

        load_candles_use_case = LoadCandles(market_data_loader=market_data_loader)
        use_case = UpdateCandles(
            load_candles_use_case=load_candles_use_case,
            security_repo=security_repo,
        )
        response = await use_case.execute(UpdateCandlesRequest())
        print(response)
