from uuid import uuid4

from app.core.entities import Security
from app.core.repository import ISecurityRepository
from app.core.unit_of_work import IUnitOfWork


class TestCases:

    @staticmethod
    async def execute_create_security(uow: IUnitOfWork, repo: ISecurityRepository):
        test_ticker = uuid4().hex
        test_board = uuid4().hex
        security = Security(ticker=test_ticker, board=test_board)

        async with uow:

            await repo.add([security])  # create security
            await repo.add([security])  # try create duplicate

            repo = repo.filter_by_ticker(test_ticker)

            # check only one exists
            count = await repo.count()
            assert count == 1

            # clean up
            securities = [sec async for sec in repo]
            await repo.remove(securities)

            # check test record deleted
            count = await repo.count()
            assert count == 0

    @staticmethod
    async def execute_create_many_securities(
        uow: IUnitOfWork, repo: ISecurityRepository
    ):
        test_board = uuid4().hex
        securities = [
            Security(
                ticker=uuid4().hex,
                board=test_board,
            )
            for _ in range(1000)
        ]
        async with uow:
            await repo.add(securities)

            repo = repo.filter_by_board(test_board)
            count = await repo.count()
            assert count == 1000

            securities = [sec async for sec in repo]
            await repo.remove(securities)

            count = await repo.count()
            assert count == 0

    @staticmethod
    async def execute_slicing(uow: IUnitOfWork, repo: ISecurityRepository):
        test_board = uuid4().hex
        securities = [
            Security(
                ticker=uuid4().hex,
                board=test_board,
            )
            for _ in range(1000)
        ]
        async with uow:
            await repo.add(securities)

            repo = repo.filter_by_board(test_board)

            retrieved_securities = []
            i, batch_size = 0, 100
            while True:
                batch_repo = repo[i, i + batch_size]
                items = [sec async for sec in batch_repo]
                retrieved_securities += items
                if not items:
                    break
                i += batch_size

            assert set(securities) == set(retrieved_securities)

            records = [r async for r in repo]
            await repo.remove(records)

            count = await repo.count()
            assert count == 0
