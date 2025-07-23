"""
utils/student_manager.py - Version avec auto-invalidation du cache
"""

import json
from datetime import datetime
from pathlib import Path

def check_student_submission(eval_info, student_info):
    """Vérifie si un étudiant a déjà soumis pour une évaluation"""
    submissions_dir = Path(eval_info['dossier']) / "soumissions_etudiants"
    
    if not submissions_dir.exists():
        return None
    
    submission_file = submissions_dir / f"{student_info['nom']}_{student_info['prenom']}_submission.json"
    
    if submission_file.exists():
        try:
            with open(submission_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    
    return None

def submit_student_copy(eval_info, student_info, uploaded_files, digital_response, submission_type):
    """Sauvegarde la soumission d'un étudiant avec auto-invalidation cache"""
    try:
        # Créer le dossier de soumissions
        eval_dir = Path(eval_info['dossier'])
        submissions_dir = eval_dir / "soumissions_etudiants"
        submissions_dir.mkdir(exist_ok=True)
        
        # Créer le dossier individuel de l'étudiant
        student_dir_name = f"{student_info['nom']}_{student_info['prenom']}"
        student_submission_dir = submissions_dir / student_dir_name
        student_submission_dir.mkdir(exist_ok=True)
        
        # Données de soumission
        submission_data = {
            "etudiant_nom": student_info['nom'],
            "etudiant_prenom": student_info['prenom'],
            "numero_etudiant": student_info['numero'],
            "evaluation_id": eval_info['id_evaluation'],
            "date_soumission": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "type_soumission": submission_type,
            "nombre_fichiers": 0,
            "taille_totale": "0 MB",
            "fichiers_soumis": []
        }
        
        # Sauvegarder les fichiers si upload
        if uploaded_files:
            total_size = 0
            for i, uploaded_file in enumerate(uploaded_files):
                filename = f"copie_page_{i+1:02d}_{uploaded_file.name}"
                file_path = student_submission_dir / filename
                
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                file_size = file_path.stat().st_size
                total_size += file_size
                
                submission_data["fichiers_soumis"].append({
                    "nom_original": uploaded_file.name,
                    "nom_sauvegarde": filename,
                    "taille": file_size
                })
            
            submission_data["nombre_fichiers"] = len(uploaded_files)
            submission_data["taille_totale"] = f"{total_size / 1024 / 1024:.1f} MB"
        
        # Sauvegarder la réponse numérique si applicable
        if submission_type == "✏️ Saisie numérique" and digital_response:
            response_file = student_submission_dir / "reponse_numerique.txt"
            with open(response_file, 'w', encoding='utf-8') as f:
                f.write(digital_response)
            
            submission_data["reponse_numerique"] = True
            submission_data["nombre_mots"] = len(digital_response.split())
        
        # Sauvegarder les métadonnées de soumission
        submission_file = submissions_dir / f"{student_dir_name}_submission.json"
        with open(submission_file, 'w', encoding='utf-8') as f:
            json.dump(submission_data, f, ensure_ascii=False, indent=2)
        
        # Copier aussi dans le dossier copies_soumises pour le professeur
        copies_dir = eval_dir / "copies_soumises"
        copies_dir.mkdir(exist_ok=True)
        
        if uploaded_files:
            for i, uploaded_file in enumerate(uploaded_files):
                copy_filename = f"{student_info['nom']}_{student_info['prenom']}_page{i+1:02d}.pdf"
                copy_path = copies_dir / copy_filename
                
                with open(copy_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
        
        # AUTO-INVALIDATION DU CACHE APRÈS SOUMISSION
        from utils.data_manager import clear_all_cache
        clear_all_cache()
        
        return True
        
    except Exception as e:
        print(f"Erreur soumission: {e}")
        return False