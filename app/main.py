import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.router import router
from app.database import create_db_and_tables

# Descobre onde a pasta raiz está
current_dir = os.path.dirname(os.path.abspath(__file__)) 
root_dir = os.path.dirname(current_dir) 

app = FastAPI()

# --- ADICIONE ISSO AQUI ---
@app.on_event("startup")
def on_startup():
    create_db_and_tables()
# --------------------------

app.mount("/img", StaticFiles(directory=os.path.join(root_dir, "img")), name="img")
app.mount("/static", StaticFiles(directory=root_dir), name="static")

@app.get("/")
async def read_index():
    index_path = os.path.join(root_dir, "index.html")
    return FileResponse(index_path)

app.include_router(router, prefix="/api")