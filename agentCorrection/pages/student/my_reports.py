"""
pages/student/my_reports.py - Version CORRIGÉE pour le champ pourcentage manquant
===============================================================================
CORRECTION : Gestion défensive des champs manquants (pourcentage, note_maximale, etc.)
"""

import streamlit as st
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from utils.data_manager import get_evaluations_list, clear_all_cache
from utils.display_helpers import display_header

def show():
    """Page téléchargement de rapports avec vérification de publication et gestion défensive"""
    if not st.session_state.get('student_logged_in', False):
        st.warning("⚠️ Veuillez vous connecter d'abord")
        return
    
    student_info = st.session_state.get('student_info', {})
    
    display_header("📄 Mes Rapports")
    
    # CHARGEMENT DES ÉVALUATIONS CORRIGÉES ET PUBLIÉES
    evaluations = get_evaluations_list()
    published_evaluations = _load_published_student_evaluations(evaluations, student_info)
    unpublished_evaluations = _load_unpublished_student_evaluations(evaluations, student_info)
    
    if not evaluations:
        st.info("📭 Aucune évaluation trouvée")
        if st.button("🔄 Actualiser les données"):
            clear_all_cache()
            st.rerun()
        return
    
    # AFFICHAGE DU STATUT DES RAPPORTS
    _show_reports_status(published_evaluations, unpublished_evaluations)
    
    # AFFICHAGE DES RAPPORTS DISPONIBLES (PUBLIÉS)
    if published_evaluations:
        st.markdown("---")
        st.subheader(f"📊 {len(published_evaluations)} Rapport(s) Disponible(s)")
        
        # LISTE DES RAPPORTS DISPONIBLES
        for eval_result in published_evaluations:
            eval_info = eval_result['evaluation_info']
            _display_report_section(eval_result, eval_info, student_info)
    
    # AFFICHAGE DES RAPPORTS NON DISPONIBLES (NON PUBLIÉS)
    if unpublished_evaluations:
        st.markdown("---")
        _show_unpublished_reports_section(unpublished_evaluations)

def _normalize_student_report_result(result, eval_info):
    """✅ NOUVELLE FONCTION : Normalise un résultat étudiant pour les rapports"""
    
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
    result['etudiant_nom'] = result.get('etudiant_nom', 'Inconnu')
    result['etudiant_prenom'] = result.get('etudiant_prenom', 'Inconnu')
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
            normalized_question = _normalize_question_report_data(question)
            normalized_questions.append(normalized_question)
        result['questions'] = normalized_questions
    
    # Assurer la compatibilité avec l'alias
    result['questions_avec_commentaires'] = result.get('questions_avec_commentaires', result['questions'])
    
    return result

def _normalize_question_report_data(question):
    """Normalise les données d'une question pour les rapports"""
    
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

def _load_published_student_evaluations(evaluations, student_info):
    """Charge les évaluations publiées pour l'étudiant avec normalisation"""
    
    published_evaluations = []
    
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
                            result = _normalize_student_report_result(result, eval_info)
                            
                            # VÉRIFICATION DU STATUT DE PUBLICATION
                            publication_status = _get_publication_status(eval_info, result)
                            
                            if publication_status == 'publie':
                                published_evaluations.append(result)
                    except:
                        continue
    
    return published_evaluations

def _load_unpublished_student_evaluations(evaluations, student_info):
    """Charge les évaluations non publiées pour l'étudiant avec normalisation"""
    
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
                            
                            # ✅ CORRECTION : Normaliser le résultat même s'il n'est pas publié
                            result = _normalize_student_report_result(result, eval_info)
                            
                            # VÉRIFICATION DU STATUT DE PUBLICATION
                            publication_status = _get_publication_status(eval_info, result)
                            
                            if publication_status != 'publie':
                                unpublished_evaluations.append({
                                    'evaluation_info': eval_info,
                                    'statut_publication': publication_status,
                                    'result': result
                                })
                    except:
                        continue
    
    return unpublished_evaluations

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

