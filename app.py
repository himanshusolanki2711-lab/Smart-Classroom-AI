import streamlit as st
import os
from datetime import datetime
import google.generativeai as genai

# --- 1. INITIAL SETTINGS & SESSION STATE ---
st.set_page_config(page_title="AKTU AI Smart Campus", layout="wide")
BASE_DIR = "AKTU_University_Data"
os.makedirs(BASE_DIR, exist_ok=True)

# Session State for Security & Data
if 'user_db' not in st.session_state:
    st.session_state.user_db = {"Authority": "admin123", "Teacher": "teacher123", "Student": "student123", "Parent": "parent123"}

if 'aktu_portals' not in st.session_state:
    st.session_state.aktu_portals = {
        "AKTU_BTech_1st_Year_CS_A": {"pwd": "123", "yr": "1st Year", "sec": "CS-A"},
        "AKTU_BTech_2nd_Year_CS_B": {"pwd": "123", "yr": "2nd Year", "sec": "CS-B"},
        "AKTU_BTech_3rd_Year_CS_AI": {"pwd": "123", "yr": "3rd Year", "sec": "CS-AI"},
        "AKTU_BTech_4th_Year_CS_DS": {"pwd": "123", "yr": "4th Year", "sec": "CS-DS"}
    }

if 'chats' not in st.session_state: st.session_state.chats = {}
if 'reviews' not in st.session_state: st.session_state.reviews = []

# --- 2. SIDEBAR: LOGIN & AI SETTINGS ---
st.sidebar.title("🛡️ AKTU Secure Portal")

# --- 🔑 LIVE API KEY OPTION ---
with st.sidebar.expander("🤖 AI Settings (Gemini)"):
    user_api_key = st.text_input("AIzaSyCN6WgtYUCjtMSFcza8zWumohMw-mH399w", type="password")
    if user_api_key:
        try:
            genai.configure(api_key=user_api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            st.success("AI Active ✅")
            ai_ready = True
        except:
            st.error("Invalid Key ❌")
            ai_ready = False
    else:
        st.warning("AI Disabled (No Key) ⚠️")
        ai_ready = False

st.sidebar.markdown("---")
role = st.sidebar.selectbox("Select Role", ["Select Role", "Authority", "Teacher", "Student", "Parent"])

access_granted = False
if role != "Select Role":
    role_pwd = st.sidebar.text_input(f"Enter {role} Password", type="password")
    if role_pwd == st.session_state.user_db[role]:
        access_granted = True
        st.sidebar.success(f"Verified: {role}")
    elif role_pwd != "":
        st.sidebar.error("Wrong Role Password")

# --- 3. MAIN DASHBOARD ---
if access_granted:
    st.title(f"🎓 AKTU Campus - {role} Dashboard")
    
    # Section Selection
    all_portals = list(st.session_state.aktu_portals.keys())
    selected_sec = st.selectbox("Choose Your Section", ["--- Select ---"] + all_portals)
    
    if selected_sec != "--- Select ---":
        # LEVEL 2 KEY
        sec_key = st.text_input("Enter Section Secret Key (123)", type="password")
        
        if sec_key == st.session_state.aktu_portals[selected_sec]["pwd"]:
            p_info = st.session_state.aktu_portals[selected_sec]
            st.success(f"Inside: {p_info['yr']} | Section {p_info['sec']}")
            
            # TABS
            t1, t2, t3, t4 = st.tabs(["📂 Archive", "🎙️ AI Notes", "💬 Class Chat", "👥 Profiles"])

            # --- TAB 1: ARCHIVE HUB ---
            with t1:
                st.subheader("📚 Subject Repository")
                subj = st.text_input("Subject Name (e.g. Maths)")
                if role == "Teacher" and subj:
                    up_file = st.file_uploader("Upload Notes")
                    if up_file and st.button("Save to Archive"):
                        today = datetime.now().strftime("%Y-%m-%d")
                        path = os.path.join(BASE_DIR, "BTech", p_info['yr'], p_info['sec'], subj, today)
                        os.makedirs(path, exist_ok=True) # Fixed Fix ✅
                        with open(os.path.join(path, up_file.name), "wb") as f:
                            f.write(up_file.getbuffer())
                        st.success("Archived Successfully!")
                
                if subj:
                    base_p = os.path.join(BASE_DIR, "BTech", p_info['yr'], p_info['sec'], subj)
                    if os.path.exists(base_p):
                        for dt in os.listdir(base_p):
                            with st.expander(f"📅 Date: {dt}"):
                                for f in os.listdir(os.path.join(base_p, dt)):
                                    st.write(f"📄 {f}")
                    else: st.info("No data yet.")

            # --- TAB 2: AI NOTES ---
            with t2:
                st.subheader("🤖 4-Way Note Generator")
                raw_data = st.text_area("Paste Transcript:")
                if st.button("Generate"):
                    if ai_ready and raw_data:
                        with st.spinner("Processing..."):
                            res = model.generate_content(f"Format into Detailed, Short, Bullets, and Revision: {raw_data}")
                            st.markdown(res.text)
                    elif not ai_ready: st.error("Pehle Sidebar mein API Key dalo!")

            # --- TAB 3: CHAT ---
            with t3:
                st.subheader("💬 Private Class Chat")
                if selected_sec not in st.session_state.chats: st.session_state.chats[selected_sec] = []
                for m in st.session_state.chats[selected_sec]:
                    with st.chat_message(m["role"]): st.write(f"**{m['u']}:** {m['t']}")
                
                msg = st.chat_input("Type message...")
                if msg:
                    st.session_state.chats[selected_sec].append({"role": "user" if role=="Student" else "assistant", "u": role, "t": msg})
                    st.rerun()

            # --- TAB 4: PROFILES ---
            with t4:
                st.subheader("👥 Student Profiles (Dummy)")
                st.json([{"Name": "Aman", "Year": p_info['yr'], "Status": "Active"}, {"Name": "Priya", "Year": p_info['yr'], "Status": "Active"}])

        elif sec_key != "": st.error("Wrong Section Key")
else:
    st.title("🏛️ AKTU AI Smart Campus")
    st.info("Log in from the sidebar. (Tip: student123 / 123)")
