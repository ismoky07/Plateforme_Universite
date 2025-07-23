#!/usr/bin/env python3
"""
Modèles de données consolidés pour le système de correction d'épreuves manuscrites
=================================================================================

Contient TOUS les modèles de données utilisés par le système :
- Modèles de base pour l'examen et les copies
- Modèles pour la transcription OCR et la correction
- Modèles pour le workflow et les statistiques
- Modèles pour les barèmes et corrigés
- Structures de données pour l'analyse d'images

Compatibilité Pydantic v1/v2 assurée.
"""

import os
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime

# ============================================
# GESTION COMPATIBILITÉ PYDANTIC V1/V2
# ============================================

try:
    from pydantic import BaseModel, Field, ConfigDict
    from pydantic.dataclasses import dataclass as pydantic_dataclass
    PYDANTIC_V2 = True
    
    class BaseConfig:
        arbitrary_types_allowed = True
        use_enum_values = True
        validate_assignment = True
        
except ImportError:
    try:
        from pydantic import BaseModel, Field
        from pydantic.dataclasses import dataclass as pydantic_dataclass
        PYDANTIC_V2 = False
        
        class BaseConfig:
            arbitrary_types_allowed = True
            use_enum_values = True
            validate_assignment = True
            
    except ImportError:
        print("⚠️ Pydantic non disponible, utilisation de dataclasses standard")
        
        class BaseModel:
            def __init__(self, **data):
                for key, value in data.items():
                    setattr(self, key, value)
            
            def dict(self):
                return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
            
            def model_dump(self):
                return self.dict()
        
        def Field(default=None, **kwargs):
            return default
            
        def pydantic_dataclass(cls):
            return dataclass(cls)
            
        PYDANTIC_V2 = False
        BaseConfig = None

# ============================================
# MODÈLES DE BASE POUR L'EXAMEN
# ============================================

class ExamenInfo(BaseModel):
    """Informations sur un examen"""
    matiere: str = Field(description="Matière de l'examen")
    classe: str = Field(description="Niveau de classe")
    type_epreuve: str = Field(default="controle", description="Type d'épreuve")
    duree_minutes: int = Field(default=120, description="Durée en minutes")
    date_examen: Optional[str] = Field(default=None, description="Date de l'examen")
    enseignant: Optional[str] = Field(default=None, description="Nom de l'enseignant")
    etablissement: Optional[str] = Field(default=None, description="Nom de l'établissement")
    consignes_specifiques: Optional[str] = Field(default=None, description="Consignes particulières")
    
    if BaseConfig:
        class Config(BaseConfig):
            pass

class CopieEleve(BaseModel):
    """Informations sur une copie d'élève"""
    nom_fichier: str = Field(description="Nom du fichier de copie")
    chemin_complet: str = Field(description="Chemin complet vers le fichier")
    nom_eleve: Optional[str] = Field(default=None, description="Nom de l'élève")
    numero_copie: Optional[str] = Field(default=None, description="Numéro de copie")
    
    # Métadonnées fichier
    taille_fichier: Optional[int] = Field(default=None, description="Taille en bytes")
    format_fichier: Optional[str] = Field(default=None, description="Extension du fichier")
    date_creation: Optional[str] = Field(default=None, description="Date de création")
    
    # Statut de traitement
    statut_validation: str = Field(default="non_traite", description="Statut de validation")
    erreurs_validation: List[str] = Field(default_factory=list, description="Erreurs de validation")
    qualite_image: Optional[str] = Field(default=None, description="Qualité de l'image")
    
    if BaseConfig:
        class Config(BaseConfig):
            pass

# ============================================
# MODÈLES POUR LES BARÈMES (consolidé depuis bareme_loader.py)
# ============================================

@dataclass
class BaremeItem:
    """Élément d'un barème de correction"""
    id: str
    titre: str
    points_max: float
    criteres: Dict[str, float]  # {'orthographe': 2.0, 'contenu': 3.0}
    elements_attendus: List[str]
    penalites: Dict[str, float]  # {'hors_sujet': -1.0, 'trop_court': -0.5}
    bonus: Dict[str, float]      # {'originalite': 0.5, 'exemples': 1.0}
    niveau_requis: str           # 'facile', 'moyen', 'difficile'

@dataclass
class BaremeComplet:
    """Barème complet d'un examen"""
    matiere: str
    classe: str
    type_epreuve: str
    duree_minutes: int
    note_totale: float
    items: List[BaremeItem]
    criteres_globaux: Dict[str, float]
    regles_arrondi: str
    penalites_globales: Dict[str, float]
    metadata: Dict[str, Any]

