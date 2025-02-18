from app.core.entities import Timeframe


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

N_CONSUMERS = 5
