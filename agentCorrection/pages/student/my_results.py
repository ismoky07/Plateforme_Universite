"""
pages/student/my_results.py - Version CORRIGÉE pour le champ pourcentage manquant
===============================================================================
CORRECTION : Gestion défensive des champs manquants (pourcentage, note_maximale, etc.)
"""

import streamlit as st
import json
from pathlib import Path
from datetime import datetime
from utils.data_manager import get_evaluations_list, clear_all_cache
from utils.display_helpers import display_header

def show():
    """Page consultation des résultats avec vérification de publication et gestion défensive"""
    if not st.session_state.get('student_logged_in', False):
        st.warning("⚠️ Veuillez vous connecter d'abord")
        return
    
    student_info = st.session_state.get('student_info', {})
    
    display_header("📊 Mes Résultats")
    
    # CHARGEMENT DES DONNÉES AVEC VÉRIFICATION DE PUBLICATION
    evaluations = get_evaluations_list()
    published_evaluations = []
    unpublished_evaluations = []
    
    for eval_info in evaluations:
        results_dir = Path(eval_info['dossier']) / "resultats"
        if results_dir.exists():
            student_folder = None
            for folder in results_dir.iterdir():
                if folder.is_dir():
                    if (student_info['nom'].lower() in folder.name.lower() and 
                        student_info['prenom'].lower() in folder.name.lower()):
                        student_folder = folder
                        break
            
            if student_folder:
                correction_file = student_folder / "correction_detaillee.json"
                if correction_file.exists():
                    try:
                        with open(correction_file, 'r', encoding='utf-8') as f:
                            result = json.load(f)
                            result['evaluation_info'] = eval_info
                            
                            # ✅ CORRECTION : Normaliser le résultat avant utilisation
                            result = _normalize_student_result(result, eval_info)
                            
                            # VÉRIFICATION DU STATUT DE PUBLICATION
                            publication_status = _get_publication_status(eval_info, result)
                            
                            if publication_status == 'publie':
                                published_evaluations.append(result)
                            else:
                                unpublished_evaluations.append({
                                    'evaluation_info': eval_info,
                                    'statut_publication': publication_status,
                                    'result': result
                                })
                    except:
                        continue
    
    # AFFICHAGE DES INFORMATIONS SELON LES STATUTS
    _show_results_summary(published_evaluations, unpublished_evaluations)
    
    # AFFICHAGE DES RÉSULTATS PUBLIÉS
    if published_evaluations:
        st.markdown("---")
        st.subheader("✅ Résultats Publiés")
        
        for eval_result in published_evaluations:
            eval_info = eval_result['evaluation_info']
            _display_published_result(eval_result, eval_info)
    
    # AFFICHAGE DES RÉSULTATS NON PUBLIÉS
    if unpublished_evaluations:
        st.markdown("---")
        _show_unpublished_results_section(unpublished_evaluations)

def _normalize_student_result(result, eval_info):
    """✅ NOUVELLE FONCTION : Normalise un résultat étudiant pour éviter les erreurs de champs manquants"""
    
    # Récupérer les valeurs avec des défauts sûrs
    note_totale = result.get('note_totale', 0.0)
    note_maximale = result.get('note_maximale', eval_info.get('note_totale', 20))
    
    # Calculer le pourcentage si manquant
    if 'pourcentage' not in result or result['pourcentage'] is None:
        pourcentage = round((note_totale / note_maximale) * 100, 1) if note_maximale > 0 else 0.0
        result['pourcentage'] = pourcentage
    
    # S'assurer que les champs essentiels existent
    if 'note_maximale' not in result:
        result['note_maximale'] = note_maximale
    
    # Normaliser les champs optionnels
    result['commentaires_generaux'] = result.get('commentaires_generaux', result.get('commentaires', ''))
    result['points_forts'] = result.get('points_forts', [])
    result['points_amelioration'] = result.get('points_amelioration', [])
    result['conseils_personnalises'] = result.get('conseils_personnalises', [])
    result['questions'] = result.get('questions', [])
    result['rang_classe'] = result.get('rang_classe', 'N/A')
    result['diagnostic_performance'] = result.get('diagnostic_performance', '')
    
    # Normaliser les questions avec leurs pourcentages
    if 'questions' in result:
        normalized_questions = []
        for question in result['questions']:
            normalized_question = _normalize_question_data(question)
            normalized_questions.append(normalized_question)
        result['questions'] = normalized_questions
    
    # Assurer la compatibilité avec l'alias
    result['questions_avec_commentaires'] = result.get('questions_avec_commentaires', result['questions'])
    
    return result

