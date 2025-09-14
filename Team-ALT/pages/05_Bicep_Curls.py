# pages/05_Bicep_Curls.py
import streamlit as st
from datetime import datetime
import sys
import os

# Add the parent directory to the path to import from root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bicepcurls_detection import bicep_curl_tracker
from style_utils import load_css
from sidebar import render_sidebar
from auth.authenticator import get_authenticator

# Set page config
st.set_page_config(
    page_title="FormFit AI - Bicep Curls",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply CSS and render sidebar
load_css()
render_sidebar()

# Get authenticator and check authentication
auth = get_authenticator()
auth.show_user_menu()

if not auth.is_authenticated():
    st.error("🔒 Vous devez être connecté pour accéder à cette fonctionnalité.")
    st.stop()

# Initialize session state variables for rep counting
if 'right_rep_count' not in st.session_state:
    st.session_state.right_rep_count = 0
if 'left_rep_count' not in st.session_state:
    st.session_state.left_rep_count = 0

# Main page header
st.title("💪 Bicep Curls Detection")
st.markdown("---")

# Instructions
with st.expander("📋 Instructions", expanded=False):
    st.markdown("""
    **Comment utiliser le détecteur de bicep curls :**
    
    1. **Position** : Placez-vous face à la caméra
    2. **Éclairage** : Assurez-vous d'avoir un bon éclairage
    3. **Espace** : Gardez suffisamment d'espace pour vos mouvements
    4. **Posture** : Gardez le dos droit et les coudes près du corps
    
    **Feedback couleurs :**
    - 🔵 **Bleu** : Bras étendu (position de départ)
    - 🟢 **Vert** : Bonne contraction (répétition comptée)
    - 🟠 **Orange** : Continuez la contraction
    """)

# Start the bicep curl tracker
bicep_curl_tracker()