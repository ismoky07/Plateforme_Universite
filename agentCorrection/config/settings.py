"""
config/settings.py - Configuration de l'application
"""

import streamlit as st
from pathlib import Path

def configure_page():
    """Configuration de la page Streamlit"""
    st.set_page_config(
        page_title="🎓 Système de Correction Automatique",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS personnalisé
    st.markdown("""
    <style>
        .main-header {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
        }
        .metric-card {
            background: white;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }
        .success-box {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
        }
        .warning-box {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
        }
        .error-box {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
        }
    </style>
    """, unsafe_allow_html=True)

class Config:
    """Configuration de l'application"""
    BASE_DIR = Path(__file__).parent.parent
    EVALUATIONS_DIR = BASE_DIR / "evaluations"
    TEMP_DIR = BASE_DIR / "temp"
    
    # Créer les dossiers nécessaires
    EVALUATIONS_DIR.mkdir(exist_ok=True)
    TEMP_DIR.mkdir(exist_ok=True)
