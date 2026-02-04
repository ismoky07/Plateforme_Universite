"""
Bareme (Grading Scale) Models
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class BaremeItem(BaseModel):
    """Single grading item in a bareme"""
    id: str
    titre: str
    points_max: float = Field(..., ge=0)
    criteres: Dict[str, float] = {}  # {"orthographe": 2.0, "grammaire": 1.5}
    elements_attendus: List[str] = []
    penalites: Dict[str, float] = {}  # {"hors_sujet": -1.0}
    bonus: Dict[str, float] = {}  # {"originalite": 0.5}
    niveau_requis: str = "moyen"  # facile, moyen, difficile


class BaremeComplet(BaseModel):
    """Complete grading scale for an evaluation"""
    id: str
    matiere: str
    classe: str
    type_epreuve: str
    duree_minutes: int = 120
    note_totale: float = 20.0
    items: List[BaremeItem] = []
    criteres_globaux: Dict[str, float] = {}
    regles_arrondi: str = "demi_point"  # entier, demi_point, dixieme
    penalites_globales: Dict[str, float] = {}
    metadata: Dict[str, Any] = {}

    def total_points(self) -> float:
        """Calculate total points from all items"""
        return sum(item.points_max for item in self.items)

    def validate_total(self) -> bool:
        """Validate that items total matches note_totale"""
        return abs(self.total_points() - self.note_totale) < 0.01


class CorrigeType(BaseModel):
    """Model answer for a question"""
    question_id: str
    reponse_ideale: str
    mots_cles: List[str] = []
    concepts_essentiels: List[str] = []
    exemples_acceptables: List[str] = []
    variantes_acceptees: List[str] = []
    erreurs_frequentes: List[Dict[str, Any]] = []  # [{"erreur": str, "penalite": float}]


class BaremeValidation(BaseModel):
    """Validation result for a bareme"""
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    suggestions: List[str] = []
    total_points_calculated: float
    total_points_expected: float
