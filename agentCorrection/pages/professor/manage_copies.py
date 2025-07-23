"""
pages/professor/manage_copies.py - Version sans problème de cache
"""

import streamlit as st
from pathlib import Path
from utils.data_manager import get_evaluations_list, save_uploaded_files, clear_all_cache
from utils.display_helpers import display_header

def show():
    """Page gestion des copies"""
    display_header("📤 Gérer les Copies")
    

    
    # CHARGEMENT INTELLIGENT DES ÉVALUATIONS
    evaluations = get_evaluations_list()
    
    if not evaluations:
        st.warning("⚠️ Aucune évaluation créée. Créez d'abord une évaluation.")
        return
    
    # SÉLECTION DE L'ÉVALUATION
    st.subheader("🎯 Sélection de l'Évaluation")
    eval_options = {f"{e['titre']} - {e['matiere']} ({e['date']})": e for e in evaluations}
    selected_eval_name = st.selectbox("Choisir l'évaluation", list(eval_options.keys()))
    selected_eval = eval_options[selected_eval_name]
    
    eval_dir = Path(selected_eval['dossier'])
    copies_dir = eval_dir / "copies_soumises"
    
    # AFFICHAGE DES COPIES EXISTANTES
    st.markdown("---")
    _show_existing_copies(copies_dir, selected_eval)
    
    # UPLOAD DE NOUVELLES COPIES
    st.markdown("---")

    _handle_copy_upload(copies_dir, selected_eval)
    
    # CONSEILS ET CONVENTIONS

    st.markdown("---")
    _show_naming_conventions()

def _show_existing_copies(copies_dir, selected_eval):
    """Affiche les copies existantes"""
    st.subheader("📄 Copies Actuelles")
    
    existing_copies = list(copies_dir.glob("*.pdf")) if copies_dir.exists() else []
    
    if existing_copies:
        # MÉTRIQUES
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📄 Copies déposées", len(existing_copies))
        with col2:
            total_size = sum(f.stat().st_size for f in existing_copies) / 1024 / 1024
            st.metric("💾 Taille totale", f"{total_size:.1f} MB")
        with col3:
            avg_size = total_size / len(existing_copies) if existing_copies else 0
            st.metric("📊 Taille moyenne", f"{avg_size:.1f} MB")
        with col4:
            status = "✅ Prêt" if len(existing_copies) > 0 else "⏳ En attente"
            st.metric("🎯 Statut", status)
        
        # LISTE DÉTAILLÉE DES COPIES
        with st.expander("📋 Détail des copies", expanded=True):
            for i, copy_file in enumerate(existing_copies, 1):
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                
                with col1:
                    st.write(f"📄 {i}. {copy_file.name}")
                
                with col2:
                    size_mb = copy_file.stat().st_size / 1024 / 1024
                    st.write(f"💾 {size_mb:.1f} MB")
                
                with col3:
                    # Timestamp de modification
                    import datetime
                    mod_time = datetime.datetime.fromtimestamp(copy_file.stat().st_mtime)
                    st.write(f"⏰ {mod_time.strftime('%d/%m %H:%M')}")
                
                with col4:
                    if st.button("🗑️", key=f"delete_{copy_file.name}", help="Supprimer cette copie"):
                        copy_file.unlink()
                        clear_all_cache()  # Actualiser après suppression
                        st.success(f"✅ {copy_file.name} supprimé")
                        st.rerun()
    
    else:
        st.info("📭 Aucune copie déposée pour cette évaluation")
        
        # SUGGESTIONS
        st.write("💡 **Pour commencer :**")
        st.write("1. Utilisez la section upload ci-dessous")
        st.write("2. Respectez les conventions de nommage")
        st.write("3. Vérifiez la qualité des PDF")

def _handle_copy_upload(copies_dir, selected_eval):
    """Gère l'upload de nouvelles copies"""
    st.subheader("📤 Ajouter des Copies")
    
    # INFORMATIONS SUR L'ÉVALUATION
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"📚 **Évaluation :** {selected_eval['titre']}")
        st.info(f"📅 **Date :** {selected_eval['date']}")
    with col2:
        st.info(f"🎓 **Matière :** {selected_eval['matiere']}")
        st.info(f"⏱️ **Durée :** {selected_eval['duree']}")
    
    # UPLOAD INTERFACE
    uploaded_files = st.file_uploader(
        "Déposer les copies PDF",
        type=['pdf'],
        accept_multiple_files=True,
        help="Formats acceptés : PDF uniquement. Nommage recommandé : NOM_Prenom_copie.pdf"
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} fichier(s) sélectionné(s)")
        
        # PRÉVISUALISATION DES FICHIERS
        total_size = 0
        for i, file in enumerate(uploaded_files, 1):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"📄 {i}. {file.name}")
            
            with col2:
                size_mb = len(file.getvalue()) / 1024 / 1024
                total_size += size_mb
                st.write(f"💾 {size_mb:.1f} MB")
            
            with col3:
                # Validation du nom
                if "_" in file.name and file.name.endswith('.pdf'):
                    st.write("✅ Format OK")
                else:
                    st.write("⚠️ Nom à vérifier")
        
        # RÉSUMÉ UPLOAD
        st.info(f"📊 **Total :** {len(uploaded_files)} fichiers, {total_size:.1f} MB")
        
        # BOUTON DE SAUVEGARDE
        if st.button("💾 Sauvegarder les copies", type="primary"):
            try:
                saved_files = save_uploaded_files(uploaded_files, copies_dir)
                
                # INVALIDATION CACHE APRÈS UPLOAD
                clear_all_cache()
                
                st.balloons()
                st.success(f"✅ {len(saved_files)} copies sauvegardées avec succès !")
                
                # AFFICHAGE DES FICHIERS SAUVÉS
                for file_path in saved_files:
                    st.write(f"📄 {Path(file_path).name}")
                
                # ACTUALISATION AUTOMATIQUE
                st.success("🔄 Données actualisées automatiquement")
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Erreur lors de la sauvegarde : {str(e)}")


def _show_naming_conventions():
    """Affiche les conventions de nommage"""
    with st.expander("💡 Conventions de nommage recommandées", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **✅ Format recommandé :**
            - `DUPONT_Marie_copie.pdf`
            - `MARTIN_Paul_examen.pdf`
            - `BERNARD_Julie.pdf`
            - `DURAND_Pierre_page1.pdf`
            """)
        
        with col2:
            st.markdown("""
            **❌ À éviter :**
            - `copy1.pdf` (pas d'identification)
            - `Marie Dupont.pdf` (espaces)
            - `dupont.docx` (mauvais format)
            - `DUPONT@marie.pdf` (caractères spéciaux)
            """)
        
