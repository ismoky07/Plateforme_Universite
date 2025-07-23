"""
utils/evaluation_closure_utils.py
=================================
Fonctions utilitaires pour la gestion des fermetures d'évaluations
"""

from datetime import datetime, timedelta
from pathlib import Path
import json
from typing import Dict, List, Optional

def get_evaluation_status(eval_info: Dict) -> str:
    """
    Détermine le statut d'une évaluation
    
    Returns:
        'ouverte', 'fermee', ou 'expiree'
    """
    
    # Vérifier si fermée manuellement
    if eval_info.get('statut') in ['fermee', 'expiree']:
        return eval_info.get('statut')
    
    # Vérifier si expirée automatiquement
    echeance = calculate_evaluation_deadline(eval_info)
    if datetime.now() > echeance:
        return 'expiree'
    
    return 'ouverte'

def calculate_evaluation_deadline(eval_info: Dict) -> datetime:
    """
    Calcule l'échéance d'une évaluation
    
    Returns:
        datetime: Date et heure d'échéance
    """
    
    # Date de l'évaluation
    eval_date = datetime.strptime(eval_info['date'], '%Y-%m-%d')
    
    # Parser la durée
    duree_str = eval_info['duree']
    
    if 'h30' in duree_str:
        heures = float(duree_str.replace('h30', '')) + 0.5
    elif 'h' in duree_str:
        heures = float(duree_str.replace('h', ''))
    else:
        heures = 2.0  # Défaut
    
    # Calculer l'échéance de base
    echeance = eval_date + timedelta(hours=heures)
    
    # Si échéance prolongée manuellement
    if eval_info.get('echeance_prolongee'):
        echeance = datetime.fromisoformat(eval_info['echeance_prolongee'])
    
    return echeance

def calculate_time_remaining(eval_info: Dict) -> Optional[str]:
    """
    Calcule le temps restant avant échéance
    
    Returns:
        str: Temps restant formaté ou None si expiré
    """
    
    echeance = calculate_evaluation_deadline(eval_info)
    maintenant = datetime.now()
    
    if maintenant >= echeance:
        return None
    
    delta = echeance - maintenant
    
    if delta.days > 0:
        return f"{delta.days} jour(s) {delta.seconds // 3600}h"
    elif delta.seconds > 3600:
        return f"{delta.seconds // 3600}h {(delta.seconds % 3600) // 60}min"
    else:
        return f"{delta.seconds // 60}min"

def is_evaluation_open_for_submission(eval_info: Dict) -> bool:
    """
    Vérifie si une évaluation est ouverte pour soumission
    
    Returns:
        bool: True si ouverte, False sinon
    """
    
    return get_evaluation_status(eval_info) == 'ouverte'

def close_evaluation_manually(eval_info: Dict) -> Dict:
    """
    Ferme manuellement une évaluation
    
    Returns:
        Dict: Informations d'évaluation mises à jour
    """
    
    eval_info['statut'] = 'fermee'
    eval_info['date_fermeture'] = datetime.now().isoformat()
    eval_info['fermeture_manuelle'] = True
    
    return eval_info

def reopen_evaluation(eval_info: Dict) -> Dict:
    """
    Rouvre une évaluation fermée
    
    Returns:
        Dict: Informations d'évaluation mises à jour
    """
    
    eval_info['statut'] = 'ouverte'
    eval_info['date_reouverture'] = datetime.now().isoformat()
    
    # Supprimer les marqueurs de fermeture
    for key in ['date_fermeture', 'fermeture_manuelle', 'date_expiration', 'expiration_automatique']:
        if key in eval_info:
            del eval_info[key]
    
    return eval_info

def extend_evaluation_deadline(eval_info: Dict, nouvelle_echeance: datetime) -> Dict:
    """
    Prolonge l'échéance d'une évaluation
    
    Args:
        eval_info: Informations d'évaluation
        nouvelle_echeance: Nouvelle date et heure d'échéance
    
    Returns:
        Dict: Informations d'évaluation mises à jour
    """
    
    eval_info['echeance_prolongee'] = nouvelle_echeance.isoformat()
    eval_info['date_prolongation'] = datetime.now().isoformat()
    
    # Rouvrir si fermée
    if eval_info.get('statut') in ['fermee', 'expiree']:
        eval_info['statut'] = 'ouverte'
    
    return eval_info

def mark_evaluation_expired(eval_info: Dict) -> Dict:
    """
    Marque une évaluation comme expirée automatiquement
    
    Returns:
        Dict: Informations d'évaluation mises à jour
    """
    
    eval_info['statut'] = 'expiree'
    eval_info['date_expiration'] = datetime.now().isoformat()
    eval_info['expiration_automatique'] = True
    
    return eval_info

