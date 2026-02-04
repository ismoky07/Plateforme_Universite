"""
Corrections API Routes
"""
import json
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, BackgroundTasks

from app.api.deps import get_professor_user, get_student_user, get_current_user
from app.core.exceptions import NotFoundException, BadRequestException
from app.models.correction import (
    CorrectionResult, ClassStatistics, CorrectionRequest,
    CorrectionProgress, CorrectionProfile
)
from app.config import settings
from app.services import process_copies_with_ai, transcribe_manuscript

router = APIRouter()

EVALUATIONS_PATH = Path(settings.DATA_DIR) / "evaluations"


def load_correction_result(eval_id: str, student_name: str) -> Optional[dict]:
    """Load correction result for a student"""
    result_dir = EVALUATIONS_PATH / eval_id / "resultats" / student_name
    result_file = result_dir / "correction_detaillee.json"

    if not result_file.exists():
        return None

    with open(result_file, "r", encoding="utf-8") as f:
        return json.load(f)


def save_correction_result(eval_id: str, student_name: str, data: dict):
    """Save correction result"""
    result_dir = EVALUATIONS_PATH / eval_id / "resultats" / student_name
    result_dir.mkdir(parents=True, exist_ok=True)

    result_file = result_dir / "correction_detaillee.json"
    with open(result_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def list_all_corrections(eval_id: str) -> List[dict]:
    """List all corrections for an evaluation"""
    results_dir = EVALUATIONS_PATH / eval_id / "resultats"

    if not results_dir.exists():
        return []

    corrections = []
    for student_dir in results_dir.iterdir():
        if student_dir.is_dir():
            result = load_correction_result(eval_id, student_dir.name)
            if result:
                corrections.append(result)

    return corrections


def calculate_class_statistics(corrections: List[dict], eval_id: str) -> dict:
    """Calculate statistics for all corrections"""
    if not corrections:
        return {}

    notes = [c.get("note_globale", 0) for c in corrections]
    note_max = corrections[0].get("note_max", 20) if corrections else 20

    # Calculate statistics
    moyenne = sum(notes) / len(notes) if notes else 0
    notes_sorted = sorted(notes)
    mediane = notes_sorted[len(notes_sorted) // 2] if notes_sorted else 0

    # Standard deviation
    variance = sum((n - moyenne) ** 2 for n in notes) / len(notes) if notes else 0
    ecart_type = variance ** 0.5

    # Passing rate (>= 10/20)
    passing_threshold = note_max / 2
    taux_reussite = len([n for n in notes if n >= passing_threshold]) / len(notes) * 100 if notes else 0

    # Distribution
    distribution = {
        "0-5": len([n for n in notes if n < 5]),
        "5-10": len([n for n in notes if 5 <= n < 10]),
        "10-12": len([n for n in notes if 10 <= n < 12]),
        "12-14": len([n for n in notes if 12 <= n < 14]),
        "14-16": len([n for n in notes if 14 <= n < 16]),
        "16-20": len([n for n in notes if n >= 16])
    }

    return {
        "evaluation_id": eval_id,
        "nombre_copies": len(corrections),
        "nombre_corriges": len(corrections),
        "moyenne_generale": round(moyenne, 2),
        "mediane": round(mediane, 2),
        "ecart_type": round(ecart_type, 2),
        "note_min": min(notes) if notes else 0,
        "note_max": max(notes) if notes else 0,
        "taux_reussite": round(taux_reussite, 1),
        "distribution_notes": distribution,
        "date_calcul": datetime.now().isoformat()
    }


async def run_ai_correction(eval_id: str, eval_data: dict, profile: str):
    """Background task to run AI correction"""
    eval_dir = EVALUATIONS_PATH / eval_id
    copies_dir = eval_dir / "copies_soumises"

    if not copies_dir.exists():
        return

    copies_data = []
    for copy_file in copies_dir.glob("*.pdf"):
        # Transcribe the copy
        transcription = transcribe_manuscript(str(copy_file), eval_data.get('matiere', 'general'))

        # Extract student name from filename
        filename = copy_file.stem
        parts = filename.split('_')
        nom = parts[0] if len(parts) > 0 else 'Etudiant'
        prenom = parts[1] if len(parts) > 1 else ''

        copies_data.append({
            'transcription': transcription.get('transcribed_text', ''),
            'etudiant_nom': nom,
            'etudiant_prenom': prenom,
            'file_path': str(copy_file)
        })

    # Process with AI
    results = process_copies_with_ai(eval_data, copies_data, profile)

    # Save results
    for result in results:
        student_name = f"{result.get('etudiant_nom', 'Unknown')}_{result.get('etudiant_prenom', '')}".replace(" ", "_")
        save_correction_result(eval_id, student_name, result)

    # Update evaluation with correction count
    eval_data['nombre_corriges'] = len(results)
    eval_file = eval_dir / "infos_evaluation.json"
    with open(eval_file, "w", encoding="utf-8") as f:
        json.dump(eval_data, f, ensure_ascii=False, indent=2, default=str)


@router.post("/process")
async def launch_correction(
    request: CorrectionRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_professor_user)
):
    """
    Launch AI correction process for an evaluation
    """
    eval_dir = EVALUATIONS_PATH / request.evaluation_id
    eval_file = eval_dir / "infos_evaluation.json"

    if not eval_file.exists():
        raise NotFoundException("Evaluation", request.evaluation_id)

    with open(eval_file, "r", encoding="utf-8") as f:
        eval_data = json.load(f)

    # Check if evaluation is closed
    if eval_data.get("statut") == "ouvert":
        raise BadRequestException("L'evaluation doit etre fermee avant la correction")

    # Count copies to correct
    copies_dir = eval_dir / "copies_soumises"
    copies_count = len(list(copies_dir.glob("*.pdf"))) if copies_dir.exists() else 0

    if copies_count == 0:
        raise BadRequestException("Aucune copie a corriger")

    # Launch AI correction in background
    profile = request.profile if request.profile else "equilibre"
    background_tasks.add_task(run_ai_correction, request.evaluation_id, eval_data, profile)

    return CorrectionProgress(
        evaluation_id=request.evaluation_id,
        total_copies=copies_count,
        copies_traitees=0,
        copies_reussies=0,
        copies_en_erreur=0,
        pourcentage_progression=0,
        statut="en_cours",
        temps_ecoule_ms=0
    )


@router.get("/evaluation/{eval_id}/results")
async def get_evaluation_results(
    eval_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get all correction results for an evaluation

    Students only see their own results if published.
    Professors see all results.
    """
    corrections = list_all_corrections(eval_id)

    # Check user role
    user_role = current_user.get("role")

    if user_role == "student":
        # Load evaluation to check publication status
        eval_file = EVALUATIONS_PATH / eval_id / "infos_evaluation.json"
        if eval_file.exists():
            with open(eval_file, "r", encoding="utf-8") as f:
                eval_data = json.load(f)

            if eval_data.get("statut_publication") != "publie":
                return {"message": "Resultats non encore publies", "results": []}

        # Filter to only student's results
        student_nom = current_user.get("nom", "")
        student_prenom = current_user.get("prenom", "")

        corrections = [
            c for c in corrections
            if c.get("etudiant_nom") == student_nom and c.get("etudiant_prenom") == student_prenom
        ]

    return corrections


@router.get("/evaluation/{eval_id}/statistics")
async def get_evaluation_statistics(
    eval_id: str,
    current_user: dict = Depends(get_professor_user)
):
    """
    Get class statistics for an evaluation (professors only)
    """
    corrections = list_all_corrections(eval_id)
    stats = calculate_class_statistics(corrections, eval_id)

    return stats


@router.get("/student/{eval_id}")
async def get_student_result(
    eval_id: str,
    nom: str = Query(...),
    prenom: str = Query(...),
    current_user: dict = Depends(get_student_user)
):
    """
    Get individual student result
    """
    # Check publication status
    eval_file = EVALUATIONS_PATH / eval_id / "infos_evaluation.json"
    if eval_file.exists():
        with open(eval_file, "r", encoding="utf-8") as f:
            eval_data = json.load(f)

        if eval_data.get("statut_publication") != "publie":
            raise BadRequestException("Les resultats ne sont pas encore publies")

    student_name = f"{nom}_{prenom}".replace(" ", "_")
    result = load_correction_result(eval_id, student_name)

    if not result:
        raise NotFoundException("Resultat", f"{nom} {prenom}")

    return result


@router.post("/evaluation/{eval_id}/result")
async def save_correction(
    eval_id: str,
    result: dict,
    current_user: dict = Depends(get_professor_user)
):
    """
    Save a correction result (for manual corrections or AI results)
    """
    student_name = f"{result.get('etudiant_nom', 'Unknown')}_{result.get('etudiant_prenom', '')}".replace(" ", "_")

    result["date_correction"] = datetime.now().isoformat()
    save_correction_result(eval_id, student_name, result)

    return {"message": f"Resultat enregistre pour {student_name}"}
