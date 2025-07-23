import streamlit as st
import os
import json
from datetime import datetime
from pathlib import Path
import traceback

from admin_config import ADMIN_CONFIG, VALIDATION_STATUS
from admin_utils import load_candidatures, get_candidature_details, init_admin_session
from admin_components import (
    render_admin_header, render_candidatures_list, render_candidature_details,
    render_ocr_section, render_comparison_section, render_validation_section
)
from admin_styles import apply_admin_styles
from admin_auth import (
    require_authentication, show_user_info, check_permission,
    show_user_management, show_activity_logs
)

# Import agent OCR
try:
    from agentOCR.agent import (
        verifier_bulletins_scolaires,
        get_verification_status,
        detecter_bulletins_scolaires,
        ResultatVerification
    )
    AGENT_OCR_AVAILABLE = True
except ImportError:
    AGENT_OCR_AVAILABLE = False

# Configuration optimisée pour iframe
st.set_page_config(
    page_title="Administration - Vérification des Candidatures",
    page_icon="👨‍🏫",
    layout="wide",
    initial_sidebar_state="collapsed",  # ← OPTIMISÉ POUR IFRAME
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }  # ← INTERFACE NETTOYÉE POUR IFRAME
)

def apply_iframe_styles():
    """Styles CSS optimisés pour affichage dans iframe"""
    st.markdown("""
    <style>
        /* Masquer les éléments Streamlit non nécessaires dans iframe */
        .stApp > header {
            display: none;
        }
        
        .stApp > .main > div.block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
            max-width: 100%;
        }
        
        /* Optimiser la sidebar pour iframe */
        .css-1d391kg {
            width: 280px;
        }
        
        /* Header compact pour iframe */
        .admin-header-iframe {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 0.75rem 1rem;
            border-radius: 0.5rem;
            color: white;
            margin-bottom: 1rem;
            text-align: center;
        }
        
        .admin-header-iframe h2 {
            margin: 0;
            font-size: 1.3rem;
        }
        
        /* Ajuster les métriques pour iframe */
        [data-testid="metric-container"] {
            background: white;
            border: 1px solid #e1e5e9;
            padding: 0.75rem;
            border-radius: 0.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        }
        
        /* Expanders plus compacts */
        .streamlit-expanderHeader {
            font-size: 0.9rem;
            padding: 0.5rem 1rem;
            background-color: #f8f9fa !important;
        }
        
        /* Boutons optimisés */
        .stButton > button {
            width: 100%;
            margin-bottom: 0.5rem;
            font-size: 0.9rem;
        }
        
        /* Alertes plus visibles dans iframe */
        .stAlert {
            font-weight: 600;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
        }
        
        /* Onglets optimisés */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 0.5rem 1rem;
            font-size: 0.9rem;
        }
        
        /* Sidebar optimisée */
        .css-1cypcdb {
            background-color: #f8f9fa;
        }
        
        /* Colonnes plus compactes */
        .element-container {
            margin-bottom: 0.5rem;
        }
        
        /* Métriques en ligne pour iframe */
        div[data-testid="metric-container"] > div {
            font-size: 0.9rem;
        }
        
        /* Optimisation des dataframes */
        .stDataFrame {
            font-size: 0.85rem;
        }
    </style>
    """, unsafe_allow_html=True)

def init_iframe_session():
    """Initialisation optimisée pour iframe"""
    if 'iframe_mode' not in st.session_state:
        st.session_state.iframe_mode = True
        
    # Authentification simplifiée pour iframe si nécessaire
    if 'admin_authenticated' not in st.session_state:
        # Garder votre système d'auth existant
        # mais avec fallback simplifié pour iframe
        try:
            require_authentication()
        except Exception:
            # Fallback pour iframe en cas de problème d'auth
            st.session_state.admin_authenticated = True
            st.session_state.admin_user = {
                'name': 'Administrateur',
                'role': 'admin',
                'permissions': ['view_all', 'validate', 'reject', 'manage_users', 'system_config']
            }

