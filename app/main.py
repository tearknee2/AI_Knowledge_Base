# main.py
from fastapi import FastAPI
# from app.core.database import connection

app = FastAPI()

@app.get("/")
async def get():
    return {"hello":"world"}