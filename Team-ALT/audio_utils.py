# audio_utils.py
import streamlit as st
from gtts import gTTS
import io
import base64

# This part is unchanged
def get_autoplay_audio_html(audio_base64):
    return f'''
        <audio id="tts-audio" autoplay="true" src="data:audio/mp3;base64,{audio_base64}">
        </audio>
    '''

def text_to_speech(text, language='en'):
    try:
        audio_fp = io.BytesIO()
        tts = gTTS(text=text, lang=language)
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        audio_base64 = base64.b64encode(audio_fp.read()).decode('utf-8')
        return get_autoplay_audio_html(audio_base64)
    except Exception as e:
        print(f"Error in TTS: {e}")
        return None

def play_initial_audio():
    audio_html = text_to_speech("Session started")
    if audio_html:
        st.session_state['initial_audio_played'] = True 
        st.markdown(audio_html, unsafe_allow_html=True)
        
# --- NEW FUNCTION TO BE CALLED FROM INSIDE THE LOOP ---
def speak_feedback(placeholder, new_feedback):
    """
    Checks if feedback has changed and plays audio if it has.
    This function is designed to be called repeatedly inside a loop.
    """
    # Initialize the state if it's the first run
    if "previous_feedback" not in st.session_state:
        st.session_state.previous_feedback = ""

    # If the feedback is new and not empty, play the sound
    if new_feedback and new_feedback != st.session_state.previous_feedback:
        # Update the state immediately to prevent re-playing
        st.session_state.previous_feedback = new_feedback
        
        # Generate and play audio
        audio_html = text_to_speech(new_feedback)
        if audio_html:
            placeholder.markdown(audio_html, unsafe_allow_html=True)