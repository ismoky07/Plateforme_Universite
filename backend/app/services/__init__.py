# Services Package
# Business logic services

from .ai_correction_service import (
    AICorrectionEngine,
    process_copies_with_ai,
    correct_single_copy_with_ai,
)

from .ai_ocr_service import (
    OCRProcessor,
    transcribe_manuscript,
    transcribe_manuscript_bytes,
)

from .pdf_report_service import (
    StudentReportGenerator,
    generate_student_pdf_report,
)

__all__ = [
    # AI Correction
    "AICorrectionEngine",
    "process_copies_with_ai",
    "correct_single_copy_with_ai",
    # OCR
    "OCRProcessor",
    "transcribe_manuscript",
    "transcribe_manuscript_bytes",
    # PDF Reports
    "StudentReportGenerator",
    "generate_student_pdf_report",
]