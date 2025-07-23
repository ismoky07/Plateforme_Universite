import os
import json
import yaml
import pandas as pd
from typing import Dict, List, Optional, Union, Any
from dataclasses import asdict
from pathlib import Path
import re

# Import des modèles consolidés
from models_correction import BaremeComplet, BaremeItem, CorrigeType

# Import des utilitaires consolidés
from utils_correction import (
    safe_print, safe_text_handling, evaluer_mots_cles, evaluer_concepts, 
    evaluer_exemples, appliquer_penalites_erreurs, generer_justifications,
    adapter_criteres_niveau, get_ajustements_niveau
)

def charger_bareme(chemin_bareme: str, format_auto: bool = True) -> BaremeComplet:
    """Charge un barème depuis JSON, Excel ou YAML"""
    
    if not os.path.exists(chemin_bareme):
        raise FileNotFoundError(f"Barème introuvable: {chemin_bareme}")
    
    extension = Path(chemin_bareme).suffix.lower()
    safe_print(f"📊 Chargement barème: {os.path.basename(chemin_bareme)}")
    
    try:
        if extension == '.json':
            return _charger_bareme_json(chemin_bareme)
        else:
            if format_auto:
                # Tentative auto-détection
                return _charger_bareme_auto_detect(chemin_bareme)
            else:
                raise ValueError(f"Format non supporté: {extension}")
    
    except Exception as e:
        safe_print(f"❌ Erreur chargement barème: {str(e)}")
        raise

def parser_corrige_type(chemin_corrige: str, format_corrige: str = "txt") -> List[CorrigeType]:
    """Analyse un corrigé de référence et extrait les éléments attendus"""
    
    safe_print(f"📋 Parsing corrigé: {os.path.basename(chemin_corrige)}")
    
    if not os.path.exists(chemin_corrige):
        safe_print(f"⚠️ Corrigé introuvable: {chemin_corrige}")
        return []
    
    try:
        if format_corrige == "json":
            return _parser_corrige_json(chemin_corrige)
        elif format_corrige in ["txt", "md"]:
            return _parser_corrige_texte(chemin_corrige)
        elif format_corrige == "docx":
            return _parser_corrige_docx(chemin_corrige)
        else:
            return _parser_corrige_texte(chemin_corrige)  # Fallback
    
    except Exception as e:
        safe_print(f"❌ Erreur parsing corrigé: {str(e)}")
        return []

def definir_criteres_evaluation(matiere: str, type_epreuve: str, classe: str) -> Dict[str, Dict]:
    """Configure les critères d'évaluation selon matière/niveau"""
    
    safe_print(f"⚙️ Configuration critères: {matiere} - {classe} - {type_epreuve}")
    
    # Critères de base par matière
    criteres_base = {
        "francais": {
            "orthographe": {"poids": 0.2, "penalite_par_erreur": -0.25, "seuil_tolerance": 5},
            "grammaire": {"poids": 0.15, "penalite_par_erreur": -0.5, "seuil_tolerance": 3},
            "vocabulaire": {"poids": 0.15, "bonus_richesse": 1.0, "penalite_pauvrete": -1.0},
            "structure": {"poids": 0.25, "bonus_plan_clair": 2.0, "penalite_desorganise": -2.0},
            "contenu": {"poids": 0.25, "bonus_pertinence": 2.0, "penalite_hors_sujet": -3.0}
        },
        
        "mathematiques": {
            "raisonnement": {"poids": 0.4, "bonus_demarche": 2.0, "penalite_erreur_logique": -2.0},
            "calculs": {"poids": 0.3, "penalite_par_erreur": -0.5, "seuil_tolerance": 2},
            "presentation": {"poids": 0.15, "bonus_clarte": 1.0, "penalite_brouillon": -1.0},
            "resultat": {"poids": 0.15, "bonus_exact": 1.0, "penalite_faux": -1.0}
        },
        
        "histoire": {
            "connaissances": {"poids": 0.35, "bonus_precision": 2.0, "penalite_erreur_fait": -1.0},
            "analyse": {"poids": 0.25, "bonus_reflexion": 2.0, "penalite_superficiel": -1.0},
            "argumentation": {"poids": 0.2, "bonus_coherence": 1.5, "penalite_contradiction": -1.5},
            "expression": {"poids": 0.2, "bonus_clarte": 1.0, "penalite_confus": -1.0}
        },
        
        "general": {
            "contenu": {"poids": 0.5, "bonus_pertinence": 2.0, "penalite_hors_sujet": -2.0},
            "forme": {"poids": 0.3, "bonus_presentation": 1.0, "penalite_negligee": -1.0},
            "originalite": {"poids": 0.2, "bonus_creativite": 1.5, "penalite_banal": 0.0}
        }
    }
    
    # Adapter selon le niveau
    criteres = criteres_base.get(matiere, criteres_base["general"]).copy()
    criteres = adapter_criteres_niveau(criteres, classe)
    
    # Adapter selon le type d'épreuve
    criteres = _adapter_criteres_type_epreuve(criteres, type_epreuve)
    
    safe_print(f"✅ {len(criteres)} critères configurés")
    return criteres

