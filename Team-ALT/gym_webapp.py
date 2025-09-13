# gym_webapp.py (Version 3.2 - Design Sport & Bug Corrigé)

import streamlit as st

# --- Importation de TOUS les modules de détection d'exercices ---
from bicepcurls_detection import bicep_curl_tracker
from shoulderpress_detection import shoulder_press_tracker
from squats_detection import squat_tracker
from wallseat_detection import wall_sit_tracker
from deadlift_detection import deadlift_tracker

# =============================================================================
# 1. CONFIGURATION DE LA PAGE ET NOUVEAU STYLE CSS "SPORT TECH"
# =============================================================================
st.set_page_config(
    page_title="FormFit AI Pro",
    page_icon="🔥",
    layout="wide"
)

# --- INJECTION DE CSS POUR UN DESIGN PERSONNALISÉ ---
st.markdown("""
<style>
    /* Importation d'une police plus moderne et sportive */
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');
    html, body, [class*="st-"] {
        font-family: 'Montserrat', sans-serif;
    }

    /* Thème principal : Noir charbon et Orange vibrant */
    .stApp {
        background-color: #111111; /* Fond principal plus sombre */
        color: #F0F0F0; /* Texte légèrement blanc cassé */
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1E1E1E; /* Fond du sidebar légèrement plus clair */
        border-right: 2px solid #FF4500; /* Bordure orange */
    }
    [data-testid="stSidebar"] h1 {
        color: #FF4500 !important; /* Couleur du titre en orange */
        text-shadow: none;
    }

    /* Boutons */
    .stButton>button {
        border: 2px solid #FF4500;
        border-radius: 25px; /* Boutons plus arrondis "pilule" */
        color: #FF4500;
        background-color: transparent;
        padding: 10px 25px;
        font-weight: 600; /* Police plus grasse */
        transition: all 0.3s ease;
        text-transform: uppercase; /* Texte en majuscules */
        letter-spacing: 1px;
    }
    .stButton>button:hover {
        background-color: #FF4500;
        color: #ffffff;
        box-shadow: 0 0 15px #FF4500; /* Effet de lueur au survol */
    }
    .stButton>button:active {
        background-color: #cc3700 !important;
        color: #ffffff !important;
    }

    /* Selectbox */
    .stSelectbox div[data-baseweb="select"] {
        background-color: #2E2E2E;
        border-radius: 10px;
    }

    /* Titres et textes */
    h1, h2, h3 {
        color: #FFFFFF;
        text-shadow: 2px 2px 4px #000000;
    }
    
    /* Conteneur d'information (st.info) */
    .st-emotion-cache-1wivap2 {
        background-color: rgba(255, 69, 0, 0.1); /* Fond semi-transparent orange */
        border-left: 5px solid #FF4500;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# 2. SIDEBAR DE NAVIGATION
# =============================================================================

with st.sidebar:
    st.image("images/pose1.jpg", width=150) # Remplacez par votre logo
    st.title("🔥 FormFit AI")
    st.sidebar.divider()
    
    if st.button("🏠 Accueil", use_container_width=True):
        st.session_state.page = "Accueil"
        st.rerun()
    if st.button("💪 Commencer", use_container_width=True):
        st.session_state.page = "Exercice"
        st.rerun()
    if st.button("🖼️ Exemples", use_container_width=True):
        st.session_state.page = "Exemples"
        st.rerun()

# Initialisation
if 'page' not in st.session_state:
    st.session_state.page = "Accueil"
if 'exercise_running' not in st.session_state:
    st.session_state.exercise_running = False

EXERCISE_FUNCTIONS = {
    "Bicep Curls": bicep_curl_tracker,
    "Shoulder Press": shoulder_press_tracker,
    "Squats": squat_tracker,
    "Wall Sit": wall_sit_tracker,
    "Deadlift": deadlift_tracker,
}

# =============================================================================
# 3. ROUTAGE ET AFFICHAGE DES PAGES
# =============================================================================

if st.session_state.page == "Accueil":
    st.title("🏠 Accueil")
    st.header("Analysez. Corrigez. Progressez.")
    st.markdown("""
    Bienvenue sur **FormFit AI** ! Notre mission est d'utiliser la vision par ordinateur pour vous fournir des retours en temps réel sur vos exercices.
    - **Analysez** votre posture.
    - **Comptez** vos répétitions automatiquement.
    - **Prémunissez-vous** contre les blessures grâce à des conseils en direct.
    Utilisez le menu sur la gauche pour commencer !
    """)

elif st.session_state.page == "Exercice":
    st.title("💪 Commencer l'exercice")

    if not st.session_state.exercise_running:
        selected_exercise = st.selectbox(
            "Choisissez un exercice à analyser :",
            options=list(EXERCISE_FUNCTIONS.keys()),
            index=None,
            placeholder="Cliquez pour choisir..."
        )
        if selected_exercise:
            if st.button(f"🚀 Démarrer {selected_exercise}", use_container_width=True):
                st.session_state.selected_exercise = selected_exercise
                st.session_state.exercise_running = True
                st.rerun()
    else:
        selected_exercise = st.session_state.selected_exercise
        st.header(f"🔥 Session en cours : {selected_exercise}")
        col1, col2 = st.columns([3, 2])
        with col1:
            tracker_function = EXERCISE_FUNCTIONS[selected_exercise]
            tracker_function()
        with col2:
            st.info("L'analyse est en direct. Suivez les conseils à l'écran.")
            if st.button("🛑 Arrêter la session", use_container_width=True):
                st.session_state.exercise_running = False
                st.session_state.pop('selected_exercise', None)
                st.rerun()
            st.markdown("---")
            st.subheader("🤖 Assistant IA (Bientôt disponible)")
            st.write("Posez vos questions sur la bonne posture, le nombre de séries, ou le temps de repos idéal.")
            st.text_area("Votre question...", key="llm_input", height=100, disabled=True)

elif st.session_state.page == "Exemples":
    st.title("🖼️ Poses d'Exemples")
    st.info("Voici des exemples de postures correctes pour vous guider.")
    
    # --- CORRECTION DU BUG D'AFFICHAGE ---
    # Remplacement des expanders par une galerie en colonnes
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Bicep Curl")
        st.image("images/pose5.jpg")
        st.subheader("Squats")
        st.image("images/pose3.jpg")
        st.subheader("Deadlift")
        st.image("images/pose1.jpg")
    with col2:
        st.subheader("Shoulder Press")
        st.image("images/pose2.jpg")
        st.subheader("Wall Sit")
        st.image("images/pose4.jpg")