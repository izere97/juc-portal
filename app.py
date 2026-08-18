import base64
from datetime import date, datetime
import io
import os
import pandas as pd
from docx import Document
from sqlalchemy import create_engine, text
import streamlit as st

# --- CONFIGURATION ---
st.set_page_config(page_title="JUC Portal", layout="wide")

# --- TRADUCTIONS ---
def get_translations():
    return {
        "English": {"title": "JUC Portal", "weekly": "Weekly Report", "strat": "Strategic Pillar Report", "dept": "Department", "submit": "Submit", "lang": "Language", "pillar": "Strategic Pillar", "dash": "📊 Bubble Dashboard", "admin": "⚙️ Admin"},
        "Français": {"title": "Portail JUC", "weekly": "Rapport Hebdomadaire", "strat": "Rapport par Pilier Stratégique", "dept": "Département", "submit": "Soumettre", "lang": "Langue", "pillar": "Pilier Stratégique", "dash": "📊 Tableau de Bord en Bulles", "admin": "⚙️ Admin"},
        "Kinyarwanda": {"title": "Urubuga JUC", "weekly": "Raporo y'icyumweru", "strat": "Raporo y'Inkingi z'Ingamba", "dept": "Ishami", "submit": "Ohereza", "lang": "Ururimi", "pillar": "Inkingi y'Ingamba", "dash": "📊 Imbonerahamwe y'Utugari", "admin": "⚙️ Ubuyobozi"},
        "Dutch": {"title": "JUC Portaal", "weekly": "Wekelijks Rapport", "strat": "Strategisch Pijler Rapport", "dept": "Afdeling", "submit": "Indienen", "lang": "Taal", "pillar": "Strategische Pijler", "dash": "📊 Bellen Dashboard", "admin": "⚙️ Beheer"},
        "Italian": {"title": "Portale JUC", "weekly": "Rapporto Settimanale", "strat": "Rapporto Pilastro Strategico", "dept": "Dipartimento", "submit": "Invia", "lang": "Lingua", "pillar": "Pilastro Strategico", "dash": "📊 Dashboard a Bolle", "admin": "⚙️ Admin"},
        "Spanish": {"title": "Portal JUC", "weekly": "Informe Semanal", "strat": "Informe de Pilar Estratégico", "dept": "Departamento", "submit": "Enviar", "lang": "Idioma", "pillar": "Pilar Estratégico", "dash": "📊 Panel de Burbujas", "admin": "⚙️ Panel"}
    }

# --- INITIALISATION ---
if "lang" not in st.session_state: st.session_state.lang = "English"
trans = get_translations()
engine = create_engine(st.secrets["DATABASE_URL"]) if "DATABASE_URL" in st.secrets else None

# --- CHARGEMENT AUTOMATIQUE DE L'IMAGE DE FOND ---
default_bg_name = "background.jpg"
if "bg_base64" not in st.session_state or not st.session_state.bg_base64:
    if os.path.exists(default_bg_name):
        with open(default_bg_name, "rb") as image_file:
            st.session_state.bg_base64 = base64.b64encode(image_file.read()).decode()
    else:
        st.session_state.bg_base64 = ""

