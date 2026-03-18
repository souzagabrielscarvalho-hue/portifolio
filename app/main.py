import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.router import router
from app.database import create_db_and_tables

current_dir = os.path.dirname(os.path.abspath(__file__)) 
root_dir = os.path.dirname(current_dir) 

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()


app.include_router(router, prefix="/api")
app.mount("/", StaticFiles(directory=root_dir, html=True), name="static")