@dataclass
class CorrigeType:
    """Corrigé de référence"""
    question_id: str
    reponse_ideale: str
    mots_cles: List[str]
    concepts_essentiels: List[str]
    exemples_acceptables: List[str]
    variantes_acceptees: List[str]
    erreurs_frequentes: List[Dict[str, str]]  # [{'erreur': 'confusion X/Y', 'penalite': -0.5}]

# ============================================
# MODÈLES POUR L'ANALYSE D'IMAGES (consolidé depuis charger_copies.py)
# ============================================

@dataclass
class StructureCopie:
    """Structure détectée d'une copie d'examen"""
    nom_fichier: str
    nombre_pages: int
    pages_detectees: List[str]
    zones_questions: List[Dict]
    qualite_images: List[str]
    orientation_correcte: bool
    format_valide: bool
    erreurs_detectees: List[str]

# ============================================
# MODÈLES POUR LA TRANSCRIPTION OCR (consolidé depuis ocr_manuscrit.py)
# ============================================

@dataclass
class TranscriptionManuscrite:
    """Résultat de transcription d'un texte manuscrit"""
    texte_transcrit: str
    qualite_ecriture: str
    confiance_globale: float
    mots_incertains: List[Dict]
    structure_detectee: Dict
    formules_maths: List[Dict]
    erreurs_transcription: List[str]
    suggestions_amelioration: List[str]

class TranscriptionManuscriteModel(BaseModel):
    """Version BaseModel de TranscriptionManuscrite pour compatibilité"""
    texte_transcrit: str = Field(description="Texte complet transcrit")
    qualite_ecriture: str = Field(description="Qualité de l'écriture détectée")
    confiance_globale: float = Field(default=0.0, description="Score de confiance 0-100%")
    
    # Détails de transcription
    mots_incertains: List[Dict[str, Any]] = Field(default_factory=list, description="Mots difficiles à lire")
    structure_detectee: Dict[str, Any] = Field(default_factory=dict, description="Structure du document")
    formules_maths: List[Dict[str, Any]] = Field(default_factory=list, description="Formules mathématiques")
    
    # Métadonnées
    temps_transcription_ms: float = Field(default=0.0, description="Temps de transcription")
    erreurs_transcription: List[str] = Field(default_factory=list, description="Erreurs rencontrées")
    suggestions_amelioration: List[str] = Field(default_factory=list, description="Suggestions d'amélioration")
    
    if BaseConfig:
        class Config(BaseConfig):
            pass

# ============================================
# MODÈLES POUR LA CORRECTION (consolidé depuis correction_engine.py)
# ============================================

@dataclass
class ResultatCorrectionDataclass:
    """Résultat détaillé d'une correction (version dataclass)"""
    note_globale: float
    note_max: float
    notes_par_critere: Dict[str, float]
    details_correction: Dict[str, Any]
    commentaires: List[str]
    suggestions: List[str]
    erreurs_detectees: List[Dict]
    bonus_appliques: List[Dict]
    penalites_appliquees: List[Dict]
    temps_correction_ms: float
    confiance_correction: float

class ResultatCorrection(BaseModel):
    """Résultat détaillé d'une correction (version BaseModel)"""
    note_globale: float = Field(description="Note finale obtenue")
    note_max: float = Field(description="Note maximale possible")
    
    # Détails de notation
    notes_par_critere: Dict[str, float] = Field(default_factory=dict, description="Notes par critère")
    details_correction: Dict[str, Any] = Field(default_factory=dict, description="Détails techniques")
    
    # Feedback pédagogique
    commentaires: List[str] = Field(default_factory=list, description="Commentaires de l'enseignant")
    suggestions: List[str] = Field(default_factory=list, description="Conseils d'amélioration")
    
    # Analyse des erreurs
    erreurs_detectees: List[Dict[str, Any]] = Field(default_factory=list, description="Erreurs trouvées")
    bonus_appliques: List[Dict[str, Any]] = Field(default_factory=list, description="Bonus accordés")
    penalites_appliquees: List[Dict[str, Any]] = Field(default_factory=list, description="Pénalités appliquées")
    
    # Métadonnées de correction
    temps_correction_ms: float = Field(default=0.0, description="Temps de correction")
    confiance_correction: float = Field(default=0.0, description="Confiance dans la correction")
    methode_correction: str = Field(default="expert_gpt4", description="Méthode utilisée")
    
    if BaseConfig:
        class Config(BaseConfig):
            pass

# ============================================
# MODÈLES POUR LE WORKFLOW
# ============================================

