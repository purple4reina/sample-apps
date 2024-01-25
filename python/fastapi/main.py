from ddtrace import patch
patch(fastapi=True)

from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/error")
async def error():
    return {"message": 1 / 0}

handler = Mangum(app)
