"""
pages/professor/dashboard.py - Version avec statuts de publication
================================================================
Dashboard affichant les statuts d'évaluation et de publication
"""

import streamlit as st
from pathlib import Path
from datetime import datetime, timedelta
from utils.data_manager import get_evaluations_list, clear_all_cache
from utils.display_helpers import display_header

def show():
    """Affiche la page tableau de bord professeur avec statuts de publication"""
    display_header("🎓 Tableau de Bord Professeur")
    
    # BOUTON D'ACTUALISATION GLOBALE
    col1, col2, col3 = st.columns([2, 1, 1])
    with col2:
        if st.button("🔄 Actualiser", help="Actualiser toutes les données"):
            clear_all_cache()
            st.success("✅ Données actualisées")
            st.rerun()
    with col3:
        # Auto-refresh toutes les 60 secondes
        if st.button("⚡ Auto-refresh", help="Actualisation automatique"):
            st.session_state.auto_refresh = not st.session_state.get('auto_refresh', False)
            if st.session_state.auto_refresh:
                st.success("🔄 Auto-refresh activé")
            else:
                st.info("⏸️ Auto-refresh désactivé")
    
    evaluations = get_evaluations_list()
    
    # MÉTRIQUES GÉNÉRALES AMÉLIORÉES
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("📚 Évaluations créées", len(evaluations))
    
    with col2:
        # Compter les évaluations ouvertes
        ouvertes = len([e for e in evaluations if _get_evaluation_status(e) == "ouverte"])
        st.metric("🟢 Évaluations ouvertes", ouvertes)
    
    with col3:
        # Compter les évaluations corrigées
        corrected_evals = 0
        for eval_info in evaluations:
            results_dir = Path(eval_info['dossier']) / "resultats"
            if results_dir.exists() and any(results_dir.iterdir()):
                corrected_evals += 1
        st.metric("✅ Évaluations corrigées", corrected_evals)
    
    with col4:
        # Compter les évaluations publiées
        published_evals = len([e for e in evaluations if e.get('statut_publication') == 'publie'])
        st.metric("📢 Résultats publiés", published_evals)
    
    with col5:
        # Compter les copies totales
        total_copies = 0
        for eval_info in evaluations:
            copies_dir = Path(eval_info['dossier']) / "copies_soumises"
            if copies_dir.exists():
                total_copies += len(list(copies_dir.glob("*.pdf")))
        st.metric("📄 Copies totales", total_copies)
    
    st.markdown("---")
    
    # ALERTES ET NOTIFICATIONS
    _show_alerts_section(evaluations)
    
    st.markdown("---")
    
    # Auto-refresh automatique
    if st.session_state.get('auto_refresh', False):
        st.info("🔄 Mode auto-refresh activé - Actualisation toutes les 60 secondes")
        import time
        time.sleep(60)
        st.rerun()
    
    # LISTE DES ÉVALUATIONS DÉTAILLÉE
    if evaluations:
        st.subheader("📋 Mes Évaluations")
        
        # Tri par date (plus récentes en premier)
        evaluations_sorted = sorted(evaluations, key=lambda x: x['date'], reverse=True)
        
        for eval_info in evaluations_sorted:
            _show_evaluation_card(eval_info)
    else:
        st.info("📝 Aucune évaluation créée. Utilisez la page 'Créer évaluation' pour commencer.")

