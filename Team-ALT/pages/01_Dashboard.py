import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from auth.authenticator import get_authenticator
from database.models import WorkoutTracker
from style_utils import load_css
from sidebar import render_sidebar

# Page configuration
st.set_page_config(
    page_title="FormFit AI - Dashboard",
    page_icon="📊",
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

# Show user menu in sidebar
auth.show_user_menu()

# Get user data
user_data = auth.get_user_data()
if not user_data:
    st.error("Erreur: Impossible de charger les données utilisateur")
    st.stop()

# Initialize workout tracker
workout_tracker = WorkoutTracker(auth.db_manager)

# Page title
st.markdown(f"""
<div style='text-align: center; padding: 1rem 0;'>
    <h1 style='color: #FF4B4B; margin-bottom: 0.5rem;'>📊 Dashboard - {user_data['name']}</h1>
    <p style='color: #666; font-size: 1.1rem;'>Suivi de vos progrès et statistiques</p>
</div>
""", unsafe_allow_html=True)

# Get workout statistics
stats = workout_tracker.get_workout_stats(user_data['id'])
recent_workouts = workout_tracker.get_user_workouts(user_data['id'], limit=10)

# Key Metrics Cards
st.markdown("## 🎯 Statistiques clés")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #FF4B4B20, #FF758F20); 
                padding: 1.5rem; border-radius: 1rem; text-align: center;'>
        <h2 style='color: #FF4B4B; margin: 0; font-size: 2rem;'>{stats['total_workouts']}</h2>
        <p style='margin: 0.5rem 0 0 0; font-weight: 600;'>Séances totales</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #FF4B4B20, #FF758F20); 
                padding: 1.5rem; border-radius: 1rem; text-align: center;'>
        <h2 style='color: #FF4B4B; margin: 0; font-size: 2rem;'>{stats['workouts_this_week']}</h2>
        <p style='margin: 0.5rem 0 0 0; font-weight: 600;'>Cette semaine</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #FF4B4B20, #FF758F20); 
                padding: 1.5rem; border-radius: 1rem; text-align: center;'>
        <h2 style='color: #FF4B4B; margin: 0; font-size: 2rem;'>{int(stats['total_calories'])}</h2>
        <p style='margin: 0.5rem 0 0 0; font-weight: 600;'>Calories brûlées</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #FF4B4B20, #FF758F20); 
                padding: 1.5rem; border-radius: 1rem; text-align: center;'>
        <h2 style='color: #FF4B4B; margin: 0; font-size: 2rem;'>{stats['avg_form_score']}/10</h2>
        <p style='margin: 0.5rem 0 0 0; font-weight: 600;'>Score forme moyen</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Progress towards goal
if user_data['current_weight'] and user_data['goal_weight']:
    current_weight = user_data['current_weight']
    goal_weight = user_data['goal_weight']
    weight_diff = abs(current_weight - goal_weight)
    progress_percentage = max(0, min(100, ((current_weight - goal_weight) / weight_diff * 100) if weight_diff > 0 else 100))
    
    st.markdown("## 🎯 Progrès vers l'objectif")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Progress bar
        st.progress(progress_percentage / 100)
        st.markdown(f"**Poids actuel:** {current_weight} kg | **Objectif:** {goal_weight} kg")
    
    with col2:
        if current_weight > goal_weight:
            remaining = current_weight - goal_weight
            st.markdown(f"""
            <div style='text-align: center; padding: 1rem; background: #FFF3CD; border-radius: 0.5rem;'>
                <p style='margin: 0; font-weight: 600; color: #856404;'>
                    {remaining:.1f} kg à perdre
                </p>
            </div>
            """, unsafe_allow_html=True)
        elif current_weight < goal_weight:
            remaining = goal_weight - current_weight
            st.markdown(f"""
            <div style='text-align: center; padding: 1rem; background: #D1ECF1; border-radius: 0.5rem;'>
                <p style='margin: 0; font-weight: 600; color: #0C5460;'>
                    {remaining:.1f} kg à gagner
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style='text-align: center; padding: 1rem; background: #D4EDDA; border-radius: 0.5rem;'>
                <p style='margin: 0; font-weight: 600; color: #155724;'>
                    🎉 Objectif atteint!
                </p>
            </div>
            """, unsafe_allow_html=True)

# Charts section
if recent_workouts:
    st.markdown("## 📈 Visualisations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Répartition des exercices")
        
        # Create exercise distribution chart
        exercise_counts = {}
        for workout in recent_workouts:
            exercise_type = workout['exercise_type']
            exercise_counts[exercise_type] = exercise_counts.get(exercise_type, 0) + 1
        
        if exercise_counts:
            fig_pie = px.pie(
                values=list(exercise_counts.values()),
                names=list(exercise_counts.keys()),
                color_discrete_sequence=['#FF4B4B', '#FF758F', '#FFA07A', '#FFB6C1', '#FFC0CB']
            )
            fig_pie.update_layout(showlegend=True, height=400)
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.markdown("### Score de forme par séance")
        
        # Create form score timeline
        workout_dates = []
        form_scores = []
        for workout in reversed(recent_workouts):  # Show chronologically
            if workout['form_score']:
                workout_dates.append(workout['workout_date'])
                form_scores.append(workout['form_score'])
        
        if form_scores:
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(
                x=workout_dates,
                y=form_scores,
                mode='lines+markers',
                name='Score de forme',
                line=dict(color='#FF4B4B', width=3),
                marker=dict(size=8)
            ))
            fig_line.update_layout(
                height=400,
                yaxis_title="Score (sur 10)",
                xaxis_title="Date",
                yaxis=dict(range=[0, 10])
            )
            st.plotly_chart(fig_line, use_container_width=True)