def _show_reports_status(published_evaluations, unpublished_evaluations):
    """Affiche le statut des rapports selon les publications"""
    
    total_corrections = len(published_evaluations) + len(unpublished_evaluations)
    
    if total_corrections == 0:
        st.info("📭 Aucune évaluation corrigée trouvée pour générer des rapports")
        
        # SUGGESTIONS
        st.markdown("---")
        st.write("💡 **Pour obtenir vos rapports :**")
        st.write("• Assurez-vous d'avoir soumis vos copies")
        st.write("• Attendez que votre professeur lance la correction")
        st.write("• Attendez que votre professeur publie les résultats")
        st.write("• Consultez vos résultats une fois publiés")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📊 Voir mes résultats"):
                st.session_state.page_redirect = "📊 Mes résultats"
                st.rerun()
        with col2:
            if st.button("📤 Voir mes soumissions"):
                st.session_state.page_redirect = "📋 Mes soumissions"
                st.rerun()
        return
    
    # MÉTRIQUES DE PUBLICATION POUR LES RAPPORTS
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📊 Évaluations corrigées", total_corrections)
    
    with col2:
        st.metric("📄 Rapports disponibles", len(published_evaluations))
    
    with col3:
        st.metric("⏳ Rapports en attente", len(unpublished_evaluations))
    
    # Message informatif selon la situation
    if len(published_evaluations) == 0 and len(unpublished_evaluations) > 0:
        st.warning("📝 **Aucun rapport disponible - Tous vos résultats sont en attente de publication**")
        st.info("Les rapports seront générés automatiquement une fois que le professeur aura publié vos résultats")
    elif len(published_evaluations) > 0 and len(unpublished_evaluations) > 0:
        st.success(f"📄 **{len(published_evaluations)} rapport(s) disponible(s)**")
        st.info(f"📝 {len(unpublished_evaluations)} rapport(s) supplémentaire(s) seront disponibles après publication")
    elif len(published_evaluations) > 0:
        st.success(f"🎉 **Tous vos rapports sont disponibles !**")

def _show_unpublished_reports_section(unpublished_evaluations):
    """Affiche la section des rapports non disponibles"""
    
    st.subheader("⏳ Rapports en Attente de Publication")
    
    # Message explicatif
    st.info("""
    **📋 Rapports non disponibles**
    
    Ces évaluations ont été corrigées mais les résultats ne sont pas encore publiés.
    Vous pourrez générer vos rapports une fois que le professeur aura publié les résultats.
    """)
    
    # Liste des rapports non disponibles
    for unpub_eval in unpublished_evaluations:
        eval_info = unpub_eval['evaluation_info']
        statut = unpub_eval['statut_publication']
        
        # Icône selon le statut
        if statut == 'brouillon':
            status_icon = "📝"
            status_text = "Résultats en brouillon"
        elif statut == 'depublie':
            status_icon = "🚫"
            status_text = "Résultats temporairement retirés"
        else:
            status_icon = "⏳"
            status_text = "En attente de publication"
        
        with st.expander(f"{status_icon} {eval_info['titre']} - {eval_info['matiere']} ({status_text})", expanded=False):
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**📅 Date évaluation :** {eval_info['date']}")
                st.write(f"**👨‍🏫 Professeur :** {eval_info.get('professeur', 'Non spécifié')}")
                st.write(f"**📊 Statut :** {status_text}")
            
            with col2:
                if statut == 'brouillon':
                    st.warning("📝 **Rapport non disponible** - Résultats en brouillon")
                    st.write("Le professeur n'a pas encore publié les résultats")
                elif statut == 'depublie':
                    st.error("🚫 **Rapport temporairement indisponible** - Résultats retirés")
                    st.write("Le professeur a temporairement retiré les résultats")
                else:
                    st.info("⏳ **Rapport en attente** - Publication en cours")
            
            # Fonctionnalités limitées
            st.write("**🔒 Fonctionnalités verrouillées :**")
            st.write("• ❌ Génération de rapports PDF")
            st.write("• ❌ Analyses graphiques détaillées")
            st.write("• ❌ Plans de révision personnalisés")
            st.write("• ❌ Téléchargements de données")
            
            st.write("**💡 Que faire ?**")
            st.write("• Attendez que le professeur publie les résultats")
            st.write("• Contactez votre professeur pour connaître le délai")
            st.write("• Actualisez régulièrement cette page")
    
    # Bouton d'actualisation
    st.markdown("---")
    if st.button("🔄 Vérifier les publications", type="primary"):
        clear_all_cache()
        st.rerun()

