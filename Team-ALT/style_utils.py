# style_utils.py

import streamlit as st

def load_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');
        html, body, [class*="st-"] {
            font-family: 'Montserrat', sans-serif;
        }
        .stApp {
            background-color: #111111;
            color: #F0F0F0;
        }
        [data-testid="stSidebar"] {
            background-color: #1E1E1E;
            border-right: 2px solid #FF4500;
            overflow-x: hidden;
        }
        [data-testid="stSidebar"] h1 {
            color: #FF4500 !important;
            text-shadow: none;
        }
        .stButton>button {
            border: 2px solid #FF4500;
            border-radius: 25px;
            color: #FF4500;
            background-color: transparent;
            padding: 10px 25px;
            font-weight: 600;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .stButton>button:hover {
            background-color: #FF4500;
            color: #ffffff;
            box-shadow: 0 0 15px #FF4500;
        }
        .st-emotion-cache-1wivap2 {
            background-color: rgba(255, 69, 0, 0.1);
            border-left: 5px solid #FF4500;
        }
    </style>
    """, unsafe_allow_html=True)