"""
Candidature Models (Student Application Forms)
"""
from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class ValidationStatus(str, Enum):
    """Candidature validation status"""
    PENDING = "en_attente"
    VALIDATED = "validee"
    REJECTED = "rejetee"
    UNDER_REVIEW = "en_cours_verification"


class DiscrepancySeverity(str, Enum):
    """Grade discrepancy severity"""
    LIGHT = "LEGER"
    MODERATE = "MODERE"
    SEVERE = "GRAVE"


class PersonalInfo(BaseModel):
    """Personal information for candidature"""
    nom: str = Field(..., min_length=2, max_length=100)
    prenom: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    telephone: Optional[str] = None
    niveau_etude: str = Field(..., description="Study level: bac, licence, master")
    date_naissance: Optional[str] = None
    nationalite: Optional[str] = None
    adresse: Optional[str] = None

    @property
    def full_name(self) -> str:
        return f"{self.prenom} {self.nom}"

    def is_complete(self) -> bool:
        return bool(self.nom and self.prenom and self.email and self.niveau_etude)


class Grade(BaseModel):
    """Grade entry for candidature"""
    id: Optional[int] = None
    matiere: str = Field(..., min_length=2, max_length=100)
    note: float = Field(..., ge=0, le=20)
    coefficient: int = Field(..., ge=1, le=20)
    periode: str  # "1er semestre", "2eme semestre", etc.
    annee: str  # "2023", "2024", etc.

    def is_valid(self) -> bool:
        return 0 <= self.note <= 20 and 1 <= self.coefficient <= 20 and bool(self.matiere)

    @property
    def weighted_value(self) -> float:
        return self.note * self.coefficient


class UploadedDocument(BaseModel):
    """Uploaded document information"""
    year: str
    filename: str
    original_filename: str
    size: int  # bytes
    file_type: str  # pdf, jpg, png
    upload_date: datetime = Field(default_factory=datetime.now)

    @property
    def size_mb(self) -> float:
        return round(self.size / (1024 * 1024), 2)


class GradeDiscrepancy(BaseModel):
    """Discrepancy between declared and official grades"""
    matiere: str
    periode: str
    annee: str
    note_declaree: float
    note_bulletin: float
    ecart: float
    gravite: DiscrepancySeverity


class IdentityVerification(BaseModel):
    """Identity verification result"""
    identite_valide: bool
    nom_formulaire: str
    prenom_formulaire: str
    identites_bulletins: List[Dict[str, str]] = []
    usurpation_detectee: bool = False
    details_erreur: Optional[str] = None


class VerificationResult(BaseModel):
    """Full verification result for a candidature"""
    candidature_id: str
    verification_identite: IdentityVerification
    discordances: List[GradeDiscrepancy] = []
    notes_non_verifiables: List[Dict[str, Any]] = []
    confiance_globale: float = 0.0
    recommandation: str = "verification_manuelle"
    date_verification: datetime = Field(default_factory=datetime.now)


class CandidatureBase(BaseModel):
    """Base candidature model"""
    personal_info: PersonalInfo
    grades: List[Grade] = []
    documents: List[UploadedDocument] = []


class CandidatureCreate(CandidatureBase):
    """Candidature creation model"""
    pass


class Candidature(CandidatureBase):
    """Full candidature model"""
    id: str
    date_soumission: datetime
    statut: ValidationStatus = ValidationStatus.PENDING
    dossier_path: str
    moyenne_generale: Optional[float] = None
    completion_percentage: float = 0.0
    verification_result: Optional[VerificationResult] = None
    commentaires_admin: List[str] = []
    date_validation: Optional[datetime] = None
    valide_par: Optional[str] = None

    class Config:
        from_attributes = True

    def calculate_average(self) -> float:
        """Calculate weighted average of valid grades"""
        valid_grades = [g for g in self.grades if g.is_valid()]
        if not valid_grades:
            return 0.0
        total_weighted = sum(g.weighted_value for g in valid_grades)
        total_coef = sum(g.coefficient for g in valid_grades)
        return round(total_weighted / total_coef, 2) if total_coef > 0 else 0.0


class CandidatureSummary(BaseModel):
    """Summary model for listing candidatures"""
    id: str
    nom: str
    prenom: str
    email: str
    niveau_etude: str
    date_soumission: datetime
    statut: ValidationStatus
    moyenne_generale: Optional[float]
    completion_percentage: float
    nombre_documents: int


class CandidatureValidationRequest(BaseModel):
    """Request to validate/reject a candidature"""
    decision: ValidationStatus
    commentaire: Optional[str] = None
    notify_candidate: bool = True
