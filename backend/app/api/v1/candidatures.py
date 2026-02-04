"""
Candidatures API Routes
"""
import uuid
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, UploadFile, File, Form

from app.api.deps import get_admin_user, get_current_user
from app.core.exceptions import NotFoundException, BadRequestException
from app.models.candidature import (
    Candidature, CandidatureCreate, CandidatureSummary,
    ValidationStatus, CandidatureValidationRequest,
    PersonalInfo, Grade
)
from app.config import settings

router = APIRouter()

CANDIDATURES_PATH = Path(settings.DATA_DIR) / "candidatures"


def ensure_candidatures_dir():
    """Ensure candidatures directory exists"""
    CANDIDATURES_PATH.mkdir(parents=True, exist_ok=True)


def load_candidature(candidature_id: str) -> Optional[dict]:
    """Load candidature from folder"""
    for folder in CANDIDATURES_PATH.iterdir():
        if folder.is_dir():
            resume_file = folder / "resume_candidature.json"
            if resume_file.exists():
                with open(resume_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("id") == candidature_id or folder.name.startswith(candidature_id.split("_")[0]):
                        data["dossier_path"] = str(folder)
                        return data
    return None


def save_candidature(folder_path: Path, data: dict):
    """Save candidature to folder"""
    folder_path.mkdir(parents=True, exist_ok=True)
    resume_file = folder_path / "resume_candidature.json"
    with open(resume_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def list_all_candidatures() -> List[dict]:
    """List all candidatures"""
    ensure_candidatures_dir()
    candidatures = []

    for folder in CANDIDATURES_PATH.iterdir():
        if folder.is_dir():
            resume_file = folder / "resume_candidature.json"
            if resume_file.exists():
                with open(resume_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    data["dossier_path"] = str(folder)
                    candidatures.append(data)

    # Sort by submission date (newest first)
    candidatures.sort(key=lambda x: x.get("date_soumission", ""), reverse=True)
    return candidatures


def calculate_completion(personal_info: dict, grades: list, documents: list) -> float:
    """Calculate completion percentage"""
    progress = 0

    # Personal info: 20%
    required_fields = ["nom", "prenom", "email", "niveau_etude"]
    if all(personal_info.get(f) for f in required_fields):
        progress += 20

    # Grades: 40% (need at least 5 valid grades)
    valid_grades = [g for g in grades if g.get("note") is not None and 0 <= g.get("note", -1) <= 20]
    if valid_grades:
        progress += min(40, (len(valid_grades) / 10) * 40)

    # Documents: 40% (need at least 1)
    if documents:
        progress += min(40, (len(documents) / 3) * 40)

    return round(progress, 1)


def calculate_average(grades: list) -> float:
    """Calculate weighted average"""
    valid_grades = [g for g in grades if g.get("note") is not None and g.get("coefficient")]
    if not valid_grades:
        return 0.0

    total_weighted = sum(g["note"] * g["coefficient"] for g in valid_grades)
    total_coef = sum(g["coefficient"] for g in valid_grades)

    return round(total_weighted / total_coef, 2) if total_coef > 0 else 0.0


@router.get("/", response_model=List[dict])
async def list_candidatures(
    statut: Optional[ValidationStatus] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_admin_user)
):
    """
    List all candidatures (admin only)
    """
    candidatures = list_all_candidatures()

    if statut:
        candidatures = [c for c in candidatures if c.get("statut") == statut.value]

    return candidatures[skip:skip + limit]


@router.post("/")
async def create_candidature(
    nom: str = Form(...),
    prenom: str = Form(...),
    email: str = Form(...),
    niveau_etude: str = Form(...),
    telephone: Optional[str] = Form(None),
    grades_json: str = Form("[]"),
    files: List[UploadFile] = File(default=[])
):
    """
    Create a new candidature

    - Upload personal information
    - Upload grades as JSON
    - Upload bulletin documents
    """
    ensure_candidatures_dir()

    # Parse grades
    try:
        grades = json.loads(grades_json)
    except json.JSONDecodeError:
        grades = []

    # Create folder name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"{nom}_{prenom}_{timestamp}".replace(" ", "_")
    candidature_id = f"CAND_{uuid.uuid4().hex[:8]}"

    folder_path = CANDIDATURES_PATH / folder_name
    folder_path.mkdir(parents=True, exist_ok=True)

    # Save uploaded documents
    documents = []
    for file in files:
        if file.filename:
            # Determine year from filename if possible
            year = datetime.now().strftime("%Y")
            safe_name = f"{year}_bulletin_{file.filename}"

            file_path = folder_path / safe_name
            content = await file.read()

            with open(file_path, "wb") as f:
                f.write(content)

            documents.append({
                "year": year,
                "filename": safe_name,
                "original_filename": file.filename,
                "size": len(content),
                "file_type": Path(file.filename).suffix.lstrip("."),
                "upload_date": datetime.now().isoformat()
            })

    # Create candidature data
    personal_info = {
        "nom": nom,
        "prenom": prenom,
        "email": email,
        "telephone": telephone,
        "niveau_etude": niveau_etude
    }

    completion = calculate_completion(personal_info, grades, documents)
    moyenne = calculate_average(grades)

    candidature_data = {
        "id": candidature_id,
        "personal_info": personal_info,
        "grades": grades,
        "documents": documents,
        "date_soumission": datetime.now().isoformat(),
        "statut": ValidationStatus.PENDING.value,
        "completion_percentage": completion,
        "moyenne_generale": moyenne,
        "dossier_path": str(folder_path)
    }

    save_candidature(folder_path, candidature_data)

    return candidature_data


@router.get("/{candidature_id}")
async def get_candidature(
    candidature_id: str,
    current_user: dict = Depends(get_admin_user)
):
    """
    Get candidature details (admin only)
    """
    candidature = load_candidature(candidature_id)

    if not candidature:
        raise NotFoundException("Candidature", candidature_id)

    return candidature


@router.post("/{candidature_id}/validate")
async def validate_candidature(
    candidature_id: str,
    request: CandidatureValidationRequest,
    current_user: dict = Depends(get_admin_user)
):
    """
    Validate or reject a candidature (admin only)
    """
    candidature = load_candidature(candidature_id)

    if not candidature:
        raise NotFoundException("Candidature", candidature_id)

    # Update status
    candidature["statut"] = request.decision.value
    candidature["date_validation"] = datetime.now().isoformat()
    candidature["valide_par"] = current_user.get("sub")

    if request.commentaire:
        if "commentaires_admin" not in candidature:
            candidature["commentaires_admin"] = []
        candidature["commentaires_admin"].append({
            "date": datetime.now().isoformat(),
            "auteur": current_user.get("sub"),
            "commentaire": request.commentaire
        })

    # Save updated candidature
    folder_path = Path(candidature["dossier_path"])
    save_candidature(folder_path, candidature)

    # Save validation status separately
    status_file = folder_path / "validation_status.json"
    with open(status_file, "w", encoding="utf-8") as f:
        json.dump({
            "statut": request.decision.value,
            "date": datetime.now().isoformat(),
            "valide_par": current_user.get("sub"),
            "commentaire": request.commentaire
        }, f, ensure_ascii=False, indent=2)

    return {
        "message": f"Candidature {candidature_id} {request.decision.value}",
        "notify_candidate": request.notify_candidate
    }


@router.post("/{candidature_id}/verify")
async def verify_candidature(
    candidature_id: str,
    current_user: dict = Depends(get_admin_user)
):
    """
    Launch OCR verification for a candidature (admin only)

    This is a placeholder - the actual OCR verification service
    would be implemented in the services layer.
    """
    candidature = load_candidature(candidature_id)

    if not candidature:
        raise NotFoundException("Candidature", candidature_id)

    # Update status to under review
    candidature["statut"] = ValidationStatus.UNDER_REVIEW.value
    folder_path = Path(candidature["dossier_path"])
    save_candidature(folder_path, candidature)

    return {
        "message": f"Verification OCR lancee pour {candidature_id}",
        "statut": "en_cours"
    }


@router.put("/{candidature_id}/grades")
async def update_candidature_grades(
    candidature_id: str,
    grades: List[dict],
    current_user: dict = Depends(get_admin_user)
):
    """
    Update candidature grades (admin only, for corrections)
    """
    candidature = load_candidature(candidature_id)

    if not candidature:
        raise NotFoundException("Candidature", candidature_id)

    candidature["grades"] = grades
    candidature["moyenne_generale"] = calculate_average(grades)
    candidature["completion_percentage"] = calculate_completion(
        candidature.get("personal_info", {}),
        grades,
        candidature.get("documents", [])
    )

    folder_path = Path(candidature["dossier_path"])
    save_candidature(folder_path, candidature)

    return candidature


@router.delete("/{candidature_id}")
async def delete_candidature(
    candidature_id: str,
    current_user: dict = Depends(get_admin_user)
):
    """
    Delete candidature (admin only)
    """
    candidature = load_candidature(candidature_id)

    if not candidature:
        raise NotFoundException("Candidature", candidature_id)

    folder_path = Path(candidature["dossier_path"])
    if folder_path.exists():
        shutil.rmtree(folder_path)

    return {"message": f"Candidature {candidature_id} supprimee"}