def calculer_points_partiels(reponse_eleve: str, corrige_ref: CorrigeType, 
                           criteres: Dict, points_max: float) -> Dict[str, float]:
    """Calcule les points partiels selon la qualité de la réponse"""
    
    resultat = {
        "points_obtenus": 0.0,
        "points_max": points_max,
        "detail_points": {},
        "justifications": []
    }
    
    try:
        # Analyse des mots-clés présents
        points_mots_cles = evaluer_mots_cles(reponse_eleve, corrige_ref.mots_cles, points_max * 0.4)
        resultat["detail_points"]["mots_cles"] = points_mots_cles
        
        # Analyse des concepts essentiels
        points_concepts = evaluer_concepts(reponse_eleve, corrige_ref.concepts_essentiels, points_max * 0.3)
        resultat["detail_points"]["concepts"] = points_concepts
        
        # Qualité des exemples
        points_exemples = evaluer_exemples(reponse_eleve, corrige_ref.exemples_acceptables, points_max * 0.2)
        resultat["detail_points"]["exemples"] = points_exemples
        
        # Bonus pour variantes créatives
        bonus_variantes = _evaluer_variantes(reponse_eleve, corrige_ref.variantes_acceptees, points_max * 0.1)
        resultat["detail_points"]["bonus_variantes"] = bonus_variantes
        
        # Pénalités pour erreurs fréquentes
        penalites = appliquer_penalites_erreurs(reponse_eleve, corrige_ref.erreurs_frequentes)
        resultat["detail_points"]["penalites"] = penalites
        
        # Calcul total
        total = points_mots_cles + points_concepts + points_exemples + bonus_variantes + penalites
        resultat["points_obtenus"] = max(0.0, min(points_max, total))
        
        # Justifications
        resultat["justifications"] = generer_justifications(resultat["detail_points"], corrige_ref)
        
        safe_print(f"🔢 Points calculés: {resultat['points_obtenus']:.1f}/{points_max}")
        
    except Exception as e:
        safe_print(f"❌ Erreur calcul points: {str(e)}")
        resultat["points_obtenus"] = 0.0
        resultat["justifications"] = [f"Erreur calcul: {str(e)}"]
    
    return resultat

def adapter_bareme_niveau(bareme: BaremeComplet, niveau_classe: str, 
                         ajustements: Dict = None) -> BaremeComplet:
    """Adapte un barème selon le niveau de classe"""
    
    if ajustements is None:
        ajustements = get_ajustements_niveau(niveau_classe)
    
    safe_print(f"🎯 Adaptation barème pour niveau: {niveau_classe}")
    
    bareme_adapte = bareme
    
    try:
        # Ajuster les critères globaux
        for critere, facteur in ajustements.get("facteurs_criteres", {}).items():
            if critere in bareme_adapte.criteres_globaux:
                bareme_adapte.criteres_globaux[critere] *= facteur
        
        # Ajuster chaque item du barème
        for item in bareme_adapte.items:
            # Ajuster la difficulté selon le niveau
            if item.niveau_requis == "difficile" and niveau_classe in ["6eme", "5eme"]:
                # Réduire les exigences pour les niveaux plus bas
                for critere in item.criteres:
                    item.criteres[critere] *= 0.8
                
            elif item.niveau_requis == "facile" and niveau_classe in ["1ere", "terminale"]:
                # Augmenter les exigences pour les niveaux élevés
                for critere in item.criteres:
                    item.criteres[critere] *= 1.2
        
        # Ajuster les pénalités selon l'âge
        tolerance_orthographe = ajustements.get("tolerance_orthographe", 1.0)
        for item in bareme_adapte.items:
            if "orthographe" in item.penalites:
                item.penalites["orthographe"] *= tolerance_orthographe
        
        safe_print(f"✅ Barème adapté au niveau {niveau_classe}")
        
    except Exception as e:
        safe_print(f"❌ Erreur adaptation: {str(e)}")
    
    return bareme_adapte

