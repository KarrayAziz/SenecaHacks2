# pages/01_Commencer.py
import streamlit as st
from style_utils import load_css
from sidebar import render_sidebar # <-- IMPORTER

# (Imports pour les modules de détection)
from bicepcurls_detection import bicep_curl_tracker
from shoulderpress_detection import shoulder_press_tracker
from squats_detection import squat_tracker
from wallseat_detection import wall_sit_tracker
from deadlift_detection import deadlift_tracker

st.set_page_config(page_title="Start - FormFit AI", page_icon="💪", layout="wide")
load_css()
render_sidebar() # <-- AFFICHER LA SIDEBAR

# (get_mock_llm_response et EXERCISE_FUNCTIONS sont identiques)
def get_mock_llm_response(user_query, exercise):
    user_query = user_query.lower()
    if "sets" in user_query: return f"For {exercise}, 3 to 4 sets are recommended."
    if "posture" in user_query: return f"For good posture in {exercise}, keep your back straight and control the movement."
    if "rest" in user_query: return "A rest of 60 to 90 seconds is ideal."
    return "That's an excellent question. I am looking into it!"

EXERCISE_FUNCTIONS = {
    "Bicep Curls": bicep_curl_tracker,
    "Shoulder Press": shoulder_press_tracker,
    "Squats": squat_tracker,
    "Wall Sit": wall_sit_tracker,
    "Deadlift": deadlift_tracker,
}

if 'view' not in st.session_state:
    st.session_state.view = 'selection'

if st.session_state.view == 'selection':
    st.title("💪 Prepare Your Session")
    selected_exercise = st.selectbox("Available exercises:", list(EXERCISE_FUNCTIONS.keys()), index=None, placeholder="Click to choose...")
    if selected_exercise:
        if st.button(f"🚀 Start {selected_exercise}", use_container_width=True):
            # play_initial_audio() <-- SUPPRIMÉ
            st.session_state.selected_exercise = selected_exercise
            st.session_state.view = 'session'
            st.session_state.messages = [{"role": "assistant", "content": f"Hello! Ready for {selected_exercise}? Ask me your questions."}]
            st.session_state.rep_count = 0
            st.session_state.previous_feedback = ""
            if selected_exercise == "Bicep Curls":
                st.session_state.left_rep_count = 0
                st.session_state.right_rep_count = 0
            import time
            time.sleep(1)
            st.rerun()

elif st.session_state.view == 'session':
    selected_exercise = st.session_state.get("selected_exercise", "N/A")
    st.header(f"🔥 Session in progress: {selected_exercise}")

    col1, col2 = st.columns([3, 2])

    # --- Le placeholder audio est supprimé ---
    # audio_placeholder = st.empty() <-- SUPPRIMÉ

    with col1:
        tracker_function = EXERCISE_FUNCTIONS[selected_exercise]
        # --- Appel de la fonction sans le placeholder ---
        tracker_function() # <-- MODIFIÉ

    with col2:
        st.info("Live analysis is active.")
        if st.button("🛑 Stop Session", use_container_width=True):
            st.session_state.view = 'rest'
            st.rerun()

        st.markdown("---")
        st.subheader("🤖 AI Fitness Assistant")
        # (La logique du chat reste identique)
        if "messages" not in st.session_state: st.session_state.messages = []
        for msg in st.session_state.messages: st.chat_message(msg["role"]).write(msg["content"])
        if prompt := st.chat_input("Your question..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)
            with st.chat_message("assistant"):
                with st.spinner("..."): response = get_mock_llm_response(prompt, selected_exercise); st.write(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

elif st.session_state.view == 'rest':
    # (Cette partie reste identique)
    st.title("🎉 Session Finished! 🎉")
    st.balloons()
    selected_exercise = st.session_state.get("selected_exercise", "N/A")
    if selected_exercise == "Bicep Curls":
        reps_done = st.session_state.get('left_rep_count', 0) + st.session_state.get('right_rep_count', 0)
    else:
        reps_done = st.session_state.get('rep_count', 0)
    st.metric(label="Exercise", value=selected_exercise)
    st.metric(label="Completed Reps", value=f"{reps_done} reps")
    rest_time = 60 + (reps_done * 2)
    st.info(f"Rest for **{rest_time} seconds**.")
    if st.button("Do another exercise", use_container_width=True):
        st.session_state.view = 'selection'
        keys_to_pop = ['selected_exercise', 'rep_count', 'left_rep_count', 'right_rep_count', 'previous_feedback']
        for key in keys_to_pop:
            st.session_state.pop(key, None)
        st.rerun()