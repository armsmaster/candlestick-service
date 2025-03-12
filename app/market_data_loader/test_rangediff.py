from app.core.date_time import Timestamp
from app.market_data_loader.rangediff import Range, rangediff


def test_rangediff():
    t = Timestamp("2025-01-01")

    assert str(t + 1) == "2025-01-02"

    remove_what = [
        Range(t + 10, t + 20),
        Range(t + 25, t + 30),
        Range(t + 35, t + 40),
    ]
    remove_from = Range(t + 0, t + 5)
    assert rangediff(remove_what, remove_from) == [remove_from]

    remove_from = Range(t + 50, t + 55)
    assert rangediff(remove_what, remove_from) == [remove_from]

    assert rangediff([], remove_from) == [remove_from]

    remove_from = Range(t + 5, t + 15)
    assert rangediff(remove_what, remove_from) == [Range(t + 5, t + 9)]

    remove_from = Range(t + 31, t + 40)
    assert rangediff(remove_what, remove_from) == [Range(t + 31, t + 34)]

    remove_from = Range(t + 15, t + 22)
    assert rangediff(remove_what, remove_from) == [Range(t + 21, t + 22)]

    remove_from = Range(t + 26, t + 33)
    assert rangediff(remove_what, remove_from) == [Range(t + 31, t + 33)]

    remove_from = Range(t + 12, t + 17)
    assert rangediff(remove_what, remove_from) == []

    remove_from = Range(t + 27, t + 29)
    assert rangediff(remove_what, remove_from) == []

    remove_from = Range(t + 5, t + 25)
    assert rangediff(remove_what, remove_from) == [
        Range(t + 5, t + 9),
        Range(t + 21, t + 24),
    ]

    remove_from = Range(t + 5, t + 50)
    assert rangediff(remove_what, remove_from) == [
        Range(t + 5, t + 9),
        Range(t + 21, t + 24),
        Range(t + 31, t + 34),
        Range(t + 41, t + 50),
    ]

    remove_from = Range(t + 20, t + 25)
    assert rangediff(remove_what, remove_from) == [Range(t + 21, t + 24)]

    remove_from = Range(t + 5, t + 10)
    assert rangediff(remove_what, remove_from) == [Range(t + 5, t + 9)]

    remove_from = Range(t + 40, t + 50)
    assert rangediff(remove_what, remove_from) == [Range(t + 41, t + 50)]
