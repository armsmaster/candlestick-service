from datetime import datetime, date, UTC
from pytz import timezone


class TimestampException(Exception):
    pass


class Timestamp:

    def __init__(self, timestamp: datetime | str):

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
                return
            except ValueError as e:
                raise TimestampException(f"Invalid iso string {timestamp}")

        raise Exception(f"Type error: {timestamp} ({type(timestamp)})")

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