def _display_report_section(eval_result, eval_info, student_info):
    """Affiche une section de rapport pour chaque évaluation publiée avec gestion défensive"""
    
    # ✅ CORRECTION : Accès défensif au pourcentage (maintenant normalisé)
    pourcentage = eval_result.get('pourcentage', 0)
    if pourcentage >= 80:
        perf_icon = "🏆"
        perf_text = "Excellent"
    elif pourcentage >= 70:
        perf_icon = "🌟"
        perf_text = "Très bien"
    elif pourcentage >= 60:
        perf_icon = "👍"
        perf_text = "Bien"
    else:
        perf_icon = "📈"
        perf_text = "À améliorer"
    
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
    
    with st.expander(f"{perf_icon} {eval_info['titre']} - {eval_info['matiere']} ({eval_info['date']}) - {publication_info}", expanded=True):
        
        # RÉSUMÉ RAPIDE avec gestion défensive
        col1, col2, col3 = st.columns(3)
        
        with col1:
            note_totale = eval_result.get('note_totale', 0)
            note_maximale = eval_result.get('note_maximale', 20)
            st.metric("Note", f"{note_totale:.1f}/{note_maximale:.0f}")
        with col2:
            st.metric("Performance", f"{perf_text}")
        with col3:
            questions_count = len(eval_result.get('questions_avec_commentaires', eval_result.get('questions', [])))
            st.metric("Questions", questions_count)
        
        st.markdown("---")
        
        # ONGLETS POUR LES DIFFÉRENTES ANALYSES
        tab1, tab2, tab3, tab4 = st.tabs(["📥 Téléchargements", "📈 Graphiques", "📋 Plan de Révision", "📊 Analyses"])
        
        with tab1:
            _display_download_section(eval_result, eval_info, student_info)
        
        with tab2:
            _display_detailed_graphs(eval_result, eval_info)
        
        with tab3:
            _display_revision_plan(eval_result, eval_info)
        
        with tab4:
            _display_detailed_analysis(eval_result, eval_info)

def _display_download_section(eval_result, eval_info, student_info):
    """Section de téléchargements pour résultats publiés"""
    
    st.success("✅ **Rapports disponibles (résultats publiés)**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**📄 Rapport Complet PDF**")
        st.write("• Page de garde")
        st.write("• Analyses détaillées")
        st.write("• Graphiques intégrés")
        st.write("• Plan de révision")
        
        _display_pdf_download_button(eval_result, eval_info, student_info, "complet")
    
    with col2:
        st.write("**📋 Résumé Exécutif**")
        st.write("• Points essentiels")
        st.write("• Recommandations")
        st.write("• Synthèse performance")
        st.write("• Format condensé")
        
        _display_pdf_download_button(eval_result, eval_info, student_info, "resume")
    
    with col3:
        st.write("**📝 Format Texte**")
        st.write("• Toujours disponible")
        st.write("• Compatible partout")
        st.write("• Données brutes")
        st.write("• Sauvegarde simple")
        
        _display_text_download_button(eval_result, eval_info, student_info)

