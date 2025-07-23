"""
main.py - Interface principale corrigée sans imports circulaires
"""

import streamlit as st
from config.settings import configure_page
from utils.navigation import sidebar_navigation

def main():
    """Interface principale Streamlit"""
    configure_page()
    
    # Gestion de la redirection de page
    if 'page_redirect' in st.session_state:
        page_target = st.session_state.page_redirect
        del st.session_state.page_redirect
        st.session_state.force_page = page_target
    
    # Navigation
    mode, page = sidebar_navigation()
    
    # Forcer une page spécifique si nécessaire
    if 'force_page' in st.session_state:
        page = st.session_state.force_page
        del st.session_state.force_page
    
    # IMPORTS DYNAMIQUES - Évite les imports circulaires
    if mode == "👨‍🏫 Interface Professeur":
        if page == "📋 Tableau de bord":
            from pages.professor.dashboard import show
            show()
        elif page == "➕ Créer évaluation":
            from pages.professor.create_evaluation import show
            show()
        elif page == "📤 Gérer copies":
            from pages.professor.manage_copies import show
            show()
        elif page == "🤖 Lancer correction":
            from pages.professor.launch_correction import show
            show()
        elif page == "📊 Consulter rapports":
            from pages.professor.view_reports import show
            show()
    
    else:  # Interface Étudiant
        if page == "🔐 Connexion":
            from pages.student.login import show
            show()
        elif page == "📝 Épreuves disponibles":
            from pages.student.available_exams import show
            show()
        elif page == "📤 Soumettre copie":
            from pages.student.submit_copy import show
            show()
        elif page == "📋 Mes soumissions":
            from pages.student.my_submissions import show
            show()
        elif page == "📊 Mes résultats":
            from pages.student.my_results import show
            show()
        elif page == "📄 Mes rapports":
            from pages.student.my_reports import show
            show()

if __name__ == "__main__":
    main()