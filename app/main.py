from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import base64

from app.odoo_client import get_projects, create_task, get_tasks_by_email

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    email: str = Form(...),
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
        "description": description,
        "email": email
    }, images)

    return {"task_id": task_id}

@app.get("/tickets")
def tickets(email: str):
    return get_tasks_by_email(email)

# servir frontend
app.mount("/", StaticFiles(directory="static", html=True), name="static")