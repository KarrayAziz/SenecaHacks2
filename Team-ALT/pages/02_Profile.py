import streamlit as st
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from auth.authenticator import get_authenticator
from database.models import User
from style_utils import load_css
from sidebar import render_sidebar

# Page configuration
st.set_page_config(
    page_title="FormFit AI - Profil",
    page_icon="👤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hide default Streamlit navigation
st.markdown("""
<style>
    [data-testid="stSidebarNav"] {display: none !important;}
    .st-emotion-cache-79elbk {display: none !important;}
    .st-emotion-cache-10p9htt {display: none !important;}
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

# Initialize user manager
user_manager = User(auth.db_manager)

# Page title
st.markdown(f"""
<div style='text-align: center; padding: 1rem 0;'>
    <h1 style='color: #FF4B4B; margin-bottom: 0.5rem;'>👤 Profil - {user_data['name']}</h1>
    <p style='color: #666; font-size: 1.1rem;'>Gérez vos informations personnelles et objectifs</p>
</div>
""", unsafe_allow_html=True)

# Profile management tabs
tab1, tab2, tab3 = st.tabs(["📝 Informations personnelles", "🎯 Objectifs fitness", "📊 Historique"])

with tab1:
    st.markdown("### 👤 Informations de base")
    
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Nom complet", value=user_data.get('name', ''))
            email = st.text_input("Email", value=user_data.get('email', ''), disabled=True)
            username = st.text_input("Nom d'utilisateur", value=user_data.get('username', ''), disabled=True)
            age = st.number_input("Âge", min_value=10, max_value=100, value=user_data.get('age', 25) or 25)
        
        with col2:
            height = st.number_input("Taille (cm)", min_value=100.0, max_value=250.0, 
                                   value=float(user_data.get('height', 170.0) or 170.0))
            current_weight = st.number_input("Poids actuel (kg)", min_value=30.0, max_value=300.0,
                                           value=float(user_data.get('current_weight', 70.0) or 70.0))
            fitness_level = st.selectbox(
                "Niveau de forme physique",
                ["Débutant", "Intermédiaire", "Avancé", "Expert"],
                index=["Débutant", "Intermédiaire", "Avancé", "Expert"].index(
                    user_data.get('fitness_level', 'Débutant') or 'Débutant'
                )
            )
        
        st.markdown("### 📊 Calculs automatiques")
        
        # Calculate BMI
        bmi = current_weight / ((height / 100) ** 2)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("IMC (BMI)", f"{bmi:.1f}")
        
        with col2:
            # BMI category
            if bmi < 18.5:
                category = "Sous-poids"
                color = "#FFA07A"
            elif bmi < 25:
                category = "Normal"
                color = "#90EE90"
            elif bmi < 30:
                category = "Surpoids"
                color = "#FFD700"
            else:
                category = "Obésité"
                color = "#FF6B6B"
            
            st.markdown(f"""
            <div style='background: {color}; padding: 1rem; border-radius: 0.5rem; text-align: center;'>
                <p style='margin: 0; font-weight: 600; color: #333;'>Catégorie: {category}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            # Ideal weight range (using BMI 20-25)
            ideal_min = 20 * ((height / 100) ** 2)
            ideal_max = 25 * ((height / 100) ** 2)
            st.metric("Poids idéal", f"{ideal_min:.0f}-{ideal_max:.0f} kg")
        
        if st.form_submit_button("💾 Sauvegarder les modifications", use_container_width=True, type="primary"):
            # Update user profile
            success = user_manager.update_user_profile(
                user_id=user_data['id'],
                name=name,
                height=height,
                current_weight=current_weight,
                age=age,
                fitness_level=fitness_level
            )
            
            if success:
                st.success("✅ Profil mis à jour avec succès!")
                # Update session state
                st.session_state.user_data.update({
                    'name': name,
                    'height': height,
                    'current_weight': current_weight,
                    'age': age,
                    'fitness_level': fitness_level
                })
                st.rerun()
            else:
                st.error("❌ Erreur lors de la mise à jour du profil")

with tab2:
    st.markdown("### 🎯 Objectifs et préférences")
    
    with st.form("goals_form"):
        goal_weight = st.number_input("Poids objectif (kg)", min_value=30.0, max_value=300.0,
                                    value=float(user_data.get('goal_weight', 65.0) or 65.0))
        
        # Goal analysis
        current = user_data.get('current_weight', 70.0) or 70.0
        weight_diff = current - goal_weight
        
        if weight_diff > 0:
            goal_type = "Perte de poids"
            goal_description = f"Objectif: perdre {weight_diff:.1f} kg"
            goal_color = "#FF6B6B"
        elif weight_diff < 0:
            goal_type = "Prise de poids"
            goal_description = f"Objectif: prendre {abs(weight_diff):.1f} kg"
            goal_color = "#4ECDC4"
        else:
            goal_type = "Maintien"
            goal_description = "Objectif: maintenir le poids actuel"
            goal_color = "#45B7D1"
        
        st.markdown(f"""
        <div style='background: {goal_color}20; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid {goal_color};'>
            <h4 style='margin: 0; color: {goal_color};'>{goal_type}</h4>
            <p style='margin: 0.5rem 0 0 0;'>{goal_description}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Fitness goals
        current_goals = user_data.get('goals', '').split(', ') if user_data.get('goals') else []
        fitness_goals = st.multiselect(
            "Objectifs de fitness",
            ["Perte de poids", "Gain de muscle", "Endurance", "Force", "Flexibilité", "Bien-être général"],
            default=current_goals
        )
        
        # Time-based goals
        st.markdown("#### ⏰ Objectifs temporels")
        col1, col2 = st.columns(2)
        
        with col1:
            target_date = st.date_input("Date objectif (optionnel)")
            workouts_per_week = st.selectbox(
                "Séances par semaine",
                [1, 2, 3, 4, 5, 6, 7],
                index=2  # Default to 3
            )
        
        with col2:
            session_duration = st.selectbox(
                "Durée par séance",
                ["15-30 min", "30-45 min", "45-60 min", "60+ min"],
                index=1
            )
            preferred_time = st.selectbox(
                "Moment préféré",
                ["Matin", "Midi", "Après-midi", "Soir", "Flexible"]
            )
        
        # Recommendations based on goals
        st.markdown("#### 💡 Recommandations personnalisées")
        
        recommendations = []
        
        if "Perte de poids" in fitness_goals:
            recommendations.append("🔥 Combinez cardio (3x/semaine) et musculation (2x/semaine)")
            recommendations.append("📊 Créez un déficit calorique de 300-500 cal/jour")
        
        if "Gain de muscle" in fitness_goals:
            recommendations.append("💪 Privilégiez la musculation 4-5x/semaine")
            recommendations.append("🍖 Augmentez vos protéines à 2g/kg de poids corporel")
        
        if "Endurance" in fitness_goals:
            recommendations.append("🏃‍♂️ Incluez du cardio progressif 4-5x/semaine")
            recommendations.append("⏱️ Augmentez progressivement la durée des séances")
        
        if "Force" in fitness_goals:
            recommendations.append("🏋️‍♂️ Concentrez-vous sur les mouvements composés")
            recommendations.append("📈 Progression par surcharge progressive")
        
        if recommendations:
            for rec in recommendations:
                st.markdown(f"- {rec}")
        
        if st.form_submit_button("🎯 Sauvegarder les objectifs", use_container_width=True, type="primary"):
            goals_str = ", ".join(fitness_goals)
            
            success = user_manager.update_user_profile(
                user_id=user_data['id'],
                goal_weight=goal_weight,
                goals=goals_str
            )
            
            if success:
                st.success("✅ Objectifs mis à jour avec succès!")
                # Update session state
                st.session_state.user_data.update({
                    'goal_weight': goal_weight,
                    'goals': goals_str
                })
                st.rerun()
            else:
                st.error("❌ Erreur lors de la mise à jour des objectifs")

with tab3:
    st.markdown("### 📊 Historique et progression")
    
    from database.models import WorkoutTracker
    workout_tracker = WorkoutTracker(auth.db_manager)
    
    # Get workout statistics
    stats = workout_tracker.get_workout_stats(user_data['id'])
    workouts = workout_tracker.get_user_workouts(user_data['id'], limit=20)
    
    # Statistics overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Séances totales", stats['total_workouts'])
    
    with col2:
        st.metric("Calories brûlées", f"{int(stats['total_calories'])}")
    
    with col3:
        st.metric("Score forme moyen", f"{stats['avg_form_score']}/10")
    
    with col4:
        st.metric("Cette semaine", f"{stats['workouts_this_week']} séances")
    
    # Progress tracking
    st.markdown("#### 📈 Suivi du poids")
    
    # Weight tracking form
    with st.expander("➕ Ajouter une mesure de poids"):
        col1, col2 = st.columns(2)
        with col1:
            new_weight = st.number_input("Nouveau poids (kg)", min_value=30.0, max_value=300.0, 
                                       value=float(user_data.get('current_weight', 70.0)))
        with col2:
            measure_date = st.date_input("Date de mesure")
        
        if st.button("📊 Enregistrer mesure"):
            # Update current weight
            success = user_manager.update_user_profile(
                user_id=user_data['id'],
                current_weight=new_weight
            )
            
            if success:
                st.success(f"✅ Poids mis à jour: {new_weight} kg")
                st.session_state.user_data['current_weight'] = new_weight
                st.rerun()
    
    # Recent workouts
    st.markdown("#### 🏃‍♂️ Séances récentes")
    
    if workouts:
        import pandas as pd
        
        # Convert to DataFrame
        df = pd.DataFrame(workouts)
        df['workout_date'] = pd.to_datetime(df['workout_date']).dt.strftime('%d/%m/%Y %H:%M')
        
        # Display table
        display_df = df[['workout_date', 'exercise_type', 'reps', 'sets', 'duration', 'form_score', 'calories_burned']].fillna('-')
        display_df.columns = ['Date', 'Exercice', 'Répétitions', 'Séries', 'Durée (min)', 'Score', 'Calories']
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Workout frequency analysis
        st.markdown("#### 📅 Analyse de fréquence")
        
        # Calculate weekly frequency
        df['date'] = pd.to_datetime(df['workout_date'].str.split(' ').str[0], format='%d/%m/%Y')
        df['week'] = df['date'].dt.isocalendar().week
        weekly_counts = df.groupby('week').size()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Fréquence moyenne", f"{weekly_counts.mean():.1f} séances/semaine")
        with col2:
            st.metric("Meilleure semaine", f"{weekly_counts.max()} séances")
    else:
        st.info("Aucune séance enregistrée. Commencez votre première séance pour voir vos statistiques ici !")

# Account management section
st.markdown("---")
st.markdown("## ⚙️ Gestion du compte")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🔄 Actions du compte")
    
    if st.button("🔄 Actualiser les données", use_container_width=True):
        # Refresh user data from database
        fresh_data = user_manager.get_user_by_id(user_data['id'])
        if fresh_data:
            st.session_state.user_data = fresh_data
            st.success("✅ Données actualisées!")
            st.rerun()
    
    if st.button("📋 Exporter mes données", use_container_width=True):
        import json
        
        # Prepare export data
        export_data = {
            'profile': user_data,
            'workouts': workouts,
            'statistics': stats,
            'export_date': st.session_state.get('current_time', 'N/A')
        }
        
        # Convert to JSON
        json_data = json.dumps(export_data, indent=2, ensure_ascii=False)
        
        st.download_button(
            label="⬇️ Télécharger JSON",
            data=json_data,
            file_name=f"formfit_data_{user_data['username']}.json",
            mime="application/json"
        )

with col2:
    st.markdown("### 🎨 Préférences")
    
    # Theme preference (for future implementation)
    theme_preference = st.selectbox(
        "Thème de l'interface",
        ["Auto", "Clair", "Sombre"],
        disabled=True,
        help="Fonctionnalité à venir"
    )
    
    # Language preference (for future implementation)
    language_preference = st.selectbox(
        "Langue",
        ["Français", "English"],
        disabled=True,
        help="Fonctionnalité à venir"
    )
    
    # Notifications (for future implementation)
    notifications = st.checkbox(
        "Rappels d'entraînement",
        value=True,
        disabled=True,
        help="Fonctionnalité à venir"
    )

# Help section
st.markdown("---")
st.markdown("## ❓ Aide et support")

with st.expander("🆘 Foire aux questions"):
    st.markdown("""
    **Q: Comment modifier mon mot de passe ?**
    R: Cette fonctionnalité sera bientôt disponible. Contactez le support en attendant.
    
    **Q: Puis-je supprimer des séances d'entraînement ?**
    R: Actuellement, les séances sont automatiquement enregistrées. La modification manuelle arrivera prochainement.
    
    **Q: Comment interpréter mon score de forme ?**
    R: Le score va de 0 à 10. 7+ = Excellente forme, 5-7 = Bonne forme, <5 = À améliorer.
    
    **Q: Que faire si mes données ne s'affichent pas ?**
    R: Utilisez le bouton "Actualiser les données" ci-dessus ou reconnectez-vous.
    """)

# Quick navigation
st.markdown("### 🧭 Navigation rapide")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🏠 Accueil", use_container_width=True):
        st.switch_page("gym_webapp.py")

with col2:
    if st.button("📊 Dashboard", use_container_width=True):
        st.switch_page("pages/01_Dashboard.py")

with col3:
    if st.button("💬 Chatbot", use_container_width=True):
        st.switch_page("pages/03_Chatbot.py")

with col4:
    if st.button("🏃‍♂️ Nouvelle séance", use_container_width=True):
        st.switch_page("pages/01_Commencer.py")

# Footer
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem; border-top: 1px solid #E6E6E6; margin-top: 2rem;'>
    <p>🔒 Vos données sont stockées localement et en sécurité</p>
    <p>💪 Continuez votre progression avec FormFit AI !</p>
</div>
""", unsafe_allow_html=True)