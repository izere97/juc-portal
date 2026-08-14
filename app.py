import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# Configuration de la page
st.set_page_config(page_title="JUC Staff & M&E Portal", layout="wide")

# Mot de passe du portail
PORTAL_PASSWORD = "JUC2026Secure"

# Gestion de l'authentification simple
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔐 JUC Staff & M&E Portal - Connexion")
    pwd = st.text_input("Entrez le mot de passe du portail :", type="password")
    if st.button("Se connecter"):
        if pwd == PORTAL_PASSWORD:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Mot de passe incorrect.")
    st.stop()

# --- WHERE TO LOOK FOR ADDED DATA & SOURCES CONFIGURATION ---
DATA_SOURCES = {
    "weekly_reports": "juc_reports",  # Table Supabase principale
    "departments_master": [
        "Monitoring & Evaluation (M&E)",
        "Administration & Finance",
        "Programs & Project Management",
        "Youth Empowerment"
    ]
}

# Initialisation de la connexion SQLAlchemy avec Supabase
@st.cache_resource
def init_connection():
    try:
        db_url = st.secrets["DATABASE_URL"]
        return create_engine(db_url)
    except Exception as e:
        st.error(f"Erreur de configuration de la base de données dans les Secrets : {e}")
        return None

engine = init_connection()

# Fonction de sauvegarde sécurisée avec diagnostic d'erreurs
def save_to_supabase(df, table_name):
    try:
        if engine is None:
            st.error("Erreur de connexion : L'engine n'est pas initialisé.")
            return False
        df.to_sql(table_name, con=engine, if_exists='append', index=False, schema='public')
        return True
    except Exception as e:
        st.error(f"Détail de l'erreur Supabase : {e}")
        return False

# Fonction pour charger et filtrer les données par département (comme avant)
def load_and_filter_data(table_name):
    if engine is None:
        return pd.DataFrame()
    try:
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql(query, con=engine)
        
        # Application du filtre des départements comme avant
        active_departments = DATA_SOURCES["departments_master"]
        if "Department" in df.columns:
            df_filtered = df[df["Department"].isin(active_departments)]
        else:
            df_filtered = df
        return df_filtered
    except Exception as e:
        # Si la table est vide ou n'a pas encore de données
        return pd.DataFrame()

# Interface principale du portail
st.title("📊 JUC Staff & M&E Portal")
st.sidebar.success("Connecté avec succès")

menu = st.sidebar.selectbox("Navigation", ["Submit Weekly Report", "View Reports & Analytics", "Pillar 1", "Pillar 2", "Pillar 3", "Pillar 4"])

if menu == "Submit Weekly Report":
    st.header("Rapport Hebdomadaire")
    with st.form("report_form"):
        date_val = str(st.date_input("Date"))
        staff_name = st.text_input("Staff Name")
        
        # Sélection du département avec la liste officielle
        department = st.selectbox("Department", DATA_SOURCES["departments_master"])
        
        activities = st.text_area("Activities")
        challenges = st.text_area("Challenges")
        projections = st.text_area("Projections")
        
        submit = st.form_submit_button("Envoyer")
        if submit:
            df_new = pd.DataFrame([{
                "Date": date_val,
                "Staff Name": staff_name,
                "Department": department,
                "Activities": activities,
                "Challenges": challenges,
                "Projections": projections
            }])
            if save_to_supabase(df_new, "juc_reports"):
                st.success("✅ Saved to Database!")

elif menu == "View Reports & Analytics":
    st.header("🔍 Où regarder les données ajoutées & Historique")
    st.info("Les données enregistrées ci-dessous proviennent directement de la base de données Supabase (Table : `juc_reports`), filtrées par les départements autorisés.")
    
    df_reports = load_and_filter_data("juc_reports")
    if not df_reports.empty:
        st.dataframe(df_reports, use_container_width=True)
    else:
        st.warning("Aucune donnée enregistrée pour le moment ou table vide.")

elif menu in ["Pillar 1", "Pillar 2", "Pillar 3", "Pillar 4"]:
    pillar_num = menu.split(" ")[1]
    table_name = f"juc_pillar_{pillar_num}"
    st.header(f"Suivi - {menu}")
    
    with st.form(f"pillar_form_{pillar_num}"):
        date_val = str(st.date_input("Date"))
        initiative = st.text_input("Initiative")
        metrics = st.text_input("Metrics")
        lead_officer = st.text_input("Lead Officer")
        status = st.selectbox("Status", ["En cours", "Terminé", "En attente"])
        
        submit_pillar = st.form_submit_button("Envoyer")
        if submit_pillar:
            df_pillar = pd.DataFrame([{
                "Date": date_val,
                "Initiative": initiative,
                "Metrics": metrics,
                "Lead Officer": lead_officer,
                "Status": status
            }])
            if save_to_supabase(df_pillar, table_name):
                st.success("✅ Saved to Database!")
