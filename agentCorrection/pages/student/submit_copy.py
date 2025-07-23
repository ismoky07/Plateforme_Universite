"""
pages/student/submit_copy.py - Version avec BLOCAGE soumission si fermée/expirée
===============================================================================
"""

import streamlit as st
from datetime import datetime, timedelta
from utils.data_manager import get_evaluations_list, clear_all_cache
from utils.student_manager import submit_student_copy
from utils.display_helpers import display_header

def show():
    """Page de soumission de copie pour une épreuve avec VÉRIFICATIONS SÉCURISÉES"""
    if not st.session_state.get('student_logged_in', False):
        st.warning("⚠️ Veuillez vous connecter d'abord")
        return
    
    display_header("📤 Soumettre ma Copie")
    

    
    # Gestion de la redirection depuis la page des épreuves
    if st.session_state.get('redirect_to_submission', False):
        selected_eval = st.session_state.get('selected_eval_for_submission')
        st.session_state.redirect_to_submission = False
        st.session_state.selected_eval_for_submission = None
    else:
        # CHARGEMENT INTELLIGENT DES ÉVALUATIONS
        evaluations = get_evaluations_list()
        
        if not evaluations:
            st.warning("⚠️ Aucune épreuve disponible")
            
            if st.button("🔄 Actualiser les épreuves", type="secondary"):
                clear_all_cache()
                st.rerun()
            return
        
        # SÉLECTION DE L'ÉPREUVE avec FILTRAGE des épreuves OUVERTES uniquement
        st.subheader("🎯 Sélection de l'Épreuve")
        
        # Filtrer les évaluations OUVERTES seulement
        current_time = datetime.now()
        evaluations_ouvertes = []
        
        for eval_info in evaluations:
            status = _get_evaluation_status(eval_info, current_time)
            if status == 'ouverte':
                evaluations_ouvertes.append(eval_info)
        
        if not evaluations_ouvertes:
            st.error("🔒 **Aucune épreuve ouverte pour soumission**")
            st.write("**Raisons possibles :**")
            st.write("• Toutes les épreuves sont fermées par le professeur")
            st.write("• Toutes les échéances sont dépassées")
            st.write("• Aucune épreuve n'a encore été créée")
            
            if st.button("🔄 Vérifier à nouveau"):
                clear_all_cache()
                st.rerun()
            return
        
        eval_options = {f"{e['titre']} - {e['matiere']} ({e['date']})": e for e in evaluations_ouvertes}
        selected_eval_name = st.selectbox("Choisir l'épreuve", list(eval_options.keys()))
        selected_eval = eval_options[selected_eval_name]
    
    student_info = st.session_state.get('student_info', {})
    
    # VÉRIFICATION SÉCURISÉE du statut de l'évaluation
    current_time = datetime.now()
    eval_status = _get_evaluation_status(selected_eval, current_time)
    
    # BLOCAGE SÉCURISÉ si évaluation fermée/expirée
    if eval_status != 'ouverte':
        _show_blocked_submission(selected_eval, eval_status, current_time)
        return
    
    # Informations sur l'épreuve
    _show_exam_info(selected_eval, student_info, current_time)
    
    st.markdown("---")
    
    # Interface de soumission (seulement si ouverte)
    uploaded_files, digital_response, submission_type = _show_submission_interface()
    
    # Vérifications et soumission avec DOUBLE VÉRIFICATION
    _handle_submission_with_security(selected_eval, student_info, uploaded_files, digital_response, submission_type)

def _show_blocked_submission(selected_eval, eval_status, current_time):
    """Affiche le blocage de soumission avec explications"""
    
    st.error("🚫 **SOUMISSION BLOQUÉE**")
    
    # Informations sur l'épreuve
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**📚 Épreuve :** {selected_eval['titre']}")
        st.write(f"**📅 Date :** {selected_eval['date']}")
        st.write(f"**⏰ Heure :** {selected_eval.get('heure_debut', '08:00')}")
    
    with col2:
        st.write(f"**⏱️ Durée :** {selected_eval['duree']}")
        echeance = _calculate_deadline(selected_eval)
        st.write(f"**🏁 Échéance :** {echeance.strftime('%d/%m/%Y %H:%M')}")
    
    st.markdown("---")
    
    # Explication du blocage selon le statut
    if eval_status == 'fermee':
        st.error("🔒 **Épreuve fermée par le professeur**")
        st.write("**Motif :** Le professeur a fermé manuellement cette épreuve")
        st.write("**Action :** Plus aucune soumission n'est acceptée")
        
        if selected_eval.get('date_fermeture'):
            date_fermeture = datetime.fromisoformat(selected_eval['date_fermeture'])
            st.write(f"**Date de fermeture :** {date_fermeture.strftime('%d/%m/%Y à %H:%M')}")
    
    elif eval_status == 'expiree':
        st.warning("⏰ **Échéance dépassée**")
        st.write("**Motif :** Le délai de soumission est terminé")
        
        echeance = _calculate_deadline(selected_eval)
        delta = current_time - echeance
        
        if delta.days > 0:
            retard = f"{delta.days} jour(s) et {delta.seconds // 3600} heure(s)"
        elif delta.seconds > 3600:
            retard = f"{delta.seconds // 3600} heure(s) et {(delta.seconds % 3600) // 60} minute(s)"
        else:
            retard = f"{delta.seconds // 60} minute(s)"
        
        st.write(f"**Retard :** {retard} après l'échéance")
    
    # Actions possibles
    st.markdown("---")
    st.info("💡 **Que faire ?**")
    st.write("• Contactez immédiatement votre professeur")
    st.write("• Expliquez votre situation (problème technique, retard, etc.)")
    st.write("• Le professeur peut éventuellement rouvrir ou prolonger l'épreuve")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("📝 Retour aux épreuves"):
            st.session_state.page_redirect = "📝 Épreuves disponibles"
            st.rerun()
    
    with col_btn2:
        if st.button("🔄 Vérifier à nouveau"):
            clear_all_cache()
            st.rerun()

