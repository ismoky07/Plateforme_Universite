# app.py - Application principale Streamlit AVEC intégration candidature ET traitement admin OPTIMISÉ + MODULES COMPLETS
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import io
import base64
import json
import os
import streamlit.components.v1 as components
import subprocess
import requests
import sys
from pathlib import Path

# Configuration de la page
st.set_page_config(
    page_title="🎓 Plateforme Universitaire",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé avec corrections de contraste OPTIMISÉ (CONSERVÉ IDENTIQUE)
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    
    .stat-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        color: #1f2937;
    }
    
    .stat-card h2 {
        color: #1f2937 !important;
        font-weight: bold;
    }
    
    .stat-card h3 {
        color: #374151 !important;
        font-weight: 600;
    }
    
    .role-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
        margin: 0.25rem;
    }
    
    .admin-badge { 
        background: #fee2e2; 
        color: #7f1d1d; 
        border: 1px solid #fca5a5;
    }
    
    .professor-badge { 
        background: #dbeafe; 
        color: #1e3a8a; 
        border: 1px solid #93c5fd;
    }
    
    .student-badge { 
        background: #d1fae5; 
        color: #14532d; 
        border: 1px solid #86efac;
    }
    
    .info-container {
        background: #f8fafc;
        color: #1e293b;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        margin: 0.5rem 0;
    }
    
    .warning-container {
        background: #fffbeb;
        color: #92400e;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #fde68a;
        margin: 0.5rem 0;
    }
    
    .success-container {
        background: #f0fdf4;
        color: #166534;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #bbf7d0;
        margin: 0.5rem 0;
    }
    
    .candidature-iframe-container {
        border: 3px solid #667eea;
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        background: white;
        position: relative;
    }
    
    .candidature-iframe-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        text-align: center;
        font-weight: bold;
        position: relative;
    }
    
    /* NOUVEAU : Container spécialisé pour admin */
    .admin-iframe-container {
        border: 3px solid #dc2626;
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 8px 25px rgba(220,38,38,0.15);
        background: white;
        position: relative;
    }
    
    .admin-iframe-header {
        background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%);
        color: white;
        padding: 1rem;
        text-align: center;
        font-weight: bold;
        position: relative;
    }
    
    .iframe-status-indicator {
        position: absolute;
        top: 10px;
        right: 15px;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: #10b981;
        box-shadow: 0 0 10px rgba(16, 185, 129, 0.5);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% {
            transform: scale(0.95);
            box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
        }
        70% {
            transform: scale(1);
            box-shadow: 0 0 0 10px rgba(16, 185, 129, 0);
        }
        100% {
            transform: scale(0.95);
            box-shadow: 0 0 0 0 rgba(16, 185, 129, 0);
        }
    }
    
    .demo-account {
        margin: 1rem 0; 
        padding: 1rem; 
        background: #f8fafc; 
        border-radius: 8px; 
        border: 1px solid #e2e8f0;
    }
    
    .demo-account code {
        background: #e5e7eb; 
        padding: 0.2rem 0.4rem; 
        border-radius: 4px; 
        color: #1f2937;
    }
    
    .stButton > button {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        border: none;
        font-weight: 600;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(45deg, #5a67d8, #6b46c1);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        transform: translateY(-1px);
    }
    
    /* Amélioration des métriques */
    [data-testid="metric-container"] {
        background: white;
        border: 1px solid #e5e7eb;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        transition: transform 0.2s ease;
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# AJOUT DES IMPORTS POUR LES MODULES PROF/ÉTUDIANT + CONFIGURATION EVALUATIONS
# ============================================================================

# Ajout des dossiers au PATH pour les imports - CORRECTION CHEMIN agentCorrection
current_dir = Path(__file__).parent
agent_correction_dir = current_dir / "agentCorrection"
pages_dir = agent_correction_dir / "pages"
utils_dir = agent_correction_dir / "utils"
evaluations_dir = current_dir / "evaluations"

if str(pages_dir) not in sys.path:
    sys.path.append(str(pages_dir))
if str(utils_dir) not in sys.path:
    sys.path.append(str(utils_dir))
if str(agent_correction_dir) not in sys.path:
    sys.path.append(str(agent_correction_dir))

# Configuration du chemin des évaluations
os.environ['EVALUATIONS_PATH'] = str(evaluations_dir)
os.environ['AGENT_CORRECTION_PATH'] = str(agent_correction_dir)

# ============================================================================
# FONCTION POUR RÉCUPÉRER LES ÉVALUATIONS DEPUIS agentCorrection/evaluations/
# ============================================================================

def get_evaluations_from_agent_correction():
    """Récupère les évaluations depuis agentCorrection/evaluations/"""
    evaluations = []
    
    try:
        if not evaluations_dir.exists():
            return evaluations
        
        # Parcourir tous les dossiers d'évaluations
        for eval_folder in evaluations_dir.iterdir():
            if eval_folder.is_dir():
                # Chercher le fichier infos_evaluation.json
                info_file = eval_folder / "infos_evaluation.json"
                if info_file.exists():
                    try:
                        with open(info_file, 'r', encoding='utf-8') as f:
                            eval_data = json.load(f)
                            eval_data['dossier'] = str(eval_folder)
                            evaluations.append(eval_data)
                    except Exception as e:
                        print(f"Erreur lecture {info_file}: {e}")
                        continue
        
        return evaluations
        
    except Exception as e:
        print(f"Erreur get_evaluations_from_agent_correction: {e}")
        return []

# ============================================================================
# CONFIGURATION GLOBALE POUR LES MODULES
# ============================================================================

def configure_modules_paths():
    """Configure les chemins pour les modules professeur et étudiant"""
    try:
        # Importer et configurer data_manager s'il existe
        from agentCorrection.utils import data_manager
        if hasattr(data_manager, 'set_evaluations_path'):
            data_manager.set_evaluations_path(str(evaluations_dir))
        return True
    except ImportError:
        return False

# Appeler la configuration
modules_configured = configure_modules_paths()

# Tentative d'import des modules
try:
    # Important: Importer en premier pour s'assurer que les modules ont accès aux chemins
    
    # Modules étudiants
    from agentCorrection.pages.student import login as student_login
    from agentCorrection.pages.student import available_exams
    from agentCorrection.pages.student import submit_copy
    from agentCorrection.pages.student import my_submissions
    from agentCorrection.pages.student import my_results
    from agentCorrection.pages.student import my_reports
    
    # Modules professeurs
    from agentCorrection.pages.professor import dashboard as professor_dashboard_module
    from agentCorrection.pages.professor import create_evaluation
    from agentCorrection.pages.professor import manage_copies
    from agentCorrection.pages.professor import launch_correction
    from agentCorrection.pages.professor import view_reports
    
    MODULES_AVAILABLE = True
    
    # Vérifier si le dossier évaluations existe
    if evaluations_dir.exists():
        evaluations_found = get_evaluations_from_agent_correction()
       
    else:
        evaluations_dir.mkdir(parents=True, exist_ok=True)    
except ImportError as e:
    MODULES_AVAILABLE = False

# ============================================================================
# DONNÉES DE DÉMONSTRATION (CONSERVÉES IDENTIQUES)
# ============================================================================

@st.cache_data
def load_demo_data():
    return {
        'users': [
            {'id': 1, 'name': 'Marie Dubois', 'email': 'admin@univ.fr', 'role': 'admin', 'password': 'admin123'},
            {'id': 2, 'name': 'Prof. Martin', 'email': 'martin@univ.fr', 'role': 'professor', 'password': 'prof123'},
            {'id': 3, 'name': 'Sarah Étudiant', 'email': 'sarah@univ.fr', 'role': 'student', 'password': 'student123'},
            {'id': 4, 'name': 'Jean Apprenant', 'email': 'jean@univ.fr', 'role': 'student', 'password': 'student123'},
        ],
        'courses': [
            {'id': 1, 'name': 'Histoire Contemporaine', 'code': 'HIST301', 'professor': 'Prof. Martin', 'students': 45, 'credits': 3},
            {'id': 2, 'name': 'Géopolitique Moderne', 'code': 'GEO201', 'professor': 'Prof. Martin', 'students': 28, 'credits': 4},
            {'id': 3, 'name': 'Méthodologie Recherche', 'code': 'METH101', 'professor': 'Prof. Martin', 'students': 15, 'credits': 2},
        ],
        'exams': [
            {
                'id': 1, 'title': 'Partiel Histoire Contemporaine', 'course': 'HIST301', 
                'date': datetime.now() + timedelta(days=7), 'duration': 120, 'status': 'published'
            },
            {
                'id': 2, 'title': 'DS Géopolitique', 'course': 'GEO201', 
                'date': datetime.now() + timedelta(days=14), 'duration': 90, 'status': 'draft'
            },
        ],
        'submissions': [
            {
                'id': 1, 'exam_id': 1, 'student': 'Sarah Étudiant', 'status': 'submitted', 
                'submitted_at': datetime.now() - timedelta(hours=2), 'ai_grade': 15.5, 'final_grade': None
            },
            {
                'id': 2, 'exam_id': 1, 'student': 'Jean Apprenant', 'status': 'graded', 
                'submitted_at': datetime.now() - timedelta(hours=5), 'ai_grade': 12.0, 'final_grade': 12.5
            },
        ]
    }

# Initialisation de la session (CONSERVÉE IDENTIQUE)
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.demo_data = load_demo_data()

# ============================================================================
# FONCTIONS POUR LA CANDIDATURE ET LE TRAITEMENT ADMIN (CONSERVÉES IDENTIQUES)
# ============================================================================

def check_admission_app_status(port=8503):
    """Vérifie si l'application d'admission est en cours d'exécution"""
    try:
        response = requests.get(f"http://localhost:{port}", timeout=3)
        return response.status_code == 200
    except:
        return False

def check_admin_processing_app_status(port=8504):
    """Vérifie si l'application de traitement admin est en cours d'exécution"""
    try:
        response = requests.get(f"http://localhost:{port}", timeout=3)
        return response.status_code == 200
    except:
        return False

def start_admission_app():
    """Lance l'application d'admission en arrière-plan"""
    try:
        admission_form_path = "forms/main.py"
        
        process = subprocess.Popen([
            "streamlit", "run", admission_form_path,
            "--server.port", "8503",
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false"
        ], 
        stdout=subprocess.DEVNULL, 
        stderr=subprocess.DEVNULL)
        
        return process
    except Exception as e:
        st.error(f"❌ Erreur lors du lancement : {e}")
        return None

def start_admin_processing_app():
    """Lance l'application de traitement des demandes d'admissions OPTIMISÉE"""
    try:
        admin_path = "admin/admin_main.py"
        
        if not os.path.exists(admin_path):
            st.error("❌ Fichier admin_main.py introuvable dans le dossier admin/")
            st.info("💡 Vérifiez que le fichier admin/admin_main.py existe")
            
            possible_paths = [
                "admin/admin_main.py",
                "admin/main.py",
                "admin_processing/main.py",
                "admin_main/main.py"
            ]
            
            st.markdown("**Chemins testés :**")
            for path in possible_paths:
                exists = os.path.exists(path)
                status = "✅" if exists else "❌"
                st.write(f"{status} {path}")
            
            return None
        
        process = subprocess.Popen([
            "streamlit", "run", admin_path,
            "--server.port", "8504",
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false"
        ], 
        stdout=subprocess.DEVNULL, 
        stderr=subprocess.DEVNULL)
        
        return process
    except Exception as e:
        st.error(f"❌ Erreur lors du lancement : {e}")
        return None

def get_candidatures_stats():
    """Récupère les VRAIES statistiques des candidatures"""
    try:
        candidatures_paths = [
            "forms/candidatures",
            "admin/candidatures",
            "candidatures"
        ]
        
        for path in candidatures_paths:
            if os.path.exists(path):
                stats = analyze_real_candidatures(path)
                if stats["total"] > 0:
                    return stats
        
        return {
            "total": 0,
            "en_attente": 0,
            "validees": 0,
            "rejetees": 0,
            "path": None
        }
        
    except Exception as e:
        print(f"Erreur dans get_candidatures_stats: {e}")
        return {
            "total": 0,
            "en_attente": 0,
            "validees": 0,
            "rejetees": 0,
            "path": None
        }

def analyze_real_candidatures(candidatures_path):
    """Analyse les vraies candidatures et retourne les statistiques réelles"""
    stats = {
        "total": 0,
        "en_attente": 0,
        "validees": 0,
        "rejetees": 0,
        "en_cours": 0,
        "path": candidatures_path
    }
    
    try:
        candidature_dirs = [d for d in os.listdir(candidatures_path) 
                          if os.path.isdir(os.path.join(candidatures_path, d))]
        
        stats["total"] = len(candidature_dirs)
        
        for candidature_dir in candidature_dirs:
            candidature_path = os.path.join(candidatures_path, candidature_dir)
            json_files = [f for f in os.listdir(candidature_path) if f.endswith('.json')]
            
            if json_files:
                json_file = os.path.join(candidature_path, json_files[0])
                
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        candidature_data = json.load(f)
                    
                    status = get_candidature_status(candidature_data, candidature_path)
                    
                    if status == "validee":
                        stats["validees"] += 1
                    elif status == "rejetee":
                        stats["rejetees"] += 1
                    elif status == "en_cours":
                        stats["en_cours"] += 1
                    else:
                        stats["en_attente"] += 1
                        
                except Exception as e:
                    print(f"Erreur lecture {json_file}: {e}")
                    stats["en_attente"] += 1
            else:
                stats["en_attente"] += 1
        
        return stats
        
    except Exception as e:
        print(f"Erreur dans analyze_real_candidatures: {e}")
        return {
            "total": 0,
            "en_attente": 0,
            "validees": 0,
            "rejetees": 0,
            "en_cours": 0,
            "path": candidatures_path
        }

def get_candidature_status(candidature_data, candidature_path):
    """Détermine le statut d'une candidature"""
    
    if 'status' in candidature_data:
        return candidature_data['status']
    
    try:
        files_in_dir = os.listdir(candidature_path)
        
        if any('validation' in f.lower() for f in files_in_dir):
            return "validee"
        elif any('rejet' in f.lower() for f in files_in_dir):
            return "rejetee"
        elif any('verification' in f.lower() for f in files_in_dir):
            return "en_cours"
    except:
        pass
    
    required_fields = ['nom', 'prenom', 'email', 'niveau_etude']
    has_required = all(field in candidature_data for field in required_fields)
    
    pdf_files = []
    try:
        pdf_files = [f for f in os.listdir(candidature_path) if f.endswith('.pdf')]
    except:
        pass
    
    if has_required and len(pdf_files) > 0:
        return "en_cours"
    else:
        return "en_attente"

def admin_processing_applications_page():
    """Page de traitement avec VRAIES DONNÉES (CONSERVÉE IDENTIQUE)"""
    
    st.markdown('<div class="main-header"><h1>📋 Traitement des Demandes d\'Admissions</h1></div>', unsafe_allow_html=True)
    
    app_running = check_admin_processing_app_status()  
    iframe_height = st.selectbox("Hauteur iframe", [700, 800, 900, 1000], index=1, key="admin_iframe_height")
    
    stats = get_candidatures_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <h3 style="color: #374151 !important; margin-top: 0;">📥 En attente</h3>
            <h2 style="color: #dc2626 !important; margin: 0.5rem 0;">{stats['en_attente']}</h2>
            <p style="color: #dc2626; margin-bottom: 0; font-weight: 600;">Réelles</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <h3 style="color: #374151 !important; margin-top: 0;">🔍 En cours</h3>
            <h2 style="color: #f59e0b !important; margin: 0.5rem 0;">{stats.get('en_cours', 0)}</h2>
            <p style="color: #f59e0b; margin-bottom: 0; font-weight: 600;">Examen</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <h3 style="color: #374151 !important; margin-top: 0;">✅ Validées</h3>
            <h2 style="color: #16a34a !important; margin: 0.5rem 0;">{stats['validees']}</h2>
            <p style="color: #16a34a; margin-bottom: 0; font-weight: 600;">Acceptées</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <h3 style="color: #374151 !important; margin-top: 0;">❌ Refusées</h3>
            <h2 style="color: #6b7280 !important; margin: 0.5rem 0;">{stats['rejetees']}</h2>
            <p style="color: #6b7280; margin-bottom: 0; font-weight: 600;">Rejetées</p>
        </div>
        """, unsafe_allow_html=True)
    
    if stats['total'] > 0:
        with st.expander(f"📋 Détail des {stats['total']} candidature(s)"):
            candidatures_details = get_candidatures_details(stats['path'])
            
            for i, candidature in enumerate(candidatures_details, 1):
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.write(f"**{i}. {candidature.get('nom', 'Inconnu')}**")
                
                with col2:
                    st.write(f"📧 {candidature.get('email', 'N/A')}")
                
                with col3:
                    st.write(f"🎓 {candidature.get('niveau_etude', 'N/A')}")
                
                with col4:
                    status = candidature.get('status', 'en_attente')
                    if status == 'validee':
                        st.success("✅ Validée")
                    elif status == 'rejetee':
                        st.error("❌ Rejetée")
                    elif status == 'en_cours':
                        st.warning("🔍 En cours")
                    else:
                        st.info("⏳ En attente")
    
    st.markdown("---")
    
    if app_running:
        st.markdown("""
        <div class="admin-iframe-container">
            <div class="admin-iframe-header">
                🛠️ Système Administrateur - Traitement & Vérification des Candidatures
                <div class="iframe-status-indicator"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        try:
            components.iframe(
                src="http://localhost:8504",
                width=None,
                height=iframe_height,
                scrolling=True
            )
        except Exception as e:
            st.error(f"❌ Erreur de chargement de l'iframe : {e}")
    else:
        st.markdown("""
        <div class="warning-container" style="text-align: center; padding: 3rem;">
            <h3>🛠️ Système de Traitement en Attente</h3>
            <p style="font-size: 1.1rem; margin: 1.5rem 0;">
                Lancez le système admin pour traiter les {stats['total']} candidature(s) détectée(s).
            </p>
            <code style="background: #1f2937; color: #f9fafb; padding: 0.5rem 1rem; border-radius: 0.25rem;">
                cd admin && streamlit run admin_main.py --server.port 8504
            </code>
        </div>
        """, unsafe_allow_html=True)

def get_candidatures_details(candidatures_path):
    """Récupère les détails de toutes les candidatures"""
    candidatures = []
    
    try:
        candidature_dirs = [d for d in os.listdir(candidatures_path) 
                          if os.path.isdir(os.path.join(candidatures_path, d))]
        
        for candidature_dir in candidature_dirs:
            candidature_path_full = os.path.join(candidatures_path, candidature_dir)
            json_files = [f for f in os.listdir(candidature_path_full) if f.endswith('.json')]
            
            if json_files:
                json_file = os.path.join(candidature_path_full, json_files[0])
                
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        candidature_data = json.load(f)
                    
                    candidature_data['status'] = get_candidature_status(candidature_data, candidature_path_full)
                    candidatures.append(candidature_data)
                    
                except Exception as e:
                    print(f"Erreur lecture {json_file}: {e}")
                    candidatures.append({
                        'nom': candidature_dir,
                        'email': 'Erreur de lecture',
                        'niveau_etude': 'N/A',
                        'status': 'erreur'
                    })
            else:
                candidatures.append({
                    'nom': candidature_dir,
                    'email': 'Fichier manquant',
                    'niveau_etude': 'N/A',
                    'status': 'en_attente'
                })
    
    except Exception as e:
        print(f"Erreur dans get_candidatures_details: {e}")
    
    return candidatures

def admission_candidature_page():
    """Page principale pour le formulaire de candidature avec iframe OPTIMISÉE (CONSERVÉE IDENTIQUE)"""
    
    st.markdown('<div class="main-header"><h1>📝 Formulaire de Candidature</h1></div>', unsafe_allow_html=True)
    
    app_running = check_admission_app_status()
    iframe_height = st.selectbox("Hauteur d'affichage", [700, 800, 900, 1000], index=1, key="student_iframe_height")
    
    st.markdown("---")
    
    if app_running:
        st.markdown("""
        <div class="candidature-iframe-container">
            <div class="candidature-iframe-header">
                📝 Formulaire de Candidature - Saisie des Notes et Bulletins Scolaires
                <div class="iframe-status-indicator"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        try:
            components.iframe(
                src="http://localhost:8503",
                width=None,
                height=iframe_height,
                scrolling=True
            )
        except Exception as e:
            st.error(f"❌ Erreur de chargement de l'iframe : {e}")
            st.markdown("""
            <div class="warning-container">
                <h4>🔧 Accès direct</h4>
                <p>En cas de problème avec l'affichage intégré :</p>
                <p><a href="http://localhost:8503" target="_blank" style="font-weight: bold;">
                    🔗 Ouvrir le formulaire dans une nouvelle fenêtre
                </a></p>
            </div>
            """, unsafe_allow_html=True)
    
    else:
        st.markdown("""
        <div class="warning-container" style="text-align: center; padding: 3rem;">
            <h3>🚀 Formulaire de Candidature</h3>
            <p style="font-size: 1.1rem; margin: 1.5rem 0;">
                Le formulaire doit être lancé séparément pour fonctionner.
            </p>
            
            <div style="background: #f3f4f6; padding: 1.5rem; border-radius: 0.5rem; margin: 1rem 0;">
                <p style="color: #374151; margin-bottom: 1rem;"><strong>Instructions de lancement :</strong></p>
                <code style="background: #1f2937; color: #f9fafb; padding: 0.5rem 1rem; border-radius: 0.25rem; display: block;">
                    cd forms<br>
                    streamlit run main.py --server.port 8503
                </code>
            </div>
            
            <p style="color: #6b7280; font-size: 0.9rem;">
                Une fois lancé, le formulaire s'affichera automatiquement dans cette page.
            </p>
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# PAGE DE CONNEXION (CONSERVÉE IDENTIQUE)
# ============================================================================

def login_page():
    """Page de connexion"""
    st.markdown('<div class="main-header"><h1>🎓 Plateforme Universitaire - Connexion</h1></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔐 Connexion")
        
        with st.form("login_form"):
            email = st.text_input("📧 Email", placeholder="Entrez votre email")
            password = st.text_input("🔒 Mot de passe", type="password", placeholder="Entrez votre mot de passe")
            submitted = st.form_submit_button("Se connecter", use_container_width=True)
            
            if submitted:
                users = st.session_state.demo_data['users']
                user = next((u for u in users if u['email'] == email and u['password'] == password), None)
                
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("❌ Email ou mot de passe incorrect")
        
        st.markdown("---")
        st.markdown("### 🧪 Comptes de démonstration")
        
        demo_accounts = [
            {"role": "👨‍💼 Administrateur", "email": "admin@univ.fr", "password": "admin123", "badge": "admin-badge"},
            {"role": "👨‍🏫 Professeur", "email": "martin@univ.fr", "password": "prof123", "badge": "professor-badge"},
            {"role": "🎓 Étudiant", "email": "sarah@univ.fr", "password": "student123", "badge": "student-badge"},
        ]
        
        for account in demo_accounts:
            st.markdown(f"""
            <div class="demo-account">
                <div class="role-badge {account['badge']}">{account['role']}</div>
                <p style="color: #1e293b; margin: 0.5rem 0 0 0;">
                    <strong>Email:</strong> <code>{account['email']}</code> | 
                    <strong>Mot de passe:</strong> <code>{account['password']}</code>
                </p>
            </div>
            """, unsafe_allow_html=True)

# ============================================================================
# DASHBOARD ADMIN (ENRICHI AVEC VRAIS STATS)
# ============================================================================

def admin_dashboard():
    """Dashboard administrateur ENRICHI avec vraies données des évaluations"""
    st.markdown('<div class="main-header"><h1>🏛️ Administration Universitaire</h1></div>', unsafe_allow_html=True)
    
    # Récupérer les vraies statistiques
    stats = get_candidatures_stats()
    evaluations = get_evaluations_from_agent_correction()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="stat-card">
            <h3 style="color: #374151 !important; margin-top: 0;">👥 Étudiants</h3>
            <h2 style="color: #1f2937 !important; margin: 0.5rem 0;">2,847</h2>
            <p style="color: #16a34a; margin-bottom: 0; font-weight: 600;">+5% ce mois</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-card">
            <h3 style="color: #374151 !important; margin-top: 0;">👨‍🏫 Professeurs</h3>
            <h2 style="color: #1f2937 !important; margin: 0.5rem 0;">89</h2>
            <p style="color: #16a34a; margin-bottom: 0; font-weight: 600;">+2% ce mois</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <h3 style="color: #374151 !important; margin-top: 0;">📚 Évaluations</h3>
            <h2 style="color: #1f2937 !important; margin: 0.5rem 0;">{len(evaluations)}</h2>
            <p style="color: #2563eb; margin-bottom: 0; font-weight: 600;">Réelles trouvées</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <h3 style="color: #374151 !important; margin-top: 0;">📝 Candidatures</h3>
            <h2 style="color: #1f2937 !important; margin: 0.5rem 0;">{stats['total']}</h2>
            <p style="color: #7c3aed; margin-bottom: 0; font-weight: 600;">Réelles détectées</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Graphiques avec vraies données
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Évaluations par matière")
        if evaluations:
            # Compter les évaluations par matière
            matieres = {}
            for eval_data in evaluations:
                matiere = eval_data.get('matiere', 'Autre')
                matieres[matiere] = matieres.get(matiere, 0) + 1
            
            fig = px.bar(x=list(matieres.keys()), y=list(matieres.values()), 
                        title="Nombre d'évaluations par matière")
            fig.update_traces(marker_color='#667eea')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aucune évaluation trouvée dans agentCorrection/evaluations/")
    
    with col2:
        st.subheader("📝 État des candidatures")
        if stats['total'] > 0:
            labels = ['En attente', 'Validées', 'Rejetées', 'En cours']
            values = [stats['en_attente'], stats['validees'], stats['rejetees'], stats.get('en_cours', 0)]
            
            fig = px.pie(values=values, names=labels, title="Répartition des candidatures")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aucune candidature détectée")
    
    # Liste des évaluations récentes
    if evaluations:
        st.markdown("---")
        st.subheader("📚 Évaluations Récentes")
        
        # Trier par date de création
        evaluations_sorted = sorted(evaluations, 
                                   key=lambda x: x.get('created_at', ''), 
                                   reverse=True)[:5]
        
        for eval_data in evaluations_sorted:
            with st.expander(f"📝 {eval_data.get('titre', 'Sans titre')} - {eval_data.get('matiere', 'N/A')}", expanded=False):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Date :** {eval_data.get('date', 'N/A')}")
                    st.write(f"**Professeur :** {eval_data.get('professeur', 'N/A')}")
                
                with col2:
                    st.write(f"**Durée :** {eval_data.get('duree', 'N/A')}")
                    st.write(f"**Note totale :** {eval_data.get('note_totale', 'N/A')}")
                
                with col3:
                    st.write(f"**Statut :** {eval_data.get('statut', 'N/A')}")
                    
                    # Compter les copies s'il y en a
                    eval_path = Path(eval_data['dossier'])
                    copies_dir = eval_path / "copies_soumises"
                    nb_copies = len(list(copies_dir.glob("*.pdf"))) if copies_dir.exists() else 0
                    st.write(f"**Copies :** {nb_copies}")
    
    # Modules principaux ENRICHIS
    st.markdown("---")
    st.subheader("🎯 Modules Principaux")
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.expander("📝 Gestion des Admissions", expanded=True):
            st.metric("Candidatures en attente", str(stats['en_attente']))
            st.metric("Candidatures validées", str(stats['validees']))
            st.metric("Candidatures rejetées", str(stats['rejetees']))
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("🔗 Traitement", key="admissions_process", use_container_width=True):
                    st.session_state.redirect_to_processing = True
                    st.rerun()
            with col_btn2:
                if st.button("📊 Statistiques", key="admissions_stats", use_container_width=True):
                    st.info("🔗 Statistiques détaillées des admissions")
    
    with col2:
        with st.expander("📚 Système d'Évaluations", expanded=True):
            st.metric("Évaluations créées", str(len(evaluations)))
            
            # Compter les évaluations ouvertes/fermées
            ouvertes = len([e for e in evaluations if e.get('statut') == 'ouverte'])
            fermees = len([e for e in evaluations if e.get('statut') in ['fermee', 'expiree']])
            
            st.metric("Évaluations ouvertes", str(ouvertes))
            st.metric("Évaluations fermées", str(fermees))
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("📊 Voir détails", key="eval_details", use_container_width=True):
                    st.info("📊 Détails des évaluations disponibles ci-dessus")
            with col_btn2:
                if st.button("🔄 Actualiser", key="refresh_evals", use_container_width=True):
                    st.rerun()

# Redirection automatique si demandée
if st.session_state.get('redirect_to_processing', False):
    st.session_state.redirect_to_processing = False
    st.session_state.selected_page = "📋 Traitement Admissions"

# ============================================================================
# DASHBOARD PROFESSEUR - APPEL SIMPLE DU MODULE EXISTANT
# ============================================================================

def professor_dashboard():
    """Dashboard professeur - Appel direct du module existant"""
    professor_dashboard_module.show()

# ============================================================================
# DASHBOARD ÉTUDIANT - APPEL SIMPLE DES MODULES EXISTANTS
# ============================================================================

def student_dashboard():
    """Dashboard étudiant - Navigation vers les modules existants"""
    
    if not MODULES_AVAILABLE:
        st.error("❌ Modules étudiant non disponibles")
        st.info("💡 Vérifiez que agentCorrection/pages/student/ existe")
        return
    
    # Vérifier si l'étudiant est connecté
    if not st.session_state.get('student_logged_in', False):
        student_login.show()
        return
    
    # Navigation entre les modules étudiant
    st.sidebar.markdown("---")
    st.sidebar.markdown("**🎓 Navigation Étudiant**")
    
    student_pages = {
        "📝 Épreuves Disponibles": "available_exams",
        "📤 Soumettre Copie": "submit_copy", 
        "📋 Mes Soumissions": "my_submissions",
        "📊 Mes Résultats": "my_results",
        "📄 Mes Rapports": "my_reports"
    }
    
    # Sélection de la page étudiant
    selected_student_page = st.sidebar.radio(
        "Pages étudiant", 
        list(student_pages.keys()),
        key="student_nav"
    )
    
    # Appeler le bon module selon la sélection
    page_module = student_pages[selected_student_page]
    
    if page_module == "available_exams":
        available_exams.show()
    elif page_module == "submit_copy":
        submit_copy.show()
    elif page_module == "my_submissions":
        my_submissions.show()
    elif page_module == "my_results":
        my_results.show()
    elif page_module == "my_reports":
        my_reports.show()

# ============================================================================
# INTERFACE CHATBOT (CONSERVÉE IDENTIQUE)
# ============================================================================

def chatbot_interface():
    """Interface du chatbot IA"""
    st.markdown('<div class="main-header"><h1>🤖 Assistant Universitaire IA</h1></div>', unsafe_allow_html=True)
    
    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "👋 Bonjour ! Je suis votre assistant IA. Comment puis-je vous aider aujourd'hui ?"}
        ]
    
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div style="background: #eff6ff; padding: 1rem; margin: 0.5rem 0; 
                        border-radius: 10px; margin-left: 2rem; border: 1px solid #bfdbfe;">
                <strong style="color: #1e40af;">Vous:</strong> 
                <span style="color: #1e293b;">{message["content"]}</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background: #faf5ff; padding: 1rem; margin: 0.5rem 0; 
                        border-radius: 10px; margin-right: 2rem; border: 1px solid #d8b4fe;">
                <strong style="color: #7c2d12;">🤖 Assistant:</strong> 
                <span style="color: #1e293b;">{message["content"]}</span>
            </div>
            """, unsafe_allow_html=True)
    
    user_input = st.text_input("💬 Votre message:", placeholder="Tapez votre question...")
    
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.messages.append({"role": "assistant", "content": "🤔 Excellente question ! Laissez-moi vous aider..."})
        st.rerun()

# ============================================================================
# FONCTION MAIN OPTIMISÉE FINALE (STRUCTURE CONSERVÉE)
# ============================================================================

def main():
    """Application principale optimisée avec candidature et traitement admin intégrés + MODULES COMPLETS"""
    
    if not st.session_state.logged_in:
        login_page()
        return
    
    with st.sidebar:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 1rem; border-radius: 10px; color: white; margin-bottom: 1rem;
                    text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">
            <h3>👋 {st.session_state.user['name']}</h3>
            <p>{st.session_state.user['role'].title()}</p>
        </div>
        """, unsafe_allow_html=True)
        
        
        # Menu de navigation ENRICHI selon le rôle
        if st.session_state.user['role'] == 'admin':
            pages = {
                "🏛️ Dashboard Admin": "admin",
                "📋 Traitement Admissions": "admin_processing",
                "🤖 Assistant IA": "chatbot",
                "📊 Statistiques": "stats"
            }
        elif st.session_state.user['role'] == 'professor':
            if MODULES_AVAILABLE:
                pages = {
                    "📋 Tableau de Bord": "dashboard",
                    "➕ Créer Évaluation": "create_evaluation",
                    "📤 Gérer Copies": "manage_copies", 
                    "🤖 Lancer Correction": "launch_correction",
                    "📊 Consulter Rapports": "view_reports",
                    "💬 Assistant IA": "chatbot"
                }
            else:
                pages = {
                    "📋 Dashboard Prof": "professor",
                    "💬 Assistant IA": "chatbot"
                }
        else:  # student
            if MODULES_AVAILABLE:
                pages = {
                    "🎓 Mon Espace": "student_dashboard",
                    "📝 Candidature": "candidature",
                    "💬 Assistant IA": "chatbot"
                }
            else:
                pages = {
                    "📋 Dashboard Étudiant": "student",
                    "📝 Candidature": "candidature",
                    "💬 Assistant IA": "chatbot"
                }
        
        selected_page = st.radio("Navigation", list(pages.keys()))
        page_key = pages[selected_page]
        
        st.markdown("---")
        
        if st.button("🚪 Déconnexion"):
            st.session_state.logged_in = False
            st.session_state.user = None
            # Nettoyer les états des sous-modules
            if 'student_logged_in' in st.session_state:
                del st.session_state.student_logged_in
            if 'selected_student_page' in st.session_state:
                del st.session_state.selected_student_page
            st.rerun()
    
    # Affichage de la page sélectionnée avec gestion d'erreurs
    try:
        if page_key == "admin":
            admin_dashboard()
        elif page_key == "admin_processing":
            admin_processing_applications_page()
        elif page_key == "dashboard":
            professor_dashboard_module.show()  # Appel direct du module dashboard
        elif page_key == "create_evaluation":
            create_evaluation.show()           # Appel direct du module
        elif page_key == "manage_copies":
            manage_copies.show()               # Appel direct du module
        elif page_key == "launch_correction":
            launch_correction.show()           # Appel direct du module
        elif page_key == "view_reports":
            view_reports.show()                # Appel direct du module
        elif page_key == "professor":
            professor_dashboard()              # Fallback
        elif page_key == "student_dashboard":
            student_dashboard()                # Navigation étudiant
        elif page_key == "student":
            student_dashboard()                # Fallback
        elif page_key == "candidature":
            admission_candidature_page()
        elif page_key == "chatbot":
            chatbot_interface()
        elif page_key == "stats":
            admin_dashboard()
        else:
            st.error(f"❌ Page non trouvée : {page_key}")
    
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement de la page : {str(e)}")
        st.info("💡 Vérifiez que agentCorrection/pages/ et agentCorrection/utils/ contiennent tous les modules nécessaires")
        
        # Informations de débogage
        if st.checkbox("🔍 Afficher détails erreur"):
            st.code(f"Erreur: {e}")
            st.code(f"Page demandée: {page_key}")
            st.code(f"Modules disponibles: {MODULES_AVAILABLE}")
            st.info("💡 Structure attendue : agentCorrection/pages/ et agentCorrection/utils/")

if __name__ == "__main__":
    main()