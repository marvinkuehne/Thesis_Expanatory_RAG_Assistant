import os
import uvicorn
from fastapi import FastAPI, File, UploadFile, Query
from pydantic import BaseModel
from azure.storage.blob import BlobServiceClient, ContentSettings
from starlette.middleware.cors import CORSMiddleware

from Loaders.Loader_Switcher import (Target, ingest)
from typing import Optional, List

from Loaders.Azure_Loader import delete_chunks_for_file, search_client
from Loaders.Chroma_Loader import delete_from_chroma_for_file
from services.search_services import update_category_for_file

from query_data import query_rag
from db.chat_db import create_session, get_sessions, save_session, load_session, conn


app = FastAPI()

# (Optional) Progress global (nicht pro User)
progress_store = {"value": 0}

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://lambent-tapioca-db599c.netlify.app",
    "https://rag-assistant-frontend.netlify.app",
    "https://ragassistant-production.up.railway.app",
    "https://rag-assistant-marvin.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Decide via HTTP the Loader "POST /process_files?target=chroma"
def parse_backend(backend: Target): #Import Target from Load_Switcher
    backend = (backend or "").lower()
    if backend == "chroma":
        return Target.CHROMA
    return Target.AZURE


# Pydantic Models: Forces Frontend API calls to pass right data format to routes
class FileItem(BaseModel):
    filename: str
    category: Optional[str] = None

class FileList(BaseModel):
    files: Optional[List[FileItem]] = None


class CategoryUpdate(BaseModel):
    filename: str
    category: Optional[str] = None  # None = category entfernen


class AskPayload(BaseModel):
    query: str
    categories: Optional[List[str]] = None


# ------
# Azure Blob setup
# ------

blob_service = BlobServiceClient.from_connection_string(os.getenv("AZURE_CONNECTION_STRING"))
container_client = blob_service.get_container_client("docs")


# -------
# RAG endpoints (global pool)
# --------

@app.post("/upload_files")
async def uploadFiles(file: UploadFile = File(...)):
    content = await file.read()
    blob_name = file.filename  # global: kein user prefix

    container_client.upload_blob(
        name=blob_name,
        data=content,
        overwrite=True,
        content_settings=ContentSettings(content_type=file.content_type),
    )

    return {"ok": True, "blob": blob_name, "size": len(content)}


@app.post("/ask")
async def askForm(payload: AskPayload, backend: str = Query("chroma")):
    try:
        answer, sources = query_rag(payload.query, payload.categories, backend=backend)


        print("ANSWER (first 200):", (answer or "")[:200])
        print("SOURCES:", sources)

        return [answer, sources]
    except Exception as e:
        return [f"Error: {str(e)}", []]





@app.get("/get_files")
async def get_files():
    out = []
    for blob in container_client.list_blobs():
        out.append({
            "filename": blob.name,
            "size": blob.size,
            "content_type": (blob.content_settings.content_type if blob.content_settings else "unknown"),
            "last_modified": (blob.last_modified.isoformat() if blob.last_modified else None),
        })
    return {"files": out}


@app.delete("/delete_file/{filename}")
async def delete_file(filename: str, backend: str = Query("azure")):
    target = parse_backend(backend)

    # 1) blob löschen (immer)
    blob_client = container_client.get_blob_client(filename)
    try:
        blob_client.delete_blob()
    except Exception:
        pass

    # 2) Index/DB löschen je nach backend
    if target == Target.AZURE:
        delete_chunks_for_file(search_client, filename)
    else:
        delete_from_chroma_for_file(filename)

    return {"ok": True, "deleted_file": filename, "backend": backend}


@app.post("/process_files")
async def processFiles(target: Target = Target.CHROMA):

    blob_names = [b.name for b in container_client.list_blobs()]

    return ingest(blob_names, target=target)

@app.get("/progress")
async def get_progress():
    return {"progress": progress_store.get("value", 0)}


@app.post("/update_category")
async def update_file_category(update: CategoryUpdate):

    # source_blob ist filename im global pool
    update_category_for_file(search_client, update.filename, update.category)
    return {"ok": True}



# -------------------------
# Chat sessions (kann user-basiert bleiben)
# -------------------------

@app.post("/create_session")
async def create_session_route(data: dict):
    user_id = data.get("user_id")
    title = data.get("title", "New Chat")
    session_id = create_session(user_id, title)
    return {"session_id": session_id, "title": title}


@app.get("/get_sessions/{user_id}")
async def get_sessions_route(user_id: str):
    return get_sessions(user_id)


@app.post("/save_session")
async def save_session_route(data: dict):
    session_id = data.get("session_id")
    messages = data.get("messages", [])
    save_session(session_id, messages)
    return {"status": "saved"}


@app.get("/get_session/{session_id}")
async def get_session_route(session_id: str):
    return load_session(session_id)


@app.delete("/delete_session/{session_id}")
def delete_session(session_id: str):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_sessions WHERE session_id = ?", (session_id,))
    conn.commit()
    return {"message": f"Session {session_id} deleted successfully"}


if __name__ == "__main__":
    uvicorn.run("router:app", host="127.0.0.1", port=8000, reload=True)

