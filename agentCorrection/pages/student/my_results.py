"""
pages/student/my_results.py - Version avec vérification de publication
====================================================================
Page consultation des résultats étudiants - Respecte les statuts de publication
"""

import streamlit as st
import json
from pathlib import Path
from datetime import datetime
from utils.data_manager import get_evaluations_list, clear_all_cache
from utils.display_helpers import display_header

def show():
    """Page consultation des résultats avec vérification de publication"""
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
    """Affiche le résumé des résultats selon les statuts de publication"""
    
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
            notes = [r['note_totale'] for r in published_evaluations]
            moyenne = sum(notes) / len(notes)
            st.metric("📈 Moyenne publiée", f"{moyenne:.1f}/20")
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
    """Affiche un résultat publié avec tous les détails"""
    
    # INDICATEUR DE PERFORMANCE
    pourcentage = eval_result['pourcentage']
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
        
        # MÉTRIQUES PRINCIPALES
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Note obtenue", f"{eval_result['note_totale']}/{eval_result.get('note_maximale', 20)}")
        
        with col2:
            st.metric("Pourcentage", f"{eval_result['pourcentage']:.1f}%")
        
        with col3:
            rang = eval_result.get('rang_classe', 'N/A')
            st.metric("Rang classe", rang)
        
        with col4:
            st.metric("Performance", f"{performance_icon} {performance_text}")
        
        # DIAGNOSTIC IA
        if eval_result.get('diagnostic_performance'):
            st.info(f"🎯 **Diagnostic IA :** {eval_result['diagnostic_performance']}")
        
        # ANALYSE PAR QUESTION AVEC COMMENTAIRES INTELLIGENTS
        questions_data = eval_result.get('questions_avec_commentaires', eval_result.get('questions', []))
        if questions_data:
            st.markdown("---")
            st.subheader("📝 Commentaires par Question")
            
            # Détail de chaque question
            for question in questions_data:
                _display_question_feedback(question)
        
        # COMMENTAIRES GÉNÉRAUX
        if 'commentaires_generaux' in eval_result:
            st.markdown("---")
            st.write("**💬 Commentaire général du professeur :**")
            st.info(eval_result['commentaires_generaux'])
        
        # POINTS FORTS ET AMÉLIORATIONS
        col1, col2 = st.columns(2)
        
        with col1:
            if 'points_forts' in eval_result and eval_result['points_forts']:
                st.success("**🎯 Vos points forts :**")
                for point in eval_result['points_forts']:
                    st.write(f"• {point}")
        
        with col2:
            if 'points_amelioration' in eval_result and eval_result['points_amelioration']:
                st.warning("**📈 Points à améliorer :**")
                for point in eval_result['points_amelioration']:
                    st.write(f"• {point}")
        
        # CONSEILS PERSONNALISÉS
        if 'conseils_personnalises' in eval_result and eval_result['conseils_personnalises']:
            st.markdown("---")
            st.write("**💡 Conseils personnalisés :**")
            for conseil in eval_result['conseils_personnalises']:
                st.write(f"• {conseil}")
        
        # ACTIONS DISPONIBLES
        st.markdown("---")
        col_action1, col_action2 = st.columns(2)
        
        with col_action1:
            if st.button(f"📄 Générer rapport", key=f"rapport_{eval_info['id_evaluation']}"):
                st.session_state.page_redirect = "📄 Mes rapports"
                st.rerun()
        
        with col_action2:
            # Lien vers les soumissions
            if st.button(f"📤 Voir ma soumission", key=f"soumission_{eval_info['id_evaluation']}"):
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
                st.write(f"**👨‍🏫 Professeur :** {eval_info['professeur']}")
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
    """Affiche le feedback pour une question"""
    numero = question.get('numero', 'N/A')
    intitule = question.get('intitule', 'Question sans titre')
    note = question.get('note', 0)
    note_max = question.get('note_max', question.get('points_total', 5))
    pourcentage = question.get('pourcentage_reussite', 0)
    
    # Si pas de pourcentage, calculer
    if pourcentage == 0 and note_max > 0:
        pourcentage = (note / note_max) * 100
    
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
            st.write(f"**Note :** {note}/{note_max} pts")
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
        st.progress(pourcentage / 100, text=f"Maîtrise: {pourcentage:.1f}%")
        
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
    """Retourne l'icône et le texte de performance"""
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
    """Retourne l'icône, couleur et niveau pour une question"""
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
    print("📊 Page my_results.py avec vérification de publication prête !")