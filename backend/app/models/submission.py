"""
Submission Models
"""
from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class SubmissionType(str, Enum):
    """Submission type enumeration"""
    SCANNED = "fichier_scanne"
    PHOTO = "photo"
    DIGITAL = "numerique"


class SubmissionStatus(str, Enum):
    """Submission status"""
    PENDING = "en_attente"
    RECEIVED = "recu"
    PROCESSING = "en_traitement"
    CORRECTED = "corrige"
    ERROR = "erreur"


class SubmittedFile(BaseModel):
    """Submitted file information"""
    nom_original: str
    nom_sauvegarde: str
    taille: int  # bytes
    type_fichier: str
    date_upload: datetime = Field(default_factory=datetime.now)


class SubmissionBase(BaseModel):
    """Base submission model"""
    evaluation_id: str
    etudiant_nom: str
    etudiant_prenom: str
    numero_etudiant: Optional[str] = None
    type_soumission: SubmissionType


class SubmissionCreate(SubmissionBase):
    """Submission creation model"""
    reponse_numerique: Optional[str] = None  # For digital submissions


class Submission(SubmissionBase):
    """Full submission model"""
    id: str
    date_soumission: datetime
    statut: SubmissionStatus = SubmissionStatus.PENDING
    fichiers_soumis: List[SubmittedFile] = []
    nombre_fichiers: int = 0
    taille_totale: int = 0  # bytes
    reponse_numerique: Optional[str] = None
    note_finale: Optional[float] = None
    corrige: bool = False
    date_correction: Optional[datetime] = None

    class Config:
        from_attributes = True

    @property
    def taille_totale_mb(self) -> float:
        """Total size in megabytes"""
        return round(self.taille_totale / (1024 * 1024), 2)


class SubmissionSummary(BaseModel):
    """Summary model for listing submissions"""
    id: str
    evaluation_id: str
    etudiant_nom: str
    etudiant_prenom: str
    date_soumission: datetime
    type_soumission: SubmissionType
    statut: SubmissionStatus
    nombre_fichiers: int
    corrige: bool
    note_finale: Optional[float] = None


class StudentSubmissionCheck(BaseModel):
    """Check if student already submitted"""
    has_submitted: bool
    submission_id: Optional[str] = None
    date_soumission: Optional[datetime] = None
    can_modify: bool = False
