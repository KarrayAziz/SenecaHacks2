import streamlit as st
import os

def render_sidebar():
    """Affiche la barre latérale cohérente sur toutes les pages."""
    with st.sidebar:
        # 1. Logo
        logo_path = "images/image.jpg"
        if os.path.exists(logo_path):
            st.image(logo_path, use_container_width=True)
        else:
            st.markdown("## 🔥 FormFit AI")

        # Titre et description
        st.title("🔥 FormFit AI")
        st.caption("Votre partenaire pour une forme parfaite.")

        st.divider()

        # 2. Menu de Navigation amélioré
        with st.container(border=True):
            st.markdown("### 📋 Navigation")
            st.page_link("gym_webapp.py", label="**Accueil**", icon="🏠")
            st.page_link("pages/01_Commencer.py", label="**Commencer la Session**", icon="🚀")
            st.page_link("pages/02_Exemples.py", label="**Exemples de Poses**", icon="💪")

        st.markdown("<br>", unsafe_allow_html=True)

        # 3. Section Statistiques rapides
        with st.container(border=True):
            st.markdown("### 📊 Statistiques")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Sessions", "0", "0")
            with col2:
                st.metric("Exercices", "0", "0")

        st.markdown("<br>", unsafe_allow_html=True)

        # 4. Section Aide rapide
        with st.expander("❓ Aide rapide"):
            st.markdown("""
            **Comment utiliser FormFit AI ?**
            1. Cliquez sur "Commencer la Session"
            2. Sélectionnez votre exercice
            3. Suivez les instructions à l'écran
            4. Recevez des retours en temps réel
            """)

        # 5. Footer
        st.markdown("---")
        st.markdown(
            """
            <div style='text-align: center; color: #888; font-size: 0.8rem;'>
            © 2025 FormFit AI<br>
            Tous droits réservés
            </div>
            """,
            unsafe_allow_html=True
        )