"""
pages/professor/create_evaluation.py - Version avec gestion de la publication
=============================================================================
Gestion des évaluations avec statuts de publication des résultats
"""

import streamlit as st
import uuid
from datetime import datetime, date, timedelta, time
from pathlib import Path
from utils.data_manager import save_evaluation_info, save_bareme, create_evaluation_structure, clear_all_cache, get_evaluations_list
from utils.display_helpers import display_header

def show():
    """Affiche la page création d'évaluation avec gestion fermeture et publication"""
    display_header("➕ Créer & Gérer Évaluations")
    
    # ONGLETS POUR SÉPARER CRÉATION ET GESTION
    tab1, tab2 = st.tabs(["➕ Créer Nouvelle Évaluation", "🔒 Gérer Évaluations Existantes"])
    
    with tab1:
        _show_create_evaluation_tab()
    
    with tab2:
        _show_manage_evaluations_tab()

def _show_create_evaluation_tab():
    """Onglet création d'évaluation"""
    
    st.subheader("➕ Créer Nouvelle Évaluation")
    
    # Configuration dynamique des questions (EN DEHORS du formulaire)
    if 'questions' not in st.session_state:
        st.session_state.questions = [{"numero": 1, "intitule": "", "points": 5.0, "type": "ouverte"}]
    
    # Section gestion des questions EN DEHORS du formulaire
    _manage_questions_section()
    
    st.markdown("---")
    
    # FORMULAIRE pour les informations générales uniquement
    _show_evaluation_form()

def _show_manage_evaluations_tab():
    """Onglet gestion des évaluations existantes avec statuts de publication"""
    
    st.subheader("🔒 Gérer Évaluations Existantes")
    
    # Bouton d'actualisation
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Actualiser", key="refresh_manage"):
            clear_all_cache()
            # Reset de l'état de prolongation
            if 'extending_eval_id' in st.session_state:
                del st.session_state.extending_eval_id
            st.rerun()
    
    # Charger les évaluations existantes
    evaluations = get_evaluations_list()
    
    if not evaluations:
        st.info("📭 Aucune évaluation créée. Utilisez l'onglet 'Créer' pour commencer.")
        return
    
    # Vérifier et mettre à jour les statuts automatiquement
    _check_automatic_closures(evaluations)
    
    # Afficher les évaluations avec leurs statuts
    st.write(f"**📊 {len(evaluations)} évaluation(s) trouvée(s)**")
    
    for eval_info in evaluations:
        _display_evaluation_management_card(eval_info)

def _display_evaluation_management_card(eval_info):
    """Affiche une carte de gestion pour chaque évaluation avec statuts de publication"""
    
    # Calculer les statuts
    current_status = _get_evaluation_status(eval_info)
    
    # Vérifier si corrigée
    results_dir = Path(eval_info['dossier']) / "resultats"
    is_corrected = results_dir.exists() and any(results_dir.iterdir())
    
    # Statut de publication
    publication_status = eval_info.get('statut_publication', 'brouillon')
    
    # Icônes selon les statuts
    if current_status == "ouverte":
        status_icon = "🟢"
        status_text = "Ouverte"
        status_color = "success"
    elif current_status == "fermee":
        status_icon = "🔴"
        status_text = "Fermée"
        status_color = "error"
    else:  # expiree
        status_icon = "⏰"
        status_text = "Expirée"
        status_color = "warning"
    
    # Icône de publication
    if publication_status == 'publie':
        pub_icon = "📢"
        pub_text = "Publiée"
    elif publication_status == 'depublie':
        pub_icon = "🚫"
        pub_text = "Dépubliée"
    else:
        pub_icon = "📝"
        pub_text = "Brouillon"
    
    # Titre avec statuts
    card_title = f"{status_icon} {eval_info['titre']} - {eval_info['matiere']} ({status_text}"
    if is_corrected:
        card_title += f" - {pub_icon} {pub_text}"
    card_title += ")"
    
    # Affichage de la carte
    with st.expander(card_title, expanded=current_status == "ouverte"):
        
        # Vérifier si on est en mode prolongation pour cette évaluation
        is_extending = st.session_state.get('extending_eval_id') == eval_info['id_evaluation']
        
        if is_extending:
            # AFFICHER LE FORMULAIRE DE PROLONGATION
            _show_extend_deadline_form_fixed(eval_info)
        else:
            # AFFICHAGE NORMAL DE LA CARTE
            _display_normal_evaluation_card_with_publication(eval_info, current_status, is_corrected, publication_status)

