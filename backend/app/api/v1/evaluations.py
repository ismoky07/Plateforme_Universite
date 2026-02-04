"""
Evaluations API Routes
"""
import uuid
import json
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException

from app.api.deps import get_professor_user, get_current_user, get_student_user
from app.core.exceptions import NotFoundException, BadRequestException
from app.models.evaluation import (
    Evaluation, EvaluationCreate, EvaluationUpdate,
    EvaluationSummary, EvaluationStatus, PublicationStatus,
    EvaluationPublishRequest
)
from app.config import settings

router = APIRouter()

# Base path for evaluations data
EVALUATIONS_PATH = Path(settings.DATA_DIR) / "evaluations"


def ensure_evaluations_dir():
    """Ensure evaluations directory exists"""
    EVALUATIONS_PATH.mkdir(parents=True, exist_ok=True)


def load_evaluation(eval_id: str) -> Optional[dict]:
    """Load evaluation from JSON file"""
    eval_dir = EVALUATIONS_PATH / eval_id
    info_file = eval_dir / "infos_evaluation.json"

    if not info_file.exists():
        return None

    with open(info_file, "r", encoding="utf-8") as f:
        return json.load(f)


def save_evaluation(eval_id: str, data: dict):
    """Save evaluation to JSON file"""
    eval_dir = EVALUATIONS_PATH / eval_id
    eval_dir.mkdir(parents=True, exist_ok=True)

    info_file = eval_dir / "infos_evaluation.json"
    with open(info_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def list_all_evaluations() -> List[dict]:
    """List all evaluations"""
    ensure_evaluations_dir()
    evaluations = []

    for eval_dir in EVALUATIONS_PATH.iterdir():
        if eval_dir.is_dir():
            eval_data = load_evaluation(eval_dir.name)
            if eval_data:
                evaluations.append(eval_data)

    # Sort by creation date (newest first)
    evaluations.sort(key=lambda x: x.get("date_creation", ""), reverse=True)
    return evaluations


@router.get("/", response_model=List[dict])
async def list_evaluations(
    matiere: Optional[str] = Query(None, description="Filter by subject"),
    statut: Optional[EvaluationStatus] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """
    List evaluations

    Students see only published evaluations.
    Professors and admins see all evaluations.
    """
    evaluations = list_all_evaluations()

    # Filter by role
    user_role = current_user.get("role")
    if user_role == "student":
        # Students only see published evaluations
        evaluations = [
            e for e in evaluations
            if e.get("statut_publication") == "publie" or e.get("statut") == "ouvert"
        ]

    # Apply filters
    if matiere:
        evaluations = [e for e in evaluations if e.get("matiere", "").lower() == matiere.lower()]

    if statut:
        evaluations = [e for e in evaluations if e.get("statut") == statut.value]

    return evaluations[skip:skip + limit]


@router.get("/available")
async def list_available_evaluations(
    current_user: dict = Depends(get_student_user)
):
    """
    List evaluations available for student submission
    """
    evaluations = list_all_evaluations()

    # Filter to only open evaluations
    available = [
        e for e in evaluations
        if e.get("statut") == "ouvert"
    ]

    return available


@router.post("/", response_model=dict)
async def create_evaluation(
    evaluation: EvaluationCreate,
    current_user: dict = Depends(get_professor_user)
):
    """
    Create a new evaluation (professors only)
    """
    ensure_evaluations_dir()

    # Generate unique ID
    eval_id = f"EVAL_{evaluation.matiere}_{evaluation.titre}_{uuid.uuid4().hex[:8]}"
    eval_id = eval_id.replace(" ", "_")

    # Create evaluation data
    eval_data = {
        "id": eval_id,
        "titre": evaluation.titre,
        "matiere": evaluation.matiere,
        "classe": evaluation.classe,
        "type_epreuve": evaluation.type_epreuve,
        "duree_minutes": evaluation.duree_minutes,
        "date_examen": evaluation.date_examen.isoformat() if evaluation.date_examen else None,
        "heure_debut": evaluation.heure_debut,
        "enseignant": evaluation.enseignant or current_user.get("sub"),
        "etablissement": evaluation.etablissement,
        "consignes_specifiques": evaluation.consignes_specifiques,
        "questions": [q.model_dump() for q in evaluation.questions],
        "note_totale": evaluation.note_totale,
        "statut": EvaluationStatus.DRAFT.value,
        "statut_publication": PublicationStatus.DRAFT.value,
        "date_creation": datetime.now().isoformat(),
        "dossier": str(EVALUATIONS_PATH / eval_id),
        "nombre_copies": 0,
        "nombre_corriges": 0
    }

    # Create directory structure
    eval_dir = EVALUATIONS_PATH / eval_id
    eval_dir.mkdir(parents=True, exist_ok=True)
    (eval_dir / "copies_soumises").mkdir(exist_ok=True)
    (eval_dir / "soumissions_etudiants").mkdir(exist_ok=True)
    (eval_dir / "resultats").mkdir(exist_ok=True)
    (eval_dir / "rapports").mkdir(exist_ok=True)
    (eval_dir / "images_correction").mkdir(exist_ok=True)

    # Save evaluation
    save_evaluation(eval_id, eval_data)

    return eval_data


@router.get("/{eval_id}")
async def get_evaluation(
    eval_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get evaluation details
    """
    eval_data = load_evaluation(eval_id)

    if not eval_data:
        raise NotFoundException("Evaluation", eval_id)

    return eval_data


@router.put("/{eval_id}")
async def update_evaluation(
    eval_id: str,
    update: EvaluationUpdate,
    current_user: dict = Depends(get_professor_user)
):
    """
    Update evaluation (professors only)
    """
    eval_data = load_evaluation(eval_id)

    if not eval_data:
        raise NotFoundException("Evaluation", eval_id)

    # Update fields
    update_dict = update.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        if key == "questions" and value:
            eval_data["questions"] = [q if isinstance(q, dict) else q.model_dump() for q in value]
        elif key == "date_examen" and value:
            eval_data[key] = value.isoformat()
        else:
            eval_data[key] = value

    save_evaluation(eval_id, eval_data)

    return eval_data


@router.post("/{eval_id}/open")
async def open_evaluation(
    eval_id: str,
    current_user: dict = Depends(get_professor_user)
):
    """
    Open evaluation for student submissions
    """
    eval_data = load_evaluation(eval_id)

    if not eval_data:
        raise NotFoundException("Evaluation", eval_id)

    eval_data["statut"] = EvaluationStatus.OPEN.value
    save_evaluation(eval_id, eval_data)

    return {"message": f"Evaluation {eval_id} ouverte aux soumissions"}


@router.post("/{eval_id}/close")
async def close_evaluation(
    eval_id: str,
    current_user: dict = Depends(get_professor_user)
):
    """
    Close evaluation for student submissions
    """
    eval_data = load_evaluation(eval_id)

    if not eval_data:
        raise NotFoundException("Evaluation", eval_id)

    eval_data["statut"] = EvaluationStatus.CLOSED.value
    save_evaluation(eval_id, eval_data)

    return {"message": f"Evaluation {eval_id} fermee"}


@router.post("/{eval_id}/publish")
async def publish_evaluation_results(
    eval_id: str,
    request: EvaluationPublishRequest,
    current_user: dict = Depends(get_professor_user)
):
    """
    Publish evaluation results to students
    """
    eval_data = load_evaluation(eval_id)

    if not eval_data:
        raise NotFoundException("Evaluation", eval_id)

    eval_data["statut_publication"] = PublicationStatus.PUBLISHED.value
    eval_data["date_publication"] = datetime.now().isoformat()
    eval_data["publie_par"] = current_user.get("sub")

    save_evaluation(eval_id, eval_data)

    return {
        "message": f"Resultats de l'evaluation {eval_id} publies",
        "notify_students": request.notify_students
    }


@router.post("/{eval_id}/unpublish")
async def unpublish_evaluation_results(
    eval_id: str,
    current_user: dict = Depends(get_professor_user)
):
    """
    Unpublish evaluation results
    """
    eval_data = load_evaluation(eval_id)

    if not eval_data:
        raise NotFoundException("Evaluation", eval_id)

    eval_data["statut_publication"] = PublicationStatus.UNPUBLISHED.value
    eval_data["date_depublication"] = datetime.now().isoformat()
    eval_data["depublie_par"] = current_user.get("sub")

    save_evaluation(eval_id, eval_data)

    return {"message": f"Resultats de l'evaluation {eval_id} depublies"}


@router.delete("/{eval_id}")
async def delete_evaluation(
    eval_id: str,
    current_user: dict = Depends(get_professor_user)
):
    """
    Delete evaluation (soft delete - marks as deleted)
    """
    eval_data = load_evaluation(eval_id)

    if not eval_data:
        raise NotFoundException("Evaluation", eval_id)

    # Soft delete - just mark as deleted
    eval_data["deleted"] = True
    eval_data["deleted_at"] = datetime.now().isoformat()
    eval_data["deleted_by"] = current_user.get("sub")

    save_evaluation(eval_id, eval_data)

    return {"message": f"Evaluation {eval_id} supprimee"}