def _show_alerts_section(evaluations):
    """Affiche la section des alertes et notifications"""
    st.subheader("🚨 Alertes & Notifications")
    
    alerts = []
    
    # Vérifier les évaluations qui arrivent à échéance
    for eval_info in evaluations:
        status = _get_evaluation_status(eval_info)
        
        if status == "ouverte":
            echeance = _calculate_deadline(eval_info)
            maintenant = datetime.now()
            
            if echeance > maintenant:
                delta = echeance - maintenant
                
                # Alerte si moins de 2 heures restantes
                if delta.total_seconds() < 2 * 3600:
                    alerts.append({
                        "type": "warning",
                        "message": f"⏰ {eval_info['titre']} se termine dans {delta.seconds // 3600}h {(delta.seconds % 3600) // 60}min",
                        "action": "Surveiller les soumissions"
                    })
        
        # Vérifier les évaluations corrigées mais non publiées
        results_dir = Path(eval_info['dossier']) / "resultats"
        if results_dir.exists() and any(results_dir.iterdir()):
            if eval_info.get('statut_publication', 'brouillon') == 'brouillon':
                alerts.append({
                    "type": "info",
                    "message": f"📝 {eval_info['titre']} corrigée mais non publiée",
                    "action": "Publier les résultats"
                })
        
        # Vérifier les évaluations fermées avec peu de copies
        copies_dir = Path(eval_info['dossier']) / "copies_soumises"
        if copies_dir.exists():
            nb_copies = len(list(copies_dir.glob("*.pdf")))
            if status in ["fermee", "expiree"] and nb_copies < 5:
                alerts.append({
                    "type": "warning",
                    "message": f"⚠️ {eval_info['titre']} fermée avec seulement {nb_copies} copies",
                    "action": "Vérifier les soumissions"
                })
    
    if alerts:
        for alert in alerts[:5]:  # Limiter à 5 alertes
            if alert["type"] == "warning":
                st.warning(f"{alert['message']} - {alert['action']}")
            elif alert["type"] == "info":
                st.info(f"{alert['message']} - {alert['action']}")
            elif alert["type"] == "error":
                st.error(f"{alert['message']} - {alert['action']}")
    else:
        st.success("✅ Aucune alerte - Tout va bien !")

def _show_evaluation_card(eval_info):
    """Affiche une carte détaillée pour chaque évaluation"""
    
    # Calculer les statuts
    eval_status = _get_evaluation_status(eval_info)
    
    # Vérifier si corrigée
    results_dir = Path(eval_info['dossier']) / "resultats"
    is_corrected = results_dir.exists() and any(results_dir.iterdir())
    
    # Statut de publication
    publication_status = eval_info.get('statut_publication', 'brouillon')
    
    # Icônes selon les statuts
    if eval_status == "ouverte":
        status_icon = "🟢"
        status_text = "Ouverte"
    elif eval_status == "fermee":
        status_icon = "🔴"
        status_text = "Fermée"
    else:  # expiree
        status_icon = "🟡"
        status_text = "Expirée"
    
    # Icône de correction
    if is_corrected:
        correction_icon = "✅"
        correction_text = "Corrigée"
    else:
        correction_icon = "⏳"
        correction_text = "En attente"
    
    # Icône de publication
    if publication_status == 'publie':
        publication_icon = "📢"
        publication_text = "Publiée"
    elif publication_status == 'depublie':
        publication_icon = "🚫"
        publication_text = "Dépubliée"
    else:
        publication_icon = "📝"
        publication_text = "Brouillon"
    
    # Titre de la carte
    card_title = f"{status_icon} {eval_info['titre']} - {eval_info['matiere']}"
    
    with st.expander(card_title, expanded=False):
        
        # Ligne 1 : Informations générales
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write(f"**📅 Date :** {eval_info['date']}")
            st.write(f"**⏰ Heure :** {eval_info.get('heure_debut', '08:00')}")
            st.write(f"**⏱️ Durée :** {eval_info['duree']}")
        
        with col2:
            st.write(f"**🎓 Promotion :** {eval_info['promotion']}")
            st.write(f"**👨‍🏫 Professeur :** {eval_info['professeur']}")
            st.write(f"**📊 Note totale :** {eval_info['note_totale']}")
        
        with col3:
            # Échéance
            echeance = _calculate_deadline(eval_info)
            st.write(f"**⏰ Échéance :** {echeance.strftime('%d/%m/%Y %H:%M')}")
            
            # Temps restant ou dépassé
            maintenant = datetime.now()
            if maintenant < echeance:
                delta = echeance - maintenant
                if delta.days > 0:
                    temps_restant = f"{delta.days}j {delta.seconds // 3600}h"
                else:
                    temps_restant = f"{delta.seconds // 3600}h {(delta.seconds % 3600) // 60}min"
                st.write(f"**⏳ Temps restant :** {temps_restant}")
            else:
                st.write(f"**⏰ Échéance :** Dépassée")
        
        # Ligne 2 : Statuts
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if eval_status == "ouverte":
                st.success(f"{status_icon} {status_text}")
            elif eval_status == "fermee":
                st.error(f"{status_icon} {status_text}")
            else:
                st.warning(f"{status_icon} {status_text}")
        
        with col2:
            if is_corrected:
                st.success(f"{correction_icon} {correction_text}")
            else:
                st.info(f"{correction_icon} {correction_text}")
        
        with col3:
            if publication_status == 'publie':
                st.success(f"{publication_icon} {publication_text}")
            elif publication_status == 'depublie':
                st.error(f"{publication_icon} {publication_text}")
            else:
                st.warning(f"{publication_icon} {publication_text}")
        
        with col4:
            # Nombre de copies
            copies_dir = Path(eval_info['dossier']) / "copies_soumises"
            nb_copies = len(list(copies_dir.glob("*.pdf"))) if copies_dir.exists() else 0
            st.metric("📄 Copies", nb_copies)
        
        # Ligne 3 : Actions
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button(f"📤 Gérer copies", key=f"copies_{eval_info['id_evaluation']}"):
                st.session_state.selected_eval = eval_info['dossier']
                st.session_state.page_redirect = "📤 Gérer copies"
                st.rerun()
        
        with col2:
            if eval_status in ["fermee", "expiree"]:
                if st.button(f"🤖 Correction", key=f"correct_{eval_info['id_evaluation']}"):
                    st.session_state.selected_eval = eval_info['dossier']
                    st.session_state.page_redirect = "🤖 Lancer correction"
                    st.rerun()
            else:
                st.button(f"🤖 Correction", key=f"correct_disabled_{eval_info['id_evaluation']}", disabled=True, help="Fermer l'évaluation d'abord")
        
        with col3:
            if is_corrected:
                if st.button(f"📊 Rapports", key=f"reports_{eval_info['id_evaluation']}"):
                    st.session_state.selected_eval = eval_info['dossier']
                    st.session_state.page_redirect = "📊 Consulter rapports"
                    st.rerun()
            else:
                st.button(f"📊 Rapports", key=f"reports_disabled_{eval_info['id_evaluation']}", disabled=True, help="Corriger d'abord")
        
        with col4:
            if st.button(f"⚙️ Gérer", key=f"manage_{eval_info['id_evaluation']}"):
                st.session_state.page_redirect = "➕ Créer & Gérer Évaluations"
                st.rerun()

