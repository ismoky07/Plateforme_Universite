"""
pages/professor/launch_correction.py - Version avec restriction évaluation fermée et triple correction IA
===============================================================================================
La correction ne peut être lancée que si l'évaluation est fermée/expirée
Triple correction IA avec moyenne et arrondi intelligent
"""

import streamlit as st
import time
import dotenv
import os
from pathlib import Path
from datetime import datetime
from utils.data_manager import get_evaluations_list, clear_all_cache, save_correction_result
from utils.display_helpers import display_header

# ==================================================
# IMPORT DE L'AGENT IA RÉEL
# ==================================================
try:
    from utils.ai_correction_engine import process_copies_with_ai
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

# Paramètres conservés pour compatibilité interface
CORRECTION_PROFILES = {
    "excellence": {
        "name": "🏆 Excellence IA (Recommandé)",
        "description": "Correction IA de qualité maximale avec GPT-4 Vision + Expert",
        "ai_profile": "excellence",
        "display_time": 3,  # Minutes par copie (affichage)
        "features": ["GPT-4 Vision OCR", "GPT-4 Expert", "Double vérification", "Feedback détaillé"]
    },
    "equilibre": {
        "name": "⚖️ Équilibré IA",
        "description": "Correction IA optimisée qualité/rapidité",
        "ai_profile": "equilibre", 
        "display_time": 2,
        "features": ["GPT-4 Vision OCR", "GPT-4 Expert", "Analyse avancée"]
    },
    "rapide": {
        "name": "⚡ Rapide IA",
        "description": "Correction IA rapide pour aperçu immédiat",
        "ai_profile": "rapide",
        "display_time": 1,
        "features": ["GPT-4 Mini", "OCR Standard", "Correction directe"]
    }
}

def show():
    """Page lancement de correction avec IA RÉELLE et restrictions"""
    display_header("🤖 Correction IA Automatique")
    
    # Vérification API OpenAI
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("❌ **Clé API OpenAI manquante !**")
        st.info("💡 Configurez votre clé API dans le fichier .env :")
        st.code("OPENAI_API_KEY=sk-proj-votre_clé_ici")
        st.stop()
    
    if not AI_AVAILABLE:
        st.error("❌ **Modules IA non disponibles !**")
        st.info("💡 Installez les dépendances manquantes :")
        st.code("pip install openai python-dotenv PyMuPDF")
        st.stop()
    
    evaluations = get_evaluations_list()
    
    if not evaluations:
        st.warning("⚠️ Aucune évaluation créée.")
        return
    
    # Sélection évaluation
    eval_options = {f"{e['titre']} - {e['matiere']} ({e['date']})": e for e in evaluations}
    selected_eval_name = st.selectbox("Choisir l'évaluation à corriger", list(eval_options.keys()))
    selected_eval = eval_options[selected_eval_name]
    
    eval_dir = Path(selected_eval['dossier'])
    copies_dir = eval_dir / "copies_soumises"
    results_dir = eval_dir / "resultats"
    
    # NOUVELLE VÉRIFICATION : Statut de l'évaluation
    evaluation_status = _get_evaluation_status(selected_eval)
    
    st.markdown("---")
    
    # Afficher le statut de l'évaluation
    _show_evaluation_status_check(selected_eval, evaluation_status)
    
    # Vérifier si la correction est autorisée
    if evaluation_status == "ouverte":
        _show_correction_blocked_message(selected_eval)
        return
    
    # Si l'évaluation est fermée/expirée, continuer avec l'interface normale
    _show_preconditions_ai(copies_dir, results_dir, selected_eval)
    
    # Sélection du profil IA
    st.markdown("---")
    _show_ai_profile_selection()
    
    # Lancement correction IA
    st.markdown("---")
    _handle_ai_correction_launch(selected_eval, copies_dir, results_dir)

def _get_evaluation_status(eval_info):
    """Détermine le statut d'une évaluation"""
    from datetime import datetime, timedelta
    
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
    from datetime import datetime, timedelta
    
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

