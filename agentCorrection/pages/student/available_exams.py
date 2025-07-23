"""
pages/student/available_exams.py - Version FINALE avec fermeture manuelle CORRIGÉE
==================================================================================
"""

import streamlit as st
from datetime import datetime, timedelta
from utils.data_manager import get_evaluations_list, clear_all_cache
from utils.student_manager import check_student_submission
from utils.display_helpers import display_header

def show():
    """Page des épreuves disponibles pour soumission avec gestion fermetures - VERSION FINALE"""
    if not st.session_state.get('student_logged_in', False):
        st.warning("⚠️ Veuillez vous connecter d'abord")
        return
    
    student_info = st.session_state.get('student_info', {})
    
    display_header("📝 Épreuves Disponibles")
    
    # EN-TÊTE AVEC INFORMATIONS ET ACTUALISATION
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.write(f"**Connecté en tant que :** {student_info['prenom']} {student_info['nom']} ({student_info['numero']})")
    with col2:
        if st.button("🔄 Actualiser", help="Actualiser la liste des épreuves"):
            clear_all_cache()
            # Forcer rechargement complet
            if 'evaluations_cache' in st.session_state:
                del st.session_state.evaluations_cache
            st.success("✅ Actualisé !")
            st.rerun()
    with col3:
        # Timestamp de dernière actualisation
        now = datetime.now()
        st.caption(f"⏰ {now.strftime('%H:%M:%S')}")
    
    # CHARGEMENT INTELLIGENT DES DONNÉES
    evaluations = get_evaluations_list()
    
    if not evaluations:
        st.info("📭 Aucune épreuve disponible pour le moment")
        
        # MESSAGE D'AIDE
        st.markdown("---")
        st.write("💡 **Que faire ?**")
        st.write("• Attendez qu'un professeur crée une épreuve")
        st.write("• Vérifiez que vous êtes connecté avec le bon compte")
        st.write("• Contactez votre professeur si une épreuve devrait être disponible")
        
        if st.button("🔄 Vérifier à nouveau", type="secondary"):
            clear_all_cache()
            st.rerun()
        return
    
    current_time = datetime.now()
    
    # ANALYSE DES ÉPREUVES AVEC NOUVEAUX STATUTS
    evaluations_stats = _analyze_evaluations_status(evaluations, student_info, current_time)
    
    # MÉTRIQUES MISES À JOUR
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📚 Total épreuves", evaluations_stats['total'])
    
    with col2:
        st.metric("🟢 Ouvertes", evaluations_stats['ouvertes'])
    
    with col3:
        st.metric("✅ Soumises", evaluations_stats['soumises'])
    
    with col4:
        st.metric("🔒 Fermées", evaluations_stats['fermees'])
    
    st.markdown("---")
    
    # AFFICHAGE DES ÉPREUVES PAR CATÉGORIE
    _display_evaluations_by_category(evaluations, student_info, current_time)
    
    # RÈGLES ET INFORMATIONS
    st.markdown("---")
    _show_evaluation_rules()

def _analyze_evaluations_status(evaluations, student_info, current_time):
    """Analyse le statut de toutes les évaluations"""
    
    stats = {
        'total': len(evaluations),
        'ouvertes': 0,
        'fermees': 0,
        'expirees': 0,
        'soumises': 0
    }
    
    for eval_info in evaluations:
        # Vérifier le statut de l'évaluation
        status = _get_evaluation_status(eval_info, current_time)
        
        if status == 'ouverte':
            stats['ouvertes'] += 1
        elif status in ['fermee', 'expiree']:
            stats['fermees'] += 1
        
        # Vérifier les soumissions
        if check_student_submission(eval_info, student_info):
            stats['soumises'] += 1
    
    return stats

def _get_evaluation_status(eval_info, current_time):
    """Détermine le statut d'une évaluation côté étudiant - LOGIQUE FINALE CORRIGÉE"""
    
    # ⚠️ PRIORITÉ 1: Fermeture manuelle par le professeur (PRIME sur tout)
    if eval_info.get('statut') == 'fermee':
        return 'fermee'
    
    # ⚠️ PRIORITÉ 2: Calculer l'échéance (avec prolongation)
    echeance = _calculate_deadline(eval_info)
    
    # ⚠️ PRIORITÉ 3: Vérifier si expirée automatiquement
    if current_time > echeance:
        return 'expiree'
    
    # ⚠️ PRIORITÉ 4: Sinon c'est ouvert
    return 'ouverte'