class CorrectionState(BaseModel):
    """État du workflow de correction"""
    
    # === CONFIGURATION D'ENTRÉE ===
    dossier_copies: str = Field(description="Dossier contenant les copies")
    bareme_path: str = Field(description="Chemin vers le barème")
    corrige_path: Optional[str] = Field(default=None, description="Chemin vers le corrigé")
    
    # Configuration pédagogique
    matiere: str = Field(default="general", description="Matière enseignée")
    classe: str = Field(default="inconnue", description="Niveau de classe")
    type_exercice: str = Field(default="redaction", description="Type d'exercice")
    
    # === DONNÉES DE TRAITEMENT ===
    fichiers_copies: Optional[List[str]] = Field(default=None, description="Liste des fichiers chargés")
    copies_validees: Optional[List[str]] = Field(default=None, description="Copies validées")
    copies_rejetees: Optional[List[str]] = Field(default=None, description="Copies rejetées")
    images_preparees: Optional[List[str]] = Field(default=None, description="Images préparées pour OCR")
    
    # Résultats de traitement
    transcriptions: Optional[Dict[str, Any]] = Field(default=None, description="Résultats OCR")
    corrections: Optional[Dict[str, Any]] = Field(default=None, description="Résultats correction")
    
    # === RESSOURCES CHARGÉES ===
    bareme: Optional[Any] = Field(default=None, description="Barème chargé")
    corriges: Optional[List[Any]] = Field(default=None, description="Corrigés de référence")
    client_ocr: Optional[Any] = Field(default=None, description="Client OCR")
    engine_correction: Optional[Any] = Field(default=None, description="Moteur de correction")
    
    # === RÉSULTATS FINAUX ===
    resultats_correction: Optional[List[Any]] = Field(default=None, description="Toutes les corrections")
    statistiques_classe: Optional[Dict[str, Any]] = Field(default=None, description="Statistiques de classe")
    rapport_path: Optional[str] = Field(default=None, description="Chemin du rapport généré")
    
    # === MÉTADONNÉES WORKFLOW ===
    workflow_status: str = Field(default="INITIALISE", description="Statut du workflow")
    temps_execution: float = Field(default=0.0, description="Temps d'exécution total")
    erreurs_rencontrees: Optional[List[str]] = Field(default=None, description="Erreurs rencontrées")
    
    # Compteurs
    nb_copies_traitees: int = Field(default=0, description="Nombre de copies traitées")
    nb_copies_reussies: int = Field(default=0, description="Nombre de corrections réussies")
    
    if BaseConfig:
        class Config(BaseConfig):
            arbitrary_types_allowed = True

# ============================================
# MODÈLES POUR LES STATISTIQUES
# ============================================

class StatistiquesClasse(BaseModel):
    """Statistiques détaillées d'une classe"""
    
    # Informations de base
    nombre_copies: int = Field(description="Nombre total de copies")
    moyenne_generale: float = Field(description="Moyenne de la classe")
    mediane: float = Field(description="Médiane des notes")
    ecart_type: float = Field(description="Écart-type")
    
    # Répartition des notes
    notes_par_critere: Dict[str, float] = Field(default_factory=dict, description="Moyennes par critère")
    distribution_notes: Dict[str, int] = Field(default_factory=dict, description="Distribution par tranches")
    
    # Indicateurs de performance
    taux_reussite: float = Field(description="Taux de réussite en %")
    note_min: float = Field(default=0.0, description="Note minimale")
    note_max: float = Field(default=0.0, description="Note maximale")
    
    # Analyse qualitative
    difficultes_communes: List[Dict[str, Any]] = Field(default_factory=list, description="Difficultés récurrentes")
    points_forts: List[str] = Field(default_factory=list, description="Points forts de la classe")
    recommendations: List[str] = Field(default_factory=list, description="Recommandations pédagogiques")
    
    if BaseConfig:
        class Config(BaseConfig):
            pass

# ============================================
# MODÈLES POUR LA CONFIGURATION
# ============================================

class ConfigurationAgent(BaseModel):
    """Configuration de l'agent de correction"""
    
    # Configuration générale
    version_agent: str = Field(default="1.0", description="Version de l'agent")
    mode_debug: bool = Field(default=False, description="Mode debug activé")
    log_level: str = Field(default="INFO", description="Niveau de log")
    
    # Configuration OCR
    qualite_ocr_minimum: str = Field(default="MOYENNE", description="Qualité OCR minimale acceptée")
    langue_principale: str = Field(default="fr", description="Langue principale des copies")
    detecter_langue_auto: bool = Field(default=True, description="Détection automatique de langue")
    
    # Configuration correction
    confiance_correction_min: float = Field(default=70.0, description="Confiance minimale correction")
    generer_bulletins: bool = Field(default=True, description="Générer les bulletins individuels")
    format_notes: str = Field(default="decimal", description="Format d'affichage des notes")
    
    # Configuration des exports
    exporter_json: bool = Field(default=True, description="Exporter en JSON")
    exporter_csv: bool = Field(default=True, description="Exporter en CSV")
    exporter_pdf: bool = Field(default=False, description="Exporter en PDF")
    
    # Paramètres avancés
    timeout_ocr_seconde: int = Field(default=120, description="Timeout OCR par copie")
    nb_tentatives_max: int = Field(default=3, description="Nombre max de tentatives")
    utiliser_cache: bool = Field(default=True, description="Utiliser le cache")
    
    if BaseConfig:
        class Config(BaseConfig):
            pass