def _show_evaluation_status_check(eval_info, status):
    """Affiche le statut de l'évaluation pour la correction"""
    st.subheader("🔍 Statut de l'Évaluation")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if status == "ouverte":
            st.error("🔴 **Évaluation OUVERTE**")
            st.write("Les étudiants peuvent encore soumettre")
        elif status == "fermee":
            st.success("🟢 **Évaluation FERMÉE**")
            st.write("Fermée manuellement par le professeur")
        else:  # expiree
            st.warning("🟡 **Évaluation EXPIRÉE**")
            st.write("Échéance automatique dépassée")
    
    with col2:
        echeance = _calculate_deadline(eval_info)
        maintenant = datetime.now()
        
        st.write(f"**⏰ Échéance :** {echeance.strftime('%d/%m/%Y %H:%M')}")
        
        if maintenant < echeance:
            delta = echeance - maintenant
            if delta.days > 0:
                temps_restant = f"{delta.days} jour(s) {delta.seconds // 3600} heure(s)"
            else:
                temps_restant = f"{delta.seconds // 3600} heure(s) {(delta.seconds % 3600) // 60} min"
            st.write(f"**⏳ Temps restant :** {temps_restant}")
        else:
            st.write("**⏰ Échéance :** Dépassée")
    
    with col3:
        # Statut correction
        if status == "ouverte":
            st.error("❌ **Correction BLOQUÉE**")
            st.write("Fermer l'évaluation d'abord")
        else:
            st.success("✅ **Correction AUTORISÉE**")
            st.write("Prête pour la correction IA")

def _show_correction_blocked_message(eval_info):
    """Affiche un message quand la correction est bloquée"""
    st.markdown("---")
    
    st.error("🚫 **CORRECTION IMPOSSIBLE**")
    
    st.warning("""
    **La correction ne peut pas être lancée car l'évaluation est encore ouverte.**
    
    **Raisons de sécurité :**
    - Les étudiants peuvent encore soumettre des copies
    - Les résultats pourraient être incomplets
    - Risque de confusion avec les soumissions tardives
    """)
    
    st.info("""
    **Solutions possibles :**
    
    1. **Attendre l'échéance automatique** : L'évaluation se fermera automatiquement
    2. **Fermer manuellement** : Allez dans "Créer & Gérer Évaluations" → Onglet "Gérer" → Fermer l'évaluation
    3. **Prolonger si nécessaire** : Si vous devez donner plus de temps aux étudiants
    """)
    
    # Boutons d'action
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔒 Fermer l'évaluation maintenant", type="primary"):
            _close_evaluation_from_correction(eval_info)
            st.success("✅ Évaluation fermée ! Vous pouvez maintenant lancer la correction.")
            st.rerun()
    
    with col2:
        if st.button("⏰ Gérer l'évaluation"):
            st.session_state.page_redirect = "➕ Créer & Gérer Évaluations"
            st.rerun()
    
    with col3:
        if st.button("🔄 Actualiser statut"):
            clear_all_cache()
            st.rerun()
    
    # Affichage du temps restant
    echeance = _calculate_deadline(eval_info)
    maintenant = datetime.now()
    
    if maintenant < echeance:
        delta = echeance - maintenant
        if delta.days > 0:
            temps_restant = f"{delta.days} jour(s) {delta.seconds // 3600} heure(s)"
        else:
            temps_restant = f"{delta.seconds // 3600} heure(s) {(delta.seconds % 3600) // 60} min"
        
        st.info(f"⏳ **Fermeture automatique dans :** {temps_restant}")

def _close_evaluation_from_correction(eval_info):
    """Ferme une évaluation depuis la page de correction"""
    # Mettre à jour le statut
    eval_info['statut'] = 'fermee'
    eval_info['date_fermeture'] = datetime.now().isoformat()
    eval_info['fermeture_manuelle'] = True
    eval_info['fermeture_depuis_correction'] = True
    
    # Sauvegarder
    from utils.data_manager import save_evaluation_info
    save_evaluation_info(eval_info['dossier'], eval_info)
    clear_all_cache()