def _calculate_deadline(eval_info):
    """Calcule l'échéance d'une évaluation - PRIORITÉ PROLONGATION"""
    
    # PRIORITÉ ABSOLUE: Si échéance prolongée, l'utiliser
    if eval_info.get('echeance_prolongee'):
        try:
            return datetime.fromisoformat(eval_info['echeance_prolongee'])
        except:
            pass  # Si erreur, utiliser calcul normal
    
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
    
    # Calculer échéance normale
    return eval_datetime + timedelta(hours=heures)

def _display_evaluations_by_category(evaluations, student_info, current_time):
    """Affiche les évaluations organisées par catégorie"""
    
    # Séparer les évaluations par statut
    ouvertes = []
    fermees = []
    soumises = []
    
    for eval_info in evaluations:
        status = _get_evaluation_status(eval_info, current_time)
        student_submission = check_student_submission(eval_info, student_info)
        
        if student_submission:
            soumises.append((eval_info, status, student_submission))
        elif status == 'ouverte':
            ouvertes.append((eval_info, status, None))
        else:
            fermees.append((eval_info, status, None))
    
    # Afficher les évaluations ouvertes en premier
    if ouvertes:
        st.subheader("🟢 Épreuves Ouvertes - Soumission Possible")
        for eval_info, status, _ in ouvertes:
            _display_evaluation_card(eval_info, status, None, student_info, current_time, "ouverte")
    
    # Afficher les évaluations soumises
    if soumises:
        st.markdown("---")
        st.subheader("✅ Épreuves Soumises")
        for eval_info, status, submission in soumises:
            _display_evaluation_card(eval_info, status, submission, student_info, current_time, "soumise")
    
    # Afficher les évaluations fermées
    if fermees:
        st.markdown("---")
        st.subheader("🔒 Épreuves Fermées")
        for eval_info, status, _ in fermees:
            _display_evaluation_card(eval_info, status, None, student_info, current_time, "fermee")

def _display_evaluation_card(eval_info, status, student_submission, student_info, current_time, category):
    """Affiche une carte d'évaluation selon son statut - VERSION FINALE"""
    
    # Déterminer l'icône et la couleur selon le statut
    if category == "ouverte":
        status_icon = "🟢"
        expanded = True
    elif category == "soumise":
        status_icon = "✅"
        expanded = False
    else:  # fermée
        if status == "expiree":
            status_icon = "⏰"
        else:
            status_icon = "🔒"
        expanded = False
    
    # Calculer l'échéance (avec prolongation incluse)
    echeance = _calculate_deadline(eval_info)
    
    with st.expander(f"{status_icon} {eval_info['titre']} - {eval_info['matiere']}", expanded=expanded):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write(f"**📅 Date :** {eval_info['date']}")
            # Afficher l'heure de début
            heure_debut = eval_info.get('heure_debut', '08:00')
            st.write(f"**⏰ Heure début :** {heure_debut}")
            st.write(f"**⏱️ Durée :** {eval_info['duree']}")
            st.write(f"**👨‍🏫 Professeur :** {eval_info['professeur']}")
        
        with col2:
            # Afficher le statut avec la logique corrigée
            if status == "ouverte":
                st.success("🟢 Ouvert pour soumission")
            elif status == "fermee":
                st.error("🔒 Fermé par le professeur")
            elif status == "expiree":
                st.warning("⏰ Échéance dépassée")
            
            # Afficher l'état de soumission
            if student_submission:
                st.info(f"✅ Soumis le {student_submission['date_soumission']}")
            else:
                st.warning("⏳ Non soumis")
            
            # Afficher si prolongation active (sauf si fermée manuellement)
            if eval_info.get('echeance_prolongee') and status != 'fermee':
                st.info("🔄 Échéance prolongée")
            
            # Afficher si fermée manuellement
            if status == 'fermee':
                st.error("🚫 Fermée manuellement")
        
        with col3:
            # Logique d'affichage du temps selon le statut
            if status == "ouverte":
                temps_restant = _calculate_time_remaining(current_time, echeance)
                if temps_restant:
                    st.metric("⏰ Temps restant", temps_restant)
                    st.caption(f"Échéance: {echeance.strftime('%d/%m %H:%M')}")
                else:
                    st.metric("⏰ Temps restant", "Expiré")
            else:
                # Affichage pour fermée/expirée
                st.write(f"**🏁 Échéance :** {echeance.strftime('%d/%m/%Y %H:%M')}")
                if status == "fermee":
                    st.write("**🚫 Statut :** Fermé manuellement")
                else:
                    st.write("**⏰ Statut :** Échéance dépassée")
        
        # ACTIONS POSSIBLES
        st.markdown("---")
        _display_action_buttons(eval_info, status, student_submission, student_info, category)