# --- STRUCTURE DE LA BASE DE DONNÉES ---
if engine:
    try:
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS juc_reports (
                    id SERIAL PRIMARY KEY,
                    submission_date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    staff_name TEXT,
                    report_type TEXT,
                    category TEXT,
                    sub_category TEXT,
                    completed_activities TEXT,
                    pending_issues TEXT,
                    challenges TEXT
                );
            """))
            conn.commit()
    except Exception as e:
        st.error(f"Erreur d'initialisation de la base de données : {e}")

# --- UI & SIDEBAR ---
st.sidebar.subheader(trans[st.session_state.lang]["lang"])
st.session_state.lang = st.sidebar.selectbox("", ["English", "Français", "Kinyarwanda", "Dutch", "Italian", "Spanish"])
t = trans[st.session_state.lang]

bg_css = f"url('data:image/jpeg;base64,{st.session_state.bg_base64}')" if st.session_state.bg_base64 else "none"

st.markdown(f"""
    <style>
    .stApp {{ background-image: {bg_css} !important; background-size: cover !important; background-attachment: fixed !important; }}
    .main .block-container {{ background: rgba(255, 255, 255, 0.93); padding: 2.5rem; border-radius: 15px; backdrop-filter: blur(8px); box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3); }}
    div[data-testid="stForm"] {{ background: rgba(255, 255, 258, 0.98) !important; padding: 25px; border-radius: 12px; border: 1px solid #e2e8f0; }}
    .bubble-card {{ background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%); border: 2px solid #cbd5e1; border-radius: 20px; padding: 20px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin-bottom: 20px; }}
    .bubble-admin {{ background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); border: 2px solid #3b82f6; border-radius: 25px; padding: 25px; text-align: center; box-shadow: 0 6px 16px rgba(59, 130, 246, 0.15); margin-bottom: 25px; }}
    </style>
""", unsafe_allow_html=True)

# --- SÉCURITÉ ---
password_input = st.sidebar.text_input("Password", type="password")
if password_input != "JUC2026Secure":
    st.warning("Access Restricted. Please enter the secure password in the sidebar.")
    st.stop()

# --- NAVIGATION ---
menu = st.sidebar.radio(t["title"], [t["weekly"], t["strat"], t["dash"], t["admin"]])

# --- 1. RAPPORT HEBDOMADAIRE ---
if menu == t["weekly"]:
    st.header(t["weekly"])
    with st.form("weekly_form"):
        col1, col2 = st.columns(2)
        staff_name = col1.text_input("Full Name / Nom complet")
        submission_date = col2.date_input("Date", value=date.today())
        dept = st.selectbox(t["dept"], ["Administration", "Finance", "Program management", "Project office", "Communication office", "Front Desk", "Monitoring and Evaluation"])
        completed_activities = st.text_area("Activités réalisées")
        pending_issues = st.text_area("Projections pour la semaine prochaine")
        challenges = st.text_area("Défis rencontrés")
        if st.form_submit_button(t["submit"]):
            with engine.connect() as conn:
                conn.execute(text("INSERT INTO juc_reports (submission_date, staff_name, report_type, category, completed_activities, pending_issues, challenges) VALUES (:sub_date, :n, 'Weekly', :c, :comp, :pend, :chal)"), 
                            {"sub_date": submission_date, "n": staff_name, "c": dept, "comp": completed_activities, "pend": pending_issues, "chal": challenges})
                conn.commit()
            st.success("Rapport soumis avec succès !")

# --- 2. RAPPORT PAR PILIER ---
elif menu == t["strat"]:
    st.header(t["strat"])
    chosen_pillar = st.selectbox(t["pillar"], ["Pillar 1: Research & Policy", "Pillar 2: Empowerment", "Pillar 3: Integral Ecology", "Pillar 4: Institutional Sustainability"])
    with st.form("strat_form"):
        staff_name = st.text_input("Nom complet")
        completed_activities = st.text_area("Activités réalisées")
        challenges = st.text_area("Défis")
        if st.form_submit_button(t["submit"]):
            with engine.connect() as conn:
                conn.execute(text("INSERT INTO juc_reports (submission_date, staff_name, report_type, category, completed_activities, challenges) VALUES (:d, :n, 'Strategic', :c, :comp, :chal)"), 
                            {"d": date.today(), "n": staff_name, "c": chosen_pillar, "comp": completed_activities, "chal": challenges})
                conn.commit()
            st.success("Soumis !")

# --- 3. DASHBOARD & EXPORT WORD ---
elif menu == t["dash"]:
    st.header(t["dash"])
    df = pd.read_sql("SELECT * FROM juc_reports", engine)
    
    col1, col2, col3 = st.columns(3)
    col1.markdown('<div class="bubble-card"><h4>Finance/Admin</h4></div>', unsafe_allow_html=True)
    col2.markdown('<div class="bubble-card"><h4>Program Mgmt</h4></div>', unsafe_allow_html=True)
    col3.markdown('<div class="bubble-card"><h4>Piliers</h4></div>', unsafe_allow_html=True)

    if not df.empty:
        cat = st.selectbox("Filtrer par catégorie :", df['category'].unique())
        filtered_df = df[df['category'] == cat]
        for _, row in filtered_df.iterrows():
            with st.expander(f"{row['staff_name']} - {row['submission_date']}"):
                st.write(f"**Activités:** {row.get('completed_activities', '')}")
                st.write(f"**Défis:** {row.get('challenges', '')}")

        if st.button("📥 Générer le rapport Word"):
            doc = Document()
            doc.add_heading(f"Rapport JUC : {cat}", 0)
            for _, row in filtered_df.iterrows():
                doc.add_paragraph(f"Staff: {row['staff_name']} | Date: {row['submission_date']}")
                doc.add_paragraph(f"Activités: {row['completed_activities']}")
                doc.add_paragraph("________________________________________")
            buffer = io.BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            st.download_button("Télécharger le fichier", buffer, f"Rapport_{cat}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

# --- 4. ADMIN ---
elif menu == t["admin"]:
    st.header(t["admin"])
    df = pd.read_sql("SELECT * FROM juc_reports ORDER BY submission_date DESC", engine)
    st.dataframe(df)
    if st.button("🗑️ Tout supprimer"):
        with engine.connect() as conn:
            conn.execute(text("DELETE FROM juc_reports"))
            conn.commit()
        st.rerun()
