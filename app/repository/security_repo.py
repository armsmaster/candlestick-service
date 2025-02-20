from sqlalchemy import insert, select

from app.core.entities import Security
from app.core.repository import ISecurityRepository

from app.repository.base_repo import BaseRepository
from app.repository.models import Security as SecurityModel


class SecurityRepository(BaseRepository, ISecurityRepository):

    def create(self, items: list[Security]):
        for item in items:
            existing = self.session.execute(
                select(SecurityModel).filter_by(
                    ticker=item.ticker,
                    board=item.board,
                )
            ).scalar_one_or_none()
            if existing is None:
                security_model = SecurityModel(ticker=item.ticker, board=item.board)
                self.session.add(security_model)

        return

    def update(self, items: list[Security]):
        """Not Implemented"""
        raise NotImplementedError

    def delete(self, items: list[Security]):
        for item in items:
            security_model = self.session.execute(
                select(SecurityModel).filter_by(
                    ticker=item.ticker,
                    board=item.board,
                )
            ).scalar_one_or_none()
            if security_model is not None:
                self.session.delete(security_model)

    def all(self) -> list[Security]:
        security_models = self.session.execute(select(SecurityModel)).scalars()
        return [Security(ticker=sm.ticker, board=sm.board) for sm in security_models]
