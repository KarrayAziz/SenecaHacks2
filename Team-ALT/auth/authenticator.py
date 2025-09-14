import streamlit as st
#import yaml
#from yaml.loader import SafeLoader
from typing import Optional, Dict, Any
import os
import sys

# Add the parent directory to the path to import database models
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database.models import DatabaseManager, User

class FormFitAuthenticator:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.user_manager = User(self.db_manager)
        
        # Initialize session state
        if 'authentication_status' not in st.session_state:
            st.session_state.authentication_status = None
        if 'user_data' not in st.session_state:
            st.session_state.user_data = None
        if 'username' not in st.session_state:
            st.session_state.username = None
    
    def login_form(self) -> bool:
        """Display login form and handle authentication"""
        st.markdown("## 🔐 Connexion")
        
        with st.form("login_form"):
            username = st.text_input("Nom d'utilisateur")
            password = st.text_input("Mot de passe", type="password")
            login_button = st.form_submit_button("Se connecter", use_container_width=True)
            
            if login_button:
                if username and password:
                    user_data = self.user_manager.authenticate_user(username, password)
                    if user_data:
                        st.session_state.authentication_status = True
                        st.session_state.user_data = user_data
                        st.session_state.username = username
                        st.success("✅ Connexion réussie!")
                        st.rerun()
                        return True
                    else:
                        st.error("❌ Nom d'utilisateur ou mot de passe incorrect")
                        return False
                else:
                    st.warning("⚠️ Veuillez remplir tous les champs")
                    return False
        
        return False
    
    def register_form(self) -> bool:
        """Display registration form"""
        st.markdown("## 📝 Inscription")
        
        with st.form("register_form"):
            # Single column layout for all fields
            username = st.text_input("Nom d'utilisateur*")
            email = st.text_input("Email*")
            name = st.text_input("Nom complet*")
            age = st.number_input("Âge", min_value=10, max_value=100, value=25)
            password = st.text_input("Mot de passe*", type="password")
            confirm_password = st.text_input("Confirmer le mot de passe*", type="password")
            height = st.number_input("Taille (cm)", min_value=100.0, max_value=250.0, value=170.0)
            current_weight = st.number_input("Poids actuel (kg)", min_value=30.0, max_value=300.0, value=70.0)
            goal_weight = st.number_input("Poids objectif (kg)", min_value=30.0, max_value=300.0, value=65.0)
            
            fitness_level = st.selectbox(
                "Niveau de forme physique",
                ["Débutant", "Intermédiaire", "Avancé", "Expert"]
            )
            
            goals = st.multiselect(
                "Objectifs de fitness",
                ["Perte de poids", "Gain de muscle", "Endurance", "Force", "Flexibilité", "Bien-être général"]
            )
            goals_str = ", ".join(goals) if goals else ""
            
            register_button = st.form_submit_button("S'inscrire", use_container_width=True)
            
            if register_button:
                # Validation
                if not all([username, email, password, confirm_password, name]):
                    st.error("❌ Veuillez remplir tous les champs obligatoires")
                    return False
                
                if password != confirm_password:
                    st.error("❌ Les mots de passe ne correspondent pas")
                    return False
                
                if len(password) < 6:
                    st.error("❌ Le mot de passe doit contenir au moins 6 caractères")
                    return False
                
                # Create user
                success = self.user_manager.create_user(
                    username=username,
                    email=email,
                    password=password,
                    name=name,
                    height=height,
                    current_weight=current_weight,
                    goal_weight=goal_weight,
                    age=age,
                    fitness_level=fitness_level,
                    goals=goals_str
                )
                
                if success:
                    st.success("✅ Inscription réussie! Vous pouvez maintenant vous connecter.")
                    st.balloons()
                    return True
                else:
                    st.error("❌ Erreur lors de l'inscription. Le nom d'utilisateur ou l'email existe peut-être déjà.")
                    return False
        
        return False

    def logout(self):
        """Logout the current user"""
        st.session_state.authentication_status = None
        st.session_state.user_data = None
        st.session_state.username = None
        st.rerun()
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return st.session_state.authentication_status == True
    
    def get_user_data(self) -> Optional[Dict]:
        """Get current user data"""
        return st.session_state.user_data
    
    def require_authentication(self):
        """Require authentication to access a page"""
        if not self.is_authenticated():
            st.warning("🔒 Vous devez être connecté pour accéder à cette page.")
            
            # Show login/register options
            tab1, tab2 = st.tabs(["Se connecter", "S'inscrire"])
            
            with tab1:
                self.login_form()
            
            with tab2:
                self.register_form()
            
            st.stop()
    
    def show_user_menu(self):
        """Show user menu in sidebar"""
        if self.is_authenticated():
            user_data = self.get_user_data()
            if user_data:
                st.sidebar.markdown(f"### 👋 Bonjour, {user_data['name']}!")
                
                # User info
                st.sidebar.markdown(f"""
                **Informations:**
                - 📧 {user_data['email']}
                - 📏 {user_data['height']} cm
                - ⚖️ {user_data['current_weight']} kg
                - 🎯 Objectif: {user_data['goal_weight']} kg
                """)
                
                # Navigation
                st.sidebar.markdown("### 🧭 Navigation")
                if st.sidebar.button("📊 Dashboard", use_container_width=True):
                    st.switch_page("pages/01_Dashboard.py")
                
                if st.sidebar.button("👤 Profil", use_container_width=True):
                    st.switch_page("pages/02_Profile.py")
                
                if st.sidebar.button("💬 Chatbot", use_container_width=True):
                    st.switch_page("pages/03_Chatbot.py")
                
                st.sidebar.markdown("---")
                
                # Logout
                if st.sidebar.button("🚪 Se déconnecter", use_container_width=True):
                    self.logout()
        else:
            st.sidebar.markdown("### 🔐 Connexion requise")
            st.sidebar.info("Connectez-vous pour accéder à toutes les fonctionnalités!")

# Helper function to get authenticator instance
@st.cache_resource
def get_authenticator():
    """Get or create authenticator instance"""
    return FormFitAuthenticator()