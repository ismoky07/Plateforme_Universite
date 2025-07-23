"""
utils/display_helpers.py - Fonctions d'aide à l'affichage
"""

import streamlit as st

def show_student_submission(eval_info, student_info):
    """Affiche les détails d'une soumission"""
    from utils.student_manager import check_student_submission
    
    submission = check_student_submission(eval_info, student_info)
    
    if submission:
        st.subheader("📋 Détails de votre soumission")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Date :** {submission['date_soumission']}")
            st.write(f"**Type :** {submission['type_soumission']}")
            st.write(f"**Fichiers :** {submission['nombre_fichiers']}")
        
        with col2:
            st.write(f"**Taille :** {submission['taille_totale']}")
            
            if submission.get('reponse_numerique'):
                st.write(f"**Mots :** {submission.get('nombre_mots', 'N/A')}")
        
        if submission.get('fichiers_soumis'):
            st.write("**Fichiers soumis :**")
            for fichier in submission['fichiers_soumis']:
                st.write(f"• {fichier['nom_original']}")

def show_submission_details(submission):
    """Affiche les détails complets d'une soumission"""
    st.write("**Détails de la soumission :**")
    st.json(submission)

def display_header(title):
    """Affiche un en-tête stylisé"""
    st.markdown(f'<div class="main-header"><h1>{title}</h1></div>', unsafe_allow_html=True)