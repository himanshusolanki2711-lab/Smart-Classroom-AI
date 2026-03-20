import streamlit as st
import google.generativeai as genai
import speech_recognition as sr
from PIL import Image
import fitz  # PyMuPDF
import os

# --- 1. CONFIG ---
genai.configure(api_key="AIzaSyCN6WgtYUCjtMSFcza8zWumohMw-mH399w")
model = genai.GenerativeModel('gemini-1.5-flash')

# Session States
if 'recording' not in st.session_state: st.session_state['recording'] = False

st.set_page_config(page_title="AI Smart Campus Pro", layout="wide")

def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# --- 2. AUTHENTICATION ---
st.sidebar.title("🔐 Secure Login")
role = st.sidebar.selectbox("Select Role", ["Student", "Parent", "Teacher", "Authority", "Admin"])
pwd = st.sidebar.text_input("Password", type="password")

if pwd == "bhai123":
    st.title(f"🚀 {role} Dashboard")
    
    tabs = st.tabs(["🔬 PYQ Frequency", "🎙️ Live Lecture", "👤 Student Profile", "🔍 Doubt Solver"])

    # --- TAB 1: PYQ ANALYSIS ---
    with tabs[0]:
        st.subheader("📑 Past Year Paper Analysis")
        pyq_files = st.file_uploader("Upload 1 or More Papers", accept_multiple_files=True, type=['pdf', 'jpg', 'png'])
        
        if pyq_files:
            st.success(f"{len(pyq_files)} Files Received")