def _display_detailed_graphs(eval_result, eval_info):
    """Affiche les graphiques détaillés de performance avec gestion défensive"""
    
    st.write("**📈 Analyse Graphique de vos Performances**")
    
    questions = eval_result.get('questions_avec_commentaires', eval_result.get('questions', []))
    
    if not questions:
        st.info("📊 Pas de données détaillées disponibles pour les graphiques")
        return
    
    # Données pour les graphiques avec gestion défensive
    question_labels = []
    scores = []
    max_scores = []
    
    for i, q in enumerate(questions):
        question_labels.append(f"Q{q.get('numero', i+1)}")
        
        # ✅ CORRECTION : Accès défensif aux données de question (maintenant normalisées)
        note = q.get('note', 0)
        note_max = q.get('note_max', q.get('points_total', 1))
        pourcentage = q.get('pourcentage_reussite', 0)
        
        scores.append(float(pourcentage))
        max_scores.append(100.0)  # 100% pour chaque question
    
    # Graphique en barres avec Streamlit
    st.write("**📊 Performance par Question (%)**")
    
    if scores:  # Vérifier qu'il y a des données
        df = pd.DataFrame({
            'Question': question_labels,
            'Votre Score (%)': scores,
            'Maximum (%)': max_scores
        })
        
        st.bar_chart(df.set_index('Question')[['Votre Score (%)']])
        
        # Tableau détaillé
        st.write("**📋 Détail des Performances**")
        
        chart_data = []
        for i, (label, score, q) in enumerate(zip(question_labels, scores, questions)):
            niveau = _get_performance_level(score)
            chart_data.append({
                'Question': label,
                'Score': f"{score:.1f}%",
                'Note': f"{q.get('note', 0):.1f}/{q.get('note_max', q.get('points_total', 5)):.1f}",
                'Niveau': niveau,
                'Type': q.get('type', 'N/A').title()
            })
        
        df_detail = pd.DataFrame(chart_data)
        st.dataframe(df_detail, use_container_width=True, hide_index=True)
        
        # Statistiques
        if scores:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                moyenne = sum(scores) / len(scores)
                st.metric("📊 Score moyen", f"{moyenne:.1f}%")
            
            with col2:
                meilleur = max(scores)
                st.metric("🏆 Meilleur", f"{meilleur:.1f}%")
            
            with col3:
                plus_faible = min(scores)
                st.metric("📈 Plus faible", f"{plus_faible:.1f}%")
            
            with col4:
                excellentes = sum(1 for s in scores if s >= 90)
                st.metric("🌟 Excellentes", f"{excellentes}/{len(scores)}")
    else:
        st.info("📊 Aucune donnée de score disponible")

def _display_revision_plan(eval_result, eval_info):
    """Affiche le plan de révision personnalisé avec gestion défensive"""
    
    st.write("**📋 Plan de Révision Personnalisé**")
    
    matiere = eval_info.get('matiere', 'Matière')
    questions = eval_result.get('questions_avec_commentaires', eval_result.get('questions', []))
    
    # Analyser les questions par niveau de performance avec gestion défensive
    questions_urgentes = []
    questions_amelioration = []
    questions_consolidation = []
    
    for q in questions:
        # ✅ CORRECTION : Accès défensif au pourcentage (maintenant normalisé)
        pourcentage = q.get('pourcentage_reussite', 0)
        
        if pourcentage < 40:
            questions_urgentes.append(q)
        elif pourcentage < 70:
            questions_amelioration.append(q)
        elif pourcentage < 90:
            questions_consolidation.append(q)
    
    # Plan structuré par priorités
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if questions_urgentes:
            st.error("🚨 **PRIORITÉ 1 - URGENT**")
            st.write(f"**{len(questions_urgentes)} question(s) à retravailler**")
            
            for q in questions_urgentes:
                numero = q.get('numero', 'N/A')
                pourcentage = q.get('pourcentage_reussite', 0)
                st.write(f"• **Q{numero}** ({pourcentage:.0f}%)")
                conseil = q.get('conseil_personnalise', "Revoir les concepts de base")
                st.caption(conseil)
        else:
            st.success("✅ **Aucune révision urgente**")
    
    with col2:
        if questions_amelioration:
            st.warning("📈 **PRIORITÉ 2 - AMÉLIORATION**")
            st.write(f"**{len(questions_amelioration)} question(s) à approfondir**")
            
            for q in questions_amelioration:
                numero = q.get('numero', 'N/A')
                pourcentage = q.get('pourcentage_reussite', 0)
                st.write(f"• **Q{numero}** ({pourcentage:.0f}%)")
                conseil = q.get('conseil_personnalise', "À approfondir")
                st.caption(conseil)
        else:
            st.info("ℹ️ **Bases solides acquises**")
    
    with col3:
        if questions_consolidation:
            st.info("🎯 **PRIORITÉ 3 - CONSOLIDATION**")
            st.write(f"**{len(questions_consolidation)} question(s) à peaufiner**")
            
            for q in questions_consolidation:
                numero = q.get('numero', 'N/A')
                pourcentage = q.get('pourcentage_reussite', 0)
                st.write(f"• **Q{numero}** ({pourcentage:.0f}%)")
                conseil = q.get('conseil_personnalise', "Peaufiner les détails")
                st.caption(conseil)
        else:
            st.success("🏆 **Maîtrise excellente**")
    
    # Planning temporel suggéré
    st.markdown("---")
    st.write("**📅 Planning de Révision Suggéré**")
    
    planning_data = [
        ["📅 **Semaine 1**", "🚨 Priorité 1", "Révisions urgentes - Reprendre les bases"],
        ["📅 **Semaine 2**", "📈 Priorité 2", "Approfondissements - Exercices supplémentaires"],
        ["📅 **Semaine 3**", "🎯 Priorité 3", "Consolidation - Peaufinage des détails"],
        ["📅 **Semaine 4**", "🧪 Évaluation", "Tests blancs - Auto-évaluation"]
    ]
    
    for periode, objectif, actions in planning_data:
        col_p1, col_p2, col_p3 = st.columns([1, 1, 2])
        with col_p1:
            st.write(periode)
        with col_p2:
            st.write(objectif)
        with col_p3:
            st.write(actions)
    
    # Téléchargement du plan
    st.markdown("---")
    plan_text = _generate_revision_plan_text(eval_result, eval_info, questions_urgentes, questions_amelioration, questions_consolidation)
    
    eval_id = eval_info.get('id_evaluation', f"eval_{hash(eval_info['titre'])}")
    st.download_button(
        label="📥 Télécharger Plan de Révision",
        data=plan_text,
        file_name=f"Plan_Revision_{eval_info.get('matiere', 'Matiere')}_{eval_info.get('date', '2024')}.txt",
        mime="text/plain",
        key=f"download_plan_{eval_id}"
    )