# ============================================
# MODÈLES POUR LES RAPPORTS
# ============================================

class RapportCorrection(BaseModel):
    """Modèle pour un rapport de correction complet"""
    
    # Métadonnées du rapport
    id_rapport: str = Field(description="Identifiant unique du rapport")
    date_generation: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Date de génération")
    version_rapport: str = Field(default="1.0", description="Version du format de rapport")
    
    # Informations de contexte
    examen_info: ExamenInfo = Field(description="Informations sur l'examen")
    configuration_utilisee: ConfigurationAgent = Field(description="Configuration utilisée")
    
    # Résultats de correction
    statistiques_globales: StatistiquesClasse = Field(description="Statistiques de la classe")
    corrections_individuelles: List[ResultatCorrection] = Field(description="Corrections par élève")
    
    # Analyses et recommandations
    analyse_qualite_ocr: Dict[str, Any] = Field(default_factory=dict, description="Analyse qualité OCR")
    recommandations_pedagogiques: List[str] = Field(default_factory=list, description="Recommandations pour l'enseignant")
    points_attention: List[str] = Field(default_factory=list, description="Points nécessitant attention")
    
    # Métadonnées techniques
    temps_total_traitement: float = Field(description="Temps total de traitement")
    erreurs_rencontrees: List[str] = Field(default_factory=list, description="Erreurs techniques")
    fichiers_generes: Dict[str, str] = Field(default_factory=dict, description="Fichiers de sortie générés")
    
    if BaseConfig:
        class Config(BaseConfig):
            pass

# ============================================
# FONCTIONS UTILITAIRES DE COMPATIBILITÉ
# ============================================

def convertir_en_dict(obj: Union[BaseModel, Any]) -> Dict[str, Any]:
    """Convertit un objet en dictionnaire avec compatibilité Pydantic v1/v2"""
    if isinstance(obj, BaseModel):
        try:
            return obj.model_dump()  # Pydantic v2
        except AttributeError:
            try:
                return obj.dict()    # Pydantic v1 fallback
            except AttributeError:
                return obj.__dict__ if hasattr(obj, '__dict__') else {"valeur": str(obj)}
    elif hasattr(obj, '__dict__'):
        return obj.__dict__
    else:
        return {"valeur": str(obj)}

def creer_modele_depuis_dict(cls, data: Dict[str, Any]):
    """Crée une instance de modèle depuis un dictionnaire"""
    try:
        if issubclass(cls, BaseModel):
            return cls(**data)
        else:
            return cls(**data)
    except Exception as e:
        print(f"Erreur création modèle {cls.__name__}: {e}")
        return None

# ============================================
# FACTORY FUNCTIONS
# ============================================

def creer_copie_eleve(nom_fichier: str, chemin_complet: str, **kwargs) -> CopieEleve:
    """Factory function pour créer une CopieEleve"""
    return CopieEleve(
        nom_fichier=nom_fichier,
        chemin_complet=chemin_complet,
        **kwargs
    )

def creer_resultat_correction_vide(note_max: float = 20.0) -> ResultatCorrection:
    """Crée un résultat de correction vide avec valeurs par défaut"""
    return ResultatCorrection(
        note_globale=0.0,
        note_max=note_max,
        commentaires=["Correction en cours..."],
        methode_correction="initialisation"
    )

def creer_state_initial(dossier_copies: str, bareme_path: str, **kwargs) -> CorrectionState:
    """Crée un état initial pour le workflow"""
    return CorrectionState(
        dossier_copies=dossier_copies,
        bareme_path=bareme_path,
        erreurs_rencontrees=[],
        **kwargs
    )

def creer_transcription_vide() -> TranscriptionManuscrite:
    """Crée une transcription vide"""
    return TranscriptionManuscrite(
        texte_transcrit="",
        qualite_ecriture="INCONNUE",
        confiance_globale=0.0,
        mots_incertains=[],
        structure_detectee={},
        formules_maths=[],
        erreurs_transcription=[],
        suggestions_amelioration=[]
    )

