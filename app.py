import base64
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine, text
import streamlit as st

# --- CONFIGURATION ---
st.set_page_config(page_title="JUC Portal", layout="wide")

# --- TRADUCTIONS ---
def get_translations():
    return {
        "English": {"title": "JUC Portal", "weekly": "Weekly Report", "strat": "Strategic Pillar Report", "dept": "Department", "submit": "Submit", "lang": "Language", "pillar": "Strategic Pillar", "dash": "📊 Dashboard", "admin": "⚙️ Admin"},
        "Français": {"title": "Portail JUC", "weekly": "Rapport Hebdomadaire", "strat": "Rapport par Pilier Stratégique", "dept": "Département", "submit": "Soumettre", "lang": "Langue", "pillar": "Pilier Stratégique", "dash": "📊 Tableau de Bord", "admin": "⚙️ Admin"},
        "Kinyarwanda": {"title": "Urubuga JUC", "weekly": "Raporo y'icyumweru", "strat": "Raporo y'Inkingi z'Ingamba", "dept": "Ishami", "submit": "Ohereza", "lang": "Ururimi", "pillar": "Inkingi y'Ingamba", "dash": "📊 Imbonerahamwe", "admin": "⚙️ Ubuyobozi"},
        "Dutch": {"title": "JUC Portaal", "weekly": "Wekelijks Rapport", "strat": "Strategisch Pijler Rapport", "dept": "Afdeling", "submit": "Indienen", "lang": "Taal", "pillar": "Strategische Pijler", "dash": "📊 Dashboard", "admin": "⚙️ Beheer"},
        "Italian": {"title": "Portale JUC", "weekly": "Rapporto Settimanale", "strat": "Rapporto Pilastro Strategico", "dept": "Dipartimento", "submit": "Invia", "lang": "Lingua", "pillar": "Pilastro Strategico", "dash": "📊 Dashboard", "admin": "⚙️ Admin"},
        "Spanish": {"title": "Portal JUC", "weekly": "Informe Semanal", "strat": "Informe de Pilar Estratégico", "dept": "Departamento", "submit": "Enviar", "lang": "Idioma", "pillar": "Pilar Estratégico", "dash": "📊 Panel", "admin": "⚙️ Admin"}
    }

# --- INITIALISATION ---
if "lang" not in st.session_state: st.session_state.lang = "English"
trans = get_translations()
engine = create_engine(st.secrets["DATABASE_URL"]) if "DATABASE_URL" in st.secrets else None

# --- CRÉATION AUTOMATIQUE DE LA TABLE SI ELLE N'EXISTE PAS ---
if engine:
    try:
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS juc_reports (
                    id SERIAL PRIMARY KEY,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    staff_name TEXT,
                    report_type TEXT,
                    category TEXT,
                    details TEXT
                );
            """))
            conn.commit()
    except Exception as e:
        st.error(f"Erreur lors de la création de la table : {e}")

# --- UI & BACKGROUND ---
st.sidebar.subheader(trans[st.session_state.lang]["lang"])
st.session_state.lang = st.sidebar.selectbox("", ["English", "Français", "Kinyarwanda", "Dutch", "Italian", "Spanish"])
t = trans[st.session_state.lang]

bg_file = st.sidebar.file_uploader("🖼️ Background Image", type=["jpg", "png"])
if bg_file:
    b64 = base64.b64encode(bg_file.read()).decode()
    st.markdown(f"<style>.stApp {{background: linear-gradient(rgba(255,255,255,0.9), rgba(255,255,255,0.9)), url(data:image/jpeg;base64,{b64}); background-size: cover;}}</style>", unsafe_allow_html=True)

if st.sidebar.text_input("Password", type="password") != "JUC2026Secure":
    st.warning("Access Restricted.")
    st.stop()

# --- NAVIGATION ---
menu = st.sidebar.radio(t["title"], [t["weekly"], t["strat"], t["dash"], t["admin"]])

# --- SOUMISSION HEBDO ---
if menu == t["weekly"]:
    st.header(t["weekly"])
    with st.form("weekly"):
        name = st.text_input("Name")
        dept = st.selectbox(t["dept"], ["Administration", "Finance", "Program management", "Project office", "Communication office", "Front Desk", "Monitoring and Evaluation"])
        details = st.text_area("Details")
        doc = st.file_uploader("Upload", type=['pdf', 'jpg'])
        if st.form_submit_button(t["submit"]):
            if engine:
                with engine.connect() as conn:
                    conn.execute(text("INSERT INTO juc_reports (staff_name, report_type, category, details) VALUES (:n, 'Weekly', :c, :d)"), 
                                {"n": name, "c": dept, "d": details})
                    conn.commit()
                st.success("Saved!")

# --- SOUMISSION STRATÉGIQUE ---
elif menu == t["strat"]:
    st.header(t["strat"])
    pillars = [
        "Pillar 1: Research, Policy Advocacy and Civic Engagement",
        "Pillar 2: Women & Youth Empowerment",
        "Pillar 3: Integral Ecology",
        "Pillar 4: Institutional Capacity"
    ]
    with st.form("strat"):
        name = st.text_input("Name")
        pillar = st.selectbox(t["pillar"], pillars)
        details = st.text_area("Details")
        if st.form_submit_button(t["submit"]):
            if engine:
                with engine.connect() as conn:
                    conn.execute(text("INSERT INTO juc_reports (staff_name, report_type, category, details) VALUES (:n, 'Strategic', :c, :d)"), 
                                {"n": name, "c": pillar, "d": details})
                    conn.commit()
                st.success("Saved!")

# --- DASHBOARD ---
elif menu == t["dash"]:
    st.header(t["dash"])
    if engine:
        try:
            df = pd.read_sql("SELECT * FROM juc_reports", engine)
            st.dataframe(df)
        except Exception as e:
            st.info("Aucune donnée à afficher pour le moment ou table vide.")

# --- ADMIN (SUPPRESSION PARTIELLE OU TOTALE) ---
elif menu == t["admin"]:
    st.header(t["admin"])
    
    if engine:
        try:
            df = pd.read_sql("SELECT id, date, staff_name, report_type, category FROM juc_reports", engine)
            if df.empty:
                st.info("La base de données est actuellement vide.")
            else:
                st.dataframe(df)
                
                st.subheader("Supprimer un enregistrement spécifique par ID")
                report_id_to_delete = st.number_input("Entrez l'ID de la ligne à supprimer", min_value=0, step=1)
                
                if st.button("Supprimer cette ligne"):
                    with engine.connect() as conn:
                        conn.execute(text("DELETE FROM juc_reports WHERE id = :id"), {"id": report_id_to_delete})
                        conn.commit()
                    st.success(f"Ligne avec l'ID {report_id_to_delete} supprimée avec succès.")
                    st.rerun()
        except Exception as e:
            st.info("Initialisation de la table en cours...")
                
        st.markdown("---")
        if st.button("🗑️ TOUT SUPPRIMER (Réinitialisation totale)"):
            with engine.connect() as conn:
                conn.execute(text("DELETE FROM juc_reports"))
                conn.commit()
            st.warning("Base de données entièrement vidée.")
            st.rerun()
