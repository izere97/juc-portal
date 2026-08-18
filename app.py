import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# --- CONFIGURATION DE LA PAGE & LOGO ---
st.set_page_config(
    page_title="JUC Staff & M&E Portal", 
    page_icon="📊", 
    layout="wide"
)

# Mot de passe du portail
PORTAL_PASSWORD = "JUC2026Secure"

# Gestion de l'authentification
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔐 JUC Staff & M&E Portal - Connexion")
    pwd = st.text_input("Entrez le mot de passe du portail / Enter portal password:", type="password")
    if st.button("Se connecter / Login"):
        if pwd == PORTAL_PASSWORD:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Mot de passe incorrect / Incorrect password.")
    st.stop()

# --- DICTIONNAIRE DE TRADUCTION ---
LANGUAGES = {
    "English": {
        "title": "📊 JUC Staff & M&E Portal",
        "nav": "Navigation",
        "submit_report": "Submit Weekly Report",
        "view_analytics": "View Reports & Analytics",
        "date": "Date",
        "staff": "Staff Name",
        "dept": "Department",
        "activities": "Activities",
        "challenges": "Challenges",
        "projections": "Projections",
        "send": "Submit",
        "success": "✅ Saved to Database!",
        "error_db": "Database connection error. Check your Supabase URI secrets.",
    },
    "Français": {
        "title": "📊 Portail du Personnel & M&E - JUC",
        "nav": "Navigation",
        "submit_report": "Soumettre le Rapport Hebdomadaire",
        "view_analytics": "Voir les Rapports & Analyses",
        "date": "Date",
        "staff": "Nom du personnel",
        "dept": "Département",
        "activities": "Activités",
        "challenges": "Défis rencontrés",
        "projections": "Projections / Perspectives",
        "send": "Envoyer",
        "success": "✅ Enregistré dans la base de données !",
        "error_db": "Erreur de connexion à la base de données. Vérifiez vos secrets Supabase.",
    },
    "Kinyarwanda": {
        "title": "📊 Urubuga rwa JUC rw'Abakozi n'igenzura (M&E)",
        "nav": "Gushakisha / Aho ujya",
        "submit_report": "Tanga Raporo y'icyumweru",
        "view_analytics": "Reba raporo n'isesengura",
        "date": "Itariki",
        "staff": "Amazina y'umukozi",
        "dept": "Ishami (Department)",
        "activities": "Ibikorwa byakozwe",
        "challenges": "Ingorane / Imbogamizi",
        "projections": "Ibyo uteganyije",
        "send": "Ohereza",
        "success": "✅ Byabitswe neza mu bubiko bw'amakuru!",
        "error_db": "Ikibazo cyo kwihuza n'ububiko bw'amakuru. Reba ibanga rya Supabase.",
    }
}

# --- BARRE LATERALE : LANGUE & LOGO ---
st.sidebar.image("https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?w=150", caption="JUC Portal") # Remplacez l'URL par votre vrai logo si besoin
selected_lang = st.sidebar.selectbox("🌐 Langue / Language / Ururimi", ["English", "Français", "Kinyarwanda"])
t = LANGUAGES[selected_lang]

# --- CONFIGURATION DES 7 DÉPARTEMENTS EXACTS ---
DEPARTMENTS_LIST = [
    "Administration",
    "Finance",
    "Program management",
    "Project office",
    "Communication office",
    "Front Desk",
    "Monitoring and Evaluation"
]

DATA_SOURCES = {
    "weekly_reports": "juc_reports",
    "departments_master": DEPARTMENTS_LIST
}

# Connexion SQLAlchemy Supabase
@st.cache_resource
def init_connection():
    try:
        db_url = st.secrets["DATABASE_URL"]
        return create_engine(db_url)
    except Exception as e:
        return None

engine = init_connection()

def save_to_supabase(df, table_name):
    try:
        if engine is None:
            return False
        df.to_sql(table_name, con=engine, if_exists='append', index=False, schema='public')
        return True
    except Exception as e:
        st.error(f"Erreur Supabase / Error: {e}")
        return False

def load_and_filter_data(table_name):
    if engine is None:
        return pd.DataFrame()
    try:
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql(query, con=engine)
        if "Department" in df.columns:
            df_filtered = df[df["Department"].isin(DATA_SOURCES["departments_master"])]
        else:
            df_filtered = df
        return df_filtered
    except Exception:
        return pd.DataFrame()

# --- INTERFACE PRINCIPALE ---
st.title(t["title"])
st.sidebar.success("Connecté / Connected")

menu = st.sidebar.selectbox(t["nav"], [t["submit_report"], t["view_analytics"], "Pillar 1", "Pillar 2", "Pillar 3", "Pillar 4"])

if menu == t["submit_report"]:
    st.header(t["submit_report"])
    with st.form("report_form"):
        date_val = str(st.date_input(t["date"]))
        staff_name = st.text_input(t["staff"])
        
        # Liste des 7 départements exacts
        department = st.selectbox(t["dept"], DATA_SOURCES["departments_master"])
        
        activities = st.text_area(t["activities"])
        challenges = st.text_area(t["challenges"])
        projections = st.text_area(t["projections"])
        
        submit = st.form_submit_button(t["send"])
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
                st.success(t["success"])
            else:
                st.error(t["error_db"])

elif menu == t["view_analytics"]:
    st.header(t["view_analytics"])
    st.info("Données récupérées en direct de Supabase et filtrées selon vos 7 départements officiels.")
    
    df_reports = load_and_filter_data("juc_reports")
    if not df_reports.empty:
        # Affichage du tableau de données
        st.dataframe(df_reports, use_container_width=True)
        
        # --- DROIT ET OUTILS D'ANALYSE DES DONNÉES ---
        st.markdown("---")
        st.subheader("📈 Espace d'Analyse des Données (Data Analytics Workspace)")
        
        col1, col2 = st.columns(2)
        with col1:
            # Filtre interactif par département pour l'analyse
            selected_dept_filter = st.selectbox("Filtrer par département pour analyse", ["Tous"] + DATA_SOURCES["departments_master"])
            if selected_dept_filter != "Tous":
                df_to_analyze = df_reports[df_reports["Department"] == selected_dept_filter]
            else:
                df_to_analyze = df_reports
            
            st.write(f"Nombre total de rapports analysés : **{len(df_to_analyze)}**")
            
        with col2:
            # Option de téléchargement pour vos analyses approfondies (Python/SQL/Excel)
            csv = df_to_analyze.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Télécharger les données filtrées (CSV)",
                data=csv,
                file_name='juc_filtered_reports_analysis.csv',
                mime='text/csv',
            )
            
        # Graphique simple d'activité par département
        if "Department" in df_reports.columns and not df_reports.empty:
            st.bar_chart(df_reports["Department"].value_counts())
            
    else:
        st.warning("Aucune donnée enregistrée pour le moment ou problème de connexion.")

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
        
        submit_pillar = st.form_submit_button(t["send"])
        if submit_pillar:
            df_pillar = pd.DataFrame([{
                "Date": date_val,
                "Initiative": initiative,
                "Metrics": metrics,
                "Lead Officer": lead_officer,
                "Status": status
            }])
            if save_to_supabase(df_pillar, table_name):
                st.success(t["success"])