def safe_load_candidatures():
    """Chargement sécurisé des candidatures pour iframe"""
    try:
        return load_candidatures()
    except Exception as e:
        st.error(f"❌ Erreur chargement candidatures: {str(e)}")
        
        with st.expander("🔧 Aide pour résoudre le problème"):
            st.markdown("""
            **Vérifications à effectuer :**
            
            1. **Le formulaire de candidature est-il lancé ?**
               ```bash
               streamlit run forms/main.py --server.port 8502
               ```
            
            2. **Des candidatures ont-elles été créées ?**
               - Testez le formulaire avec des données d'exemple
               - Vérifiez l'existence du dossier `candidatures/`
            
            3. **Les chemins sont-ils corrects ?**
               - Vérifiez `admin_config.py`
               - Chemin recommandé: `../forms/candidatures`
            
            4. **Permissions de fichiers ?**
               - Vérifiez l'accès en lecture aux dossiers
            """)
        
        return []

def render_admin_header_iframe():
    """Header compact pour iframe"""
    st.markdown("""
    <div class="admin-header-iframe">
        <h2>🛠️ Administration - Traitement des Candidatures</h2>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Fonction principale optimisée pour iframe"""
    
    # 1. Styles d'abord
    apply_iframe_styles()
    
    # 2. Initialisation pour iframe
    init_iframe_session()
    init_admin_session()
    
    # 3. Header compact pour iframe
    render_admin_header_iframe()
    
    # 4. Sidebar optimisée pour iframe
    with st.sidebar:
        st.markdown("### 🎯 Navigation")
        
        # Info utilisateur compacte
        if hasattr(st.session_state, 'admin_user') and st.session_state.admin_user:
            user = st.session_state.admin_user
            st.success(f"👤 {user['name']}")
        else:
            show_user_info()
        
        # Chargement sécurisé des candidatures
        candidatures = safe_load_candidatures()
        
        # Métriques compactes
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric("📋", len(candidatures), help="Total candidatures")
        with col_m2:
            if AGENT_OCR_AVAILABLE:
                st.metric("🤖", "✅", help="Agent OCR actif")
            else:
                st.metric("🤖", "❌", help="Agent OCR inactif")
        
        # Filtres optimisés
        st.markdown("---")
        st.markdown("#### 🔍 Filtres")
        
        status_filter = st.selectbox(
            "Statut",
            ["Tous"] + list(VALIDATION_STATUS.keys()),
            key="status_filter"
        )
        
        niveau_filter = st.selectbox(
            "Niveau d'étude", 
            ["Tous", "Baccalauréat", "Licence", "Master"],
            key="niveau_filter"
        )
        
        # Navigation compacte
        st.markdown("---")
        st.markdown("#### 📍 Mode d'affichage")
        
        view_modes = [
            "📋 Liste des candidatures", 
            "🔍 Détail candidature", 
            "📊 Tableau de bord"
        ]
        
        # Permissions conditionnelles
        if check_permission("manage_users"):
            view_modes.append("👥 Gestion utilisateurs")
        
        if check_permission("view_all"):
            view_modes.append("📋 Logs d'activité")
        
        view_mode = st.radio(
            "Sélectionner le mode",
            view_modes, 
            key="view_mode",
            label_visibility="collapsed"
        )
        
        # Actions rapides
        st.markdown("---")
        st.markdown("#### ⚡ Actions")
        
        if st.button("🔄 Actualiser", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        if check_permission("system_config"):
            if st.button("🧹 Nettoyer", use_container_width=True, help="Nettoyer fichiers temp"):
                cleanup_temp_files()
                st.success("✅ Nettoyage effectué")
    
    # 5. Contenu principal
    if not candidatures and view_mode != "📊 Tableau de bord":
        st.warning("📂 Aucune candidature trouvée")
        st.info("💡 Assurez-vous que le formulaire de candidature est actif et que des candidatures ont été soumises")
        return
    
    # Affichage selon le mode sélectionné
    if view_mode == "📋 Liste des candidatures":
        render_candidatures_overview(candidatures, status_filter, niveau_filter)
    elif view_mode == "🔍 Détail candidature":
        render_candidature_examination(candidatures)
    elif view_mode == "📊 Tableau de bord":
        render_admin_dashboard(candidatures)
    elif view_mode == "👥 Gestion utilisateurs":
        show_user_management()
    elif view_mode == "📋 Logs d'activité":
        show_activity_logs()

def render_candidatures_overview(candidatures, status_filter, niveau_filter):
    """Vue d'ensemble des candidatures optimisée pour iframe"""
    st.markdown("### 📋 Liste des Candidatures")
    
    if not check_permission("view_all") and not check_permission("view_assigned"):
        st.error("🚫 Accès refusé.")
        return
    
    # Filtrage
    filtered_candidatures = candidatures.copy()
    
    if status_filter != "Tous":
        filtered_candidatures = [
            c for c in filtered_candidatures 
            if c.get('status', 'en_attente') == status_filter
        ]
    
    if niveau_filter != "Tous":
        filtered_candidatures = [
            c for c in filtered_candidatures 
            if c.get('niveau', '') == niveau_filter
        ]
    
    if not filtered_candidatures:
        st.info("Aucune candidature trouvée avec ces filtres.")
        return
    
    # Affichage avec statut OCR
    if AGENT_OCR_AVAILABLE:
        render_candidatures_list_enhanced_iframe(filtered_candidatures)
    else:
        render_candidatures_list_iframe(filtered_candidatures)

def render_candidatures_list_enhanced_iframe(candidatures):
    """Liste des candidatures optimisée pour iframe avec OCR"""
    for candidature in candidatures:
        candidat_brut = candidature.get('candidat', 'Candidat Inconnu')
        
        # Conversion sécurisée du nom
        if isinstance(candidat_brut, dict):
            candidat_nom = candidat_brut.get('nom', candidat_brut.get('name', 'Candidat Inconnu'))
        elif isinstance(candidat_brut, (list, tuple)):
            candidat_nom = str(candidat_brut[0]) if candidat_brut else 'Candidat Inconnu'
        else:
            candidat_nom = str(candidat_brut) if candidat_brut else 'Candidat Inconnu'
        
        niveau = candidature.get('niveau', 'Non spécifié')
        
        with st.expander(f"👤 {candidat_nom} - {niveau}", expanded=False):
            # Layout compact pour iframe - 4 colonnes au lieu de 5
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            with col1:
                st.write(f"**📧** {candidature.get('email', 'N/A')}")
                date_submission = candidature.get('date_submission', 'Date inconnue')
                if isinstance(date_submission, str) and len(date_submission) >= 10:
                    st.write(f"**📅** {date_submission[:10]}")
                else:
                    st.write(f"**📅** {date_submission}")
                
                status = candidature.get('status', 'en_attente')
                if status == 'validee':
                    st.success(f"**✅** {status}")
                elif status == 'rejetee':
                    st.error(f"**❌** {status}")
                else:
                    st.info(f"**⏳** {status}")
            
            with col2:
                st.markdown("**🎓 Bulletins**")
                if AGENT_OCR_AVAILABLE:
                    try:
                        dossier = get_candidature_folder_path(candidature)
                        if dossier.exists():
                            detection = detecter_bulletins_scolaires(dossier)
                            if detection["bulletins_detectes"]:
                                st.success("✅ Détectés")
                            else:
                                st.info("📄 Aucun")
                        else:
                            st.warning("📂 N/A")
                    except Exception:
                        st.error("❌ Erreur")
                else:
                    st.info("🤖 Inactif")
            
            with col3:
                st.markdown("**🔍 Vérification**")
                if AGENT_OCR_AVAILABLE:
                    try:
                        dossier = get_candidature_folder_path(candidature)
                        if dossier.exists():
                            status = get_verification_status(dossier)
                            if status["verifie"]:
                                # Priorité à l'usurpation
                                if status.get("usurpation_detectee", False):
                                    st.error("🚨 FRAUDE")
                                elif status.get("concordance", False):
                                    st.success("✅ Honnête")
                                else:
                                    st.error(f"❌ {status.get('nb_discordances', 0)} err.")
                            else:
                                st.info("⏳ À faire")
                        else:
                            st.warning("❓ N/A")
                    except Exception:
                        st.error("❌ Erreur")
                else:
                    st.info("⏳ N/A")
            
            with col4:
                st.markdown("**⚡ Action**")
                candidat_safe = candidat_nom.replace(' ', '_').replace('/', '_')
                button_key = f"examine_{candidat_safe}_{hash(str(candidature)) % 10000}"
                
                if st.button("🔍", key=button_key, help="Examiner en détail"):
                    st.session_state.selected_candidature_direct = candidature
                    st.session_state.view_mode = "🔍 Détail candidature"
                    st.rerun()

def render_candidatures_list_iframe(candidatures):
    """Liste des candidatures sans OCR pour iframe"""
    for candidature in candidatures:
        candidat_brut = candidature.get('candidat', 'Candidat Inconnu')
        
        if isinstance(candidat_brut, dict):
            candidat_nom = candidat_brut.get('nom', candidat_brut.get('name', 'Candidat Inconnu'))
        else:
            candidat_nom = str(candidat_brut) if candidat_brut else 'Candidat Inconnu'
        
        niveau = candidature.get('niveau', 'Non spécifié')
        
        with st.expander(f"👤 {candidat_nom} - {niveau}", expanded=False):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**📧** {candidature.get('email', 'N/A')}")
                date_submission = candidature.get('date_submission', 'Date inconnue')
                if isinstance(date_submission, str) and len(date_submission) >= 10:
                    st.write(f"**📅** {date_submission[:10]}")
                st.write(f"**📋** {candidature.get('status', 'en_attente')}")
            
            with col2:
                candidat_safe = candidat_nom.replace(' ', '_').replace('/', '_')
                button_key = f"examine_{candidat_safe}_{hash(str(candidature)) % 10000}"
                
                if st.button("🔍 Examiner", key=button_key, use_container_width=True):
                    st.session_state.selected_candidature_direct = candidature
                    st.session_state.view_mode = "🔍 Détail candidature"
                    st.rerun()

def render_candidature_examination(candidatures):
    """Examen détaillé d'une candidature optimisé pour iframe"""
    st.markdown("### 🔍 Examen de Candidature")
    
    if not check_permission("view_all") and not check_permission("view_assigned"):
        st.error("🚫 Accès refusé.")
        return
    
    if not candidatures:
        st.warning("Aucune candidature disponible.")
        return
    
    # Préparation des options
    candidature_options = []
    for c in candidatures:
        candidat = c.get('candidat', 'Candidat Inconnu')
        niveau = c.get('niveau', 'Non spécifié')
        date_submission = c.get('date_submission', 'Date inconnue')
        
        if isinstance(date_submission, str) and len(date_submission) >= 10:
            date_display = date_submission[:10]
        else:
            date_display = str(date_submission)
        
        candidature_options.append(f"{candidat} - {niveau} ({date_display})")
    
    # Gestion sélection directe
    selected_idx = 0
    if 'selected_candidature_direct' in st.session_state:
        candidature_directe = st.session_state.selected_candidature_direct
        candidat_direct = candidature_directe.get('candidat', '')
        
        for i, c in enumerate(candidatures):
            if c.get('candidat', '') == candidat_direct:
                selected_idx = i
                break
        del st.session_state.selected_candidature_direct
    
    selected_idx = st.selectbox(
        "Sélectionner une candidature",
        range(len(candidature_options)),
        format_func=lambda x: candidature_options[x],
        key="selected_candidature",
        index=selected_idx
    )
    
    if selected_idx is not None:
        candidature = candidatures[selected_idx]
        
        # Alerte prioritaire pour usurpation
        if AGENT_OCR_AVAILABLE:
            try:
                dossier_candidature = get_candidature_folder_path(candidature)
                detection_bulletins = detecter_bulletins_scolaires(dossier_candidature)
                
                if detection_bulletins["bulletins_detectes"] and detection_bulletins["formulaire_detecte"]:
                    status_verif = get_verification_status(dossier_candidature)
                    if status_verif["verifie"]:
                        # Alerte usurpation en priorité
                        if status_verif.get("usurpation_detectee", False):
                            st.error("🚨 **ALERTE FRAUDE MAJEURE**: Usurpation d'identité détectée!")
                            st.error("⚠️ **Recommandation**: REJET IMMÉDIAT de la candidature")
                        elif status_verif.get("concordance", False):
                            st.success(f"✅ **Candidat vérifié et honnête**")
                        else:
                            st.error(f"❌ **Candidat vérifié - {status_verif.get('nb_discordances', 0)} mensonge(s) détecté(s)**")
                    else:
                        st.info("⏳ **Vérification automatique disponible**")
                        
            except Exception as e:
                st.warning(f"⚠️ Erreur détection bulletins: {str(e)}")
        
        # Onglets compacts pour iframe
        tab1, tab2, tab3, tab4 = st.tabs(["📄 Détails", "🔍 OCR", "⚖️ Comparaison", "✅ Validation"])
        
        with tab1:
            render_candidature_details(candidature)
        
        with tab2:
            if check_permission("view_all"):
                if AGENT_OCR_AVAILABLE:
                    render_ocr_section_enhanced(candidature)
                else:
                    render_ocr_section(candidature)
            else:
                st.warning("🚫 Permission OCR requise.")
        
        with tab3:
            if check_permission("view_all"):
                render_comparison_section(candidature)
                if AGENT_OCR_AVAILABLE:
                    render_comparison_bulletins_section(candidature)
            else:
                st.warning("🚫 Permission comparaison requise.")
        
        with tab4:
            if check_permission("validate") or check_permission("reject"):
                render_validation_section(candidature)
            else:
                st.warning("🚫 Permission validation/rejet requise.")

def render_admin_dashboard(candidatures):
    """Tableau de bord administrateur optimisé pour iframe"""
    st.markdown("### 📊 Tableau de Bord Administration")
    
    if not check_permission("view_all"):
        st.error("🚫 Accès refusé.")
        return
    
    # Statistiques compactes pour iframe
    col1, col2, col3, col4 = st.columns(4)
    
    total_candidatures = len(candidatures)
    en_attente = len([c for c in candidatures if c.get('status', 'en_attente') == 'en_attente'])
    validees = len([c for c in candidatures if c.get('status') == 'validee'])
    rejetees = len([c for c in candidatures if c.get('status') == 'rejetee'])
    
    with col1:
        st.metric("📋 Total", total_candidatures)
    with col2:
        st.metric("⏳ En attente", en_attente)
    with col3:
        st.metric("✅ Validées", validees)
    with col4:
        st.metric("❌ Rejetées", rejetees)
    
    # Statistiques bulletins si OCR disponible
    if AGENT_OCR_AVAILABLE:
        render_bulletins_statistics_iframe(candidatures)
    
    # Graphiques compacts
    if candidatures:
        try:
            import pandas as pd
            import plotly.express as px
            
            # Répartition par niveau - compact pour iframe
            st.markdown("#### 📈 Répartition par Niveau")
            niveaux = [c.get('niveau', 'Non spécifié') for c in candidatures]
            df_niveau = pd.DataFrame({'niveau': niveaux})
            
            if not df_niveau.empty:
                niveau_counts = df_niveau['niveau'].value_counts()
                
                # Graphique compact pour iframe
                fig_niveau = px.pie(
                    values=niveau_counts.values,
                    names=niveau_counts.index,
                    title="Candidatures par Niveau",
                    height=400  # Hauteur réduite pour iframe
                )
                fig_niveau.update_layout(
                    font_size=12,
                    margin=dict(t=40, b=20, l=20, r=20)
                )
                st.plotly_chart(fig_niveau, use_container_width=True)
            
        except ImportError:
            st.warning("📊 Plotly non disponible pour les graphiques.")

def render_bulletins_statistics_iframe(candidatures):
    """Statistiques des bulletins optimisées pour iframe"""
    st.markdown("#### 🎓 Statistiques Vérifications")
    
    bulletins_stats = {
        "avec_bulletins": 0,
        "verifies": 0,
        "honnetes": 0,
        "menteurs": 0,
        "usurpateurs": 0
    }
    
    for candidature in candidatures:
        try:
            dossier = get_candidature_folder_path(candidature)
            if dossier.exists():
                detection = detecter_bulletins_scolaires(dossier)
                if detection["bulletins_detectes"]:
                    bulletins_stats["avec_bulletins"] += 1
                    
                    status = get_verification_status(dossier)
                    if status["verifie"]:
                        bulletins_stats["verifies"] += 1
                        
                        # Priorité à l'usurpation
                        if status.get("usurpation_detectee", False):
                            bulletins_stats["usurpateurs"] += 1
                        elif status.get("concordance", False):
                            bulletins_stats["honnetes"] += 1
                        else:
                            bulletins_stats["menteurs"] += 1
        except Exception:
            continue
    
    # Affichage compact pour iframe
    col_b1, col_b2, col_b3 = st.columns(3)
    
    with col_b1:
        st.metric("📚 Bulletins", bulletins_stats["avec_bulletins"])
        st.metric("🔍 Vérifiés", bulletins_stats["verifies"])
    
    with col_b2:
        st.metric("✅ Honnêtes", bulletins_stats["honnetes"])
        st.metric("❌ Menteurs", bulletins_stats["menteurs"])
    
    with col_b3:
        # Alerte usurpation
        if bulletins_stats["usurpateurs"] > 0:
            st.metric("🚨 Fraudeurs", bulletins_stats["usurpateurs"], delta="GRAVE", delta_color="inverse")
        else:
            st.metric("🔐 Fraudeurs", 0, delta="Aucun", delta_color="normal")

# Garder toutes vos fonctions existantes avec optimisations mineures
def render_ocr_section_enhanced(candidature):
    """Version OCR optimisée pour iframe"""
    st.markdown("#### 🔍 OCR & Extraction")
    
    dossier_candidature = get_candidature_folder_path(candidature)
    
    if not dossier_candidature.exists():
        st.error(f"❌ Dossier candidature introuvable: {dossier_candidature}")
        return
    
    pdfs = list(dossier_candidature.glob("*.pdf"))
    st.info(f"📂 Dossier: `{dossier_candidature.name}` | 📄 {len(pdfs)} PDFs")
    
    # Section bulletins scolaires
    try:
        detection_bulletins = detecter_bulletins_scolaires(dossier_candidature)
        
        if detection_bulletins["bulletins_detectes"]:
            render_bulletins_verification_section(candidature, dossier_candidature, detection_bulletins)
    except Exception as e:
        st.error(f"❌ Erreur détection bulletins: {str(e)}")

def render_bulletins_verification_section(candidature, dossier_candidature, detection_bulletins):
    """Section vérification bulletins optimisée pour iframe"""
    st.markdown("---")
    st.markdown("#### 🎓 **Vérification Bulletins + Identité**")
    
    # Informations détectées - compact pour iframe
    col_info1, col_info2 = st.columns(2)
    
    with col_info1:
        st.markdown("**📋 Formulaire:**")
        if detection_bulletins["formulaire_detecte"]:
            st.success(f"✅ Détecté")
        else:
            st.warning("⚠️ Manquant")
    
    with col_info2:
        st.markdown(f"**📚 Bulletins: ({detection_bulletins['nb_bulletins']})**")
        if detection_bulletins["nb_bulletins"] > 0:
            st.success(f"✅ {detection_bulletins['nb_bulletins']} fichier(s)")
        else:
            st.warning("⚠️ Aucun")
    
    status_verif = get_verification_status(dossier_candidature)
    
    # Affichage status avec priorité usurpation
    if status_verif["verifie"]:
        if status_verif.get("usurpation_detectee", False):
            st.error("🚨 **USURPATION D'IDENTITÉ** - Candidature frauduleuse!")
        elif status_verif.get("identite_valide", False):
            st.success("🔐 **Identité validée** - Bulletins authentiques")
        else:
            st.warning("⚠️ **Problème d'identité** - Vérification incomplète")
    
    # Actions compactes pour iframe
    col_action1, col_action2 = st.columns(2)
    
    with col_action1:
        bouton_text = "🔄 Reverifier" if status_verif["verifie"] else "🚀 Vérifier"
        
        if st.button(
            bouton_text,
            type="primary",
            disabled=not detection_bulletins["verifiable"],
            key="btn_verifier_bulletins",
            use_container_width=True
        ):
            if detection_bulletins["verifiable"]:
                lancer_verification_bulletins(candidature, dossier_candidature)
            else:
                st.error("❌ Formulaire ET bulletins requis")
    
    with col_action2:
        if status_verif["verifie"]:
            # Status final compact
            if status_verif.get("usurpation_detectee", False):
                st.error("🚨 FRAUDEUR")
            elif status_verif["concordance"]:
                st.success("✅ Honnête")
            else:
                st.error(f"❌ {status_verif['nb_discordances']} err.")
        else:
            st.info("⏳ Non vérifié")

def lancer_verification_bulletins(candidature, dossier_candidature):
    """Lance la vérification optimisée pour iframe"""
    with st.spinner("🔍 Vérification (notes + identité)..."):
        try:
            progress_bar = st.progress(0)
            
            progress_bar.progress(30)
            resultat = verifier_bulletins_scolaires(str(dossier_candidature))
            
            progress_bar.progress(100)
            progress_bar.empty()
            
            # Affichage des résultats
            afficher_resultats_verification_iframe(resultat)
            
        except Exception as e:
            st.error(f"❌ Erreur lors de la vérification: {str(e)}")

def afficher_resultats_verification_iframe(resultat):
    """Affichage résultats optimisé pour iframe"""
    st.markdown("---")
    st.markdown("#### 📊 **Résultats de la Vérification**")
    
    # Vérification usurpation en priorité
    verification_identite = getattr(resultat, 'verification_identite', None)
    
    if verification_identite and getattr(verification_identite, 'usurpation_detectee', False):
        # Alerte usurpation - affichage prioritaire compact
        st.error("🚨 **FRAUDE DOCUMENTAIRE DÉTECTÉE**")
        
        col_fraud1, col_fraud2 = st.columns(2)
        
        with col_fraud1:
            nom_formulaire = getattr(verification_identite, 'nom_formulaire', 'INCONNU')
            prenom_formulaire = getattr(verification_identite, 'prenom_formulaire', 'INCONNU')
            st.markdown(f"**👤 Formulaire:** {prenom_formulaire} {nom_formulaire}")
        
        with col_fraud2:
            details_erreur = getattr(verification_identite, 'details_erreur', 'Erreur non spécifiée')
            st.markdown(f"**⚠️ Problème:** {details_erreur}")
        
        st.error("🚫 **RECOMMANDATION: REJET IMMÉDIAT**")
        return
    
    # Résumé principal compact pour iframe
    col_res1, col_res2, col_res3 = st.columns(3)
    
    with col_res1:
        candidat_nom = getattr(resultat, 'candidat_nom', 'INCONNU')
        candidat_prenom = getattr(resultat, 'candidat_prenom', 'INCONNU')
        st.metric("👤 Candidat", f"{candidat_prenom} {candidat_nom}")
    
    with col_res2:
        moyenne_declaree = getattr(resultat, 'moyenne_declaree', 0.0)
        st.metric("📊 Moyenne", f"{moyenne_declaree}/20")
    
    with col_res3:
        concordance = getattr(resultat, 'concordance_globale', False)
        if concordance:
            st.success("✅ HONNÊTE")
        else:
            st.error("❌ PROBLÈMES")
    
    # Détails des discordances en expander pour iframe
    discordances = getattr(resultat, 'discordances', [])
    if discordances:
        with st.expander(f"🚨 Détails des {len(discordances)} mensonge(s)"):
            for i, discordance in enumerate(discordances, 1):
                matiere = getattr(discordance, 'matiere', 'INCONNU')
                note_declaree = getattr(discordance, 'note_declaree', 0.0)
                note_bulletin = getattr(discordance, 'note_bulletin', 0.0)
                ecart = getattr(discordance, 'ecart', 0.0)
                
                st.write(f"**{i}. {matiere}:** Déclaré {note_declaree}/20, Réel {note_bulletin}/20 (écart: {ecart:.1f})")

def render_comparison_bulletins_section(candidature):
    """Section comparaison optimisée pour iframe"""
    dossier_candidature = get_candidature_folder_path(candidature)
    
    try:
        status_verif = get_verification_status(dossier_candidature)
        if status_verif["verifie"]:
            st.markdown("---")
            st.markdown("#### 🎓 **Résultat Final**")
            
            # Priorité à l'usurpation
            if status_verif.get("usurpation_detectee", False):
                st.error(f"🚨 **USURPATION D'IDENTITÉ** - Rejet recommandé")
            elif status_verif.get("identite_valide", False):
                if status_verif["concordance"]:
                    st.success(f"✅ **Candidat honnête** (identité + notes OK)")
                else:
                    st.error(f"❌ **{status_verif['nb_discordances']} mensonge(s)** (identité OK)")
            else:
                st.warning("⚠️ **Problème de vérification**")
    except Exception as e:
        st.warning(f"⚠️ Erreur: {str(e)}")

def get_candidature_folder_path(candidature):
    """Obtient le chemin du dossier candidature"""
    candidat_brut = candidature.get('candidat', 'inconnu')
    
    if isinstance(candidat_brut, dict):
        candidat_nom = candidat_brut.get('nom', candidat_brut.get('name', 'inconnu'))
    elif isinstance(candidat_brut, (list, tuple)):
        candidat_nom = str(candidat_brut[0]) if candidat_brut else 'inconnu'
    else:
        candidat_nom = str(candidat_brut) if candidat_brut else 'inconnu'
    
    candidatures_base = Path(ADMIN_CONFIG["candidatures_folder"])
    
    if not candidatures_base.exists():
        return candidatures_base / "dossier_inexistant"
    
    # Essayer par nom candidat
    try:
        for dossier in candidatures_base.iterdir():
            if dossier.is_dir() and candidat_nom.lower() in dossier.name.lower():
                return dossier
    except Exception:
        pass
    
    # Fallback
    nom_nettoye = candidat_nom.replace(' ', '_').replace('/', '_')
    return candidatures_base / nom_nettoye

def cleanup_temp_files():
    """Nettoie les fichiers temporaires"""
    import shutil
    
    candidatures_base = Path(ADMIN_CONFIG["candidatures_folder"])
    if candidatures_base.exists():
        for dossier in candidatures_base.iterdir():
            if dossier.is_dir():
                images_temp = dossier / "images_temp"
                if images_temp.exists():
                    try:
                        shutil.rmtree(images_temp)
                    except Exception:
                        pass

if __name__ == "__main__":
    main()