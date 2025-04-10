from fastapi import FastAPI

from app.io.rest_api.api import router as router_api

app = FastAPI(
    title="Candlestick Service",
    contact={
        "name": "Edward Gordin",
        "url": "https://github.com/armsmaster/candlestick-service",
        "email": "edward.gordin@gmail.com",
    },
)
app.include_router(router_api)
