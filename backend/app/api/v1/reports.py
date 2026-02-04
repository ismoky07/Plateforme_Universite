"""
Reports API Routes
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse, StreamingResponse, Response
import io

from app.api.deps import get_professor_user, get_student_user, get_current_user
from app.core.exceptions import NotFoundException, BadRequestException
from app.config import settings
from app.services import generate_student_pdf_report

router = APIRouter()

EVALUATIONS_PATH = Path(settings.DATA_DIR) / "evaluations"


@router.get("/evaluation/{eval_id}")
async def list_evaluation_reports(
    eval_id: str,
    current_user: dict = Depends(get_professor_user)
):
    """
    List available reports for an evaluation (professors only)
    """
    reports_dir = EVALUATIONS_PATH / eval_id / "rapports"

    if not reports_dir.exists():
        return []

    reports = []
    for report_file in reports_dir.iterdir():
        if report_file.is_file():
            reports.append({
                "filename": report_file.name,
                "type": report_file.suffix.lstrip("."),
                "size": report_file.stat().st_size,
                "created": datetime.fromtimestamp(report_file.stat().st_ctime).isoformat()
            })

    return reports


@router.get("/evaluation/{eval_id}/student/{student_name}")
async def get_student_report(
    eval_id: str,
    student_name: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get student report

    Students can only access their own reports if published.
    """
    # Check publication status for students
    user_role = current_user.get("role")
    if user_role == "student":
        eval_file = EVALUATIONS_PATH / eval_id / "infos_evaluation.json"
        if eval_file.exists():
            with open(eval_file, "r", encoding="utf-8") as f:
                eval_data = json.load(f)

            if eval_data.get("statut_publication") != "publie":
                raise BadRequestException("Les rapports ne sont pas encore disponibles")

            # Verify student identity
            token_nom = current_user.get("nom", "")
            token_prenom = current_user.get("prenom", "")
            expected_name = f"{token_nom}_{token_prenom}".replace(" ", "_")

            if student_name != expected_name:
                raise BadRequestException("Vous ne pouvez acceder qu'a votre propre rapport")

    # Look for report
    reports_dir = EVALUATIONS_PATH / eval_id / "rapports"
    report_patterns = [
        f"{student_name}_rapport.pdf",
        f"rapport_{student_name}.pdf",
        f"{student_name}.pdf"
    ]

    for pattern in report_patterns:
        report_file = reports_dir / pattern
        if report_file.exists():
            return FileResponse(
                report_file,
                media_type="application/pdf",
                filename=f"rapport_{student_name}.pdf"
            )

    raise NotFoundException("Rapport", student_name)


@router.post("/evaluation/{eval_id}/generate")
async def generate_reports(
    eval_id: str,
    format: str = Query("pdf", enum=["pdf", "xlsx", "json"]),
    current_user: dict = Depends(get_professor_user)
):
    """
    Generate reports for an evaluation (professors only)
    """
    eval_dir = EVALUATIONS_PATH / eval_id
    eval_file = eval_dir / "infos_evaluation.json"

    if not eval_file.exists():
        raise NotFoundException("Evaluation", eval_id)

    with open(eval_file, "r", encoding="utf-8") as f:
        eval_data = json.load(f)

    # Check if corrections exist
    results_dir = eval_dir / "resultats"
    if not results_dir.exists() or not list(results_dir.iterdir()):
        raise BadRequestException("Aucune correction disponible pour generer des rapports")

    # Create reports directory
    reports_dir = eval_dir / "rapports"
    reports_dir.mkdir(exist_ok=True)

    generated_count = 0

    # Generate PDF reports for each student
    if format == "pdf":
        for student_dir in results_dir.iterdir():
            if student_dir.is_dir():
                result_file = student_dir / "correction_detaillee.json"
                if result_file.exists():
                    with open(result_file, "r", encoding="utf-8") as f:
                        result_data = json.load(f)

                    student_info = {
                        "nom": result_data.get("etudiant_nom", ""),
                        "prenom": result_data.get("etudiant_prenom", "")
                    }

                    try:
                        pdf_bytes = generate_student_pdf_report(result_data, eval_data, student_info)
                        pdf_path = reports_dir / f"{student_dir.name}_rapport.pdf"
                        with open(pdf_path, "wb") as pdf_file:
                            pdf_file.write(pdf_bytes)
                        generated_count += 1
                    except Exception as e:
                        print(f"Erreur generation PDF pour {student_dir.name}: {e}")

    return {
        "message": f"Generation des rapports {format} terminee",
        "evaluation_id": eval_id,
        "format": format,
        "rapports_generes": generated_count,
        "statut": "termine"
    }