def _show_preconditions_ai(copies_dir, results_dir, selected_eval):
    """Vérifications avec indicateurs IA"""
    st.subheader("🔍 Vérifications IA")
    
    existing_copies = list(copies_dir.glob("*.pdf")) if copies_dir.exists() else []
    already_corrected = results_dir.exists() and any(results_dir.iterdir())
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if existing_copies:
            st.success(f"✅ {len(existing_copies)} copies détectées")
        else:
            st.error("❌ Aucune copie trouvée")
    
    with col2:
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and AI_AVAILABLE:
            st.success("✅ IA GPT-4 prête")
        else:
            st.error("❌ IA non disponible")
    
    with col3:
        if already_corrected:
            st.info("ℹ️ Déjà corrigée")
            if st.button("🔄 Recorriger avec IA", help="Relancer avec IA"):
                st.session_state.force_ai_recorrection = True
        else:
            st.success("✅ Prête pour IA")
    
    with col4:
        bareme_file = Path(selected_eval['dossier']) / "bareme_evaluation.json"
        if bareme_file.exists():
            st.success("✅ Barème chargé")
        else:
            st.warning("⚠️ Barème manquant")
    
    # Détails copies avec estimation IA
    if existing_copies:
        with st.expander("📋 Copies pour correction IA", expanded=False):
            for i, copy_file in enumerate(existing_copies, 1):
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"📄 {i}. {copy_file.name}")
                with col2:
                    size_mb = copy_file.stat().st_size / 1024 / 1024
                    st.write(f"💾 {size_mb:.1f} MB")
                with col3:
                    profile_time = st.session_state.get('selected_ai_profile', 'excellence')
                    estimated_time = CORRECTION_PROFILES[profile_time]["display_time"] * 3  # Multiplié par 3 pour triple correction
                    st.write(f"🤖 ~{estimated_time}min IA")

def _show_ai_profile_selection():
    """Sélection du profil de correction IA"""
    st.subheader("🎯 Profil de Correction IA")
    
    # Interface améliorée pour les profils IA
    profile_names = list(CORRECTION_PROFILES.keys())
    profile_labels = [CORRECTION_PROFILES[p]["name"] for p in profile_names]
    
    selected_index = st.selectbox(
        "Choisir le profil de correction IA",
        range(len(profile_labels)),
        format_func=lambda x: profile_labels[x],
        index=0  # Excellence par défaut
    )
    
    selected_profile = profile_names[selected_index]
    st.session_state.selected_ai_profile = selected_profile
    
    # Affichage des détails du profil
    profile_info = CORRECTION_PROFILES[selected_profile]
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.info(f"**{profile_info['name']}**")
        st.write(profile_info["description"])
        
        st.write("**🔧 Fonctionnalités IA :**")
        for feature in profile_info["features"]:
            st.write(f"  • {feature}")
        
        # Nouvelle info sur la triple correction
        st.warning("**🔄 Triple Correction :**")
        st.write("  • 3 corrections indépendantes par copie")
        st.write("  • Moyenne arithmétique des 3 notes")
        st.write("  • Arrondi intelligent des résultats")
    
    with col2:
        st.metric("⏱️ Temps par copie", f"{profile_info['display_time'] * 3} min")  # Multiplié par 3
        st.metric("🤖 Type IA", "GPT-4" if "GPT-4" in profile_info["features"][0] else "GPT-4 Mini")
        st.metric("🔄 Corrections", "3x par copie")

def _handle_ai_correction_launch(selected_eval, copies_dir, results_dir):
    """Gestion lancement correction IA RÉELLE avec triple correction"""
    existing_copies = list(copies_dir.glob("*.pdf")) if copies_dir.exists() else []
    
    if not existing_copies:
        st.error("❌ Impossible de lancer la correction IA : aucune copie détectée")
        return
    
    selected_profile = st.session_state.get('selected_ai_profile', 'excellence')
    profile_info = CORRECTION_PROFILES[selected_profile]
    
    # Informations de lancement
    total_copies = len(existing_copies)
    estimated_time = total_copies * profile_info["display_time"] * 3  # Multiplié par 3 pour triple correction
    
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"🤖 **{total_copies}** copies pour triple correction IA")
    with col2:
        st.info(f"⏱️ Temps estimé : **{estimated_time}** minutes")
    
    # Message sur la vraie IA avec triple correction
    st.success(f"🧠 **Triple Correction IA Véritable** - {profile_info['name']}")
    st.warning("💰 **Attention :** Correction payante via API OpenAI (~0.30-1.50€ par copie pour 3 corrections)")
    
    # Informations sur l'arrondi
    st.info("""
    **📏 Règles d'arrondi intelligent :**
    • < 0.5 : entier inférieur (10.33 → 10)
    • > 0.5 : entier supérieur (11.66 → 12)  
    • = 0.5 : conserver .5 (10.5 → 10.5)
    """)
    
    # Bouton de lancement IA
    if st.button("🚀 LANCER TRIPLE CORRECTION IA", type="primary"):
        _run_real_ai_correction(selected_eval, existing_copies, results_dir, selected_profile)

