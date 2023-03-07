from ddtrace import patch
from fastapi import FastAPI
from mangum import Mangum

patch(fastapi=True)
app = FastAPI()

@app.get("/")
async def root():
  return {"message": "Hello World"}

handler = Mangum(app)