def _normalize_question_data(question):
    """Normalise les données d'une question"""
    
    # Valeurs de base
    note = question.get('note', 0)
    note_max = question.get('note_max', question.get('points_total', 5))
    
    # Calculer le pourcentage si manquant
    if 'pourcentage_reussite' not in question and note_max > 0:
        question['pourcentage_reussite'] = round((note / note_max) * 100, 1)
    elif 'pourcentage_reussite' not in question:
        question['pourcentage_reussite'] = 0.0
    
    # Normaliser les autres champs
    question['numero'] = question.get('numero', 'N/A')
    question['intitule'] = question.get('intitule', 'Question sans titre')
    question['type'] = question.get('type', 'ouverte')
    question['commentaire_intelligent'] = question.get('commentaire_intelligent', question.get('commentaire', ''))
    question['conseil_personnalise'] = question.get('conseil_personnalise', '')
    
    return question

def _get_publication_status(eval_info, result):
    """Détermine le statut de publication d'un résultat"""
    
    # Priorité 1: Statut dans le résultat individuel
    if 'statut_publication' in result:
        return result['statut_publication']
    
    # Priorité 2: Statut global de l'évaluation
    if 'statut_publication' in eval_info:
        return eval_info['statut_publication']
    
    # Par défaut: brouillon (non publié)
    return 'brouillon'

def _show_results_summary(published_evaluations, unpublished_evaluations):
    """Affiche le résumé des résultats selon les statuts de publication avec gestion défensive"""
    
    total_corrections = len(published_evaluations) + len(unpublished_evaluations)
    
    if total_corrections == 0:
        st.info("📭 Aucune évaluation corrigée trouvée pour votre profil")
        
        # Suggestions d'actions
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📤 Voir mes soumissions"):
                st.session_state.page_redirect = "📋 Mes soumissions"
                st.rerun()
        with col2:
            if st.button("🔄 Vérifier à nouveau", type="secondary"):
                clear_all_cache()
                st.rerun()
        return
    
    # MÉTRIQUES DE PUBLICATION
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Évaluations corrigées", total_corrections)
    
    with col2:
        st.metric("✅ Résultats publiés", len(published_evaluations))
    
    with col3:
        st.metric("📝 En attente de publication", len(unpublished_evaluations))
    
    with col4:
        if published_evaluations:
            # ✅ CORRECTION : Accès défensif aux notes
            notes = [float(r.get('note_totale', 0)) for r in published_evaluations if r.get('note_totale') is not None]
            if notes:
                moyenne = sum(notes) / len(notes)
                st.metric("📈 Moyenne publiée", f"{moyenne:.1f}/20")
            else:
                st.metric("📈 Moyenne publiée", "N/A")
        else:
            st.metric("📈 Moyenne publiée", "N/A")
    
    # Message informatif selon la situation
    if len(published_evaluations) == 0 and len(unpublished_evaluations) > 0:
        st.info("📝 **Tous vos résultats sont en attente de publication par le professeur**")
    elif len(published_evaluations) > 0 and len(unpublished_evaluations) > 0:
        st.success(f"✅ **{len(published_evaluations)} résultat(s) disponible(s), {len(unpublished_evaluations)} en attente**")
    elif len(published_evaluations) > 0:
        st.success(f"🎉 **Tous vos résultats sont publiés !**")

