from fastapi import FastAPI

from app.io.rest_api.api import router as router_api

app = FastAPI()
app.include_router(router_api)


@app.get("/hello/")
async def hello():
    return {"msg": "Hello World"}
