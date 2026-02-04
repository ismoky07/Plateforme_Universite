"""
Evaluation Models
"""
from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class EvaluationStatus(str, Enum):
    """Evaluation status enumeration"""
    DRAFT = "brouillon"
    PUBLISHED = "publie"
    UNPUBLISHED = "depublie"
    OPEN = "ouvert"
    CLOSED = "ferme"
    EXPIRED = "expire"


class PublicationStatus(str, Enum):
    """Publication status for results"""
    DRAFT = "brouillon"
    PUBLISHED = "publie"
    UNPUBLISHED = "depublie"


class Question(BaseModel):
    """Question model for evaluations"""
    id: str
    numero: int
    texte: str
    points: float = Field(..., ge=0)
    type_question: str = "redaction"  # redaction, qcm, calcul, etc.
    criteres: Optional[Dict[str, float]] = None
    reponse_attendue: Optional[str] = None


class EvaluationBase(BaseModel):
    """Base evaluation model"""
    titre: str = Field(..., min_length=3, max_length=200)
    matiere: str = Field(..., min_length=2, max_length=100)
    classe: str = Field(..., min_length=2, max_length=50)
    type_epreuve: str = "examen"  # examen, controle, devoir
    duree_minutes: int = Field(120, ge=15, le=480)
    date_examen: Optional[datetime] = None
    heure_debut: Optional[str] = None
    enseignant: Optional[str] = None
    etablissement: Optional[str] = None
    consignes_specifiques: Optional[str] = None


class EvaluationCreate(EvaluationBase):
    """Evaluation creation model"""
    questions: List[Question] = []
    note_totale: float = Field(20.0, ge=1)


class EvaluationUpdate(BaseModel):
    """Evaluation update model"""
    titre: Optional[str] = None
    matiere: Optional[str] = None
    classe: Optional[str] = None
    type_epreuve: Optional[str] = None
    duree_minutes: Optional[int] = None
    date_examen: Optional[datetime] = None
    heure_debut: Optional[str] = None
    consignes_specifiques: Optional[str] = None
    questions: Optional[List[Question]] = None


class Evaluation(EvaluationBase):
    """Full evaluation model"""
    id: str
    questions: List[Question] = []
    note_totale: float = 20.0
    statut: EvaluationStatus = EvaluationStatus.DRAFT
    statut_publication: PublicationStatus = PublicationStatus.DRAFT
    date_creation: datetime
    date_publication: Optional[datetime] = None
    date_depublication: Optional[datetime] = None
    publie_par: Optional[str] = None
    depublie_par: Optional[str] = None
    dossier: str  # Path to evaluation folder
    nombre_copies: int = 0
    nombre_corriges: int = 0

    class Config:
        from_attributes = True


class EvaluationSummary(BaseModel):
    """Summary model for listing evaluations"""
    id: str
    titre: str
    matiere: str
    classe: str
    type_epreuve: str
    date_examen: Optional[datetime]
    statut: EvaluationStatus
    statut_publication: PublicationStatus
    nombre_copies: int
    nombre_corriges: int
    date_creation: datetime


class EvaluationPublishRequest(BaseModel):
    """Request model for publishing evaluation results"""
    notify_students: bool = False
    message: Optional[str] = None
