"""
pages/student/login.py - Page connexion étudiant
"""

import streamlit as st
from utils.display_helpers import display_header

def show():
    """Affiche la page connexion étudiant"""
    display_header("🔐 Connexion Étudiant")
    
    st.info("💡 Connectez-vous avec vos identifiants pour accéder à vos résultats de correction.")
    
    with st.form("connexion_etudiant"):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            numero_etudiant = st.text_input("Numéro étudiant", placeholder="Ex: 12345678")
            nom = st.text_input("Nom de famille", placeholder="TAH")
            prenom = st.text_input("Prénom", placeholder="Sarah")
        
        submitted = st.form_submit_button("🔐 Se connecter", type="primary")
        
        if submitted:
            if numero_etudiant and nom and prenom:
                st.session_state.student_logged_in = True
                st.session_state.student_info = {
                    "numero": numero_etudiant,
                    "nom": nom.upper(),
                    "prenom": prenom.capitalize()
                }
                st.success("✅ Connexion réussie !")
                st.rerun()
            else:
                st.error("❌ Veuillez remplir tous les champs")