def _get_evaluation_status(eval_info, current_time):
    """Détermine le statut d'une évaluation - MÊME LOGIQUE que available_exams.py"""
    
    # PRIORITÉ 1: Fermeture manuelle par le professeur
    if eval_info.get('statut') == 'fermee':
        return 'fermee'
    
    # PRIORITÉ 2: Calculer l'échéance (avec prolongation)
    echeance = _calculate_deadline(eval_info)
    
    # PRIORITÉ 3: Vérifier si expirée automatiquement
    if current_time > echeance:
        return 'expiree'
    
    # PRIORITÉ 4: Sinon c'est ouvert
    return 'ouverte'

def _calculate_deadline(eval_info):
    """Calcule l'échéance d'une évaluation - MÊME LOGIQUE que available_exams.py"""
    
    # PRIORITÉ ABSOLUE: Si échéance prolongée, l'utiliser
    if eval_info.get('echeance_prolongee'):
        try:
            return datetime.fromisoformat(eval_info['echeance_prolongee'])
        except:
            pass
    
    # Calcul normal avec heure de début
    date_str = eval_info['date']
    heure_debut_str = eval_info.get('heure_debut', '08:00')
    
    # Créer datetime avec date ET heure
    eval_datetime = datetime.strptime(f"{date_str} {heure_debut_str}", '%Y-%m-%d %H:%M')
    
    # Durée en heures
    duree_str = eval_info['duree']
    
    if 'h30' in duree_str:
        heures = float(duree_str.replace('h30', '')) + 0.5
    elif 'h' in duree_str:
        heures = float(duree_str.replace('h', ''))
    else:
        heures = 2.0
    
    return eval_datetime + timedelta(hours=heures)

def _show_exam_info(selected_eval, student_info, current_time):
    """Affiche les informations sur l'épreuve avec statut"""
    st.subheader(f"📚 {selected_eval['titre']}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"**Matière :** {selected_eval['matiere']}")
        st.write(f"**Date :** {selected_eval['date']}")
        st.write(f"**Heure :** {selected_eval.get('heure_debut', '08:00')}")
    with col2:
        st.write(f"**Durée :** {selected_eval['duree']}")
        st.write(f"**Professeur :** {selected_eval['professeur']}")
        
        echeance = _calculate_deadline(selected_eval)
        st.write(f"**Échéance :** {echeance.strftime('%d/%m/%Y %H:%M')}")
    with col3:
        st.write(f"**Étudiant :** {student_info['prenom']} {student_info['nom']}")
        st.write(f"**N° :** {student_info['numero']}")
        
        # Afficher temps restant
        temps_restant = _calculate_time_remaining(current_time, echeance)
        if temps_restant:
            st.success(f"⏰ **{temps_restant}** restant")
        else:
            st.error("⏰ **Temps écoulé !**")

def _calculate_time_remaining(current_time, deadline):
    """Calcule le temps restant avant échéance"""
    
    if current_time >= deadline:
        return None
    
    delta = deadline - current_time
    
    if delta.days > 0:
        return f"{delta.days}j {delta.seconds // 3600}h"
    elif delta.seconds > 3600:
        return f"{delta.seconds // 3600}h {(delta.seconds % 3600) // 60}min"
    else:
        return f"{delta.seconds // 60}min"

def _show_submission_interface():
    """Affiche l'interface de soumission"""
    st.subheader("📄 Télécharger ma copie")
    
    submission_type = st.radio(
        "Type de soumission",
        ["📱 Photos/Scans", "📄 PDF unique", "✏️ Saisie numérique"]
    )
    
    uploaded_files = None
    digital_response = ""
    
    if submission_type == "📱 Photos/Scans":
        uploaded_files = _handle_photo_upload()
        
    elif submission_type == "📄 PDF unique":
        uploaded_files = _handle_pdf_upload()
        
    else:  # Saisie numérique
        digital_response = _handle_digital_input()
    
    return uploaded_files, digital_response, submission_type

def _handle_photo_upload():
    """Gère l'upload de photos/scans"""
    st.info("💡 Prenez des photos claires de chaque page de votre copie")
    uploaded_files = st.file_uploader(
        "Télécharger les photos de votre copie",
        type=['jpg', 'jpeg', 'png', 'pdf'],
        accept_multiple_files=True,
        help="Formats acceptés : JPG, PNG, PDF. Assurez-vous que le texte est lisible !"
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} fichier(s) sélectionné(s)")
        
        for i, file in enumerate(uploaded_files, 1):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"📄 Page {i}: {file.name}")
            with col2:
                size_mb = len(file.getvalue()) / 1024 / 1024
                st.write(f"{size_mb:.1f} MB")
    
    return uploaded_files

