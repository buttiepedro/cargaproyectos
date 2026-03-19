from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import base64

from app.odoo_client import get_projects, create_task

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # después podés restringir a tu dominio
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/projects")
def projects():
    return get_projects()

@app.post("/task")
async def task(
    tipo: str = Form(...),
    project_id: int = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    files: list[UploadFile] = File([])
):
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

# servir frontend
app.mount("/", StaticFiles(directory="static", html=True), name="static")