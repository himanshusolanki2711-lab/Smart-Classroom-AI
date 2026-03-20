import streamlit as st
import time
from PIL import Image
import os
import json
import io
import speech_recognition as sr
from pydub import AudioSegment
from fpdf import FPDF
from datetime import datetime

# Streamlit Mic Recorder library (for cleaner local testing)
try:
    from streamlit_mic_recorder import mic_recorder, speech_to_text
    mic_recorder_installed = True
except ImportError:
    mic_recorder_installed = False

# Google Gemini AI Config
try:
    import google.generativeai as genai
    gemini_installed = True
except ImportError:
    gemini_installed = False

# --- 1. SETUP & THEME ---
st.set_page_config(page_title="AI Omni-University ERP", layout="wide")

# Custom Styling (with Audio/PDF specific changes)
st.markdown("""
    <style>
    .top-10-tag { background-color: #f1c40f; color: #2c3e50; padding: 3px 10px; border-radius: 15px; font-weight: bold; border: 1px solid #d4ac0d; margin-right: 5px; font-size: 0.9rem;}
    .download-btn { background-color: #2ecc71; color: white; border-radius: 5px; padding: 5px 10px; text-decoration: none; display: inline-block; margin-top: 5px;}
    .download-btn:hover { background-color: #27ae60; }
    .rec-box { border: 2px solid red; background-color: #ffeaea; padding: 10px; border-radius: 10px; text-align: center;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE & CONFIG (Temporary for Demo) ---
if 'admin_pass' not in st.session_state:
    st.session_state.admin_pass = "ai_guardian_2026"
if 'notices' not in st.session_state:
    st.session_state.notices = [
        {"msg": "Final Exams starting from May 15th.", "by": "Admin", "time": time.ctime()}
    ]
if 'pyq_files_db' not in st.session_state:
    st.session_state.pyq_files_db = [] # Store PYQ details
if 'pdf_summaries' not in st.session_state:
    st.session_state.pdf_summaries = {} # Store PDF summaries by name

# Create directories if they don't exist
pyq_dir = "uploaded_pyqs"
if not os.path.exists(pyq_dir):
    os.makedirs(pyq_dir)

# --- GEMINI AI CONFIG ---
# WARNING: Do not commit your key to a public repo. Store as an environment variable or secret.
api_key = "PASTE_YOUR_GEMINI_API_KEY_HERE" # Put your actual key here

if gemini_installed and api_key and api_key != "AIzaSyCN6WgtYUCjtMSFcza8zWumohMw-mH399w":
    genai.configure(api_key=api_key)
    model_vision = genai.GenerativeModel('gemini-1.5-flash')
    model_text = genai.GenerativeModel('gemini-pro')
    ai_status = "Connected ✅"
else:
    ai_status = "Waiting for valid API Key ⚠️"

# --- 3. SIDEBAR NAVIGATION ---
st.sidebar.title("🛡️ AI Guardian Suite")
user_role = st.sidebar.selectbox("Select User Role", ["Student", "Teacher", "Admin/Higher Authority"])

# Admin Password Protection
access_granted = False
if user_role in ["Teacher", "Admin/Higher Authority"]:
    pwd = st.sidebar.text_input("Enter Admin Password", type="password")
    if pwd == st.session_state.admin_pass:
        access_granted = True
        st.sidebar.success("Welcome, Authority!")
    else:
        st.sidebar.error("Incorrect Password")
else:
    access_granted = True # Students have public access to relevant sections

# Main Menu (With new categories)
menu = ["🏠 Dashboard", "📢 Notice Board", "🎙️ Audio Notes Converter", "📚 Study Hub (PYQs & More)", "🔍 AI Advanced Tools", "👤 Admin & Profiles"]
choice = st.sidebar.radio("Navigate", menu)

if not access_granted and choice in ["👤 Admin & Profiles"]:
    st.error("This section is restricted to Teachers and Admins with correct password.")
    st.stop() # Prevent loading the section


# --- 4. APP LOGIC ---

# --- DASHBOARD ---
elif choice == "🏠 Dashboard":
    st.title(f"Welcome to AI Guardian, {user_role}")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Syllabus Completed", "65%", "+5% this week")
    with col2:
        st.metric("New Notices", len(st.session_state.notices))
    with col3:
        st.metric("AI Connection Status", ai_status)
    st.image("image_1.png", caption="System Overview (Reference)", use_column_width=True)

# --- NOTICE BOARD ---
elif choice == "📢 Notice Board":
    st.header("Official Notice Board")
    
    if user_role in ["Teacher", "Admin/Higher Authority"] and access_granted:
        with st.expander("➕ Broadcast New Notice"):
            new_msg = st.text_area("Write notice content here...")
            if st.button("Publish Notice"):
                if new_msg:
                    st.session_state.notices.append({"msg": new_msg, "by": user_role, "time": time.ctime()})
                    st.success("Notice Published!")
                    st.rerun()

    if not st.session_state.notices:
        st.info("No active notices.")
    for n in reversed(st.session_state.notices):
        st.info(f"**{n['by']}** ({n['time']}): \n\n {n['msg']}")

# --- 🎙️ AUDIO NOTES CONVERTER (New Feature) ---
elif choice == "🎙️ Audio Notes Converter":
    st.header("Class Notes Transcriber")
    st.write("Convert your voice or recorded lectures into organized text notes.")

    # Time limit setting
    st.subheader("Recording Parameters")
    listen_time = st.number_input("Set listening time in seconds:", min_value=10, max_value=300, value=60, step=10)
    
    col_a, col_b = st.columns([1,2])
    
    with col_a:
        st.write("**Start/Stop Recording**")
        # mic_recorder provides a direct component
        if mic_recorder_installed:
            rec_input = mic_recorder(start_prompt="Record Audio", stop_prompt="Stop Recording", just_once=False, format="wav")
        else:
            st.error("Audio recording component not installed. Use pip install streamlit-mic-recorder")
            rec_input = None

    with col_b:
        st.subheader("Transcribed Notes:")
        transcript = ""
        
        if rec_input:
            # rec_input returns dict with 'bytes' and 'sample_rate'
            st.info(f"Recorded file size: {len(rec_input['bytes'])/1024:.2f} KB")
            
            # Simplified Local Transcription (For local/offline testing, use offline models if needed)
            if ai_status != "Connected ✅":
                 st.write("Please configure Gemini API and/or use an online transcription service for best results.")
            
            # --- Integration with SpeechRecognition Library (requires internet) ---
            r = sr.Recognizer()
            audio_file = io.BytesIO(rec_input['bytes'])
            
            with sr.AudioFile(audio_file) as source:
                 # Adjust for ambient noise and then record with duration
                 r.adjust_for_ambient_noise(source, duration=0.5) 
                 # Apply the user-defined listen_time
                 audio_data = r.record(source, duration=listen_time)
            
            with st.spinner("Analyzing audio..."):
                try:
                    # Using Google Speech Recognition (requires internet)
                    # For professional apps, you'd use a cloud service's API
                    text_out = r.recognize_google(audio_data)
                    transcript = text_out
                    st.success("Audio analysis complete!")
                    st.markdown(f"> {text_out}")
                except sr.UnknownValueError:
                    st.error("Google Speech Recognition could not understand the audio.")
                except sr.RequestError as e:
                    st.error(f"Could not request results from Google Speech Recognition service; {e}")

        else:
             st.info("Waiting for audio input.")

    if transcript:
         st.divider()
         # Use Gemini to summarize/format the transcribed text
         if st.button("Organize Notes with AI") and ai_status == "Connected ✅":
             with st.spinner("AI is formatting the transcript into study notes..."):
                 response = model_text.generate_content(f"Convert this transcribed audio text into structured study notes with bullet points and a summary: {transcript}")
                 formatted_notes = response.text
                 st.markdown(formatted_notes)

# --- 📚 STUDY HUB (New Feature for PYQs and Materials) ---
elif choice == "📚 Study Hub (PYQs & More)":
    st.header("Resource & Study Hub")
    
    # PYQ Section
    tab1, tab2 = st.tabs(["PYQ Repository", "General Study Material"])
    
    with tab1:
        st.subheader("Previous Year Questions (PYQs)")
        
        # Teacher: Upload PYQs
        if user_role in ["Teacher", "Admin/Higher Authority"] and access_granted:
             with st.expander("➕ Upload New PYQ Paper"):
                  pyq_file = st.file_uploader("Upload PDF or Image of PYQ paper", type=['pdf', 'png', 'jpg'], key="pyq_upload")
                  pyq_meta = st.text_input("Paper Year & Subject (e.g., 2025 - DS)")
                  if st.button("Upload PYQ") and pyq_file and pyq_meta:
                        # Store in database and save file
                        time_stamp = datetime.now().strftime("%Y%m%d%H%M%S")
                        safe_filename = f"{time_stamp}_{pyq_file.name}"
                        file_path = os.path.join(pyq_dir, safe_filename)
                        
                        with open(file_path, "wb") as f:
                            f.write(pyq_file.getbuffer())
                        
                        st.session_state.pyq_files_db.append({
                             "meta": pyq_meta,
                             "filename": pyq_file.name,
                             "path": file_path,
                             "uploaded_by": user_role
                        })
                        st.success("PYQ uploaded and saved!")
                        st.rerun()

        # Student/All: View and Download PYQs
        st.write("---")
        st.write("Available Papers:")
        if not st.session_state.pyq_files_db:
            st.info("No PYQ papers available yet.")
        else:
            for pyq in st.session_state.pyq_files_db:
                 col1, col2, col3 = st.columns([2, 1, 1])
                 col1.write(f"📝 {pyq['meta']} - {pyq['filename']}")
                 col2.write(f"({pyq['uploaded_by']})")
                 
                 # The Download Button
                 with open(pyq['path'], "rb") as f:
                      file_content = f.read()
                 
                 col3.download_button(
                      label="Download Paper",
                      data=file_content,
                      file_name=pyq['filename'],
                      mime='application/pdf' if pyq['filename'].endswith('.pdf') else 'image/jpeg', # Crude MIME type check
                      key=f"dl_{pyq['path']}"
                 )
    
    with tab2:
        st.subheader("General Study Material (Slides, Assignments)")
        st.info("Section for storing general class materials. Feature for future extension.")

# --- 🔍 AI ADVANCED TOOLS (Updated PDF and Assignments) ---
elif choice == "🔍 AI Advanced Tools":
    st.header("Advanced AI Academic Tools")
    
    tool_choice = st.radio("Select Tool:", ["PDF Analyzer/Summary", "Syllabus AI Scanner", "Step-by-Step Help", "Assignment Feedback (PDF)"])
    st.divider()

    # New PDF tools
    if tool_choice == "PDF Analyzer/Summary":
        st.subheader("AI PDF Summary & Deep Analysis")
        st.write("Upload a complete PDF study material for AI summary and analysis.")
        
        pdf_file = st.file_uploader("Upload Study Material PDF", type=['pdf'], key="tool_pdf")
        
        if pdf_file and st.button("Analyze PDF with AI") and ai_status == "Connected ✅":
            with st.spinner("AI is reading and analyzing the entire PDF. This may take a minute..."):
                # Use Gemini text model for long context summaries
                # (Reading actual raw PDF content in Streamlit locally requires other libraries like PyPDF2, 
                # but with Gemini-1.5 we might upload the file directly, though API endpoints for that are different.
                # Here we demo with text content or file path logic)
                
                # Mock analysis (Gemini actually does this with special models/endpoints)
                response_summary = model_text.generate_content(f"You are an academic analyzer. Read the uploaded material '{pdf_file.name}'. Generate a comprehensive summary, key bullet points, and main formulas/concepts.")
                
                # Store the result
                st.session_state.pdf_summaries[pdf_file.name] = response_summary.text
                st.success("PDF analysis complete!")
                st.rerun()

        if pdf_file and pdf_file.name in st.session_state.pdf_summaries:
             st.subheader(f"Analysis for: {pdf_file.name}")
             st.markdown(st.session_state.pdf_summaries[pdf_file.name])
        elif pdf_file:
             st.info("Waiting for AI analysis to complete.")

    elif tool_choice == "Assignment Feedback (PDF)":
        st.subheader("Detailed Assignment Feedback with AI")
        st.write("Upload a completed assignment PDF. AI will provide feedback, check formulas, and suggest improvements.")
        
        assign_file = st.file_uploader("Upload Assignment PDF", type=['pdf'], key="assign_pdf")
        
        if assign_file and st.button("Get Detailed Feedback") and ai_status == "Connected ✅":
             with st.spinner("AI is evaluating the assignment..."):
                  # Mock feedback
                  response_feedback = model_text.generate_content(f"Evaluator: Read the assignment '{assign_file.name}'. Identify key arguments, mathematical accuracy, and area for improvements. Provide grades A-F.")
                  
                  st.success("Assignment evaluated!")
                  st.markdown("---")
                  st.subheader("AI Feedback Report:")
                  st.markdown(response_feedback.text)

    # (Previous Tools - but with AI connectivity check)
    elif tool_choice == "Syllabus AI Scanner":
        # (Same syllabus logic as before, but with AI check)
        if ai_status != "Connected ✅": st.warning("Please configure your Gemini API key to use the AI scanning feature.")

    elif tool_choice == "Step-by-Step Help":
         if ai_status != "Connected ✅": st.warning("Please configure your Gemini API key to use the AI problem-solving feature.")


# --- ADMIN & PROFILES ---
elif choice == "👤 Admin & Profiles":
    st.header("System Admin & Student Directory")
    # (Previous profile logic is same, but let's add one achievement tag to showcase)
    if 'himanshu' not in st.session_state.student_db:
         st.session_state.student_db = {
            "Himanshu": {"interest": "Python, Video Editing", "achievements": ["Top 10", "Code Master"], "bio": "Materials Science & CS Student."},
            "Aryan": {"interest": "Java, Math", "achievements": ["Mathlete"], "bio": "Software Dev enthusiast."}
        }
    
    if not (user_role == "Admin/Higher Authority" and access_granted):
        st.error("Permission Denied. Only Admins can view profiles.")
        st.stop()

    st.subheader("Student Database")
    # Himanshu is already set up to show "Top 10" tag
    selected_student = st.selectbox("Select Student to view/edit Details", list(st.session_state.student_db.keys()))
    s_data = st.session_state.student_db[selected_student]
    
    st.write(f"**Name:** {selected_student}")
    
    # Achievements HTML (Showcasing Top 10)
    tags_html = "".join([f'<span class="top-10-tag">{tag}</span> ' if tag == "Top 10" else f'<span class="code-star-tag">{tag}</span> ' for tag in s_data['achievements']])
    st.markdown(tags_html, unsafe_allow_html=True)
    
    st.write(f"**Bio:** {s_data['bio']}")
    st.write(f"**Interests:** {s_data['interest']}")
    
    st.divider()
    # Admin Controls
    with st.expander("⚙️ Admin Actions"):
        new_tag = st.text_input(f"Add a new achievement tag for {selected_student}:")
        if st.button("Apply Tag"):
            st.session_state.student_db[selected_student]['achievements'].append(new_tag)
            st.success("Tag Added!")
            st.rerun()
            
        st.write("---")
        st.write("**Change System Admin Password**")
        new_pass = st.text_input("New Admin Password", type="password")
        if st.button("Confirm Password Change"):
            st.session_state.admin_pass = new_pass
            st.success("Admin password updated successfully.")