def _handle_pdf_upload():
    """Gère l'upload de PDF"""
    st.info("💡 Téléchargez votre copie au format PDF")
    uploaded_file = st.file_uploader(
        "Télécharger votre copie PDF",
        type=['pdf'],
        accept_multiple_files=False,
        help="Format accepté : PDF uniquement"
    )
    
    if uploaded_file:
        uploaded_files = [uploaded_file]
        size_mb = len(uploaded_file.getvalue()) / 1024 / 1024
        st.success(f"✅ PDF téléchargé ({size_mb:.1f} MB)")
        return uploaded_files
    
    return None

def _handle_digital_input():
    """Gère la saisie numérique"""
    st.info("💡 Rédigez votre réponse directement dans l'interface")
    digital_response = st.text_area(
        "Votre réponse",
        height=400,
        placeholder="Rédigez votre réponse ici...\n\n1. Question 1:\n...\n\n2. Question 2:\n..."
    )
    
    if digital_response:
        word_count = len(digital_response.split())
        char_count = len(digital_response)
        st.info(f"📝 {word_count} mots, {char_count} caractères")
    
    return digital_response

def _handle_submission_with_security(selected_eval, student_info, uploaded_files, digital_response, submission_type):
    """Gère le processus de soumission avec DOUBLE VÉRIFICATION sécurisée"""
    
    # Vérifications avant soumission
    st.markdown("---")
    st.subheader("✅ Vérifications avant soumission")
    
    checks = []
    
    if submission_type in ["📱 Photos/Scans", "📄 PDF unique"]:
        if uploaded_files:
            checks.append("✅ Fichier(s) téléchargé(s)")
        else:
            checks.append("❌ Aucun fichier sélectionné")
    else:
        if digital_response.strip():
            checks.append("✅ Réponse rédigée")
        else:
            checks.append("❌ Aucune réponse saisie")
    
    # VÉRIFICATION SÉCURISÉE du statut avant soumission
    current_time = datetime.now()
    eval_status = _get_evaluation_status(selected_eval, current_time)
    
    if eval_status == 'ouverte':
        checks.append("✅ Épreuve ouverte")
    else:
        checks.append(f"❌ Épreuve {eval_status}")
    
    for check in checks:
        st.write(check)
    
    st.markdown("---")
    
    confirmation = st.checkbox(
        "🔒 Je confirme que cette copie est mon propre travail et que je souhaite la soumettre définitivement",
        value=False
    )
    
    # CONDITION RENFORCÉE pour la soumission
    can_submit = (
        (uploaded_files and len(uploaded_files) > 0) or 
        (submission_type == "✏️ Saisie numérique" and digital_response.strip())
    ) and confirmation and eval_status == 'ouverte'  # NOUVELLE CONDITION SÉCURISÉE
    
    # Message d'alerte si épreuve fermée/expirée
    if eval_status != 'ouverte':
        if eval_status == 'fermee':
            st.error("🚫 **IMPOSSIBLE DE SOUMETTRE** - Épreuve fermée par le professeur")
        else:
            st.error("🚫 **IMPOSSIBLE DE SOUMETTRE** - Échéance dépassée")
        
        st.warning("⚠️ Contactez votre professeur en urgence si vous pensez qu'il y a une erreur")
    
    if st.button("🚀 SOUMETTRE MA COPIE", type="primary", disabled=not can_submit):
        
        # TRIPLE VÉRIFICATION ULTIME avant soumission
        final_status = _get_evaluation_status(selected_eval, datetime.now())
        
        if final_status != 'ouverte':
            st.error("🚫 **SOUMISSION REFUSÉE** - L'épreuve vient d'être fermée ou l'échéance a été atteinte")
            st.warning("⏰ Actualisez la page et contactez votre professeur")
            if st.button("🔄 Actualiser maintenant"):
                clear_all_cache()
                st.rerun()
            return
        
        # Procéder à la soumission seulement si tout est OK
        if submit_student_copy(selected_eval, student_info, uploaded_files, digital_response, submission_type):
            # INVALIDATION CACHE APRÈS SOUMISSION
            clear_all_cache()
            
            st.balloons()
            st.success("🎉 Copie soumise avec succès !")
            st.info("📧 Vous recevrez une confirmation par email")
            st.info("🤖 La correction automatique sera lancée par votre professeur")
            
            # ACTUALISATION AUTOMATIQUE
            st.success("🔄 Vos données ont été actualisées automatiquement")
            
            if st.button("📋 Retour aux épreuves"):
                st.rerun()
        else:
            st.error("❌ Erreur lors de la soumission. Veuillez réessayer.")

if __name__ == "__main__":
    print("📤 Submit Copy avec blocage sécurisé prêt !")