def _display_published_result(eval_result, eval_info):
    """Affiche un résultat publié avec tous les détails et gestion défensive"""
    
    # ✅ CORRECTION : Accès défensif au pourcentage (maintenant normalisé)
    pourcentage = eval_result.get('pourcentage', 0)
    performance_icon, performance_text = _get_performance_indicator(pourcentage)
    
    # Date de publication
    date_publication = eval_info.get('date_publication', 'Date inconnue')
    if date_publication != 'Date inconnue':
        try:
            date_formatted = datetime.fromisoformat(date_publication).strftime('%d/%m/%Y')
            publication_info = f"📢 Publié le {date_formatted}"
        except:
            publication_info = "📢 Publié"
    else:
        publication_info = "📢 Publié"
    
    with st.expander(f"{performance_icon} {eval_info['titre']} - {eval_info['matiere']} ({eval_info['date']}) - {publication_info}", expanded=True):
        
        # MÉTRIQUES PRINCIPALES avec gestion défensive
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            note_totale = eval_result.get('note_totale', 0)
            note_maximale = eval_result.get('note_maximale', 20)
            st.metric("Note obtenue", f"{note_totale:.1f}/{note_maximale:.0f}")
        
        with col2:
            st.metric("Pourcentage", f"{pourcentage:.1f}%")
        
        with col3:
            rang = eval_result.get('rang_classe', 'N/A')
            st.metric("Rang classe", rang)
        
        with col4:
            st.metric("Performance", f"{performance_icon} {performance_text}")
        
        # DIAGNOSTIC IA
        diagnostic = eval_result.get('diagnostic_performance', '')
        if diagnostic:
            st.info(f"🎯 **Diagnostic IA :** {diagnostic}")
        
        # ANALYSE PAR QUESTION AVEC COMMENTAIRES INTELLIGENTS
        questions_data = eval_result.get('questions_avec_commentaires', eval_result.get('questions', []))
        if questions_data:
            st.markdown("---")
            st.subheader("📝 Commentaires par Question")
            
            # Détail de chaque question
            for question in questions_data:
                _display_question_feedback(question)
        
        # COMMENTAIRES GÉNÉRAUX
        commentaires = eval_result.get('commentaires_generaux', '')
        if commentaires:
            st.markdown("---")
            st.write("**💬 Commentaire général du professeur :**")
            st.info(commentaires)
        
        # POINTS FORTS ET AMÉLIORATIONS
        col1, col2 = st.columns(2)
        
        with col1:
            points_forts = eval_result.get('points_forts', [])
            if points_forts:
                st.success("**🎯 Vos points forts :**")
                for point in points_forts:
                    st.write(f"• {point}")
        
        with col2:
            points_amelioration = eval_result.get('points_amelioration', [])
            if points_amelioration:
                st.warning("**📈 Points à améliorer :**")
                for point in points_amelioration:
                    st.write(f"• {point}")
        
        # CONSEILS PERSONNALISÉS
        conseils = eval_result.get('conseils_personnalises', [])
        if conseils:
            st.markdown("---")
            st.write("**💡 Conseils personnalisés :**")
            for conseil in conseils:
                st.write(f"• {conseil}")
        
        # ACTIONS DISPONIBLES
        st.markdown("---")
        col_action1, col_action2 = st.columns(2)
        
        with col_action1:
            eval_id = eval_info.get('id_evaluation', f"eval_{hash(eval_info['titre'])}")
            if st.button(f"📄 Générer rapport", key=f"rapport_{eval_id}"):
                st.session_state.page_redirect = "📄 Mes rapports"
                st.rerun()
        
        with col_action2:
            # Lien vers les soumissions
            if st.button(f"📤 Voir ma soumission", key=f"soumission_{eval_id}"):
                st.session_state.page_redirect = "📋 Mes soumissions"
                st.rerun()

def _show_unpublished_results_section(unpublished_evaluations):
    """Affiche la section des résultats non publiés"""
    
    st.subheader("📝 Résultats en Attente de Publication")
    
    # Message explicatif
    st.info("""
    **📋 Résultats corrigés mais non publiés**
    
    Ces évaluations ont été corrigées par votre professeur mais ne sont pas encore publiées.
    Vous pourrez consulter vos résultats une fois que le professeur les aura publiés.
    """)
    
    # Liste des évaluations non publiées
    for unpub_eval in unpublished_evaluations:
        eval_info = unpub_eval['evaluation_info']
        statut = unpub_eval['statut_publication']
        
        # Icône selon le statut
        if statut == 'brouillon':
            status_icon = "📝"
            status_text = "En brouillon"
            status_color = "info"
        elif statut == 'depublie':
            status_icon = "🚫"
            status_text = "Temporairement retiré"
            status_color = "warning"
        else:
            status_icon = "⏳"
            status_text = "En attente"
            status_color = "info"
        
        with st.expander(f"{status_icon} {eval_info['titre']} - {eval_info['matiere']} ({status_text})", expanded=False):
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**📅 Date évaluation :** {eval_info['date']}")
                st.write(f"**👨‍🏫 Professeur :** {eval_info.get('professeur', 'Non spécifié')}")
                st.write(f"**📊 Statut :** {status_text}")
            
            with col2:
                if statut == 'brouillon':
                    st.info("📝 **En brouillon** - Le professeur n'a pas encore publié les résultats")
                elif statut == 'depublie':
                    st.warning("🚫 **Temporairement retiré** - Le professeur a retiré les résultats temporairement")
                else:
                    st.info("⏳ **En attente** - Publication en cours")
            
            # Actions limitées
            st.write("**💡 Actions disponibles :**")
            st.write("• Contactez votre professeur pour connaître le délai de publication")
            st.write("• Actualisez régulièrement cette page")
            st.write("• Consultez vos autres résultats déjà publiés")
    
    # Bouton d'actualisation
    st.markdown("---")
    col_refresh1, col_refresh2 = st.columns(2)
    
    with col_refresh1:
        if st.button("🔄 Actualiser les résultats", type="primary"):
            clear_all_cache()
            st.rerun()
    
    with col_refresh2:
        if st.button("📧 Contacter le professeur"):
            st.info("📧 Fonctionnalité de contact à implémenter")

