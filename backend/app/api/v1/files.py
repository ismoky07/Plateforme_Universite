"""
Files API Routes
"""
import uuid
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

from app.api.deps import get_current_user, get_professor_user
from app.core.exceptions import NotFoundException, BadRequestException
from app.config import settings

router = APIRouter()

UPLOADS_PATH = Path(settings.DATA_DIR) / "uploads"
EVALUATIONS_PATH = Path(settings.DATA_DIR) / "evaluations"


def ensure_uploads_dir():
    """Ensure uploads directory exists"""
    UPLOADS_PATH.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    folder: Optional[str] = Query(None, description="Target folder"),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload a file

    - **file**: File to upload
    - **folder**: Optional target folder
    """
    ensure_uploads_dir()

    # Check file size
    content = await file.read()
    max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    if len(content) > max_size:
        raise BadRequestException(f"Fichier trop volumineux (max {settings.MAX_UPLOAD_SIZE_MB}MB)")

    # Generate unique filename
    file_id = uuid.uuid4().hex[:12]
    ext = Path(file.filename).suffix if file.filename else ""
    safe_name = f"{file_id}{ext}"

    # Determine target path
    if folder:
        target_dir = UPLOADS_PATH / folder
    else:
        target_dir = UPLOADS_PATH / datetime.now().strftime("%Y%m%d")

    target_dir.mkdir(parents=True, exist_ok=True)
    file_path = target_dir / safe_name

    # Save file
    with open(file_path, "wb") as f:
        f.write(content)

    return {
        "id": file_id,
        "filename": safe_name,
        "original_filename": file.filename,
        "size": len(content),
        "path": str(file_path.relative_to(Path(settings.DATA_DIR))),
        "uploaded_at": datetime.now().isoformat()
    }


@router.post("/upload/multiple")
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    folder: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload multiple files
    """
    results = []
    total_size = 0
    max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    for file in files:
        content = await file.read()
        total_size += len(content)

        if total_size > max_size * 5:  # Allow 5x max for multiple files
            raise BadRequestException("Taille totale des fichiers trop importante")

        file_id = uuid.uuid4().hex[:12]
        ext = Path(file.filename).suffix if file.filename else ""
        safe_name = f"{file_id}{ext}"

        if folder:
            target_dir = UPLOADS_PATH / folder
        else:
            target_dir = UPLOADS_PATH / datetime.now().strftime("%Y%m%d")

        target_dir.mkdir(parents=True, exist_ok=True)
        file_path = target_dir / safe_name

        with open(file_path, "wb") as f:
            f.write(content)

        results.append({
            "id": file_id,
            "filename": safe_name,
            "original_filename": file.filename,
            "size": len(content)
        })

    return {
        "uploaded": len(results),
        "total_size": total_size,
        "files": results
    }


@router.get("/download/{file_path:path}")
async def download_file(
    file_path: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Download a file by path
    """
    full_path = Path(settings.DATA_DIR) / file_path

    if not full_path.exists():
        raise NotFoundException("Fichier", file_path)

    # Security check - ensure file is within data directory
    try:
        full_path.resolve().relative_to(Path(settings.DATA_DIR).resolve())
    except ValueError:
        raise BadRequestException("Chemin de fichier invalide")

    return FileResponse(
        full_path,
        filename=full_path.name
    )


@router.get("/evaluation/{eval_id}/copies")
async def list_evaluation_copies(
    eval_id: str,
    current_user: dict = Depends(get_professor_user)
):
    """
    List all copy files for an evaluation (professors only)
    """
    copies_dir = EVALUATIONS_PATH / eval_id / "copies_soumises"

    if not copies_dir.exists():
        return []

    copies = []
    for file_path in copies_dir.iterdir():
        if file_path.is_file():
            copies.append({
                "filename": file_path.name,
                "size": file_path.stat().st_size,
                "type": file_path.suffix.lstrip("."),
                "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            })

    return copies


@router.get("/evaluation/{eval_id}/copy/{filename}")
async def download_copy(
    eval_id: str,
    filename: str,
    current_user: dict = Depends(get_professor_user)
):
    """
    Download a specific copy file (professors only)
    """
    file_path = EVALUATIONS_PATH / eval_id / "copies_soumises" / filename

    if not file_path.exists():
        raise NotFoundException("Copie", filename)

    return FileResponse(
        file_path,
        filename=filename
    )


@router.delete("/evaluation/{eval_id}/copy/{filename}")
async def delete_copy(
    eval_id: str,
    filename: str,
    current_user: dict = Depends(get_professor_user)
):
    """
    Delete a copy file (professors only)
    """
    file_path = EVALUATIONS_PATH / eval_id / "copies_soumises" / filename

    if not file_path.exists():
        raise NotFoundException("Copie", filename)

    file_path.unlink()

    return {"message": f"Copie {filename} supprimee"}


@router.post("/evaluation/{eval_id}/copies")
async def upload_copies(
    eval_id: str,
    files: List[UploadFile] = File(...),
    current_user: dict = Depends(get_professor_user)
):
    """
    Upload copy files for an evaluation (professors only)
    """
    eval_dir = EVALUATIONS_PATH / eval_id

    if not eval_dir.exists():
        raise NotFoundException("Evaluation", eval_id)

    copies_dir = eval_dir / "copies_soumises"
    copies_dir.mkdir(exist_ok=True)

    uploaded = []
    for file in files:
        if file.filename:
            content = await file.read()
            file_path = copies_dir / file.filename

            with open(file_path, "wb") as f:
                f.write(content)

            uploaded.append({
                "filename": file.filename,
                "size": len(content)
            })

    return {
        "uploaded": len(uploaded),
        "files": uploaded
    }