# Recent workouts table
st.markdown("## 📝 Séances récentes")

if recent_workouts:
    # Convert to DataFrame for better display
    df_workouts = pd.DataFrame(recent_workouts)
    
    # Format the dataframe
    df_display = df_workouts.copy()
    df_display['workout_date'] = pd.to_datetime(df_display['workout_date']).dt.strftime('%d/%m/%Y %H:%M')
    df_display = df_display[['workout_date', 'exercise_type', 'reps', 'sets', 'duration', 'form_score', 'calories_burned']]
    df_display.columns = ['Date', 'Exercice', 'Répétitions', 'Séries', 'Durée (min)', 'Score forme', 'Calories']
    
    # Fill NaN values
    df_display = df_display.fillna('-')
    
    st.dataframe(df_display, use_container_width=True, hide_index=True)
else:
    st.info("Aucune séance d'entraînement enregistrée. Commencez votre première séance!")

# Quick actions
st.markdown("## ⚡ Actions rapides")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🏃‍♂️ Nouvelle séance", use_container_width=True, type="primary"):
        st.switch_page("pages/01_Commencer.py")

with col2:
    if st.button("👤 Modifier profil", use_container_width=True):
        st.switch_page("pages/02_Profile.py")

with col3:
    if st.button("💬 Chatbot fitness", use_container_width=True):
        st.switch_page("pages/03_Chatbot.py")

with col4:
    if st.button("📊 Exercices spécifiques", use_container_width=True):
        # Show available exercises
        exercises = [
            ("Squats", "pages/squats_detection.py"),
            ("Bicep Curls", "pages/bicepcurls_detection.py"),
            ("Deadlift", "pages/deadlift_detection.py"),
            ("Shoulder Press", "pages/shoulderpress_detection.py"),
            ("Wall Seat", "pages/wallseat_detection.py")
        ]
        
        selected_exercise = st.selectbox(
            "Choisir un exercice:",
            options=[ex[0] for ex in exercises],
            key="exercise_selector"
        )
        
        for name, page in exercises:
            if selected_exercise == name:
                if st.button(f"Commencer {name}", key=f"start_{name}"):
                    st.switch_page(page)
                break

# Motivational section
st.markdown("## 💪 Motivation du jour")

motivational_quotes = [
    "La seule mauvaise séance d'entraînement est celle que vous ne faites pas! 💪",
    "Chaque répétition vous rapproche de votre objectif! 🎯",
    "La constance bat la perfection. Continuez! 🔥",
    "Votre corps peut le faire. C'est votre esprit qu'il faut convaincre! 🧠",
    "Transformez vos 'je ne peux pas' en 'je le ferai'! ✨"
]

import random
daily_quote = random.choice(motivational_quotes)

st.markdown(f"""
<div style='text-align: center; background: linear-gradient(135deg, #FF4B4B20, #FF758F20);
            padding: 2rem; border-radius: 1rem; margin: 2rem 0;'>
    <h3 style='color: #FF4B4B; margin-bottom: 1rem;'>💫 Citation inspirante</h3>
    <p style='font-size: 1.2rem; font-style: italic; margin: 0;'>{daily_quote}</p>
</div>
""", unsafe_allow_html=True)

# Footer with tips
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p><strong>💡 Conseil:</strong> Utilisez régulièrement notre système d'analyse pour améliorer votre forme et prévenir les blessures!</p>
</div>
""", unsafe_allow_html=True)