def _display_detailed_analysis(eval_result, eval_info):
    """Affiche l'analyse détaillée avancée avec gestion défensive"""
    
    st.write("**📊 Analyse Détaillée Avancée**")
    
    questions = eval_result.get('questions_avec_commentaires', eval_result.get('questions', []))
    
    if not questions:
        st.info("📊 Pas de données détaillées disponibles")
        return
    
    # Analyse par type de question avec gestion défensive
    types_questions = {}
    for q in questions:
        q_type = q.get('type', 'ouverte')
        if q_type not in types_questions:
            types_questions[q_type] = {'total': 0, 'score_total': 0, 'questions': []}
        
        # ✅ CORRECTION : Accès défensif au pourcentage (maintenant normalisé)
        pourcentage = q.get('pourcentage_reussite', 0)
        
        types_questions[q_type]['total'] += 1
        types_questions[q_type]['score_total'] += float(pourcentage)
        types_questions[q_type]['questions'].append(q)
    
    st.write("**🎯 Performance par Type de Question**")
    
    for q_type, data in types_questions.items():
        moyenne_type = data['score_total'] / data['total'] if data['total'] > 0 else 0
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.write(f"**{q_type.title()}**")
        
        with col2:
            st.write(f"Moyenne: {moyenne_type:.1f}%")
        
        with col3:
            st.write(f"({data['total']} question(s))")
        
        # Barre de progression
        progress_value = max(0, min(100, moyenne_type)) / 100
        st.progress(progress_value, text=f"Maîtrise {q_type}: {moyenne_type:.1f}%")
    
    # Recommandations par type
    st.markdown("---")
    st.write("**💡 Recommandations par Type de Question**")
    
    for q_type, data in types_questions.items():
        moyenne_type = data['score_total'] / data['total'] if data['total'] > 0 else 0
        
        if moyenne_type < 60:
            st.warning(f"📈 **{q_type.title()}** : Travail nécessaire sur ce type d'exercice")
            recommandations = _get_type_recommendations(q_type, "faible")
        elif moyenne_type < 80:
            st.info(f"🔄 **{q_type.title()}** : Bonne base, à approfondir")
            recommandations = _get_type_recommendations(q_type, "moyen")
        else:
            st.success(f"🏆 **{q_type.title()}** : Excellente maîtrise")
            recommandations = _get_type_recommendations(q_type, "excellent")
        
        for rec in recommandations:
            st.write(f"  • {rec}")

