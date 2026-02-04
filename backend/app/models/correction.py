"""
Correction Models
"""
from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class CorrectionProfile(str, Enum):
    """AI correction profile"""
    EXCELLENCE = "excellence"  # GPT-4, detailed, slow
    BALANCED = "equilibre"     # GPT-4o, balanced
    FAST = "rapide"            # GPT-4o-mini, fast


class QualityLevel(str, Enum):
    """Writing quality level"""
    EXCELLENT = "EXCELLENT"
    GOOD = "BON"
    AVERAGE = "MOYEN"
    DIFFICULT = "DIFFICILE"
    ILLEGIBLE = "ILLISIBLE"


class TranscriptionResult(BaseModel):
    """OCR transcription result"""
    texte_transcrit: str
    qualite_ecriture: QualityLevel = QualityLevel.AVERAGE
    confiance_globale: float = Field(0.0, ge=0, le=100)
    mots_incertains: List[Dict[str, Any]] = []
    structure_detectee: Dict[str, Any] = {}
    formules_maths: List[Dict[str, Any]] = []
    temps_transcription_ms: float = 0.0
    erreurs_transcription: List[str] = []
    suggestions_amelioration: List[str] = []
    nombre_pages: int = 1
    nombre_mots: int = 0
    nombre_caracteres: int = 0
    matiere: str = "general"
    type_exercice: str = "redaction"
    modele_utilise: str = "gpt-4o"


class QuestionCorrection(BaseModel):
    """Correction for a single question"""
    question_id: str
    numero_question: int
    note_obtenue: float
    note_max: float
    pourcentage: float
    commentaire_intelligent: str
    conseil_personnalise: str
    erreurs_identifiees: List[str] = []
    points_forts: List[str] = []
    points_amelioration: List[str] = []


class CorrectionResult(BaseModel):
    """Full correction result for a student"""
    id: str
    evaluation_id: str
    submission_id: str
    etudiant_nom: str
    etudiant_prenom: str
    note_globale: float
    note_max: float
    pourcentage: float
    rang: Optional[int] = None
    performance: str = "moyen"  # excellent, bon, moyen, insuffisant
    notes_par_question: List[QuestionCorrection] = []
    notes_par_critere: Dict[str, float] = {}
    commentaires_generaux: List[str] = []
    suggestions_globales: List[str] = []
    points_forts: List[str] = []
    points_amelioration: List[str] = []
    conseils_revision: List[str] = []
    erreurs_detectees: List[Dict[str, Any]] = []
    bonus_appliques: List[Dict[str, Any]] = []
    penalites_appliquees: List[Dict[str, Any]] = []
    temps_correction_ms: float = 0.0
    confiance_correction: float = 0.0
    methode_correction: str = "expert_gpt4"
    transcription: Optional[TranscriptionResult] = None
    statut_publication: str = "brouillon"
    date_correction: datetime = Field(default_factory=datetime.now)
    date_publication: Optional[datetime] = None

    class Config:
        from_attributes = True


class ClassStatistics(BaseModel):
    """Statistics for an entire class/evaluation"""
    evaluation_id: str
    nombre_copies: int
    nombre_corriges: int
    moyenne_generale: float
    mediane: float
    ecart_type: float
    note_min: float
    note_max: float
    taux_reussite: float  # % of students above passing grade
    distribution_notes: Dict[str, int] = {}  # {"0-5": 2, "5-10": 5, ...}
    notes_par_critere: Dict[str, float] = {}
    difficultes_communes: List[Dict[str, Any]] = []
    points_forts_classe: List[str] = []
    recommandations_pedagogiques: List[str] = []
    date_calcul: datetime = Field(default_factory=datetime.now)


class CorrectionRequest(BaseModel):
    """Request to launch AI correction"""
    evaluation_id: str
    profile: CorrectionProfile = CorrectionProfile.BALANCED
    copies_to_correct: Optional[List[str]] = None  # None = all copies
    options: Dict[str, Any] = {}


class CorrectionProgress(BaseModel):
    """Correction progress update"""
    evaluation_id: str
    total_copies: int
    copies_traitees: int
    copies_reussies: int
    copies_en_erreur: int
    pourcentage_progression: float
    statut: str = "en_cours"  # en_cours, termine, erreur
    temps_ecoule_ms: float = 0.0
    temps_estime_restant_ms: Optional[float] = None
    erreurs: List[str] = []
