"""
Submissions API Routes
"""
import uuid
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, UploadFile, File, Form, HTTPException

from app.api.deps import get_student_user, get_professor_user, get_current_user
from app.core.exceptions import NotFoundException, BadRequestException
from app.models.submission import (
    Submission, SubmissionCreate, SubmissionSummary,
    SubmissionType, SubmissionStatus, StudentSubmissionCheck
)
from app.config import settings

router = APIRouter()

EVALUATIONS_PATH = Path(settings.DATA_DIR) / "evaluations"


def get_submission_path(eval_id: str, student_name: str) -> Path:
    """Get path for student submission"""
    return EVALUATIONS_PATH / eval_id / "soumissions_etudiants" / student_name


def load_submission(eval_id: str, student_name: str) -> Optional[dict]:
    """Load submission from JSON file"""
    sub_dir = get_submission_path(eval_id, student_name)
    sub_file = sub_dir / f"{student_name}_submission.json"

    if not sub_file.exists():
        # Try alternate naming
        for f in sub_dir.glob("*_submission.json"):
            with open(f, "r", encoding="utf-8") as file:
                return json.load(file)
        return None

    with open(sub_file, "r", encoding="utf-8") as f:
        return json.load(f)


def save_submission(eval_id: str, student_name: str, data: dict):
    """Save submission to JSON file"""
    sub_dir = get_submission_path(eval_id, student_name)
    sub_dir.mkdir(parents=True, exist_ok=True)

    sub_file = sub_dir / f"{student_name}_submission.json"
    with open(sub_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def list_submissions_for_evaluation(eval_id: str) -> List[dict]:
    """List all submissions for an evaluation"""
    submissions_dir = EVALUATIONS_PATH / eval_id / "soumissions_etudiants"

    if not submissions_dir.exists():
        return []

    submissions = []
    for student_dir in submissions_dir.iterdir():
        if student_dir.is_dir():
            sub_data = load_submission(eval_id, student_dir.name)
            if sub_data:
                submissions.append(sub_data)

    return submissions


@router.post("/")
async def create_submission(
    evaluation_id: str = Form(...),
    nom: str = Form(...),
    prenom: str = Form(...),
    numero_etudiant: Optional[str] = Form(None),
    type_soumission: SubmissionType = Form(...),
    reponse_numerique: Optional[str] = Form(None),
    files: List[UploadFile] = File(default=[]),
    current_user: dict = Depends(get_student_user)
):
    """
    Submit exam copy

    - Upload scanned/photo files OR
    - Submit digital response text
    """
    # Check evaluation exists and is open
    eval_dir = EVALUATIONS_PATH / evaluation_id
    eval_file = eval_dir / "infos_evaluation.json"

    if not eval_file.exists():
        raise NotFoundException("Evaluation", evaluation_id)

    with open(eval_file, "r", encoding="utf-8") as f:
        eval_data = json.load(f)

    if eval_data.get("statut") != "ouvert":
        raise BadRequestException("L'evaluation n'est pas ouverte aux soumissions")

    # Create student name for folder
    student_name = f"{nom}_{prenom}".replace(" ", "_")
    submission_id = f"{student_name}_{uuid.uuid4().hex[:8]}"

    # Create submission directory
    sub_dir = get_submission_path(evaluation_id, student_name)
    sub_dir.mkdir(parents=True, exist_ok=True)

    # Save uploaded files
    saved_files = []
    total_size = 0

    for i, file in enumerate(files):
        if file.filename:
            # Generate safe filename
            ext = Path(file.filename).suffix
            safe_name = f"copie_page_{i+1:02d}{ext}"

            file_path = sub_dir / safe_name
            content = await file.read()

            with open(file_path, "wb") as f:
                f.write(content)

            file_size = len(content)
            total_size += file_size

            saved_files.append({
                "nom_original": file.filename,
                "nom_sauvegarde": safe_name,
                "taille": file_size,
                "type_fichier": ext.lstrip("."),
                "date_upload": datetime.now().isoformat()
            })

            # Also copy to copies_soumises for teacher view
            copies_dir = eval_dir / "copies_soumises"
            copies_dir.mkdir(exist_ok=True)
            shutil.copy(file_path, copies_dir / f"{student_name}_{safe_name}")

    # Save digital response if provided
    if reponse_numerique and type_soumission == SubmissionType.DIGITAL:
        response_file = sub_dir / "reponse_numerique.txt"
        with open(response_file, "w", encoding="utf-8") as f:
            f.write(reponse_numerique)

    # Create submission record
    submission_data = {
        "id": submission_id,
        "evaluation_id": evaluation_id,
        "etudiant_nom": nom,
        "etudiant_prenom": prenom,
        "numero_etudiant": numero_etudiant,
        "type_soumission": type_soumission.value,
        "date_soumission": datetime.now().isoformat(),
        "statut": SubmissionStatus.RECEIVED.value,
        "fichiers_soumis": saved_files,
        "nombre_fichiers": len(saved_files),
        "taille_totale": total_size,
        "reponse_numerique": bool(reponse_numerique),
        "corrige": False
    }

    save_submission(evaluation_id, student_name, submission_data)

    # Update evaluation copy count
    eval_data["nombre_copies"] = eval_data.get("nombre_copies", 0) + 1
    with open(eval_file, "w", encoding="utf-8") as f:
        json.dump(eval_data, f, ensure_ascii=False, indent=2, default=str)

    return submission_data


@router.get("/evaluation/{eval_id}")
async def list_evaluation_submissions(
    eval_id: str,
    current_user: dict = Depends(get_professor_user)
):
    """
    List all submissions for an evaluation (professors only)
    """
    submissions = list_submissions_for_evaluation(eval_id)
    return submissions


@router.get("/check/{eval_id}")
async def check_student_submission(
    eval_id: str,
    nom: str = Query(...),
    prenom: str = Query(...),
    current_user: dict = Depends(get_student_user)
):
    """
    Check if student has already submitted
    """
    student_name = f"{nom}_{prenom}".replace(" ", "_")
    submission = load_submission(eval_id, student_name)

    if submission:
        return StudentSubmissionCheck(
            has_submitted=True,
            submission_id=submission.get("id"),
            date_soumission=submission.get("date_soumission"),
            can_modify=submission.get("statut") == SubmissionStatus.RECEIVED.value
        )

    return StudentSubmissionCheck(
        has_submitted=False,
        can_modify=True
    )


@router.get("/{submission_id}")
async def get_submission(
    submission_id: str,
    eval_id: str = Query(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Get submission details
    """
    submissions = list_submissions_for_evaluation(eval_id)

    for sub in submissions:
        if sub.get("id") == submission_id:
            return sub

    raise NotFoundException("Soumission", submission_id)


@router.delete("/{submission_id}")
async def delete_submission(
    submission_id: str,
    eval_id: str = Query(...),
    current_user: dict = Depends(get_professor_user)
):
    """
    Delete submission (professors only)
    """
    submissions = list_submissions_for_evaluation(eval_id)

    for sub in submissions:
        if sub.get("id") == submission_id:
            student_name = f"{sub['etudiant_nom']}_{sub['etudiant_prenom']}".replace(" ", "_")
            sub_dir = get_submission_path(eval_id, student_name)

            if sub_dir.exists():
                shutil.rmtree(sub_dir)

            return {"message": f"Soumission {submission_id} supprimee"}

    raise NotFoundException("Soumission", submission_id)
