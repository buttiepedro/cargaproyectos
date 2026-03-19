
from fastapi import FastAPI, UploadFile, File, Form, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import base64
import os

from app.odoo_client import get_projects, create_task

load_dotenv()

API_KEY = os.getenv("API_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def check_api_key(key):
    if key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.get("/projects")
def projects(x_api_key: str = Header(None)):
    check_api_key(x_api_key)
    return get_projects()

@app.post("/task")
async def task(
    tipo: str = Form(...),
    project_id: int = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    files: list[UploadFile] = File([]),
    x_api_key: str = Header(None)
):
    check_api_key(x_api_key)

    images = []
    for file in files:
        content = await file.read()
        images.append({
            "filename": file.filename,
            "content": base64.b64encode(content).decode("utf-8")
        })

    task_id = create_task({
        "tipo": tipo,
        "project_id": project_id,
        "title": title,
        "description": description
    }, images)

    return {"task_id": task_id}

app.mount("/", StaticFiles(directory="static", html=True), name="static")