def valider_bareme(bareme: BaremeComplet) -> Dict[str, List[str]]:
    """Valide la cohérence d'un barème"""
    
    safe_print(f"🔍 Validation barème: {bareme.matiere}")
    
    validation = {
        "erreurs": [],
        "avertissements": [],
        "suggestions": []
    }
    
    try:
        # Vérifier la somme des points
        total_points = sum(item.points_max for item in bareme.items)
        if abs(total_points - bareme.note_totale) > 0.1:
            validation["erreurs"].append(f"Somme des points ({total_points}) ≠ note totale ({bareme.note_totale})")
        
        # Vérifier les critères
        for item in bareme.items:
            somme_criteres = sum(item.criteres.values())
            if abs(somme_criteres - item.points_max) > 0.1:
                validation["avertissements"].append(f"Item {item.id}: somme critères ({somme_criteres}) ≠ points max ({item.points_max})")
        
        # Vérifier la cohérence des niveaux
        niveaux_count = {}
        for item in bareme.items:
            niveaux_count[item.niveau_requis] = niveaux_count.get(item.niveau_requis, 0) + 1
        
        if niveaux_count.get("difficile", 0) > len(bareme.items) * 0.5:
            validation["avertissements"].append("Beaucoup d'items difficiles, ajuster la difficulté")
        
        # Suggestions d'amélioration
        if not any("bonus" in item.bonus for item in bareme.items):
            validation["suggestions"].append("Ajouter des bonus pour valoriser l'excellence")
        
        if len(validation["erreurs"]) == 0:
            safe_print("✅ Barème valide")
        else:
            safe_print(f"⚠️ {len(validation['erreurs'])} erreur(s) détectée(s)")
    
    except Exception as e:
        validation["erreurs"].append(f"Erreur validation: {str(e)}")
    
    return validation

def sauvegarder_bareme(bareme: BaremeComplet, chemin_sortie: str, format_sortie: str = "json"):
    """Sauvegarde un barème dans le format spécifié"""
    
    safe_print(f"💾 Sauvegarde barème: {chemin_sortie}")
    
    try:
        os.makedirs(os.path.dirname(chemin_sortie), exist_ok=True)
        
        if format_sortie == "json":
            with open(chemin_sortie, 'w', encoding='utf-8') as f:
                json.dump(asdict(bareme), f, ensure_ascii=False, indent=2)
        
        elif format_sortie == "yaml":
            with open(chemin_sortie, 'w', encoding='utf-8') as f:
                yaml.dump(asdict(bareme), f, default_flow_style=False, allow_unicode=True)
        
        safe_print(f"✅ Barème sauvegardé: {format_sortie}")
        
    except Exception as e:
        safe_print(f"❌ Erreur sauvegarde: {str(e)}")

# ==========================================
# FONCTIONS UTILITAIRES INTERNES
# ==========================================

