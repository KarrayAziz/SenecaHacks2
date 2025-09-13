# gym_webapp.py (Page d'Accueil)
import streamlit as st
from style_utils import load_css
from sidebar import render_sidebar
import os

st.set_page_config(
    page_title="FormFit AI - Accueil",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Appliquer le style CSS et afficher la barre latérale
load_css()
render_sidebar()

# --- CONTENU PRINCIPAL ---
# Titre principal avec style
st.markdown("""
<div style='text-align: center; padding: 2rem 0;'>
    <h1 style='color: #FF4B4B; font-size: 3rem; margin-bottom: 0.5rem;'>
        Analysez. Corrigez. Progressez.
    </h1>
    <h2 style='color: #666; font-weight: 300; margin-bottom: 2rem;'>
        Votre assistant personnel pour une posture parfaite et la prévention des blessures
    </h2>
</div>
""", unsafe_allow_html=True)

# Section d'introduction
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
    <div style='text-align: center; background: linear-gradient(135deg, #FF4B4B20, #FF758F20);
                padding: 2rem; border-radius: 1rem; margin: 2rem 0;'>
        <h3>🎯 Bienvenue sur FormFit AI !</h3>
        <p>Notre mission est d'utiliser la vision par ordinateur pour vous fournir
        des retours en temps réel sur vos exercices.</p>
    </div>
    """, unsafe_allow_html=True)

# Fonctionnalités principales
st.markdown("## 🌟 Fonctionnalités principales")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style='text-align: center; padding: 1.5rem; border-radius: 1rem;
                background: linear-gradient(135deg, #FF4B4B10, #FF758F10);'>
        <h2 style='color: #FF4B4B;'>📊</h2>
        <h4>Analysez</h4>
        <p>Analyse précise de votre posture en temps réel</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style='text-align: center; padding: 1.5rem; border-radius: 1rem;
                background: linear-gradient(135deg, #FF4B4B10, #FF758F10);'>
        <h2 style='color: #FF4B4B;'>🔧</h2>
        <h4>Corrigez</h4>
        <p>Conseils personnalisés pour améliorer votre technique</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style='text-align: center; padding: 1.5rem; border-radius: 1rem;
                background: linear-gradient(135deg, #FF4B4B10, #FF758F10);'>
        <h2 style='color: #FF4B4B;'>📈</h2>
        <h4>Progressez</h4>
        <p>Suivi automatique de vos répétitions et progrès</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Call to action
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
    <div style='text-align: center; padding: 2rem; background: #FF4B4B;
                border-radius: 1rem; color: white; margin: 2rem 0;'>
        <h3>🚀 Prêt à commencer ?</h3>
        <p>Utilisez le menu sur la gauche pour démarrer votre transformation !</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🏃‍♂️ Commencer maintenant", use_container_width=True, type="primary"):
        st.switch_page("pages/01_Commencer.py")

# Section avantages
st.markdown("## ✅ Pourquoi choisir FormFit AI ?")

advantages = [
    {"icon": "🎯", "title": "Précision", "desc": "Analyse précise basée sur l'IA"},
    {"icon": "⚡", "title": "Temps réel", "desc": "Retours instantanés pendant l'exercice"},
    {"icon": "🛡️", "title": "Sécurité", "desc": "Prévention des blessures intégrée"},
    {"icon": "📱", "title": "Simplicité", "desc": "Interface intuitive et facile à utiliser"}
]

cols = st.columns(4)
for i, adv in enumerate(advantages):
    with cols[i]:
        st.markdown(f"""
        <div style='text-align: center; padding: 1rem;'>
            <div style='font-size: 2rem; margin-bottom: 0.5rem;'>{adv['icon']}</div>
            <h5>{adv['title']}</h5>
            <p style='font-size: 0.9rem; color: #666;'>{adv['desc']}</p>
        </div>
        """, unsafe_allow_html=True)