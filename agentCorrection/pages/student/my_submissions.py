
"""
pages/student/my_submissions.py - Version sans problème de cache
"""

import streamlit as st
from pathlib import Path
from utils.data_manager import get_evaluations_list, clear_all_cache
from utils.student_manager import check_student_submission
from utils.display_helpers import display_header, show_submission_details

def show():
    """Page de suivi des soumissions de l'étudiant"""
    if not st.session_state.get('student_logged_in', False):
        st.warning("⚠️ Veuillez vous connecter d'abord")
        return
    
    student_info = st.session_state.get('student_info', {})
    
    display_header("📤 Mes Soumissions")
    
    
    # CHARGEMENT INTELLIGENT DES DONNÉES
    evaluations = get_evaluations_list()
    submissions = []
    
    for eval_info in evaluations:
        submission = check_student_submission(eval_info, student_info)
        if submission:
            submission['evaluation_info'] = eval_info
            submissions.append(submission)
    
    if not submissions:
        st.info("📭 Aucune soumission trouvée")
        
        # SUGGESTIONS
        st.markdown("---")
        st.write("💡 **Suggestions :**")
        st.write("• Vérifiez les épreuves disponibles")
        st.write("• Soumettez vos copies pour les voir apparaître ici")
        st.write("• Assurez-vous d'être connecté avec le bon compte")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📝 Voir épreuves disponibles"):
                st.session_state.page_redirect = "📝 Épreuves disponibles"
                st.rerun()
        with col2:
            if st.button("🔄 Actualiser", type="secondary"):
                clear_all_cache()
                st.rerun()
        return
    
    # MÉTRIQUES DES SOUMISSIONS
    total_submissions = len(submissions)
    corrected_submissions = 0
    pending_submissions = 0
    
    for submission in submissions:
        eval_info = submission['evaluation_info']
        results_dir = Path(eval_info['dossier']) / "resultats"
        student_dir_name = f"{student_info['nom']}_{student_info['prenom']}"
        student_result_dir = results_dir / student_dir_name
        
        if student_result_dir.exists():
            corrected_submissions += 1
        else:
            pending_submissions += 1
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📤 Total soumissions", total_submissions)
    with col2:
        st.metric("✅ Corrigées", corrected_submissions)
    with col3:
        st.metric("⏳ En attente", pending_submissions)
    
    st.markdown("---")
    st.subheader(f"📋 Mes {len(submissions)} soumission(s)")
    
    for submission in submissions:
        eval_info = submission['evaluation_info']
        
        # VÉRIFICATION STATUT CORRECTION
        results_dir = Path(eval_info['dossier']) / "resultats"
        student_dir_name = f"{student_info['nom']}_{student_info['prenom']}"
        student_result_dir = results_dir / student_dir_name
        
        is_corrected = student_result_dir.exists()
        status_icon = "✅" if is_corrected else "⏳"
        
        with st.expander(f"{status_icon} {eval_info['titre']} - Soumis le {submission['date_soumission']}", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**Matière :** {eval_info['matiere']}")
                st.write(f"**Type :** {submission['type_soumission']}")
                st.write(f"**Fichiers :** {submission['nombre_fichiers']}")
                
                if submission.get('reponse_numerique'):
                    st.write(f"**Mots :** {submission.get('nombre_mots', 'N/A')}")
            
            with col2:
                st.write(f"**Date soumission :** {submission['date_soumission']}")
                st.write(f"**Taille :** {submission.get('taille_totale', 'N/A')}")
                
                if is_corrected:
                    st.success("✅ Corrigée")
                else:
                    st.warning("⏳ En attente de correction")
            
            with col3:
                # ACTIONS
                if st.button(f"👀 Détails complets", key=f"details_{eval_info['id_evaluation']}"):
                    show_submission_details(submission)
                
                if is_corrected:
                    if st.button(f"📊 Voir résultat", key=f"result_{eval_info['id_evaluation']}", type="primary"):
                        st.session_state.page_redirect = "📊 Mes résultats"
                        st.rerun()
                else:
                    st.caption("🔄 Actualisez pour vérifier l'état")
    
    # AUTO-REFRESH
    if st.session_state.get('auto_refresh_submissions', False):
        st.info("⚡ Mode auto-refresh activé - Vérification toutes les 30 secondes")
        import time
        time.sleep(30)
        clear_all_cache()
        st.rerun()