def _charger_bareme_json(chemin: str) -> BaremeComplet:
    """Charge un barème depuis un fichier JSON"""
    with open(chemin, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Convertir les items
    items = [BaremeItem(**item) for item in data.get('items', [])]
    
    return BaremeComplet(
        matiere=data.get('matiere', 'general'),
        classe=data.get('classe', 'inconnue'),
        type_epreuve=data.get('type_epreuve', 'controle'),
        duree_minutes=data.get('duree_minutes', 60),
        note_totale=data.get('note_totale', 20.0),
        items=items,
        criteres_globaux=data.get('criteres_globaux', {}),
        regles_arrondi=data.get('regles_arrondi', 'au_demi_point'),
        penalites_globales=data.get('penalites_globales', {}),
        metadata=data.get('metadata', {})
    )

def _parser_corrige_texte(chemin: str) -> List[CorrigeType]:
    """Parse un corrigé en format texte libre"""
    corriges = []
    
    with open(chemin, 'r', encoding='utf-8') as f:
        contenu = f.read()
    
    # Pattern pour identifier les questions
    questions = re.split(r'(?:^|\n)(?:Question|Exercice|Q\.?)\s*(\d+)', contenu, flags=re.MULTILINE)
    
    for i in range(1, len(questions), 2):
        if i + 1 < len(questions):
            question_id = f"Q{questions[i].strip()}"
            reponse = questions[i + 1].strip()
            
            # Extraire mots-clés (mots en MAJUSCULES ou entre guillemets)
            mots_cles = re.findall(r'\b[A-Z]{3,}\b|"([^"]+)"', reponse)
            mots_cles = [m[0] if isinstance(m, tuple) and m[0] else m for m in mots_cles]
            
            # Extraire concepts (lignes commençant par "Concept:" ou "Important:")
            concepts = re.findall(r'(?:Concept|Important|Essentiel):\s*(.+)', reponse)
            
            corrige = CorrigeType(
                question_id=question_id,
                reponse_ideale=reponse,
                mots_cles=mots_cles[:5],  # Limiter à 5
                concepts_essentiels=concepts,
                exemples_acceptables=[],
                variantes_acceptees=[],
                erreurs_frequentes=[]
            )
            corriges.append(corrige)
    
    return corriges

def _evaluer_variantes(reponse: str, variantes: List[str], bonus_max: float) -> float:
    """Évalue les variantes créatives de réponse"""
    if not variantes:
        return 0.0
    
    reponse_lower = reponse.lower()
    variantes_trouvees = sum(1 for var in variantes if var.lower() in reponse_lower)
    
    return min(bonus_max, (variantes_trouvees / len(variantes)) * bonus_max)

def _adapter_criteres_type_epreuve(criteres: Dict, type_epreuve: str) -> Dict:
    """Adapte les critères selon le type d'épreuve"""
    
    if type_epreuve == "qcm":
        # Pour les QCM, privilégier le contenu
        if "contenu" in criteres:
            criteres["contenu"]["poids"] = 0.8
        if "structure" in criteres:
            criteres["structure"]["poids"] = 0.1
    
    elif type_epreuve == "dissertation":
        # Pour les dissertations, équilibrer structure et contenu
        if "structure" in criteres:
            criteres["structure"]["poids"] = 0.4
        if "contenu" in criteres:
            criteres["contenu"]["poids"] = 0.4
    
    return criteres

def _charger_bareme_auto_detect(chemin: str) -> BaremeComplet:
    """Tentative de chargement avec auto-détection du format"""
    
    # Essayer JSON en premier
    try:
        return _charger_bareme_json(chemin)
    except:
        pass
    
    # Format non reconnu
    raise ValueError("Format de barème non reconnu")

def _parser_corrige_json(chemin: str) -> List[CorrigeType]:
    """Parse un corrigé au format JSON structuré"""
    with open(chemin, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    corriges = []
    for item in data.get('corriges', []):
        corrige = CorrigeType(**item)
        corriges.append(corrige)
    
    return corriges

def _parser_corrige_docx(chemin: str) -> List[CorrigeType]:
    """Parse un corrigé au format Word (nécessite python-docx)"""
    try:
        import docx
        doc = docx.Document(chemin)
        
        contenu = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        return _parser_corrige_texte_content(contenu)
    
    except ImportError:
        safe_print("⚠️ Module python-docx non installé, utilisation du parser texte")
        return []

def _parser_corrige_texte_content(contenu: str) -> List[CorrigeType]:
    """Parse le contenu textuel d'un corrigé"""
    # Réutilise la logique de _parser_corrige_texte mais sur le contenu directement
    corriges = []
    
    questions = re.split(r'(?:^|\n)(?:Question|Exercice|Q\.?)\s*(\d+)', contenu, flags=re.MULTILINE)
    
    for i in range(1, len(questions), 2):
        if i + 1 < len(questions):
            question_id = f"Q{questions[i].strip()}"
            reponse = questions[i + 1].strip()
            
            mots_cles = re.findall(r'\b[A-Z]{3,}\b|"([^"]+)"', reponse)
            mots_cles = [m[0] if isinstance(m, tuple) and m[0] else m for m in mots_cles]
            
            concepts = re.findall(r'(?:Concept|Important|Essentiel):\s*(.+)', reponse)
            
            corrige = CorrigeType(
                question_id=question_id,
                reponse_ideale=reponse,
                mots_cles=mots_cles[:5],
                concepts_essentiels=concepts,
                exemples_acceptables=[],
                variantes_acceptees=[],
                erreurs_frequentes=[]
            )
            corriges.append(corrige)
    
    return corriges