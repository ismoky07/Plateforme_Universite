# Models Package
from app.models.user import User, UserRole, UserInDB
from app.models.evaluation import Evaluation, EvaluationStatus, Question
from app.models.submission import Submission, SubmissionType
from app.models.correction import CorrectionResult, ClassStatistics
from app.models.candidature import Candidature, PersonalInfo, Grade, UploadedDocument
from app.models.bareme import BaremeItem, BaremeComplet

__all__ = [
    "User", "UserRole", "UserInDB",
    "Evaluation", "EvaluationStatus", "Question",
    "Submission", "SubmissionType",
    "CorrectionResult", "ClassStatistics",
    "Candidature", "PersonalInfo", "Grade", "UploadedDocument",
    "BaremeItem", "BaremeComplet"
]
