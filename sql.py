import sqlite3
from fastapi import FastAPI

app = FastAPI()


@app.on_event("startup")
async def startup():
    app.db_connection = sqlite3.connect('chinook.db')


@app.on_event("shutdown")
async def shutdown():
    app.db_connection.close()
@app.get("/tracks")
async def root():
    cursor = app.db_connection.cursor()
    tracks = cursor.execute("SELECT name FROM tracks").fetchall()
    return {
        "tracks": tracks,
    }
