from app.core.date_time import Timestamp
from app.market_data_loader.range_operations import Range, rangemerge


def test_rangemerge():
    t = Timestamp("2025-01-01")

    assert str(t + 1) == "2025-01-02"

    ranges = [
        Range(t + 10, t + 20),
        Range(t + 25, t + 30),
        Range(t + 35, t + 40),
    ]
    assert rangemerge(ranges) == ranges

    ranges = [
        Range(t + 10, t + 20),
        Range(t + 20, t + 30),
        Range(t + 35, t + 40),
    ]
    assert rangemerge(ranges) == [Range(t + 10, t + 30), Range(t + 35, t + 40)]

    ranges = [
        Range(t + 10, t + 20),
        Range(t + 21, t + 30),
        Range(t + 35, t + 40),
    ]
    assert rangemerge(ranges) == [Range(t + 10, t + 30), Range(t + 35, t + 40)]

    ranges = [
        Range(t + 10, t + 20),
        Range(t + 25, t + 35),
        Range(t + 35, t + 40),
    ]
    assert rangemerge(ranges) == [Range(t + 10, t + 20), Range(t + 25, t + 40)]

    ranges = [
        Range(t + 10, t + 20),
        Range(t + 25, t + 34),
        Range(t + 35, t + 40),
    ]
    assert rangemerge(ranges) == [Range(t + 10, t + 20), Range(t + 25, t + 40)]

    ranges = [
        Range(t + 10, t + 20),
        Range(t + 5, t + 50),
        Range(t + 35, t + 40),
    ]
    assert rangemerge(ranges) == [Range(t + 5, t + 50)]

    ranges = [
        Range(t + 10, t + 20),
        Range(t + 25, t + 50),
        Range(t + 35, t + 40),
    ]
    assert rangemerge(ranges) == [Range(t + 10, t + 20), Range(t + 25, t + 50)]

    ranges = [
        Range(t + 10, t + 20),
        Range(t + 35, t + 50),
        Range(t + 35, t + 40),
    ]
    assert rangemerge(ranges) == [Range(t + 10, t + 20), Range(t + 35, t + 50)]