def _display_normal_evaluation_card_with_publication(eval_info, current_status, is_corrected, publication_status):
    """Affichage normal de la carte d'évaluation avec statuts de publication"""
    
    # Informations principales
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write(f"**📅 Date :** {eval_info['date']}")
        st.write(f"**⏰ Heure :** {eval_info.get('heure_debut', '08:00')}")
        st.write(f"**⏱️ Durée :** {eval_info['duree']}")
        st.write(f"**🎓 Promotion :** {eval_info['promotion']}")
    
    with col2:
        st.write(f"**👨‍🏫 Professeur :** {eval_info['professeur']}")
        st.write(f"**📊 Note totale :** {eval_info['note_totale']}")
        
        # Calcul échéance
        echeance = _calculate_deadline(eval_info)
        st.write(f"**⏰ Échéance :** {echeance.strftime('%d/%m/%Y %H:%M')}")
    
    with col3:
        # Statut actuel
        if current_status == "ouverte":
            st.success(f"🟢 Ouverte")
        elif current_status == "fermee":
            st.error(f"🔴 Fermée")
        else:
            st.warning(f"⏰ Expirée")
        
        # Statut de correction
        if is_corrected:
            st.success("✅ Corrigée")
        else:
            st.info("⏳ Non corrigée")
        
        # Statut de publication
        if publication_status == 'publie':
            st.success(f"📢 Publiée")
        elif publication_status == 'depublie':
            st.error(f"🚫 Dépubliée")
        else:
            st.warning(f"📝 Brouillon")
        
        # Temps restant
        temps_restant = _calculate_time_remaining(eval_info)
        if temps_restant:
            st.info(f"⏳ {temps_restant}")
        else:
            st.info("⏰ Échéance dépassée")
    
    # Statistiques de soumission
    st.markdown("---")
    _display_submission_stats(eval_info)
    
    # Informations de publication détaillées
    if is_corrected:
        st.markdown("---")
        _display_publication_details(eval_info)
    
    # Actions de gestion
    st.markdown("---")
    _display_management_actions(eval_info, current_status, is_corrected)

def _display_publication_details(eval_info):
    """Affiche les détails de publication"""
    
    publication_status = eval_info.get('statut_publication', 'brouillon')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**📢 Statut de Publication :**")
        
        if publication_status == 'publie':
            st.success("✅ Résultats publiés aux étudiants")
            date_pub = eval_info.get('date_publication', 'Date inconnue')
            if date_pub != 'Date inconnue':
                try:
                    date_formatted = datetime.fromisoformat(date_pub).strftime('%d/%m/%Y à %H:%M')
                    st.write(f"📅 Publié le : {date_formatted}")
                except:
                    st.write(f"📅 Publié le : {date_pub}")
            
            publie_par = eval_info.get('publie_par', 'Inconnu')
            st.write(f"👤 Publié par : {publie_par}")
        
        elif publication_status == 'depublie':
            st.error("🚫 Résultats dépubliés")
            date_depub = eval_info.get('date_depublication', 'Date inconnue')
            if date_depub != 'Date inconnue':
                try:
                    date_formatted = datetime.fromisoformat(date_depub).strftime('%d/%m/%Y à %H:%M')
                    st.write(f"📅 Dépublié le : {date_formatted}")
                except:
                    st.write(f"📅 Dépublié le : {date_depub}")
        
        else:
            st.warning("📝 Résultats en brouillon")
            st.write("Les étudiants ne peuvent pas voir leurs résultats")
    
    with col2:
        # Statistiques de consultation (si publiés)
        if publication_status == 'publie':
            st.write("**📊 Statistiques de consultation :**")
            # TODO: Implémenter le tracking des consultations
            st.write("📈 Consultations : À implémenter")
            st.write("📧 Notifications : À implémenter")
        else:
            st.write("**💡 Action requise :**")
            if publication_status == 'brouillon':
                st.info("Publiez les résultats pour les rendre visibles aux étudiants")
            else:
                st.info("Republier les résultats si nécessaire")

