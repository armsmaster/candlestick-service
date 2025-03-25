"""Timestamp."""

from datetime import date, datetime, timedelta
from typing import overload

from pytz import timezone


class TimestampException(Exception):
    """TimestampException."""

    pass


class Timestamp:
    """Timestamp class."""

    @overload
    def __init__(self, timestamp: datetime):
        """Initialize from datetime object."""
        ...

    @overload
    def __init__(self, timestamp: datetime, tz: str):
        """Initialize from datetime object and tz string."""
        ...

    @overload
    def __init__(self, timestamp: str):
        """Initialize from ISO date/datetime string."""
        ...

    @overload
    def __init__(self, timestamp: str, tz: str):
        """Initialize from ISO date/datetime string and tz string."""
        ...

    def __init__(self, timestamp: datetime | str, tz: str | None = None):
        """Initialize."""
        self.tz = timezone(tz) if tz is not None else None
        self.dt = timestamp

    @staticmethod
    def now(time_zone: str = "UTC") -> "Timestamp":
        """Initialize with current timestamp value."""
        tz = timezone(time_zone)
        return Timestamp(datetime.now(tz))

    @staticmethod
    def today() -> "Timestamp":
        """Initialize with current date value."""
        return Timestamp(Timestamp.now().date())

    @property
    def dt(self) -> datetime:
        """Return date/datetime value."""
        return self.data

    @dt.setter
    def dt(self, timestamp: datetime | str):
        """Set date/datetime value."""
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
                raise TimestampException(f"Invalid iso string {timestamp} ({e=})")

        raise Exception(f"Type error: {timestamp} ({type(timestamp)})")

    def _localize(self) -> None:
        """Localize."""
        if self.tz is not None:
            self.data = self.tz.localize(self.data)

    def __eq__(self, other: "Timestamp"):
        """Equals."""
        return self.data == other.data

    def __gt__(self, other: "Timestamp"):
        """Compare >."""
        return self.data > other.data

    def __ge__(self, other: "Timestamp"):
        """Compare >=."""
        return self.data >= other.data

    def __hash__(self):
        """Return hash."""
        return hash(self.data)

    def __repr__(self):
        """Return repr."""
        return self.data.isoformat()

    def __str__(self):
        """Return str."""
        return self.data.isoformat()

    def __add__(self, value: int):
        """Add days."""
        return Timestamp(self.data + timedelta(days=value))

    def __sub__(self, value: int):
        """Subtract days."""
        return Timestamp(self.data - timedelta(days=value))

    def date(self):
        """Return `datetime.date` value."""
        if isinstance(self.data, datetime):
            return self.data.date()

        if isinstance(self.data, date):
            return self.data