def _display_pdf_download_button(eval_result, eval_info, student_info, report_type):
    """Bouton de téléchargement PDF pour résultats publiés"""
    
    eval_id = eval_info.get('id_evaluation', f"eval_{hash(eval_info['titre'])}")
    student_key = f"{student_info['nom']}_{student_info['prenom']}"
    button_key = f"pdf_{report_type}_{eval_id}_{student_key}"
    
    if report_type == "complet":
        button_label = "📄 Télécharger PDF Complet"
        filename_suffix = "Complet"
    else:
        button_label = "📋 Télécharger Résumé PDF"
        filename_suffix = "Resume"
    
    if st.button(button_label, key=button_key):
        
        with st.spinner(f"🔄 Génération du rapport PDF..."):
            try:
                from utils.pdf_report_generator import generate_student_pdf_report
                
                pdf_data = generate_student_pdf_report(eval_result, eval_info, student_info)
                
                filename = f"Rapport_{filename_suffix}_{student_info['nom']}_{student_info['prenom']}_{eval_info.get('matiere', 'Matiere')}_{eval_info.get('date', '2024')}.pdf"
                filename = filename.replace(" ", "_").replace("/", "-").replace(":", "")
                
                st.download_button(
                    label=f"📥 Télécharger {button_label.split()[-1]}",
                    data=pdf_data,
                    file_name=filename,
                    mime="application/pdf",
                    key=f"download_{button_key}"
                )
                
                st.success(f"✅ PDF généré ! Cliquez ci-dessus pour télécharger.")
                
            except ImportError:
                st.error("❌ Module PDF non disponible")
                st.info("💡 Installez : `pip install reportlab`")
                
            except Exception as e:
                st.error(f"❌ Erreur : {str(e)}")

def _display_text_download_button(eval_result, eval_info, student_info):
    """Bouton de téléchargement texte pour résultats publiés"""
    
    eval_id = eval_info.get('id_evaluation', f"eval_{hash(eval_info['titre'])}")
    button_key = f"txt_{eval_id}"
    
    if st.button("📝 Télécharger Format Texte", key=button_key):
        
        rapport_text = _generate_complete_text_report(eval_result, eval_info, student_info)
        
        filename = f"Rapport_{student_info['nom']}_{student_info['prenom']}_{eval_info.get('matiere', 'Matiere')}.txt"
        filename = filename.replace(" ", "_").replace("/", "-")
        
        st.download_button(
            label="📥 Télécharger Rapport Texte",
            data=rapport_text,
            file_name=filename,
            mime="text/plain",
            key=f"download_txt_{button_key}"
        )
        
        st.success("✅ Rapport texte prêt !")

def _generate_complete_text_report(eval_result, eval_info, student_info):
    """Génère un rapport texte complet avec toutes les analyses"""
    
    # Date de publication
    date_publication = eval_info.get('date_publication', 'Date inconnue')
    if date_publication != 'Date inconnue':
        try:
            date_formatted = datetime.fromisoformat(date_publication).strftime('%d/%m/%Y à %H:%M')
        except:
            date_formatted = date_publication
    else:
        date_formatted = 'Date inconnue'
    
    # ✅ CORRECTION : Accès défensif aux données de l'étudiant et de l'évaluation
    nom = student_info.get('nom', 'Inconnu')
    prenom = student_info.get('prenom', 'Inconnu')
    numero = student_info.get('numero', 'N/A')
    titre = eval_info.get('titre', 'Sans titre')
    matiere = eval_info.get('matiere', 'Matière inconnue')
    date_eval = eval_info.get('date', 'Date inconnue')
    note_totale = eval_result.get('note_totale', 0)
    note_maximale = eval_result.get('note_maximale', 20)
    pourcentage = eval_result.get('pourcentage', 0)
    rang = eval_result.get('rang_classe', 'N/A')
    
    rapport = f"""
═══════════════════════════════════════════════════════════════════════════════
                    RAPPORT COMPLET DE CORRECTION
═══════════════════════════════════════════════════════════════════════════════

ÉTUDIANT : {prenom} {nom} ({numero})
ÉVALUATION : {titre} - {matiere}
DATE ÉVALUATION : {date_eval}
DATE PUBLICATION : {date_formatted}

RÉSULTATS GÉNÉRAUX
==================
Note finale : {note_totale:.1f}/{note_maximale:.0f}
Pourcentage : {pourcentage:.1f}%
Rang classe : {rang}

STATUT DE PUBLICATION
====================
✅ Résultats publiés et accessibles
📊 Rapport généré automatiquement
📧 Étudiant notifié de la publication

[Contenu détaillé avec analyses, graphiques textuels, plan de révision...]
"""
    
    return rapport