def _run_real_ai_correction(selected_eval, existing_copies, results_dir, profile):
    """Lance la correction IA RÉELLE avec TRIPLE vérification et moyenne"""
    
    def arrondir_note_intelligente(note):
        """
        Arrondit une note selon les règles demandées :
        - < 0.5 : entier inférieur (10.33 → 10)
        - > 0.5 : entier supérieur (11.66 → 12)  
        - = 0.5 : garder .5 (10.5 → 10.5)
        """
        partie_entiere = int(note)
        partie_decimale = round(note - partie_entiere, 2)
        
        if partie_decimale < 0.5:
            return partie_entiere
        elif partie_decimale > 0.5:
            return partie_entiere + 1
        else:  # partie_decimale == 0.5
            return partie_entiere + 0.5
    
    with st.spinner("🧠 Triple correction IA véritable en cours..."):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Étapes réelles avec triple correction
        real_steps = [
            "🔍 Initialisation moteur IA GPT-4...",
            "📋 Chargement du barème d'évaluation...",
            "🤖 Activation GPT-4 Vision pour OCR...",
            "📸 Préparation des copies PDF...",
        ]
        
        try:
            # Étapes préliminaires
            for i, step in enumerate(real_steps):
                status_text.text(step)
                progress_bar.progress((i + 1) / (len(real_steps) + len(existing_copies) * 3 + 2))
                time.sleep(1)
            
            final_results = []
            total_corrections = len(existing_copies) * 3
            current_correction = 0
            
            # TRIPLE CORRECTION pour chaque copie
            for copy_idx, copy_path in enumerate(existing_copies):
                copy_name = copy_path.stem
                status_text.text(f"📄 Copie {copy_idx + 1}/{len(existing_copies)}: {copy_name}")
                
                # Stockage des 3 corrections pour cette copie
                corrections_multiples = []
                
                # 3 corrections indépendantes
                for correction_num in range(1, 4):
                    current_correction += 1
                    status_text.text(f"🤖 Copie {copy_idx + 1}/{len(existing_copies)} - Correction {correction_num}/3: {copy_name}")
                    progress_bar.progress((len(real_steps) + current_correction) / (len(real_steps) + total_corrections + 2))
                    
                    # APPEL RÉEL À L'IA pour cette correction
                    correction_result = process_copies_with_ai(
                        evaluation_info=selected_eval,
                        copies_paths=[str(copy_path)],  # Une seule copie à la fois
                        profile=profile
                    )
                    
                    if correction_result:
                        corrections_multiples.append(correction_result[0])  # Premier (et seul) résultat
                    else:
                        st.warning(f"⚠️ Aucun résultat pour la correction {correction_num} de {copy_name}")
                    
                    time.sleep(0.5)  # Petite pause entre corrections
                
                # CALCUL DE LA MOYENNE des 3 corrections
                if len(corrections_multiples) == 3:
                    try:
                        status_text.text(f"📊 Calcul moyenne pour {copy_name}...")
                        
                        # Moyennes des notes principales
                        notes_totales = [r.get('note_totale', 0) for r in corrections_multiples]
                        moyenne_brute = sum(notes_totales) / len(notes_totales)
                        note_finale = arrondir_note_intelligente(moyenne_brute)
                        
                        # Moyenne des notes par question si disponible
                        notes_par_question = {}
                        if corrections_multiples[0].get('questions'):
                            # La structure questions est une liste de dictionnaires avec 'note' et 'numero'
                            questions_disponibles = corrections_multiples[0]['questions']
                            
                            for i, question_ref in enumerate(questions_disponibles):
                                q_key = f"Q{question_ref.get('numero', i+1)}"
                                notes_question = []
                                
                                for correction in corrections_multiples:
                                    if correction.get('questions') and len(correction['questions']) > i:
                                        note_q = correction['questions'][i].get('note', 0)
                                        notes_question.append(note_q)
                                
                                if notes_question:
                                    moyenne_question = sum(notes_question) / len(notes_question)
                                    notes_par_question[q_key] = {
                                        'note': arrondir_note_intelligente(moyenne_question),
                                        'note_brute': round(moyenne_question, 2),
                                        'corrections_individuelles': notes_question
                                    }
                        
                        # Consolidation des commentaires (prendre le plus complet)
                        commentaires_consolide = corrections_multiples[0].get('commentaires_generaux', 
                                                                        corrections_multiples[0].get('commentaires', ''))
                        
                        # Moyenne des métriques de qualité avec gestion des clés manquantes
                        qualite_correction = {
                            'confiance_ocr': sum(r.get('qualite_correction', {}).get('confiance_ocr', 0.8) for r in corrections_multiples) / 3,
                            'coherence_correction': sum(r.get('qualite_correction', {}).get('coherence_correction', 0.85) for r in corrections_multiples) / 3,
                            'nombre_corrections': 3,
                            'note_brute_moyenne': round(moyenne_brute, 2),
                            'ecart_type': round(((sum((n - moyenne_brute)**2 for n in notes_totales) / 3) ** 0.5), 2),
                            'notes_individuelles': notes_totales
                        }
                        
                        # Résultat final consolidé avec les bonnes clés
                        resultat_final = {
                            'etudiant_nom': corrections_multiples[0]['etudiant_nom'],
                            'etudiant_prenom': corrections_multiples[0]['etudiant_prenom'],
                            'note_totale': note_finale,
                            'note_brute_moyenne': round(moyenne_brute, 2),
                            'notes_detaillees': notes_par_question,
                            'commentaires_generaux': commentaires_consolide,
                            'points_forts': corrections_multiples[0].get('points_forts', []),
                            'points_amelioration': corrections_multiples[0].get('points_amelioration', []),
                            'conseils_personnalises': corrections_multiples[0].get('conseils_personnalises', []),
                            'questions': corrections_multiples[0].get('questions', []),
                            'qualite_correction': qualite_correction,
                            'methode_correction': 'triple_ia_moyenne',
                            'statut_publication': 'brouillon',
                            'date_correction': datetime.now().isoformat(),
                            'corrections_multiples': corrections_multiples,  # Garde trace des 3 corrections
                            'necessite_revision_humaine': qualite_correction['ecart_type'] > 2.0  # Si écart-type > 2 points
                        }
                        
                        final_results.append(resultat_final)
                        
                        # Affichage temps réel de la progression
                        st.info(f"✅ {copy_name}: Note finale **{note_finale}**/20 (moyenne de {notes_totales} = {round(moyenne_brute, 2)})")
                        
                    except Exception as e:
                        st.error(f"❌ Erreur lors du calcul pour {copy_name}: {str(e)}")
                        # En cas d'erreur, créer un résultat minimal avec les données disponibles
                        if corrections_multiples:
                            # Utiliser la première correction comme base
                            resultat_minimal = {
                                'etudiant_nom': corrections_multiples[0].get('etudiant_nom', 'Inconnu'),
                                'etudiant_prenom': corrections_multiples[0].get('etudiant_prenom', 'Inconnu'),
                                'note_totale': corrections_multiples[0].get('note_totale', 0),
                                'note_brute_moyenne': corrections_multiples[0].get('note_totale', 0),
                                'commentaires_generaux': f"Erreur dans la triple correction: {str(e)}",
                                'qualite_correction': {'ecart_type': 0, 'nombre_corrections': len(corrections_multiples)},
                                'methode_correction': 'erreur_triple_correction',
                                'statut_publication': 'brouillon',
                                'date_correction': datetime.now().isoformat(),
                                'necessite_revision_humaine': True,
                                'corrections_multiples': corrections_multiples
                            }
                            final_results.append(resultat_minimal)
                        continue
                else:
                    st.warning(f"⚠️ Seulement {len(corrections_multiples)} corrections réussies pour {copy_name}")
            
            # Sauvegarde des résultats finaux
            status_text.text("💾 Sauvegarde des résultats consolidés...")
            progress_bar.progress(0.95)
            
            results_dir.mkdir(exist_ok=True)
            
            for result in final_results:
                save_correction_result(
                    selected_eval['dossier'],
                    f"{result['etudiant_nom']}_{result['etudiant_prenom']}",
                    result
                )
            
            # Mettre à jour les infos de l'évaluation
            selected_eval['statut_correction'] = 'corrigee'
            selected_eval['date_correction'] = datetime.now().isoformat()
            selected_eval['statut_publication'] = 'brouillon'
            selected_eval['methode_correction'] = 'triple_ia_moyenne'
            
            from utils.data_manager import save_evaluation_info
            save_evaluation_info(selected_eval['dossier'], selected_eval)
            
            progress_bar.progress(1.0)
            status_text.text("✅ Triple correction IA terminée avec moyennes calculées !")
            
            # Affichage des résultats avec statistiques de fiabilité
            _display_triple_ai_results(final_results, selected_eval, profile)
            
        except Exception as e:
            st.error(f"❌ Erreur correction IA triple : {str(e)}")
            st.info("💡 Vérifiez votre clé API et réessayez")

