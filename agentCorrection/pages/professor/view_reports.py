"""
pages/professor/view_reports.py - Version CORRIGÉE pour le champ pourcentage manquant
==================================================================================
CORRECTION : Gestion défensive des champs manquants (pourcentage, note_maximale, etc.)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_manager import (
    get_evaluations_list, 
    get_correction_results, 
    clear_all_cache,
    publish_evaluation_results,
    unpublish_evaluation_results,
    get_evaluation_publication_status,
    debug_evaluation_files

)
from utils.display_helpers import display_header
from pathlib import Path
from datetime import datetime
import json

def show():
    """Page consultation des rapports avec gestion défensive des champs manquants"""
    display_header("📊 Consulter les Rapports")
    
    # CHARGEMENT INTELLIGENT DES ÉVALUATIONS
    evaluations = get_evaluations_list()
    corrected_evaluations = []
    
    for eval_info in evaluations:
        results_dir = Path(eval_info['dossier']) / "resultats"
        if results_dir.exists() and any(results_dir.iterdir()):
            corrected_evaluations.append(eval_info)
    
    if not corrected_evaluations:
        st.warning("⚠️ Aucune évaluation corrigée trouvée.")
        return
    
    # SÉLECTION DE L'ÉVALUATION
    if 'selected_eval' in st.session_state:
        selected_eval_dir = st.session_state.selected_eval
        selected_eval = next((e for e in corrected_evaluations if e['dossier'] == selected_eval_dir), corrected_evaluations[0])
        del st.session_state.selected_eval
    else:
        eval_options = {f"{e['titre']} - {e['matiere']} ({e['date']})": e for e in corrected_evaluations}
        selected_eval_name = st.selectbox("Choisir l'évaluation", list(eval_options.keys()))
        selected_eval = eval_options[selected_eval_name]
    
    # CHARGEMENT DES RÉSULTATS AVEC NORMALISATION
    results = get_correction_results(selected_eval['dossier'])
    
    if not results:
        st.error("❌ Aucun résultat trouvé pour cette évaluation")
        if st.button("🔄 Recharger"):
            clear_all_cache()
            st.rerun()
        return
    
    # ✅ CORRECTION : Normaliser tous les résultats pour éviter les erreurs de champs manquants
    results = _normalize_results(results, selected_eval)
    
    # AFFICHAGE DU SYSTÈME DE PUBLICATION CORRIGÉ
    st.markdown("---")
    _show_publication_system_fixed(selected_eval, results)
    
    # ONGLETS POUR DIFFÉRENTES VUES
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Vue d'ensemble", "📈 Statistiques détaillées", "👥 Résultats individuels", "📁 Téléchargements"])
    
    with tab1:
        _show_overview_tab(results, selected_eval)
    
    with tab2:
        _show_detailed_stats_tab(results)
    
    with tab3:
        _show_individual_results_tab(results)
    
    with tab4:
        _show_downloads_tab(results, selected_eval)

def _normalize_results(results, eval_info):
    """✅ NOUVELLE FONCTION : Normalise tous les résultats pour éviter les erreurs de champs manquants"""
    
    normalized_results = []
    note_max_default = eval_info.get('note_totale', 20)
    
    for i, result in enumerate(results):
        # Récupérer les valeurs avec des défauts sûrs
        note_totale = result.get('note_totale', 0.0)
        note_maximale = result.get('note_maximale', note_max_default)
        
        # Calculer le pourcentage si manquant
        if 'pourcentage' not in result:
            pourcentage = round((note_totale / note_maximale) * 100, 1) if note_maximale > 0 else 0.0
        else:
            pourcentage = result['pourcentage']
        
        # Normaliser le résultat avec tous les champs requis
        normalized_result = {
            # Champs obligatoires avec défauts sûrs
            'etudiant_nom': result.get('etudiant_nom', f'Etudiant{i+1}'),
            'etudiant_prenom': result.get('etudiant_prenom', f'Prenom{i+1}'),
            'note_totale': float(note_totale),
            'note_maximale': float(note_maximale),
            'pourcentage': float(pourcentage),
            'rang_classe': result.get('rang_classe', i+1),
            'timestamp': result.get('timestamp', result.get('date_correction', datetime.now().isoformat())),
            
            # Champs optionnels avec défauts
            'commentaires_generaux': result.get('commentaires_generaux', result.get('commentaires', '')),
            'points_forts': result.get('points_forts', []),
            'points_amelioration': result.get('points_amelioration', []),
            'conseils_personnalises': result.get('conseils_personnalises', []),
            'questions': result.get('questions', []),
            'necessite_revision_humaine': result.get('necessite_revision_humaine', False),
            'statut_publication': result.get('statut_publication', 'brouillon'),
            'date_correction': result.get('date_correction', datetime.now().isoformat()),
            'methode_correction': result.get('methode_correction', 'standard'),
            
            # Gestion défensive pour les structures imbriquées
            'detection_triche': _normalize_detection_triche(result.get('detection_triche', {})),
            'qualite_correction': _normalize_qualite_correction(result.get('qualite_correction', {})),
        }
        
        # Conserver tous les autres champs existants
        for key, value in result.items():
            if key not in normalized_result:
                normalized_result[key] = value
        
        normalized_results.append(normalized_result)
    
    return normalized_results

def _normalize_detection_triche(detection_data):
    """Normalise les données de détection de triche"""
    return {
        'similarite_detectee': detection_data.get('similarite_detectee', False),
        'score_max': detection_data.get('score_max', 0.0),
        'algorithme': detection_data.get('algorithme', 'standard')
    }

def _normalize_qualite_correction(qualite_data):
    """Normalise les données de qualité de correction"""
    return {
        'profil_utilise': qualite_data.get('profil_utilise', 'Standard'),
        'confiance_ocr': qualite_data.get('confiance_ocr', 0.8),
        'modele_ia': qualite_data.get('modele_ia', 'standard'),
        'verification_double': qualite_data.get('verification_double', False),
        'ecart_type': qualite_data.get('ecart_type', 0.0),
        'nombre_corrections': qualite_data.get('nombre_corrections', 1),
        'notes_individuelles': qualite_data.get('notes_individuelles', [])
    }

def _show_publication_system_fixed(eval_info, results):
    """Affiche le système de publication des résultats - VERSION CORRIGÉE"""
    st.subheader("📢 Gestion de la Publication")
    
    # ✅ CORRECTION : Utiliser la fonction du data_manager pour le statut
    publication_status = get_evaluation_publication_status(eval_info['dossier'])
    
    # DEBUG - Informations détaillées
    with st.expander("🔍 DEBUG - Informations détaillées", expanded=False):
        st.write(f"**Statut détecté :** {publication_status}")
        st.write(f"**Dossier :** {eval_info['dossier']}")
        st.write(f"**Statut dans eval_info :** {eval_info.get('statut_publication', 'N/A')}")
        
        # Vérifier les fichiers
        eval_path = Path(eval_info['dossier'])
        possible_files = [
            eval_path / "infos_evaluation.json",
            eval_path / "evaluation_info.json"
        ]
        
        st.write("**Fichiers d'info présents :**")
        for f in possible_files:
            if f.exists():
                st.write(f"✅ {f.name}")
                try:
                    with open(f, 'r', encoding='utf-8') as file:
                        data = json.load(file)
                        st.write(f"   Statut dans fichier : {data.get('statut_publication', 'N/A')}")
                except:
                    st.write(f"   ❌ Erreur lecture")
            else:
                st.write(f"❌ {f.name}")
        
        if st.button("🔍 Diagnostic complet"):
            debug_evaluation_files(eval_info['dossier'])
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        # Affichage du statut
        if publication_status == 'brouillon':
            st.warning("📝 **Statut :** Brouillon (non visible aux étudiants)")
            st.info("Les résultats ne sont pas encore accessibles aux étudiants")
        elif publication_status == 'publie':
            st.success("✅ **Statut :** Publié (visible aux étudiants)")
            date_pub = eval_info.get('date_publication', 'Date inconnue')
            if date_pub != 'Date inconnue':
                try:
                    date_formatted = datetime.fromisoformat(date_pub).strftime('%d/%m/%Y à %H:%M')
                    st.info(f"📅 Publié le : {date_formatted}")
                except:
                    st.info(f"📅 Publié le : {date_pub}")
        else:  # depublie
            st.error("🚫 **Statut :** Dépublié (retiré aux étudiants)")
            st.info("Les résultats ont été temporairement retirés")
    
    with col2:
        # Métriques de publication
        st.metric("📄 Copies corrigées", len(results))
        if publication_status == 'publie':
            st.metric("👁️ Visible aux étudiants", "OUI", delta="Publié")
        else:
            st.metric("👁️ Visible aux étudiants", "NON", delta="Privé")
    
    with col3:
        # Actions de publication CORRIGÉES
        if publication_status in ['brouillon', 'depublie']:
            if st.button("📢 PUBLIER les résultats", type="primary", key="btn_publish", help="Rendre les résultats visibles aux étudiants"):
                with st.spinner("Publication en cours..."):
                    if _publish_results_fixed(eval_info, results):
                        st.success("✅ Résultats publiés avec succès !")
                        st.balloons()
                        # Forcer le rechargement
                        st.session_state.force_reload = True
                        st.rerun()
                    else:
                        st.error("❌ Erreur lors de la publication")
        
        if publication_status == 'publie':
            if st.button("🚫 DÉPUBLIER les résultats", key="btn_unpublish", help="Retirer temporairement les résultats"):
                with st.spinner("Dépublication en cours..."):
                    if _unpublish_results_fixed(eval_info, results):
                        st.success("✅ Résultats dépubliés avec succès !")
                        # Forcer le rechargement
                        st.session_state.force_reload = True
                        st.rerun()
                    else:
                        st.error("❌ Erreur lors de la dépublication")
    
    # Vérifier si un rechargement est nécessaire
    if st.session_state.get('force_reload', False):
        st.session_state.force_reload = False
        clear_all_cache()
        st.rerun()
    
    # Bouton de rechargement manuel
    if st.button("🔄 Actualiser les données", key="btn_refresh"):
        clear_all_cache()
        st.rerun()
    
    # Informations supplémentaires
    with st.expander("ℹ️ Informations sur la publication", expanded=False):
        st.write("**🔍 Statuts de publication :**")
        st.write("• **Brouillon** : Résultats non visibles aux étudiants (statut par défaut après correction)")
        st.write("• **Publié** : Résultats accessibles aux étudiants via leur espace personnel")
        st.write("• **Dépublié** : Résultats temporairement retirés (utile pour corrections)")
        
        st.write("\n**📧 Notifications automatiques :**")
        st.write("• Les étudiants recevront un email lors de la publication")
        st.write("• Seuls les étudiants concernés par cette évaluation seront notifiés")
        
        st.write("\n**🔒 Sécurité :**")
        st.write("• Chaque étudiant ne peut voir que ses propres résultats")
        st.write("• Les résultats sont chiffrés et sécurisés")
        st.write("• Historique des publications conservé")

def _publish_results_fixed(eval_info, results):
    """Publie les résultats pour les étudiants - VERSION CORRIGÉE"""
    
    try:
        st.write("🔄 Début de la publication...")
        
        # ✅ CORRECTION : Utiliser la fonction du data_manager
        success = publish_evaluation_results(eval_info['dossier'], eval_info)
        
        if success:
            st.write("✅ Publication réussie via data_manager")
            return True
        else:
            st.error("❌ Échec de la publication via data_manager")
            return False
        
    except Exception as e:
        st.error(f"❌ Erreur lors de la publication : {str(e)}")
        return False

def _unpublish_results_fixed(eval_info, results):
    """Dépublie les résultats (les retire aux étudiants) - VERSION CORRIGÉE"""
    
    try:
        st.write("🔄 Début de la dépublication...")
        
        # ✅ CORRECTION : Utiliser la fonction du data_manager
        success = unpublish_evaluation_results(eval_info['dossier'], eval_info)
        
        if success:
            st.write("✅ Dépublication réussie via data_manager")
            
            # Vérification immédiate
            new_status = get_evaluation_publication_status(eval_info['dossier'])
            st.write(f"🔍 Nouveau statut détecté : {new_status}")
            
            return True
        else:
            st.error("❌ Échec de la dépublication via data_manager")
            return False
        
    except Exception as e:
        st.error(f"❌ Erreur lors de la dépublication : {str(e)}")
        st.write(f"🔍 Détails de l'erreur : {e}")
        return False

def _show_overview_tab(results, selected_eval):
    """Affiche l'onglet vue d'ensemble avec gestion défensive"""
    st.subheader("📊 Statistiques Globales")
    
    # ✅ CORRECTION : Accès défensif aux notes
    notes = [float(r.get('note_totale', 0)) for r in results if r.get('note_totale') is not None]
    
    if not notes:
        st.error("❌ Aucune note valide trouvée")
        return
        
    moyenne = sum(notes) / len(notes)
    note_max = max(notes)
    note_min = min(notes)
    taux_reussite = len([n for n in notes if n >= 10]) / len(notes) * 100
    
    # MÉTRIQUES PRINCIPALES
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("📄 Copies", len(results))
    with col2:
        st.metric("📊 Moyenne", f"{moyenne:.2f}/20")
    with col3:
        st.metric("🏆 Note max", f"{note_max:.1f}/20")
    with col4:
        st.metric("📉 Note min", f"{note_min:.1f}/20")
    with col5:
        st.metric("✅ Taux réussite", f"{taux_reussite:.1f}%")
    
    # INDICATEUR DE PUBLICATION
    publication_status = get_evaluation_publication_status(selected_eval['dossier'])
    if publication_status == 'publie':
        st.success("👁️ **Résultats publiés** - Visibles aux étudiants")
    else:
        st.warning("📝 **Résultats en brouillon** - Non visibles aux étudiants")
    
    # GRAPHIQUE DE DISTRIBUTION
    st.markdown("---")
    st.subheader("📈 Distribution des Notes")
    
    fig = px.histogram(
        x=notes,
        nbins=10,
        title="Distribution des Notes de Classe",
        labels={'x': 'Note (/20)', 'y': 'Nombre d\'étudiants'},
        color_discrete_sequence=['#667eea']
    )
    fig.add_vline(x=moyenne, line_dash="dash", line_color="red", annotation_text=f"Moyenne: {moyenne:.2f}")
    fig.add_vline(x=10, line_dash="dot", line_color="green", annotation_text="Seuil réussite: 10")
    
    st.plotly_chart(fig, use_container_width=True)
    
    # INDICATEURS DE QUALITÉ
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        revisions_needed = len([r for r in results if r.get('necessite_revision_humaine', False)])
        st.metric("⚠️ Révisions nécessaires", revisions_needed)
    
    with col2:
        triche_detected = len([r for r in results if r.get('detection_triche', {}).get('similarite_detectee', False)])
        st.metric("🚨 Triche détectée", triche_detected)
    
    with col3:
        excellentes = len([n for n in notes if n >= 16])
        st.metric("🌟 Notes excellentes", excellentes)

def _show_detailed_stats_tab(results):
    """Affiche l'onglet statistiques détaillées avec gestion défensive"""
    st.subheader("📈 Analyses Détaillées")
    
    # ✅ CORRECTION : Accès défensif aux notes
    notes = [float(r.get('note_totale', 0)) for r in results if r.get('note_totale') is not None]
    
    if not notes:
        st.error("❌ Aucune note valide trouvée")
        return
    
    # RÉPARTITION PAR TRANCHES
    tranches = {
        "Excellent (16-20)": len([n for n in notes if n >= 16]),
        "Bien (14-16)": len([n for n in notes if 14 <= n < 16]),
        "Assez bien (12-14)": len([n for n in notes if 12 <= n < 14]),
        "Passable (10-12)": len([n for n in notes if 10 <= n < 12]),
        "Insuffisant (<10)": len([n for n in notes if n < 10])
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_pie = px.pie(
            values=list(tranches.values()),
            names=list(tranches.keys()),
            title="Répartition par Niveau"
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        fig_bar = px.bar(
            x=list(tranches.values()),
            y=list(tranches.keys()),
            orientation='h',
            title="Nombre d'étudiants par tranche",
            color=list(tranches.values()),
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # STATISTIQUES AVANCÉES
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    import statistics
    
    with col1:
        mediane = statistics.median(notes)
        st.metric("📊 Médiane", f"{mediane:.2f}")
    
    with col2:
        ecart_type = statistics.stdev(notes) if len(notes) > 1 else 0
        st.metric("📏 Écart-type", f"{ecart_type:.2f}")
    
    with col3:
        q1 = statistics.quantiles(notes, n=4)[0] if len(notes) >= 4 else min(notes)
        st.metric("📈 1er quartile", f"{q1:.2f}")
    
    with col4:
        q3 = statistics.quantiles(notes, n=4)[2] if len(notes) >= 4 else max(notes)
        st.metric("📈 3ème quartile", f"{q3:.2f}")

def _show_individual_results_tab(results):
    """Affiche l'onglet résultats individuels avec gestion défensive"""
    st.subheader("👥 Résultats Individuels")
    
    # Indicateur de publication
    publication_status = results[0].get('statut_publication', 'brouillon') if results else 'brouillon'
    
    if publication_status == 'publie':
        st.success("✅ Ces résultats sont visibles aux étudiants")
    else:
        st.warning("📝 Ces résultats ne sont pas encore publiés aux étudiants")
    
    # ✅ CORRECTION : Tableau avec accès défensif aux champs
    df_results = pd.DataFrame([
        {
            "Rang": r.get('rang_classe', 'N/A'),
            "Nom": r.get('etudiant_nom', 'Inconnu'),
            "Prénom": r.get('etudiant_prenom', 'Inconnu'),
            "Note": f"{r.get('note_totale', 0):.1f}/{r.get('note_maximale', 20):.0f}",
            "Pourcentage": f"{r.get('pourcentage', 0):.1f}%",
            "Révision": "⚠️" if r.get('necessite_revision_humaine', False) else "✅",
            "Triche": "🚨" if r.get('detection_triche', {}).get('similarite_detectee', False) else "✅",
            "Publié": "✅" if r.get('statut_publication', 'brouillon') == 'publie' else "📝"
        }
        for r in sorted(results, key=lambda x: x.get('note_totale', 0), reverse=True)
    ])
    
    st.dataframe(df_results, use_container_width=True, hide_index=True)
    
    # RECHERCHE ET FILTRAGE
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_name = st.text_input("🔍 Rechercher par nom", placeholder="DUPONT")
    
    with col2:
        min_note = st.number_input("Note minimum", 0.0, 20.0, 0.0)
    
    with col3:
        max_note = st.number_input("Note maximum", 0.0, 20.0, 20.0)
    
    # FILTRAGE avec gestion défensive
    if search_name or min_note > 0 or max_note < 20:
        filtered_results = []
        for r in results:
            nom = r.get('etudiant_nom', '')
            note = r.get('note_totale', 0)
            
            if search_name and search_name.upper() not in nom.upper():
                continue
            if note < min_note or note > max_note:
                continue
            filtered_results.append(r)
        
        st.write(f"📊 {len(filtered_results)} résultat(s) trouvé(s)")
        
        if filtered_results:
            for r in filtered_results:
                status_icon = "✅" if r.get('statut_publication', 'brouillon') == 'publie' else "📝"
                nom = r.get('etudiant_nom', 'Inconnu')
                prenom = r.get('etudiant_prenom', 'Inconnu')
                note = r.get('note_totale', 0)
                note_max = r.get('note_maximale', 20)
                
                with st.expander(f"{status_icon} {prenom} {nom} - {note:.1f}/{note_max:.0f}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Pourcentage :** {r.get('pourcentage', 0):.1f}%")
                        st.write(f"**Rang :** {r.get('rang_classe', 'N/A')}")
                        st.write(f"**Statut publication :** {r.get('statut_publication', 'brouillon')}")
                    with col2:
                        commentaires = r.get('commentaires_generaux', r.get('commentaires', ''))
                        if commentaires:
                            st.write(f"**Commentaire :** {commentaires}")

def _show_downloads_tab(results, selected_eval):
    """Affiche l'onglet téléchargements avec gestion défensive"""
    st.subheader("📁 Téléchargements")
    
    # Informations de publication
    publication_status = get_evaluation_publication_status(selected_eval['dossier'])
    
    if publication_status == 'publie':
        st.info("ℹ️ **Résultats publiés** - Les rapports incluent les données visibles aux étudiants")
    else:
        st.warning("⚠️ **Résultats non publiés** - Les rapports sont pour usage interne uniquement")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**📊 Rapport Professeur Global**")
        if st.button("📊 Télécharger Excel", type="primary"):
            # ✅ CORRECTION : DataFrame avec accès défensif
            df_export = pd.DataFrame([
                {
                    "Nom": r.get('etudiant_nom', 'Inconnu'),
                    "Prénom": r.get('etudiant_prenom', 'Inconnu'),
                    "Note": r.get('note_totale', 0),
                    "Note_Max": r.get('note_maximale', 20),
                    "Pourcentage": r.get('pourcentage', 0),
                    "Rang": r.get('rang_classe', 'N/A'),
                    "Commentaires": r.get('commentaires_generaux', r.get('commentaires', '')),
                    "Revision_Necessaire": r.get('necessite_revision_humaine', False),
                    "Triche_Detectee": r.get('detection_triche', {}).get('similarite_detectee', False),
                    "Statut_Publication": r.get('statut_publication', 'brouillon'),
                    "Date_Correction": r.get('date_correction', ''),
                    "Methode_Correction": r.get('methode_correction', 'standard'),
                    "Ecart_Type": r.get('qualite_correction', {}).get('ecart_type', 0),
                    "Nombre_Corrections": r.get('qualite_correction', {}).get('nombre_corrections', 1),
                    "Publie": "OUI" if r.get('statut_publication', 'brouillon') == 'publie' else "NON"
                }
                for r in results
            ])
            
            # Créer le fichier Excel en mémoire
            from io import BytesIO
            excel_buffer = BytesIO()
            df_export.to_excel(excel_buffer, index=False, sheet_name="Resultats")
            excel_data = excel_buffer.getvalue()
            
            # Nom du fichier
            filename = f"Rapport_{selected_eval['titre']}_{selected_eval['date']}.xlsx"
            
            st.download_button(
                label="📥 Télécharger le rapport Excel",
                data=excel_data,
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    with col2:
        st.write("**📧 Rapport de Publication**")
        if st.button("📧 Télécharger rapport publication"):
            # Créer rapport de publication
            publication_report = _create_publication_report(selected_eval, results)
            
            st.download_button(
                label="📥 Télécharger rapport publication",
                data=publication_report,
                file_name=f"Publication_{selected_eval['titre']}.txt",
                mime="text/plain"
            )

def _create_publication_report(eval_info, results):
    """Crée un rapport de publication avec gestion défensive"""
    
    publication_status = get_evaluation_publication_status(eval_info['dossier'])
    
    # ✅ CORRECTION : Calculs avec gestion défensive
    notes_valides = [r.get('note_totale', 0) for r in results if r.get('note_totale') is not None]
    moyenne = sum(notes_valides) / len(notes_valides) if notes_valides else 0
    note_max = max(notes_valides) if notes_valides else 0
    note_min = min(notes_valides) if notes_valides else 0
    taux_reussite = len([n for n in notes_valides if n >= 10]) / len(notes_valides) * 100 if notes_valides else 0
    
    report = f"""
RAPPORT DE PUBLICATION - {eval_info.get('titre', 'Sans titre')}
{'='*50}

INFORMATIONS GÉNÉRALES
- Évaluation : {eval_info.get('titre', 'Sans titre')}
- Matière : {eval_info.get('matiere', 'Non spécifiée')}
- Date : {eval_info.get('date', 'Non spécifiée')}
- Professeur : {eval_info.get('professeur', 'Non spécifié')}

STATUT DE PUBLICATION
- Statut actuel : {publication_status.upper()}
- Nombre de copies : {len(results)}
- Date de correction : {eval_info.get('date_correction', 'Non spécifiée')}
"""
    
    if publication_status == 'publie':
        report += f"""
- Date de publication : {eval_info.get('date_publication', 'Non spécifiée')}
- Publié par : {eval_info.get('publie_par', 'Non spécifié')}
"""
    
    if publication_status == 'depublie':
        report += f"""
- Date de dépublication : {eval_info.get('date_depublication', 'Non spécifiée')}
- Dépublié par : {eval_info.get('depublie_par', 'Non spécifié')}
"""
    
    report += f"""

STATISTIQUES
- Note moyenne : {moyenne:.2f}/20
- Note maximale : {note_max:.1f}/20
- Note minimale : {note_min:.1f}/20
- Taux de réussite : {taux_reussite:.1f}%

DÉTAILS DES RÉSULTATS
"""
    
    # ✅ CORRECTION : Tri avec gestion défensive
    results_sorted = sorted(results, key=lambda x: x.get('note_totale', 0), reverse=True)
    for r in results_sorted:
        nom = r.get('etudiant_nom', 'Inconnu')
        prenom = r.get('etudiant_prenom', 'Inconnu')
        note = r.get('note_totale', 0)
        pourcentage = r.get('pourcentage', 0)
        report += f"- {prenom} {nom} : {note:.1f}/20 ({pourcentage:.1f}%)\n"
    
    return report

if __name__ == "__main__":
    print("📊 View Reports avec gestion défensive des champs manquants prêt !")