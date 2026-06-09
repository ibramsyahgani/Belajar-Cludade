import os
import re
import json
import base64
import tempfile
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .ai_service import process_cv_with_gemini
from .docx_generator import generate_docx
from .admin import router as admin_router

app = FastAPI(title="CV Harvard Auto-Formatter")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_router)

ALLOWED_MIME = {"image/jpeg", "image/png", "application/pdf"}
MAX_SIZE = 10 * 1024 * 1024  # 10MB


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/process")
async def process_cv(
    name: str = Form(...),
    email: str = Form(...),
    file: UploadFile = File(...)
):
    # Validate MIME type
    if file.content_type not in ALLOWED_MIME:
        raise HTTPException(400, "Format file tidak didukung. Gunakan JPG, PNG, atau PDF.")

    file_bytes = await file.read()
    if len(file_bytes) > MAX_SIZE:
        raise HTTPException(400, "Ukuran file terlalu besar. Maksimum 10MB.")

    if len(file_bytes) < 1000:
        raise HTTPException(400, "File terlalu kecil atau kosong.")

    try:
        cv_data = await process_cv_with_gemini(file_bytes, file.content_type, name, email)
    except ValueError as e:
        raise HTTPException(422, str(e))
    except Exception as e:
        raise HTTPException(500, f"Gagal memproses CV: {str(e)}")
    finally:
        del file_bytes

    try:
        docx_bytes = generate_docx(cv_data)
    except Exception as e:
        raise HTTPException(500, f"Gagal membuat dokumen: {str(e)}")

    safe_name = re.sub(r'[^\w\s-]', '', name).strip().replace(' ', '_')
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"CV_{safe_name}_{date_str}.docx"

    return {
        "status": "ok",
        "filename": filename,
        "docx_b64": base64.b64encode(docx_bytes).decode(),
        "preview": cv_data.model_dump(),
        "notes": cv_data.notes
    }


# Serve frontend
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

    @app.get("/")
    async def serve_index():
        return FileResponse(str(frontend_path / "index.html"))

    @app.get("/admin-panel")
    async def serve_admin():
        return FileResponse(str(frontend_path / "admin.html"))
