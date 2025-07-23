"""
utils/data_manager.py - Version CORRIGÉE avec gestion publication
================================================================
CORRECTION : Nom de fichier unifié + fonctions publication
"""

import streamlit as st
import pandas as pd
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import uuid
import hashlib

# ==================================================
# SYSTÈME DE CACHE INTELLIGENT GLOBAL
# ==================================================

class CacheManager:
    """Gestionnaire de cache intelligent pour toute l'application"""
    
    @staticmethod
    def get_directory_hash(directory_path: Path):
        """Génère un hash basé sur le contenu d'un dossier"""
        if not directory_path.exists():
            return "empty"
        
        # Hash basé sur la liste des fichiers et leurs timestamps
        file_list = []
        try:
            for item in directory_path.rglob("*"):
                if item.is_file():
                    file_list.append(f"{item.relative_to(directory_path)}_{item.stat().st_mtime}")
        except:
            pass
        
        content = "".join(sorted(file_list))
        return hashlib.md5(content.encode()).hexdigest()[:8]
    
    @staticmethod
    def get_evaluations_cache_key():
        """Clé de cache pour les évaluations"""
        evaluations_dir = Path("./evaluations")
        return CacheManager.get_directory_hash(evaluations_dir)
    
    @staticmethod
    def get_submissions_cache_key(eval_id: str):
        """Clé de cache pour les soumissions d'une évaluation"""
        submissions_dir = Path(f"./evaluations") / f"*{eval_id}*" / "soumissions_etudiants"
        # Trouver le bon dossier
        for eval_dir in Path("./evaluations").iterdir():
            if eval_id in str(eval_dir) and eval_dir.is_dir():
                submissions_dir = eval_dir / "soumissions_etudiants"
                break
        return CacheManager.get_directory_hash(submissions_dir)
    
    @staticmethod
    def get_results_cache_key(eval_id: str):
        """Clé de cache pour les résultats d'une évaluation"""
        results_dir = Path("./evaluations")
        for eval_dir in results_dir.iterdir():
            if eval_id in str(eval_dir) and eval_dir.is_dir():
                results_dir = eval_dir / "resultats"
                break
        return CacheManager.get_directory_hash(results_dir)

# ==================================================
# FONCTIONS DE DONNÉES AVEC CACHE INTELLIGENT
# ==================================================

@st.cache_data
def _load_evaluations_cached(_cache_key=None):
    """Fonction cachée pour charger les évaluations"""
    evaluations_dir = Path("./evaluations")
    evaluations_dir.mkdir(exist_ok=True)
    
    evaluations = []
    for eval_dir in evaluations_dir.iterdir():
        if eval_dir.is_dir():
            # ✅ CORRECTION : Nom de fichier unifié
            info_file = eval_dir / "infos_evaluation.json"
            if info_file.exists():
                try:
                    with open(info_file, 'r', encoding='utf-8') as f:
                        info = json.load(f)
                        info['dossier'] = str(eval_dir)
                        evaluations.append(info)
                except Exception as e:
                    print(f"Erreur lecture {info_file}: {e}")
                    continue
    
    # Trier par date de création (plus récent en premier)
    evaluations.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    return evaluations

def load_evaluations_list():
    """Charge la liste des évaluations avec cache intelligent"""
    cache_key = CacheManager.get_evaluations_cache_key()
    return _load_evaluations_cached(_cache_key=cache_key)

@st.cache_data  
def _load_correction_results_cached(eval_dir: str, _cache_key=None):
    """Fonction cachée pour charger les résultats"""
    results_dir = Path(eval_dir) / "resultats"
    if not results_dir.exists():
        return []
    
    results = []
    for student_dir in results_dir.iterdir():
        if student_dir.is_dir():
            correction_file = student_dir / "correction_detaillee.json"
            if correction_file.exists():
                try:
                    with open(correction_file, 'r', encoding='utf-8') as f:
                        result = json.load(f)
                        results.append(result)
                except:
                    continue
    
    return results

def load_correction_results(eval_dir: str):
    """Charge les résultats de correction avec cache intelligent"""
    # Extraire l'ID de l'évaluation du chemin
    eval_id = Path(eval_dir).name.split('_')[-1] if '_' in Path(eval_dir).name else "unknown"
    cache_key = CacheManager.get_results_cache_key(eval_id)
    return _load_correction_results_cached(eval_dir, _cache_key=cache_key)

@st.cache_data
def _load_submissions_cached(eval_dir: str, _cache_key=None):
    """Fonction cachée pour charger les soumissions"""
    submissions_dir = Path(eval_dir) / "soumissions_etudiants"
    if not submissions_dir.exists():
        return []
    
    submissions = []
    for submission_file in submissions_dir.glob("*_submission.json"):
        try:
            with open(submission_file, 'r', encoding='utf-8') as f:
                submission = json.load(f)
                submissions.append(submission)
        except:
            continue
    
    return submissions

