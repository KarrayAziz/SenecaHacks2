import streamlit as st
import sys
import os
import json
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from auth.authenticator import get_authenticator
from database.models import ChatHistory, WorkoutTracker
from style_utils import load_css
from sidebar import render_sidebar

# Page configuration
st.set_page_config(
    page_title="FormFit AI - Chatbot",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hide default Streamlit navigation
st.markdown("""
<style>
    [data-testid="stSidebarNav"] {display: none !important;}
    .st-emotion-cache-79elbk {display: none !important;}
    .st-emotion-cache-10p9htt {display: none !important;}
    
    /* Chat styling */
    .chat-message {
        padding: 1rem;
        border-radius: 1rem;
        margin: 0.5rem 0;
    }
    .user-message {
        background: linear-gradient(135deg, #FF4B4B20, #FF758F20);
        border-left: 4px solid #FF4B4B;
    }
    .bot-message {
        background: #F0F2F6;
        border-left: 4px solid #666;
    }
    .chat-container {
        height: 400px;
        overflow-y: auto;
        padding: 1rem;
        border: 1px solid #E6E6E6;
        border-radius: 0.5rem;
        background: white;
    }
</style>
""", unsafe_allow_html=True)

# Load styles and sidebar
load_css()
render_sidebar()

# Get authenticator and require authentication
auth = get_authenticator()
auth.require_authentication()
auth.show_user_menu()

# Get user data
user_data = auth.get_user_data()
if not user_data:
    st.error("Erreur: Impossible de charger les données utilisateur")
    st.stop()

# Initialize chat history and workout tracker
chat_history = ChatHistory(auth.db_manager)
workout_tracker = WorkoutTracker(auth.db_manager)

# Page title
st.markdown(f"""
<div style='text-align: center; padding: 1rem 0;'>
    <h1 style='color: #FF4B4B; margin-bottom: 0.5rem;'>💬 Assistant Fitness IA</h1>
    <p style='color: #666; font-size: 1.1rem;'>Votre coach personnel intelligent</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state for chat
if 'chat_messages' not in st.session_state:
    # Load chat history from database
    history = chat_history.get_chat_history(user_data['id'], limit=20)
    st.session_state.chat_messages = []
    for chat in history:
        st.session_state.chat_messages.append({"role": "user", "content": chat['message']})
        st.session_state.chat_messages.append({"role": "assistant", "content": chat['response']})

# Fitness knowledge base for simple responses
def get_fitness_response(message: str, user_data: dict, workout_stats: dict) -> str:
    """Simple rule-based chatbot with user context"""
    message_lower = message.lower()
    
    # Personalized greeting
    if any(word in message_lower for word in ['salut', 'bonjour', 'hello', 'hey']):
        return f"Bonjour {user_data['name']} ! 👋 Comment puis-je vous aider avec votre fitness aujourd'hui ?"
    
    # Progress inquiries
    if any(word in message_lower for word in ['progrès', 'progress', 'statistiques', 'stats']):
        return f"""📊 Voici vos statistiques actuelles :
        
✅ **Séances totales :** {workout_stats['total_workouts']}
🔥 **Calories brûlées :** {int(workout_stats['total_calories'])} cal
📅 **Cette semaine :** {workout_stats['workouts_this_week']} séances
⭐ **Score forme moyen :** {workout_stats['avg_form_score']}/10

Continuez comme ça ! 💪"""
    
    # Weight/goal related
    if any(word in message_lower for word in ['poids', 'weight', 'objectif', 'goal']):
        current = user_data['current_weight']
        goal = user_data['goal_weight']
        if current and goal:
            diff = current - goal
            if diff > 0:
                return f"🎯 Votre objectif est de perdre {diff:.1f} kg. Avec une alimentation équilibrée et {workout_stats['workouts_this_week']} séances par semaine, vous êtes sur la bonne voie !"
            elif diff < 0:
                return f"🎯 Votre objectif est de prendre {abs(diff):.1f} kg. N'oubliez pas de combiner exercices de force et nutrition adaptée !"
            else:
                return "🎉 Félicitations ! Vous avez atteint votre objectif de poids. Maintenant, concentrons-nous sur le maintien !"
    
    # Exercise recommendations
    if any(word in message_lower for word in ['exercice', 'workout', 'entraînement', 'recommandation']):
        level = user_data.get('fitness_level', 'Débutant').lower()
        if 'débutant' in level:
            return """🏃‍♂️ **Recommandations pour débutant :**

• **Squats** - Excellent pour les jambes et fessiers
• **Pompes** (ou version genoux) - Renforce le haut du corps  
• **Planche** - Core et stabilité
• **Marche rapide** - Cardio doux

Commencez par 2-3 séances par semaine, 15-20 minutes chacune. Notre système d'analyse vous aidera à perfectionner votre forme ! 💪"""
        
        elif 'intermédiaire' in level:
            return """🔥 **Programme intermédiaire :**

• **Squats avec poids** - 3x12
• **Développé-couché** - 3x10  
• **Deadlifts** - 3x8
• **Burpees** - 3x10
• **HIIT** 2x par semaine

4-5 séances par semaine recommandées. Utilisez notre analyse de forme pour optimiser chaque mouvement ! 🎯"""
        
        else:
            return """💪 **Programme avancé :**

• **Squats bulgares** - 4x12 chaque jambe
• **Développé incliné** - 4x8
• **Deadlifts sumo** - 4x6  
• **Muscle-ups** - 4x5
• **Sprints** - 8x30s

5-6 séances par semaine. Votre niveau permet des mouvements complexes - notre IA vous aidera à maintenir la perfection technique ! 🚀"""
    
    # Nutrition advice
    if any(word in message_lower for word in ['nutrition', 'alimentation', 'manger', 'régime', 'diet']):
        goals = user_data.get('goals', '').lower()
        if 'perte de poids' in goals:
            return """🥗 **Conseils nutrition pour la perte de poids :**

• **Déficit calorique** : 300-500 cal/jour
• **Protéines** : 1.6-2g par kg de poids corporel
• **Légumes** : La moitié de votre assiette
• **Hydratation** : 2-3L d'eau par jour
• **Repas** : 4-5 petits repas plutôt que 3 gros

N'oubliez pas : 70% nutrition, 30% exercice pour la perte de poids ! 📊"""
        
        elif 'gain de muscle' in goals:
            return """🍖 **Nutrition pour la prise de masse :**

• **Surplus calorique** : 200-400 cal/jour  
• **Protéines** : 2-2.5g par kg de poids corporel
• **Glucides** : Autour de l'entraînement
• **Lipides** : 0.8-1g par kg de poids corporel
• **Post-workout** : Protéines + glucides dans les 30min

La construction musculaire nécessite du carburant ! 💪"""
        
        else:
            return """🍽️ **Conseils nutrition généraux :**

• **Variété** : Tous les groupes alimentaires
• **Timing** : Repas réguliers
• **Qualité** : Aliments non transformés
• **Portions** : Écoutez votre satiété
• **Plaisir** : 80/20 rule - soyez strict 80% du temps

Une alimentation équilibrée est la base de la performance ! ⚖️"""
    
    # Motivation
    if any(word in message_lower for word in ['motivation', 'encouragement', 'difficile', 'abandonner']):
        return f"""💪 **Message de motivation pour {user_data['name']} :**

Vous avez déjà fait {workout_stats['total_workouts']} séances - c'est fantastique ! 🎉

🌟 **Rappelez-vous :**
• Chaque petit pas compte
• La progression n'est pas toujours linéaire
• Votre futur vous sera reconnaissant
• Vous êtes plus fort que vos excuses

{workout_stats['workouts_this_week']} séances cette semaine montrent votre détermination. Continuez, vous êtes sur la bonne voie ! 🚀"""
    
    # Default response
    return """🤖 **Je suis votre assistant fitness !** Je peux vous aider avec :

• 📊 **Vos statistiques** et progrès
• 🏋️ **Recommandations d'exercices** personnalisées  
• 🥗 **Conseils nutritionnels** selon vos objectifs
• 💪 **Motivation** et encouragement
• 🎯 **Planification** d'entraînement

Posez-moi une question spécifique sur votre fitness ! 💬"""

# Chat interface
st.markdown("## 💬 Conversation")

# Chat container
chat_container = st.container()

with chat_container:
    # Display chat history
    for message in st.session_state.chat_messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>👤 Vous :</strong><br>
                {message["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message bot-message">
                <strong>🤖 Assistant :</strong><br>
                {message["content"]}
            </div>
            """, unsafe_allow_html=True)

# Chat input
st.markdown("### Posez votre question :")

user_input = st.text_area(
    "Écrivez votre message...",
    key="user_input",
    height=100,
    placeholder="Ex: Comment puis-je améliorer ma forme pour les squats ?"
)

col1, col2 = st.columns([1, 4])
with col1:
    if st.button("📤 Envoyer", use_container_width=True, type="primary"):
        if user_input.strip():
            # Add user message
            st.session_state.chat_messages.append({"role": "user", "content": user_input})
            
            # Get workout stats for context
            workout_stats = workout_tracker.get_workout_stats(user_data['id'])
            
            # Generate response
            response = get_fitness_response(user_input, user_data, workout_stats)
            
            # Add assistant response
            st.session_state.chat_messages.append({"role": "assistant", "content": response})
            
            # Save to database
            chat_history.save_chat(user_data['id'], user_input, response)
            
            st.rerun()

with col2:
    if st.button("🗑️ Effacer conversation", use_container_width=True):
        st.session_state.chat_messages = []
        st.rerun()

# Suggested questions
st.markdown("### 💡 Questions suggérées :")

suggestions = [
    "Quels sont mes progrès cette semaine ?",
    "Recommande-moi des exercices pour débutant",
    "Comment améliorer ma nutrition ?",
    "J'ai besoin de motivation !",
    "Quel est mon score de forme moyen ?"
]

cols = st.columns(len(suggestions))
for i, suggestion in enumerate(suggestions):
    with cols[i]:
        if st.button(suggestion, key=f"suggestion_{i}", use_container_width=True):
            # Add suggested question as if user typed it
            st.session_state.chat_messages.append({"role": "user", "content": suggestion})
            
            # Get response
            workout_stats = workout_tracker.get_workout_stats(user_data['id'])
            response = get_fitness_response(suggestion, user_data, workout_stats)
            st.session_state.chat_messages.append({"role": "assistant", "content": response})
            
            # Save to database
            chat_history.save_chat(user_data['id'], suggestion, response)
            st.rerun()

# Quick actions
st.markdown("---")
st.markdown("### ⚡ Actions rapides")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📊 Voir Dashboard", use_container_width=True):
        st.switch_page("pages/01_Dashboard.py")

with col2:
    if st.button("🏃‍♂️ Nouvelle séance", use_container_width=True):
        st.switch_page("pages/01_Commencer.py")

with col3:
    if st.button("👤 Modifier profil", use_container_width=True):
        st.switch_page("pages/02_Profile.py")

# Info box
st.markdown("""
<div style='background: #F0F8FF; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #007ACC; margin: 2rem 0;'>
    <p><strong>💡 Astuce :</strong> Plus vous utilisez l'assistant, plus il comprend vos besoins ! N'hésitez pas à poser des questions spécifiques sur votre entraînement, nutrition ou motivation.</p>
</div>
""", unsafe_allow_html=True)