def _display_action_buttons(eval_info, status, student_submission, student_info, category):
    """Affiche les boutons d'action selon le contexte"""
    
    if category == "ouverte" and status == "ouverte":
        # Évaluation ouverte - Soumission possible
        if not student_submission:
            if st.button(f"📤 Soumettre ma copie", key=f"submit_{eval_info['id_evaluation']}", type="primary"):
                st.session_state.selected_eval_for_submission = eval_info
                st.session_state.redirect_to_submission = True
                st.rerun()
        else:
            # Déjà soumis mais peut modifier
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button(f"👀 Voir ma soumission", key=f"view_submission_{eval_info['id_evaluation']}"):
                    from utils.display_helpers import show_student_submission
                    show_student_submission(eval_info, student_info)
            with col_btn2:
                if st.button(f"🔄 Modifier ma copie", key=f"resubmit_{eval_info['id_evaluation']}"):
                    st.session_state.selected_eval_for_submission = eval_info
                    st.session_state.redirect_to_submission = True
                    st.rerun()
    
    elif category == "soumise":
        # Évaluation soumise - Consultation uniquement
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button(f"👀 Voir ma soumission", key=f"view_sub_{eval_info['id_evaluation']}"):
                from utils.display_helpers import show_student_submission
                show_student_submission(eval_info, student_info)
        
        with col_btn2:
            # Vérifier si déjà corrigée
            from pathlib import Path
            results_dir = Path(eval_info['dossier']) / "resultats"
            student_dir_name = f"{student_info['nom']}_{student_info['prenom']}"
            is_corrected = (results_dir / student_dir_name).exists()
            
            if is_corrected:
                if st.button(f"📊 Voir mes résultats", key=f"results_{eval_info['id_evaluation']}", type="primary"):
                    st.session_state.page_redirect = "📊 Mes résultats"
                    st.rerun()
            else:
                st.info("⏳ En attente de correction")
    
    else:  # Fermée
        # Évaluation fermée - Information uniquement
        if student_submission:
            st.info("✅ **Bonne nouvelle !** Votre copie a été soumise à temps")
            st.write("Elle sera corrigée par votre professeur")
            
            if st.button(f"👀 Voir ma soumission", key=f"view_closed_{eval_info['id_evaluation']}"):
                from utils.display_helpers import show_student_submission
                show_student_submission(eval_info, student_info)
        else:
            if status == "fermee":
                st.error("🔒 **Épreuve fermée par le professeur**")
                st.write("Il n'est plus possible de soumettre")
            else:  # expiree
                st.warning("⏰ **Échéance dépassée**")
                st.write("Le délai de soumission est terminé")

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

def _show_evaluation_rules():
    """Affiche les règles et informations importantes"""
    
    with st.expander("📋 Règles Importantes", expanded=False):
        st.markdown("""
        ### ⏰ Échéances et Fermetures
        
        **🟢 Épreuve Ouverte :**
        - Vous pouvez soumettre ou modifier votre copie
        - Respectez l'échéance indiquée (date ET heure)
        - Soumettez avant la fermeture !
        
        **🔒 Épreuve Fermée :**
        - Plus de soumission possible
        - Les copies soumises à temps seront corrigées
        - Les copies tardives ne seront pas acceptées
        
        **⏰ Échéance Automatique :**
        - Les épreuves se ferment automatiquement à l'heure précise
        - Le professeur peut fermer manuellement à tout moment
        - Le professeur peut prolonger l'échéance si nécessaire
        - L'heure de début ET la durée déterminent l'échéance finale
        
        **🔄 Prolongations :**
        - Le professeur peut prolonger une échéance à tout moment
        - Les prolongations priment sur les échéances automatiques
        - Une épreuve prolongée redevient automatiquement ouverte
        - Actualisez régulièrement pour voir les prolongations
        
        **🚫 Fermeture Manuelle :**
        - Le professeur peut fermer une épreuve à tout moment
        - La fermeture manuelle PRIME sur les prolongations
        - Une épreuve fermée manuellement reste fermée même si l'échéance n'est pas atteinte
        
        ### 💡 Conseils
        - Soumettez dès que possible, n'attendez pas la dernière minute
        - Vérifiez régulièrement les échéances (date ET heure)
        - Les prolongations sont affichées avec 🔄
        - Les fermetures manuelles sont affichées avec 🚫
        - En cas de problème technique, contactez immédiatement votre professeur
        
        ### 🕒 Exemples
        - **Épreuve normale :** 25/06/2025 14:00-16:00 → Fermeture à 16:00
        - **Épreuve prolongée :** 25/06/2025 14:00-18:00 🔄 → Fermeture à 18:00
        - **Épreuve fermée manuellement :** 🚫 Fermée à 15:30 (même si échéance à 16:00)
        """)

if __name__ == "__main__":
    print("📝 Available Exams avec fermeture manuelle CORRIGÉE !")