def _generate_revision_plan_text(eval_result, eval_info, urgentes, amelioration, consolidation):
    """Génère le plan de révision en format texte avec gestion défensive"""
    
    # ✅ CORRECTION : Accès défensif aux données
    matiere = eval_info.get('matiere', 'N/A')
    titre = eval_info.get('titre', 'Sans titre')
    nom = eval_result.get('etudiant_nom', 'Inconnu')
    prenom = eval_result.get('etudiant_prenom', 'Inconnu')
    
    plan = f"""
PLAN DE RÉVISION PERSONNALISÉ
=============================

Matière : {matiere}
Évaluation : {titre}
Étudiant : {prenom} {nom}
Statut : ✅ Résultats publiés

PRIORITÉ 1 - RÉVISIONS URGENTES ({len(urgentes)} question(s))
===============================================
"""
    
    for q in urgentes:
        numero = q.get('numero', 'N/A')
        conseil = q.get('conseil_personnalise', 'Révision nécessaire')
        plan += f"• Question {numero} : {conseil}\n"
    
    plan += f"""
PRIORITÉ 2 - APPROFONDISSEMENTS ({len(amelioration)} question(s))
=====================================
"""
    
    for q in amelioration:
        numero = q.get('numero', 'N/A')
        conseil = q.get('conseil_personnalise', 'À approfondir')
        plan += f"• Question {numero} : {conseil}\n"
    
    plan += """
PLANNING SUGGÉRÉ
================
Semaine 1 : Focus priorité 1
Semaine 2 : Travail priorité 2  
Semaine 3 : Consolidation
Semaine 4 : Auto-évaluation
"""
    
    return plan

def _get_performance_level(pourcentage):
    """Retourne le niveau de performance avec gestion défensive"""
    pourcentage = float(pourcentage) if pourcentage is not None else 0
    
    if pourcentage >= 90:
        return "🏆 Excellent"
    elif pourcentage >= 75:
        return "🌟 Très bien"  
    elif pourcentage >= 60:
        return "👍 Bien"
    elif pourcentage >= 40:
        return "🔄 Moyen"
    else:
        return "📈 À améliorer"

def _get_type_recommendations(question_type, niveau):
    """Retourne des recommandations selon le type de question"""
    
    recommendations = {
        "calcul": {
            "excellent": ["Essayez des méthodes alternatives", "Aidez vos camarades"],
            "moyen": ["Vérifiez vos calculs étape par étape", "Attention aux unités"],
            "faible": ["Reprenez les formules de base", "Entraînez-vous sur des exemples simples"]
        },
        "demonstration": {
            "excellent": ["Explorez des démonstrations alternatives", "Travaillez la concision"],
            "moyen": ["Structurez mieux votre raisonnement", "Justifiez chaque étape"],
            "faible": ["Apprenez la méthodologie de démonstration", "Travaillez sur des exemples guidés"]
        },
        "qcm": {
            "excellent": ["Expliquez pourquoi les autres réponses sont fausses"],
            "moyen": ["Lisez attentivement les nuances", "Éliminez les réponses évidentes"],
            "faible": ["Révisez les définitions de base", "Entraînez-vous sur des QCM similaires"]
        },
        "ouverte": {
            "excellent": ["Enrichissez vos arguments", "Ajoutez des exemples"],
            "moyen": ["Structurez mieux vos idées", "Développez vos arguments"],
            "faible": ["Assurez-vous de comprendre la question", "Travaillez la rédaction"]
        }
    }
    
    return recommendations.get(question_type, {}).get(niveau, ["Continuez vos efforts"])

if __name__ == "__main__":
    print("📄 Page my_reports.py avec gestion défensive des champs manquants prête !")