def _display_question_feedback(question):
    """Affiche le feedback pour une question avec gestion défensive"""
    
    # ✅ CORRECTION : Accès défensif aux données de question (maintenant normalisées)
    numero = question.get('numero', 'N/A')
    intitule = question.get('intitule', 'Question sans titre')
    note = question.get('note', 0)
    note_max = question.get('note_max', question.get('points_total', 5))
    pourcentage = question.get('pourcentage_reussite', 0)
    
    commentaire = question.get('commentaire_intelligent', question.get('commentaire', ''))
    conseil = question.get('conseil_personnalise', '')
    question_type = question.get('type', 'ouverte')
    
    # Indicateur de performance pour la question
    q_icon, q_color, q_level = _get_question_performance(pourcentage)
    
    # Container simple
    with st.container():
        # En-tête de la question
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.write(f"**Question {numero}** - {question_type.title()}")
            st.caption(f"📋 {intitule}")
        
        with col2:
            st.write(f"**Note :** {note:.1f}/{note_max:.1f} pts")
            st.write(f"**Score :** {pourcentage:.1f}%")
        
        with col3:
            # Badge de performance
            if q_color == "success":
                st.success(f"{q_icon} {q_level}")
            elif q_color == "info":
                st.info(f"{q_icon} {q_level}")
            elif q_color == "warning":
                st.warning(f"{q_icon} {q_level}")
            else:
                st.error(f"{q_icon} {q_level}")
        
        # Barre de progression visuelle
        progress_value = max(0, min(100, pourcentage)) / 100  # S'assurer que c'est entre 0 et 1
        st.progress(progress_value, text=f"Maîtrise: {pourcentage:.1f}%")
        
        # Commentaire intelligent
        if commentaire:
            st.markdown("**💭 Analyse détaillée :**")
            st.info(commentaire)
        
        # Conseil personnalisé
        if conseil:
            st.markdown("**💡 Conseil personnalisé :**")
            st.success(conseil)
        
        st.markdown("---")

def _get_performance_indicator(pourcentage):
    """Retourne l'icône et le texte de performance avec gestion défensive"""
    pourcentage = float(pourcentage) if pourcentage is not None else 0
    
    if pourcentage >= 90:
        return "🏆", "Excellent"
    elif pourcentage >= 80:
        return "🌟", "Très bien"
    elif pourcentage >= 70:
        return "👍", "Bien"
    elif pourcentage >= 60:
        return "🟡", "Correct"
    elif pourcentage >= 40:
        return "🟠", "Passable"
    else:
        return "🔴", "Insuffisant"

def _get_question_performance(pourcentage):
    """Retourne l'icône, couleur et niveau pour une question avec gestion défensive"""
    pourcentage = float(pourcentage) if pourcentage is not None else 0
    
    if pourcentage >= 90:
        return "🏆", "success", "Excellent"
    elif pourcentage >= 75:
        return "🌟", "success", "Très bien"
    elif pourcentage >= 60:
        return "👍", "info", "Bien"
    elif pourcentage >= 40:
        return "🔄", "warning", "Moyen"
    elif pourcentage >= 20:
        return "⚠️", "warning", "Faible"
    else:
        return "🚨", "error", "Très faible"

if __name__ == "__main__":
    print("📊 Page my_results.py avec gestion défensive des champs manquants prête !")