def _display_triple_ai_results(ai_results, selected_eval, profile):
    """Affiche les résultats de correction IA triple avec statistiques de fiabilité"""
    
    clear_all_cache()
    st.balloons()
    
    st.success("🎉 Triple correction IA terminée avec succès !")
    
    # IMPORTANT : Affichage du statut de publication
    st.info("📋 **Statut :** Résultats en brouillon (non publiés aux étudiants)")
    
    # Métriques avec statistiques de fiabilité
    if ai_results:
        notes_finales = [r.get('note_totale', 0) for r in ai_results]
        notes_brutes = [r.get('note_brute_moyenne', 0) for r in ai_results]
        ecarts_types = [r.get('qualite_correction', {}).get('ecart_type', 0) for r in ai_results]
        
        avg_score = sum(notes_finales) / len(notes_finales) if notes_finales else 0
        avg_ecart = sum(ecarts_types) / len(ecarts_types) if ecarts_types else 0
        revision_needed = sum(1 for r in ai_results if r.get('necessite_revision_humaine', False))
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📄 Copies IA", len(ai_results))
        
        with col2:
            st.metric("📊 Moyenne finale", f"{avg_score:.1f}/20")
        
        with col3:
            st.metric("🎯 Fiabilité", f"{avg_ecart:.1f} pts écart")
        
        with col4:
            st.metric("⚠️ À réviser", f"{revision_needed}")
    
    # Détails de la triple correction
    st.markdown("---")
    st.success(f"**🔄 Triple correction IA réalisée - Profil {profile.title()}**")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("🧮 **Méthode de correction :**")
        st.write("  • 3 corrections indépendantes par copie")
        st.write("  • Moyenne arithmétique des 3 notes")
        st.write("  • Arrondi intelligent des notes")
        st.write("  • Calcul d'écart-type pour fiabilité")
    
    with col2:
        st.info("📏 **Règles d'arrondi :**")
        st.write("  • < 0.5 : entier inférieur (10.33 → 10)")
        st.write("  • > 0.5 : entier supérieur (11.66 → 12)")
        st.write("  • = 0.5 : conserver .5 (10.5 → 10.5)")
        st.write("  • Révision si écart-type > 2 points")
    
    # Tableau détaillé des résultats
    if ai_results:
        with st.expander("📊 Détail des corrections multiples", expanded=True):
            for result in ai_results:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    nom = result.get('etudiant_nom', 'Inconnu')
                    prenom = result.get('etudiant_prenom', 'Inconnu')
                    st.write(f"**{prenom} {nom}**")
                
                with col2:
                    notes_indiv = result.get('qualite_correction', {}).get('notes_individuelles', [])
                    if notes_indiv:
                        st.write(f"🔄 Notes: {notes_indiv}")
                    else:
                        st.write("🔄 Notes: N/A")
                
                with col3:
                    moyenne_brute = result.get('note_brute_moyenne', 0)
                    note_finale = result.get('note_totale', 0)
                    st.write(f"📊 Moyenne: {moyenne_brute}")
                    st.write(f"🎯 **Final: {note_finale}**")
                
                with col4:
                    ecart = result.get('qualite_correction', {}).get('ecart_type', 0)
                    if ecart > 2.0:
                        st.error(f"⚠️ Écart: {ecart}")
                    elif ecart > 1.0:
                        st.warning(f"⚠️ Écart: {ecart}")
                    else:
                        st.success(f"✅ Écart: {ecart}")
                
                st.markdown("---")
    
    # Actions post-correction
    st.warning("🔄 **Prochaines étapes :**")
    st.write("1. **Vérifier les copies à réviser** (écart-type élevé)")
    st.write("2. **Consulter les rapports détaillés**")
    st.write("3. **Publier les résultats** pour les étudiants")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Consulter rapports", type="primary"):
            st.session_state.selected_eval = selected_eval['dossier']
            st.session_state.page_redirect = "📊 Consulter rapports"
            st.rerun()
    
    with col2:
        if st.button("📋 Tableau de bord"):
            st.session_state.page_redirect = "📋 Tableau de bord"
            st.rerun()
    
    with col3:
        if st.button("🔄 Actualiser"):
            clear_all_cache()
            st.rerun()

if __name__ == "__main__":
    print("🎯 Launch Correction avec restrictions d'évaluation fermée et triple correction IA prêt !")