def _get_evaluation_status(eval_info):
    """Détermine le statut d'une évaluation"""
    
    # Vérifier si fermée manuellement
    if eval_info.get('statut') == 'fermee':
        return 'fermee'
    
    # Vérifier si expirée automatiquement
    echeance = _calculate_deadline(eval_info)
    if datetime.now() > echeance:
        return 'expiree'
    
    return 'ouverte'

def _calculate_deadline(eval_info):
    """Calcule l'échéance d'une évaluation avec heure de début"""
    
    # Date et heure de début de l'évaluation
    date_str = eval_info['date']
    heure_debut_str = eval_info.get('heure_debut', '08:00')
    
    # Créer datetime avec date ET heure
    eval_datetime = datetime.strptime(f"{date_str} {heure_debut_str}", '%Y-%m-%d %H:%M')
    
    # Durée en heures
    duree_str = eval_info['duree']
    
    # Parser la durée
    if 'h30' in duree_str:
        heures = float(duree_str.replace('h30', '')) + 0.5
    elif 'h' in duree_str:
        heures = float(duree_str.replace('h', ''))
    else:
        heures = 2.0  # Défaut
    
    # Ajouter les heures à la date AVEC heure de début
    echeance = eval_datetime + timedelta(hours=heures)
    
    # Si échéance prolongée manuellement
    if eval_info.get('echeance_prolongee'):
        echeance = datetime.fromisoformat(eval_info['echeance_prolongee'])
    
    return echeance

if __name__ == "__main__":
    print("🎓 Dashboard avec statuts de publication prêt !")