def creer_structure_copie_vide(nom_fichier: str) -> StructureCopie:
    """Crée une structure de copie vide"""
    return StructureCopie(
        nom_fichier=nom_fichier,
        nombre_pages=0,
        pages_detectees=[],
        zones_questions=[],
        qualite_images=[],
        orientation_correcte=True,
        format_valide=False,
        erreurs_detectees=[]
    )

# ============================================
# FONCTIONS D'EXPORT/IMPORT
# ============================================

def exporter_resultats_json(resultats: List[ResultatCorrection], chemin_sortie: str) -> bool:
    """Exporte les résultats en JSON"""
    try:
        import json
        
        # Convertir en dictionnaires
        data = [convertir_en_dict(r) for r in resultats]
        
        with open(chemin_sortie, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        
        return True
    except Exception as e:
        print(f"Erreur export JSON: {e}")
        return False

def importer_resultats_json(chemin_fichier: str) -> List[ResultatCorrection]:
    """Importe des résultats depuis JSON"""
    try:
        import json
        
        with open(chemin_fichier, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        resultats = []
        for item in data:
            try:
                resultat = creer_modele_depuis_dict(ResultatCorrection, item)
                if resultat:
                    resultats.append(resultat)
            except Exception as e:
                print(f"Erreur import item: {e}")
                continue
        
        return resultats
    except Exception as e:
        print(f"Erreur import JSON: {e}")
        return []

# ============================================
# VALIDATION ET HELPERS
# ============================================

def valider_state_correction(state: CorrectionState) -> List[str]:
    """Valide un état de correction"""
    erreurs = []
    
    # Vérifications de base
    if not state.dossier_copies or not os.path.exists(state.dossier_copies):
        erreurs.append("Dossier copies inexistant ou invalide")
    
    if not state.bareme_path or not os.path.exists(state.bareme_path):
        erreurs.append("Fichier barème inexistant ou invalide")
    
    # Vérifications de cohérence
    if state.nb_copies_reussies > state.nb_copies_traitees:
        erreurs.append("Nombre de copies réussies > copies traitées")
    
    if state.workflow_status not in ["INITIALISE", "EN_COURS", "TERMINE", "ERREUR"]:
        erreurs.append("Statut workflow invalide")
    
    return erreurs

def generer_resume_etat(state: CorrectionState) -> Dict[str, Any]:
    """Génère un résumé de l'état de correction"""
    return {
        "statut": state.workflow_status,
        "progression": f"{state.nb_copies_reussies}/{state.nb_copies_traitees}",
        "temps_execution": f"{state.temps_execution:.1f}s",
        "erreurs": len(state.erreurs_rencontrees) if state.erreurs_rencontrees else 0,
        "matiere": state.matiere,
        "classe": state.classe
    }

# ============================================
# EXPORTS ET COMPATIBILITÉ
# ============================================

# Classes principales exportées
__all__ = [
    # Classes de base
    'BaseModel',
    'ExamenInfo',
    'CopieEleve', 
    
    # Modèles barème
    'BaremeItem',
    'BaremeComplet',
    'CorrigeType',
    
    # Modèles analyse images
    'StructureCopie',
    
    # Modèles transcription
    'TranscriptionManuscrite',
    'TranscriptionManuscriteModel',
    
    # Modèles correction
    'ResultatCorrection',
    'ResultatCorrectionDataclass',
    
    # Modèles workflow
    'CorrectionState',
    'StatistiquesClasse',
    'ConfigurationAgent',
    'RapportCorrection',
    
    # Fonctions utilitaires
    'convertir_en_dict',
    'creer_modele_depuis_dict',
    'creer_copie_eleve',
    'creer_resultat_correction_vide',
    'creer_state_initial',
    'creer_transcription_vide',
    'creer_structure_copie_vide',
    
    # Import/Export
    'exporter_resultats_json',
    'importer_resultats_json',
    
    # Validation
    'valider_state_correction',
    'generer_resume_etat',
    
    # Constantes
    'PYDANTIC_V2'
]

# Aliases pour compatibilité avec l'ancien système
InfoDocument = CopieEleve  # Alias pour compatibilité
State = CorrectionState    # Alias pour compatibilité
DocumentInfo = CopieEleve  # Alias pour compatibilité

# Initialisation du module
if __name__ == "__main__":
    print(f"📋 Modèles de correction consolidés initialisés")
    print(f"🔧 Pydantic v2: {PYDANTIC_V2}")
    print(f"📊 {len(__all__)} classes/fonctions exportées")