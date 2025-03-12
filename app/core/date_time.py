from typing import overload
from datetime import datetime, date, UTC
from pytz import timezone


class TimestampException(Exception):
    pass


class Timestamp:

    @overload
    def __init__(self, timestamp: datetime): ...

    @overload
    def __init__(self, timestamp: datetime, tz: str): ...

    @overload
    def __init__(self, timestamp: str): ...

    @overload
    def __init__(self, timestamp: str, tz: str): ...

    def __init__(self, timestamp: datetime | str, tz: str | None = None):
        self.tz = timezone(tz) if tz is not None else None
        self.dt = timestamp

    @staticmethod
    def now(time_zone: str = "UTC") -> "Timestamp":
        tz = timezone(time_zone)
        return Timestamp(datetime.now(tz))

    @property
    def dt(self) -> datetime:
        return self.data

    @dt.setter
    def dt(self, timestamp: datetime | str):
        if isinstance(timestamp, datetime):
            self.data = timestamp
            self._localize()
            return

        if isinstance(timestamp, date):
            self.data = timestamp
            return

        if isinstance(timestamp, str):
            try:
                self.data = datetime.fromisoformat(timestamp)
                if (
                    self.data.hour
                    == self.data.minute
                    == self.data.second
                    == self.data.microsecond
                    == 0
                ):
                    self.data = self.data.date()
                else:
                    self._localize()
                return
            except ValueError as e:
                raise TimestampException(f"Invalid iso string {timestamp}")

        raise Exception(f"Type error: {timestamp} ({type(timestamp)})")

    def _localize(self) -> None:
        if self.tz is not None:
            self.data = self.tz.localize(self.data)

    def __eq__(self, other: "Timestamp"):
        return self.data == other.data

    def __gt__(self, other: "Timestamp"):
        return self.data > other.data

    def __ge__(self, other: "Timestamp"):
        return self.data >= other.data

    def __hash__(self):
        return hash(self.data)

    def __repr__(self):
        return self.data.isoformat()

    def __str__(self):
        return self.data.isoformat()