def get_evaluations_by_status(evaluations: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Classe les évaluations par statut
    
    Returns:
        Dict: Évaluations classées par statut
    """
    
    result = {
        'ouvertes': [],
        'fermees': [],
        'expirees': []
    }
    
    for eval_info in evaluations:
        status = get_evaluation_status(eval_info)
        
        if status == 'ouverte':
            result['ouvertes'].append(eval_info)
        elif status == 'fermee':
            result['fermees'].append(eval_info)
        else:  # expiree
            result['expirees'].append(eval_info)
    
    return result

def update_evaluation_info(eval_dir: str, updated_info: Dict) -> bool:
    """
    Met à jour les informations d'une évaluation
    
    Args:
        eval_dir: Chemin vers le dossier d'évaluation
        updated_info: Informations mises à jour
    
    Returns:
        bool: True si succès, False sinon
    """
    
    try:
        info_file = Path(eval_dir) / "infos_evaluation.json"
        
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(updated_info, f, ensure_ascii=False, indent=2)
        
        return True
        
    except Exception as e:
        print(f"Erreur mise à jour évaluation: {e}")
        return False

def check_automatic_closures(evaluations: List[Dict]) -> List[Dict]:
    """
    Vérifie et met à jour automatiquement les évaluations expirées
    
    Returns:
        List[Dict]: Liste des évaluations mises à jour
    """
    
    updated_evaluations = []
    
    for eval_info in evaluations:
        current_status = get_evaluation_status(eval_info)
        
        # Si l'évaluation est expirée mais pas encore marquée
        if current_status == 'expiree' and eval_info.get('statut') != 'expiree':
            eval_info = mark_evaluation_expired(eval_info)
            
            # Mettre à jour le fichier
            if eval_info.get('dossier'):
                update_evaluation_info(eval_info['dossier'], eval_info)
        
        updated_evaluations.append(eval_info)
    
    return updated_evaluations

def get_submission_statistics(eval_info: Dict) -> Dict:
    """
    Calcule les statistiques de soumission pour une évaluation
    
    Returns:
        Dict: Statistiques de soumission
    """
    
    try:
        eval_dir = Path(eval_info['dossier'])
        copies_dir = eval_dir / "copies_soumises"
        results_dir = eval_dir / "resultats"
        
        # Compter les copies
        copies_count = len(list(copies_dir.glob("*.pdf"))) if copies_dir.exists() else 0
        
        # Vérifier la correction
        is_corrected = results_dir.exists() and any(results_dir.iterdir())
        
        # Calculer le taux de soumission (approximatif)
        # Note: Ceci nécessiterait une liste d'étudiants inscrits pour être précis
        
        return {
            'copies_soumises': copies_count,
            'est_corrigee': is_corrected,
            'statut_correction': 'Corrigée' if is_corrected else 'En attente'
        }
        
    except Exception as e:
        return {
            'copies_soumises': 0,
            'est_corrigee': False,
            'statut_correction': 'Erreur',
            'erreur': str(e)
        }

def format_evaluation_status_message(eval_info: Dict) -> str:
    """
    Formate un message de statut pour une évaluation
    
    Returns:
        str: Message de statut formaté
    """
    
    status = get_evaluation_status(eval_info)
    echeance = calculate_evaluation_deadline(eval_info)
    temps_restant = calculate_time_remaining(eval_info)
    
    if status == 'ouverte':
        if temps_restant:
            return f"🟢 Ouverte - Échéance dans {temps_restant}"
        else:
            return "⏰ Ouverte - Échéance très proche"
    elif status == 'fermee':
        return f"🔒 Fermée manuellement le {eval_info.get('date_fermeture', 'date inconnue')}"
    else:  # expiree
        return f"⏰ Expirée - Échéance dépassée le {echeance.strftime('%d/%m/%Y à %H:%M')}"

def can_student_submit(eval_info: Dict, student_info: Dict) -> tuple[bool, str]:
    """
    Vérifie si un étudiant peut soumettre pour une évaluation
    
    Returns:
        tuple: (peut_soumettre, message_explication)
    """
    
    status = get_evaluation_status(eval_info)
    
    if status == 'ouverte':
        temps_restant = calculate_time_remaining(eval_info)
        if temps_restant:
            return True, f"Soumission possible - {temps_restant} restant"
        else:
            return False, "Échéance très proche - Soumettez rapidement"
    elif status == 'fermee':
        return False, "Évaluation fermée par le professeur"
    else:  # expiree
        return False, "Échéance de soumission dépassée"

# Fonction de maintenance pour nettoyer les anciennes évaluations
def cleanup_old_evaluations(evaluations: List[Dict], days_old: int = 30) -> List[Dict]:
    """
    Identifie les évaluations anciennes pour nettoyage
    
    Args:
        evaluations: Liste des évaluations
        days_old: Nombre de jours pour considérer comme ancien
    
    Returns:
        List[Dict]: Évaluations anciennes
    """
    
    cutoff_date = datetime.now() - timedelta(days=days_old)
    old_evaluations = []
    
    for eval_info in evaluations:
        eval_date = datetime.strptime(eval_info['date'], '%Y-%m-%d')
        
        if eval_date < cutoff_date:
            old_evaluations.append(eval_info)
    
    return old_evaluations

if __name__ == "__main__":
    print("🔧 Utils gestion fermeture évaluations prêts !")