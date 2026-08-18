import base64
from datetime import date
import os
import pandas as pd
from sqlalchemy import create_engine, text
import streamlit as st

# --- CONFIGURATION ---
st.set_page_config(page_title="JUC Portal", layout="wide")

# --- TRADUCTIONS ---
def get_translations():
    return {
        "English": {"title": "JUC Portal", "weekly": "Weekly Report", "strat": "Strategic Pillar Report", "dept": "Department", "submit": "Submit", "lang": "Language", "pillar": "Strategic Pillar", "dash": "📊 Dashboard", "admin": "⚙️ Admin"},
        "Français": {"title": "Portail JUC", "weekly": "Rapport Hebdomadaire", "strat": "Rapport par Pilier Stratégique", "dept": "Département", "submit": "Soumettre", "lang": "Langue", "pillar": "Pilier Stratégique", "dash": "📊 Tableau de Bord", "admin": "⚙️ Admin"}
    }

if "lang" not in st.session_state: st.session_state.lang = "English"
trans = get_translations()

# --- CONNEXION BASE DE DONNÉES NEON ---
try:
    engine = create_engine(st.secrets["DATABASE_URL"])
except Exception as e:
    st.error("Erreur de connexion à la base de données. Vérifiez vos secrets Streamlit.")
    engine = None

# --- BACKGROUND & STYLE ---
default_bg_name = "background.jpg"
if "bg_base64" not in st.session_state or not st.session_state.bg_base64:
    if os.path.exists(default_bg_name):
        with open(default_bg_name, "rb") as image_file:
            st.session_state.bg_base64 = base64.b64encode(image_file.read()).decode()
    else: st.session_state.bg_base64 = ""

bg_css = f"url('data:image/jpeg;base64,{st.session_state.bg_base64}')" if st.session_state.bg_base64 else "none"

st.markdown(f"""
    <style>
    .stApp {{ background-image: {bg_css} !important; background-size: cover; background-attachment: fixed; }}
    .main .block-container {{ background: rgba(255, 255, 255, 0.93); padding: 2.5rem; border-radius: 15px; backdrop-filter: blur(8px); }}
    /* Style professionnel zones de texte */
    textarea {{ font-family: 'Arial', sans-serif !important; font-size: 16px !important; line-height: 1.5 !important; border: 2px solid #cbd5e1 !important; border-radius: 8px !important; }}
    textarea:focus {{ border-color: #3b82f6 !important; outline: none !important; }}
    </style>
""", unsafe_allow_html=True)

# --- NAVIGATION ---
t = trans[st.session_state.lang]
st.sidebar.subheader(t["lang"])
st.session_state.lang = st.sidebar.selectbox("", ["English", "Français"])
password = st.sidebar.text_input("Password", type="password")

if password != "JUC2026Secure":
    st.warning("Access Restricted. Please enter the password.")
    st.stop()

menu = st.sidebar.radio(t["title"], [t["weekly"], t["strat"], t["dash"], t["admin"]])

# --- 1. RAPPORT HEBDOMADAIRE ---
if menu == t["weekly"]:
    st.header(t["weekly"])
    with st.form("weekly_form"):
        col1, col2 = st.columns(2)
        staff_name = col1.text_input("Full Name")
        submission_date = col2.date_input("Date", value=date.today())
        
        completed = st.text_area("Activities completed")
        st.caption("💡 Use numbered list: 1. Activity... 2. Activity...")
        
        pending = st.text_area("Projections for next week")
        st.caption("💡 Use numbered list: 1. Next task... 2. Next task...")
        
        challenges = st.text_area("Challenges Encountered")
        
        if st.form_submit_button(t["submit"]):
            if not staff_name:
                st.warning("Please enter your full name.")
            elif engine:
                try:
                    with engine.connect() as conn:
                        query = text("""
                            INSERT INTO juc_reports (staff_name, submission_date, completed_activities, pending_issues, challenges) 
                            VALUES (:name, :date, :completed, :pending, :challenges)
                        """)
                        conn.execute(query, {
                            "name": staff_name, 
                            "date": submission_date, 
                            "completed": completed, 
                            "pending": pending, 
                            "challenges": challenges
                        })
                        conn.commit()
                    st.success("✅ Report submitted and saved to Neon Database!")
                except Exception as ex:
                    st.error(f"Error saving to database: {ex}")

# --- 2. DASHBOARD ---
elif menu == t["dash"]:
    st.header(t["dash"])
    if engine:
        try:
            df = pd.read_sql("SELECT * FROM juc_reports ORDER BY id DESC", engine)
            st.dataframe(df, use_container_width=True)
        except Exception as ex:
            st.info("No reports found yet or table needs to be created.")

# --- 3. ADMIN ---
elif menu == t["admin"]:
    st.header(t["admin"])
    st.warning("⚠️ Administrative actions affect live database records.")
    
    if st.button("🗑️ DELETE ALL REPORTS"):
        if engine:
            try:
                with engine.connect() as conn:
                    conn.execute(text("DELETE FROM juc_reports"))
                    conn.commit()
                st.success("All reports have been permanently deleted.")
                st.rerun()
            except Exception as ex:
                st.error(f"Error clearing data: {ex}")