def load_submissions_list(eval_dir: str):
    """Charge la liste des soumissions avec cache intelligent"""
    eval_id = Path(eval_dir).name.split('_')[-1] if '_' in Path(eval_dir).name else "unknown"
    cache_key = CacheManager.get_submissions_cache_key(eval_id)
    return _load_submissions_cached(eval_dir, _cache_key=cache_key)

# ==================================================
# FONCTIONS D'INVALIDATION GLOBALE
# ==================================================

def clear_all_cache():
    """Invalide tout le cache de l'application"""
    _load_evaluations_cached.clear()
    _load_correction_results_cached.clear()
    _load_submissions_cached.clear()
    st.cache_data.clear()

def clear_evaluations_cache():
    """Invalide uniquement le cache des évaluations"""
    _load_evaluations_cached.clear()

def clear_results_cache():
    """Invalide le cache des résultats"""
    _load_correction_results_cached.clear()

def clear_submissions_cache():
    """Invalide le cache des soumissions"""
    _load_submissions_cached.clear()

# ==================================================
# FONCTIONS DE SAUVEGARDE AVEC AUTO-INVALIDATION
# ==================================================

def save_evaluation_info(dossier: str, infos: Dict):
    """Sauvegarde les informations d'évaluation et invalide le cache"""
    # ✅ CORRECTION : Nom de fichier unifié
    info_file = Path(dossier) / "infos_evaluation.json"
    
    try:
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(infos, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Sauvegarde réussie : {info_file}")
        print(f"   Statut publication : {infos.get('statut_publication', 'N/A')}")
        
        # Auto-invalidation
        clear_evaluations_cache()
        return True
        
    except Exception as e:
        print(f"❌ Erreur sauvegarde {info_file}: {e}")
        return False

def save_bareme(dossier: str, bareme: Dict):
    """Sauvegarde le barème d'évaluation"""
    bareme_file = Path(dossier) / "bareme_evaluation.json"
    with open(bareme_file, 'w', encoding='utf-8') as f:
        json.dump(bareme, f, ensure_ascii=False, indent=2)

def create_evaluation_structure(dossier: str):
    """Crée la structure de dossiers pour une évaluation"""
    base_path = Path(dossier)
    subdirs = ["copies_soumises", "soumissions_etudiants", "images_correction", "resultats", "rapports"]
    
    for subdir in subdirs:
        (base_path / subdir).mkdir(exist_ok=True)

def save_uploaded_files(uploaded_files, target_dir: Path):
    """Sauvegarde les fichiers uploadés avec invalidation cache"""
    target_dir.mkdir(exist_ok=True)
    saved_files = []
    
    for uploaded_file in uploaded_files:
        file_path = target_dir / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        saved_files.append(str(file_path))
    
    # Auto-invalidation si c'est dans le dossier copies_soumises
    if "copies_soumises" in str(target_dir):
        clear_evaluations_cache()
    
    return saved_files

def save_correction_result(eval_dir: str, student_name: str, result_data: Dict):
    """Sauvegarde un résultat de correction avec invalidation cache"""
    results_dir = Path(eval_dir) / "resultats"
    student_dir = results_dir / student_name
    student_dir.mkdir(parents=True, exist_ok=True)
    
    result_file = student_dir / "correction_detaillee.json"
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    
    # Auto-invalidation
    clear_results_cache()

# ==================================================
# ✅ NOUVELLES FONCTIONS POUR LA PUBLICATION
# ==================================================

def publish_evaluation_results(eval_dir: str, eval_info: Dict):
    """Publie les résultats d'une évaluation"""
    
    # Mettre à jour le statut de l'évaluation
    eval_info['statut_publication'] = 'publie'
    eval_info['date_publication'] = datetime.now().isoformat()
    eval_info['publie_par'] = eval_info.get('professeur', 'Professeur')
    
    # Sauvegarder les infos de l'évaluation
    if not save_evaluation_info(eval_dir, eval_info):
        return False
    
    # Mettre à jour tous les résultats individuels
    results_dir = Path(eval_dir) / "resultats"
    if results_dir.exists():
        for student_dir in results_dir.iterdir():
            if student_dir.is_dir():
                correction_file = student_dir / "correction_detaillee.json"
                if correction_file.exists():
                    try:
                        # Lire le fichier
                        with open(correction_file, 'r', encoding='utf-8') as f:
                            result_data = json.load(f)
                        
                        # Mettre à jour le statut
                        result_data['statut_publication'] = 'publie'
                        result_data['date_maj_publication'] = datetime.now().isoformat()
                        
                        # Sauvegarder
                        with open(correction_file, 'w', encoding='utf-8') as f:
                            json.dump(result_data, f, ensure_ascii=False, indent=2)
                        
                        print(f"✅ Publication mise à jour : {student_dir.name}")
                        
                    except Exception as e:
                        print(f"❌ Erreur mise à jour {student_dir.name}: {e}")
    
    # Invalidation complète du cache
    clear_all_cache()
    return True

def unpublish_evaluation_results(eval_dir: str, eval_info: Dict):
    """Dépublie les résultats d'une évaluation"""
    
    # Mettre à jour le statut de l'évaluation
    eval_info['statut_publication'] = 'depublie'
    eval_info['date_depublication'] = datetime.now().isoformat()
    eval_info['depublie_par'] = eval_info.get('professeur', 'Professeur')
    
    # Sauvegarder les infos de l'évaluation
    if not save_evaluation_info(eval_dir, eval_info):
        return False
    
    # Mettre à jour tous les résultats individuels
    results_dir = Path(eval_dir) / "resultats"
    if results_dir.exists():
        for student_dir in results_dir.iterdir():
            if student_dir.is_dir():
                correction_file = student_dir / "correction_detaillee.json"
                if correction_file.exists():
                    try:
                        # Lire le fichier
                        with open(correction_file, 'r', encoding='utf-8') as f:
                            result_data = json.load(f)
                        
                        # Mettre à jour le statut
                        result_data['statut_publication'] = 'depublie'
                        result_data['date_maj_publication'] = datetime.now().isoformat()
                        
                        # Sauvegarder
                        with open(correction_file, 'w', encoding='utf-8') as f:
                            json.dump(result_data, f, ensure_ascii=False, indent=2)
                        
                        print(f"✅ Dépublication mise à jour : {student_dir.name}")
                        
                    except Exception as e:
                        print(f"❌ Erreur mise à jour {student_dir.name}: {e}")
    
    # Invalidation complète du cache
    clear_all_cache()
    return True

def get_evaluation_publication_status(eval_dir: str):
    """Récupère le statut de publication d'une évaluation"""
    
    info_file = Path(eval_dir) / "infos_evaluation.json"
    if info_file.exists():
        try:
            with open(info_file, 'r', encoding='utf-8') as f:
                info = json.load(f)
                return info.get('statut_publication', 'brouillon')
        except:
            pass
    
    return 'brouillon'

# ==================================================
# FONCTIONS WRAPPER POUR COMPATIBILITÉ
# ==================================================

def get_evaluations_list():
    """Fonction wrapper pour charger les évaluations"""
    return load_evaluations_list()

def get_correction_results(eval_dir: str):
    """Fonction wrapper pour charger les résultats"""
    return load_correction_results(eval_dir)

def get_submissions_list(eval_dir: str):
    """Fonction wrapper pour charger les soumissions"""
    return load_submissions_list(eval_dir)

# ==================================================
# FONCTIONS DE DEBUG
# ==================================================

def debug_evaluation_files(eval_dir: str):
    """Debug : Affiche les fichiers d'une évaluation"""
    
    eval_path = Path(eval_dir)
    print(f"\n🔍 DEBUG - Contenu de {eval_path.name}:")
    
    # Fichier principal
    info_file = eval_path / "infos_evaluation.json"
    if info_file.exists():
        try:
            with open(info_file, 'r', encoding='utf-8') as f:
                info = json.load(f)
                print(f"  ✅ infos_evaluation.json trouvé")
                print(f"     Statut publication : {info.get('statut_publication', 'N/A')}")
                print(f"     Date publication : {info.get('date_publication', 'N/A')}")
        except Exception as e:
            print(f"  ❌ Erreur lecture infos_evaluation.json : {e}")
    else:
        print(f"  ❌ infos_evaluation.json MANQUANT")
    
    # Dossier résultats
    results_dir = eval_path / "resultats"
    if results_dir.exists():
        print(f"  ✅ Dossier resultats trouvé")
        for student_dir in results_dir.iterdir():
            if student_dir.is_dir():
                correction_file = student_dir / "correction_detaillee.json"
                if correction_file.exists():
                    try:
                        with open(correction_file, 'r', encoding='utf-8') as f:
                            result = json.load(f)
                            status = result.get('statut_publication', 'N/A')
                            print(f"     📄 {student_dir.name} : {status}")
                    except:
                        print(f"     ❌ Erreur lecture {student_dir.name}")
    else:
        print(f"  ❌ Dossier resultats MANQUANT")

if __name__ == "__main__":
    print("🔧 Data Manager CORRIGÉ pour la publication prêt !")