@router.get("/evaluation/{eval_id}/student/{student_name}/pdf")
async def generate_single_student_report(
    eval_id: str,
    student_name: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate and download a single student report PDF
    """
    eval_dir = EVALUATIONS_PATH / eval_id
    eval_file = eval_dir / "infos_evaluation.json"

    if not eval_file.exists():
        raise NotFoundException("Evaluation", eval_id)

    with open(eval_file, "r", encoding="utf-8") as f:
        eval_data = json.load(f)

    # Check publication status for students
    user_role = current_user.get("role")
    if user_role == "student":
        if eval_data.get("statut_publication") != "publie":
            raise BadRequestException("Les rapports ne sont pas encore disponibles")

        token_nom = current_user.get("nom", "")
        token_prenom = current_user.get("prenom", "")
        expected_name = f"{token_nom}_{token_prenom}".replace(" ", "_")

        if student_name != expected_name:
            raise BadRequestException("Vous ne pouvez acceder qu'a votre propre rapport")

    # Load student result
    result_file = eval_dir / "resultats" / student_name / "correction_detaillee.json"
    if not result_file.exists():
        raise NotFoundException("Resultat", student_name)

    with open(result_file, "r", encoding="utf-8") as f:
        result_data = json.load(f)

    student_info = {
        "nom": result_data.get("etudiant_nom", ""),
        "prenom": result_data.get("etudiant_prenom", "")
    }

    # Generate PDF
    pdf_bytes = generate_student_pdf_report(result_data, eval_data, student_info)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=rapport_{student_name}.pdf"}
    )


@router.get("/evaluation/{eval_id}/export")
async def export_results(
    eval_id: str,
    format: str = Query("xlsx", enum=["xlsx", "csv", "json"]),
    current_user: dict = Depends(get_professor_user)
):
    """
    Export all results for an evaluation
    """
    results_dir = EVALUATIONS_PATH / eval_id / "resultats"

    if not results_dir.exists():
        raise NotFoundException("Resultats", eval_id)

    # Collect all results
    all_results = []
    for student_dir in results_dir.iterdir():
        if student_dir.is_dir():
            result_file = student_dir / "correction_detaillee.json"
            if result_file.exists():
                with open(result_file, "r", encoding="utf-8") as f:
                    all_results.append(json.load(f))

    if not all_results:
        raise BadRequestException("Aucun resultat a exporter")

    if format == "json":
        return all_results

    # For xlsx/csv, return simple format
    export_data = []
    for result in all_results:
        export_data.append({
            "Nom": result.get("etudiant_nom", ""),
            "Prenom": result.get("etudiant_prenom", ""),
            "Note": result.get("note_globale", 0),
            "Note Max": result.get("note_max", 20),
            "Pourcentage": result.get("pourcentage", 0),
            "Performance": result.get("performance", ""),
            "Date Correction": result.get("date_correction", "")
        })

    return export_data


@router.get("/student/my-reports")
async def get_my_reports(
    current_user: dict = Depends(get_student_user)
):
    """
    Get all reports for current student
    """
    nom = current_user.get("nom", "")
    prenom = current_user.get("prenom", "")

    if not nom or not prenom:
        raise BadRequestException("Informations etudiant manquantes")

    student_name = f"{nom}_{prenom}".replace(" ", "_")
    reports = []

    # Search all evaluations for student's reports
    if EVALUATIONS_PATH.exists():
        for eval_dir in EVALUATIONS_PATH.iterdir():
            if eval_dir.is_dir():
                # Check if published
                eval_file = eval_dir / "infos_evaluation.json"
                if eval_file.exists():
                    with open(eval_file, "r", encoding="utf-8") as f:
                        eval_data = json.load(f)

                    if eval_data.get("statut_publication") != "publie":
                        continue

                    # Check for student's result
                    result_dir = eval_dir / "resultats" / student_name
                    if result_dir.exists():
                        result_file = result_dir / "correction_detaillee.json"
                        if result_file.exists():
                            with open(result_file, "r", encoding="utf-8") as f:
                                result_data = json.load(f)

                            reports.append({
                                "evaluation_id": eval_dir.name,
                                "evaluation_titre": eval_data.get("titre", ""),
                                "matiere": eval_data.get("matiere", ""),
                                "note": result_data.get("note_globale", 0),
                                "note_max": result_data.get("note_max", 20),
                                "date_correction": result_data.get("date_correction", ""),
                                "has_pdf": (eval_dir / "rapports" / f"{student_name}_rapport.pdf").exists()
                            })

    return reports
