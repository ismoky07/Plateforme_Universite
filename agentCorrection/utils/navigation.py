"""
utils/navigation.py - Gestion de la navigation
"""

import streamlit as st

def sidebar_navigation():
    """Gère la navigation principale"""
    st.sidebar.markdown("## 🎓 Navigation")
    
    # Sélection du mode
    mode = st.sidebar.selectbox(
        "Choisir le mode",
        ["👨‍🏫 Interface Professeur", "👨‍🎓 Interface Étudiant"],
        key="mode_selection"
    )
    
    st.sidebar.markdown("---")
    
    if mode == "👨‍🏫 Interface Professeur":
        page = st.sidebar.radio(
            "Pages Professeur",
            [
                "📋 Tableau de bord",
                "➕ Créer évaluation",
                "📤 Gérer copies",
                "🤖 Lancer correction",
                "📊 Consulter rapports"
            ]
        )
    else:
        page = st.sidebar.radio(
            "Pages Étudiant",
            [
                "🔐 Connexion",
                "📝 Épreuves disponibles",
                "📤 Soumettre copie",
                "📋 Mes soumissions",
                "📊 Mes résultats",
                "📄 Mes rapports"
            ]
        )
    
    return mode, page