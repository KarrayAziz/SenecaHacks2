# pages/02_Exemples.py
import streamlit as st
from style_utils import load_css
from sidebar import render_sidebar # <-- IMPORTER

st.set_page_config(page_title="Pose Examples", page_icon="🖼️", layout="wide")
load_css()
render_sidebar() # <-- AFFICHER LA SIDEBAR

st.title("🖼️ Example Poses")
st.info("Here are some examples of correct postures to guide you.")

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