def _show_extend_deadline_form_fixed(eval_info):
    """FORMULAIRE DE PROLONGATION CORRIGÉ - Évite les rechargements ET corrige l'erreur de date"""
    
    st.subheader(f"⏰ Prolonger l'échéance - {eval_info['titre']}")
    
    # Échéance actuelle
    echeance_actuelle = _calculate_deadline(eval_info)
    st.write(f"**Échéance actuelle :** {echeance_actuelle.strftime('%d/%m/%Y à %H:%M')}")
    
    # UTILISER UN FORMULAIRE POUR ÉVITER LES RECHARGEMENTS
    with st.form(f"form_extend_{eval_info['id_evaluation']}"):
        st.write("**Nouvelle échéance :**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # CORRECTION : Utiliser max() pour éviter l'erreur de date
            today = date.today()
            default_date = max(echeance_actuelle.date(), today)  # ✅ CORRECTION ICI
            
            nouvelle_date = st.date_input(
                "Date",
                value=default_date,
                min_value=today,  # Pas de date dans le passé
                key=f"extend_date_{eval_info['id_evaluation']}"
            )
        
        with col2:
            nouvelle_heure = st.time_input(
                "Heure",
                value=echeance_actuelle.time(),
                key=f"extend_time_{eval_info['id_evaluation']}"
            )
        
        # Aperçu de la nouvelle échéance
        nouvelle_echeance_preview = datetime.combine(nouvelle_date, nouvelle_heure)
        st.info(f"🎯 **Nouvelle échéance :** {nouvelle_echeance_preview.strftime('%d/%m/%Y à %H:%M')}")
        
        # Boutons dans le formulaire
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            submit_extend = st.form_submit_button("✅ Appliquer Prolongation", type="primary")
        
        with col_btn2:
            cancel_extend = st.form_submit_button("❌ Annuler")
    
    # TRAITEMENT EN DEHORS DU FORMULAIRE
    if submit_extend:
        nouvelle_echeance = datetime.combine(nouvelle_date, nouvelle_heure)
        _extend_evaluation_deadline(eval_info, nouvelle_echeance)
        # Supprimer l'état de prolongation
        if 'extending_eval_id' in st.session_state:
            del st.session_state.extending_eval_id
        st.success("✅ Échéance prolongée avec succès")
        st.rerun()
    
    if cancel_extend:
        # Supprimer l'état de prolongation
        if 'extending_eval_id' in st.session_state:
            del st.session_state.extending_eval_id
        st.rerun()

def _display_submission_stats(eval_info):
    """Affiche les statistiques de soumission"""
    
    # Compter les copies soumises
    copies_dir = Path(eval_info['dossier']) / "copies_soumises"
    copies_count = len(list(copies_dir.glob("*.pdf"))) if copies_dir.exists() else 0
    
    # Vérifier si déjà corrigée
    results_dir = Path(eval_info['dossier']) / "resultats"
    is_corrected = results_dir.exists() and any(results_dir.iterdir())
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📄 Copies soumises", copies_count)
    
    with col2:
        correction_status = "✅ Corrigée" if is_corrected else "⏳ En attente"
        st.write(f"**État correction :** {correction_status}")
    
    with col3:
        if copies_count > 0:
            st.write(f"**Dernière soumission :** Récente")
        else:
            st.write("**Soumissions :** Aucune")

def _display_management_actions(eval_info, current_status, is_corrected):
    """Affiche les actions de gestion possibles avec publication"""
    
    st.write("**🔧 Actions disponibles :**")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Fermer/Ouvrir manuellement
        if current_status == "ouverte":
            if st.button("🔒 Fermer Évaluation", key=f"close_{eval_info['id_evaluation']}", help="Fermer manuellement l'évaluation"):
                _close_evaluation(eval_info)
                st.success("✅ Évaluation fermée")
                st.rerun()
        elif current_status == "fermee":
            if st.button("🔓 Rouvrir Évaluation", key=f"reopen_{eval_info['id_evaluation']}", help="Rouvrir l'évaluation"):
                _reopen_evaluation(eval_info)
                st.success("✅ Évaluation rouverte")
                st.rerun()
        else:  # expirée
            if st.button("🔓 Rouvrir (Expirée)", key=f"reopen_exp_{eval_info['id_evaluation']}", help="Rouvrir une évaluation expirée"):
                _reopen_evaluation(eval_info)
                st.success("✅ Évaluation rouverte")
                st.rerun()
    
    with col2:
        # Prolonger l'échéance
        if st.button("⏰ Prolonger", key=f"extend_{eval_info['id_evaluation']}", help="Prolonger l'échéance"):
            # Activer le mode prolongation pour cette évaluation
            st.session_state.extending_eval_id = eval_info['id_evaluation']
            st.rerun()
    
    with col3:
        # Voir les copies
        if st.button("📄 Voir Copies", key=f"copies_{eval_info['id_evaluation']}"):
            st.session_state.selected_eval = eval_info['dossier']
            st.session_state.page_redirect = "📤 Gérer copies"
            st.rerun()
    
    with col4:
        # Lancer correction (si fermée et copies disponibles)
        copies_dir = Path(eval_info['dossier']) / "copies_soumises"
        copies_count = len(list(copies_dir.glob("*.pdf"))) if copies_dir.exists() else 0
        
        if current_status in ["fermee", "expiree"] and copies_count > 0:
            if st.button("🤖 Lancer Correction", key=f"correct_{eval_info['id_evaluation']}", type="primary"):
                st.session_state.selected_eval = eval_info['dossier']
                st.session_state.page_redirect = "🤖 Lancer correction"
                st.rerun()
        else:
            if current_status == "ouverte":
                st.button("🤖 Correction", key=f"correct_disabled_{eval_info['id_evaluation']}", disabled=True, help="Fermer l'évaluation d'abord")
            else:
                st.button("🤖 Correction", key=f"correct_no_copies_{eval_info['id_evaluation']}", disabled=True, help="Aucune copie disponible")
    
    # Ligne 2 : Actions spéciales
    if is_corrected:
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📊 Consulter Rapports", key=f"reports_{eval_info['id_evaluation']}"):
                st.session_state.selected_eval = eval_info['dossier']
                st.session_state.page_redirect = "📊 Consulter rapports"
                st.rerun()
        
        with col2:
            publication_status = eval_info.get('statut_publication', 'brouillon')
            if publication_status in ['brouillon', 'depublie']:
                if st.button("📢 Publier Résultats", key=f"publish_{eval_info['id_evaluation']}", type="primary"):
                    _publish_results_from_management(eval_info)
                    st.success("✅ Résultats publiés !")
                    st.rerun()
            else:
                if st.button("🚫 Dépublier", key=f"unpublish_{eval_info['id_evaluation']}"):
                    _unpublish_results_from_management(eval_info)
                    st.success("✅ Résultats dépubliés")
                    st.rerun()
        
        with col3:
            if st.button("📧 Notifier Étudiants", key=f"notify_{eval_info['id_evaluation']}"):
                # TODO: Implémenter les notifications
                st.info("📧 Notifications envoyées (à implémenter)")
        
        with col4:
            if st.button("🔄 Recorriger", key=f"recorrect_{eval_info['id_evaluation']}"):
                st.session_state.selected_eval = eval_info['dossier']
                st.session_state.page_redirect = "🤖 Lancer correction"
                st.rerun()

def _publish_results_from_management(eval_info):
    """Publie les résultats depuis la gestion"""
    
    # Mettre à jour le statut
    eval_info['statut_publication'] = 'publie'
    eval_info['date_publication'] = datetime.now().isoformat()
    eval_info['publie_par'] = eval_info.get('professeur', 'Professeur')
    
    # Mettre à jour tous les résultats
    _update_results_publication_status(eval_info['dossier'], 'publie')
    
    # Sauvegarder
    _save_evaluation_info(eval_info)
    clear_all_cache()

def _unpublish_results_from_management(eval_info):
    """Dépublie les résultats depuis la gestion"""
    
    # Mettre à jour le statut
    eval_info['statut_publication'] = 'depublie'
    eval_info['date_depublication'] = datetime.now().isoformat()
    eval_info['depublie_par'] = eval_info.get('professeur', 'Professeur')
    
    # Mettre à jour tous les résultats
    _update_results_publication_status(eval_info['dossier'], 'depublie')
    
    # Sauvegarder
    _save_evaluation_info(eval_info)
    clear_all_cache()

def _update_results_publication_status(eval_dir, status):
    """Met à jour le statut de publication de tous les résultats"""
    
    results_dir = Path(eval_dir) / "resultats"
    
    if not results_dir.exists():
        return
    
    # Parcourir tous les fichiers de résultats
    for result_file in results_dir.glob("*.json"):
        try:
            import json
            
            # Lire le fichier de résultat
            with open(result_file, 'r', encoding='utf-8') as f:
                result_data = json.load(f)
            
            # Mettre à jour le statut
            result_data['statut_publication'] = status
            result_data['date_maj_publication'] = datetime.now().isoformat()
            
            # Sauvegarder
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Erreur mise à jour publication {result_file}: {e}")

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
    heure_debut_str = eval_info.get('heure_debut', '08:00')  # Défaut 8h00 si pas spécifié
    
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

def _calculate_time_remaining(eval_info):
    """Calcule le temps restant avant échéance"""
    
    echeance = _calculate_deadline(eval_info)
    maintenant = datetime.now()
    
    if maintenant >= echeance:
        return None
    
    delta = echeance - maintenant
    
    if delta.days > 0:
        return f"{delta.days} jour(s) {delta.seconds // 3600} heure(s)"
    elif delta.seconds > 3600:
        return f"{delta.seconds // 3600} heure(s) {(delta.seconds % 3600) // 60} min"
    else:
        return f"{delta.seconds // 60} minutes"

def _check_automatic_closures(evaluations):
    """Vérifie et met à jour automatiquement les évaluations expirées"""
    
    for eval_info in evaluations:
        if _get_evaluation_status(eval_info) == 'expiree' and eval_info.get('statut') != 'fermee':
            # Marquer comme expirée automatiquement
            _mark_evaluation_expired(eval_info)

def _close_evaluation(eval_info):
    """Ferme manuellement une évaluation"""
    
    # Mettre à jour le fichier d'information
    eval_info['statut'] = 'fermee'
    eval_info['date_fermeture'] = datetime.now().isoformat()
    eval_info['fermeture_manuelle'] = True
    
    # Sauvegarder
    _save_evaluation_info(eval_info)
    clear_all_cache()

def _reopen_evaluation(eval_info):
    """Rouvre une évaluation fermée"""
    
    # Mettre à jour le statut
    eval_info['statut'] = 'ouverte'
    eval_info['date_reouverture'] = datetime.now().isoformat()
    
    # Supprimer les marqueurs de fermeture
    if 'date_fermeture' in eval_info:
        del eval_info['date_fermeture']
    if 'fermeture_manuelle' in eval_info:
        del eval_info['fermeture_manuelle']
    
    # Sauvegarder
    _save_evaluation_info(eval_info)
    clear_all_cache()

def _extend_evaluation_deadline(eval_info, nouvelle_echeance):
    """Prolonge l'échéance d'une évaluation"""
    
    # Enregistrer la nouvelle échéance
    eval_info['echeance_prolongee'] = nouvelle_echeance.isoformat()
    eval_info['date_prolongation'] = datetime.now().isoformat()
    
    # Rouvrir si fermée
    if eval_info.get('statut') == 'fermee':
        eval_info['statut'] = 'ouverte'
    
    # Sauvegarder
    _save_evaluation_info(eval_info)
    clear_all_cache()

def _mark_evaluation_expired(eval_info):
    """Marque une évaluation comme expirée automatiquement"""
    
    eval_info['statut'] = 'expiree'
    eval_info['date_expiration'] = datetime.now().isoformat()
    eval_info['expiration_automatique'] = True
    
    # Sauvegarder
    _save_evaluation_info(eval_info)

def _save_evaluation_info(eval_info):
    """Sauvegarde les informations d'évaluation mises à jour"""
    
    eval_dir = eval_info['dossier']
    save_evaluation_info(eval_dir, eval_info)

# ===== FONCTIONS ORIGINALES DE CRÉATION =====

def _manage_questions_section():
    """Gère la section de configuration des questions"""
    st.subheader("📊 Configuration du Barème")
    
    st.write("**Questions de l'évaluation :**")
    
    # Afficher les questions existantes avec boutons de suppression
    for i, question in enumerate(st.session_state.questions):
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        
        with col1:
            new_intitule = st.text_input(
                f"Question {i+1}", 
                value=question['intitule'],
                placeholder="Ex: Résoudre l'équation différentielle...",
                key=f"q_intitule_{i}"
            )
            st.session_state.questions[i]['intitule'] = new_intitule
        
        with col2:
            new_points = st.number_input(
                "Points", 
                min_value=0.5, 
                max_value=20.0, 
                value=question['points'],
                step=0.5,
                key=f"q_points_{i}"
            )
            st.session_state.questions[i]['points'] = new_points
        
        with col3:
            new_type = st.selectbox(
                "Type", 
                ["ouverte", "calcul", "demonstration", "qcm"],
                index=["ouverte", "calcul", "demonstration", "qcm"].index(question['type']),
                key=f"q_type_{i}"
            )
            st.session_state.questions[i]['type'] = new_type
        
        with col4:
            if st.button("🗑️", key=f"delete_{i}", help="Supprimer question"):
                if len(st.session_state.questions) > 1:
                    del st.session_state.questions[i]
                    st.rerun()
    
    # Boutons d'action pour les questions
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Ajouter question"):
            new_num = len(st.session_state.questions) + 1
            st.session_state.questions.append({
                "numero": new_num, 
                "intitule": "", 
                "points": 5.0, 
                "type": "ouverte"
            })
            st.rerun()
    
    with col2:
        total_points = sum(q['points'] for q in st.session_state.questions)
        st.metric("Total points", f"{total_points}")

def _show_evaluation_form():
    """Affiche le formulaire de création d'évaluation"""
    with st.form("creation_evaluation"):
        st.subheader("📋 Informations Générales")
        
        col1, col2 = st.columns(2)
        
        with col1:
            titre = st.text_input("Titre de l'évaluation *", placeholder="Ex: Examen Final Mathématiques")
            matiere = st.selectbox("Matière *", [
                "Mathématiques", "Physique", "Chimie", "Informatique", 
                "Biologie", "Histoire", "Philosophie", "Économie", 
                "Droit", "Français", "Anglais", "Autre"
            ])
            date_eval = st.date_input("Date de l'évaluation", value=date.today())
            heure_debut = st.time_input("Heure de début", value=time(8, 0))
        
        with col2:
            duree = st.selectbox("Durée", ["1h", "1h30", "2h", "2h30", "3h", "4h"])
            professeur = st.text_input("Nom du professeur *", placeholder="Dr. Martin")
            promotion = st.text_input("Promotion *", placeholder="L2 Mathématiques 2024-2025")
        
        st.markdown("---")
        
        # Affichage récapitulatif des questions (lecture seule)
        st.write("**Récapitulatif des questions :**")
        for i, q in enumerate(st.session_state.questions):
            if q['intitule']:
                st.write(f"• Q{i+1}: {q['intitule']} ({q['points']} pts - {q['type']})")
        
        # Bouton de soumission
        submitted = st.form_submit_button("🎯 Créer l'Évaluation", type="primary")
    
    # Traitement en dehors du formulaire
    if submitted:
        _process_evaluation_creation(titre, matiere, date_eval, heure_debut, duree, professeur, promotion)

def _process_evaluation_creation(titre, matiere, date_eval, heure_debut, duree, professeur, promotion):
    """Traite la création d'une évaluation avec heure de début et statut de publication"""
    # Validation
    if not titre or not professeur or not promotion:
        st.error("❌ Veuillez remplir tous les champs obligatoires (*)")
        return
    
    if not any(q['intitule'].strip() for q in st.session_state.questions):
        st.error("❌ Veuillez définir au moins une question")
        return
    
    try:
        # Créer l'ID unique et le dossier
        eval_id = str(uuid.uuid4())[:8]
        eval_name = f"EVAL_{matiere}_{titre}_{eval_id}".replace(" ", "_")
        eval_dir = Path("./evaluations") / eval_name
        
        # Créer la structure
        eval_dir.mkdir(parents=True, exist_ok=True)
        create_evaluation_structure(str(eval_dir))
        
        # Préparer les données AVEC l'heure de début et statut de publication
        total_points = sum(q['points'] for q in st.session_state.questions)
        infos_evaluation = {
            "id_evaluation": eval_id,
            "titre": titre,
            "matiere": matiere,
            "date": date_eval.strftime('%Y-%m-%d'),
            "heure_debut": heure_debut.strftime('%H:%M'),
            "duree": duree,
            "professeur": professeur,
            "promotion": promotion,
            "note_totale": total_points,
            "created_at": datetime.now().isoformat(),
            "statut": "ouverte",
            "statut_publication": "brouillon",  # Statut par défaut
            "dossier": str(eval_dir)
        }
        
        # Nettoyer et structurer les questions
        questions_clean = []
        for q in st.session_state.questions:
            if q['intitule'].strip():
                questions_clean.append({
                    "numero": q['numero'],
                    "intitule": q['intitule'].strip(),
                    "points_total": q['points'],
                    "type": q['type'],
                    "criteres": ["Pertinence", "Exactitude", "Clarté"],
                    "mots_cles": []
                })
        
        bareme = {
            "examen": titre,
            "date": date_eval.strftime('%Y-%m-%d'),
            "heure_debut": heure_debut.strftime('%H:%M'),
            "duree": duree,
            "note_totale": total_points,
            "questions": questions_clean
        }
        
        # Sauvegarder les fichiers
        save_evaluation_info(str(eval_dir), infos_evaluation)
        save_bareme(str(eval_dir), bareme)
        
        # INVALIDATION GLOBALE POUR ACTUALISATION PARTOUT
        clear_all_cache()
        
        # Reset session state
        del st.session_state.questions
        
        st.balloons()
        st.success(f"✅ Évaluation '{titre}' créée avec succès !")
        
        # Calculer et afficher l'échéance CORRECTE
        echeance = _calculate_deadline(infos_evaluation)
        st.info(f"⏰ **Début :** {date_eval.strftime('%d/%m/%Y')} à {heure_debut.strftime('%H:%M')}")
        st.info(f"🏁 **Échéance :** {echeance.strftime('%d/%m/%Y à %H:%M')}")
        st.success(f"🎯 **Durée réelle :** {duree} de {heure_debut.strftime('%H:%M')} à {echeance.strftime('%H:%M')}")
        
        # Afficher les informations de publication
        st.info("📝 **Statut de publication :** Brouillon (les résultats ne seront pas visibles aux étudiants après correction)")

        # Afficher les prochaines étapes
        st.markdown("""
        ### 🎯 Prochaines étapes :
        1. **📤 Gérer copies** : Uploadez les copies PDF des étudiants
        2. **🔒 Gérer fermeture** : Contrôlez l'ouverture/fermeture dans l'onglet 'Gérer'
        3. **🤖 Lancer correction** : Démarrez la correction automatique après fermeture
        4. **📢 Publier résultats** : Rendez les résultats visibles aux étudiants
        5. **📊 Consulter rapports** : Visualisez les statistiques
        """)
        
    except Exception as e:
        st.error(f"❌ Erreur lors de la création : {str(e)}")

if __name__ == "__main__":
    print("🎯 Create Evaluation avec gestion de la publication prêt !")