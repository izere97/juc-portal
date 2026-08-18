import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="JUC Staff & M&E Portal",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CONFIGURATION DE LA BASE DE DONNÉES (NEON) ---
# Récupération de l'URL depuis les secrets Streamlit Cloud
try:
    DATABASE_URL = st.secrets["DATABASE_URL"]
except Exception:
    DATABASE_URL = None

@st.cache_resource
def init_connection():
    if not DATABASE_URL:
        return None
    return create_engine(DATABASE_URL)

engine = init_connection()

# --- CRÉATION DE LA TABLE SI ELLE N'EXISTE PAS ---
def create_table_if_not_exists():
    if engine is None:
        return
    try:
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS juc_reports (
                    id SERIAL PRIMARY KEY,
                    date TIMESTAMP,
                    staff_name TEXT,
                    department TEXT,
                    activities TEXT,
                    challenges TEXT,
                    next_steps TEXT
                );
            """))
            conn.commit()
    except Exception as e:
        st.error(f"Erreur d'initialisation de la base de données : {e}")

if engine:
    create_table_if_not_exists()

# --- DICTIONNAIRES DE TRADUCTION ---
translations = {
    "English": {
        "title": "Jesuit Urumuri Centre (JUC)",
        "subtitle": "Staff & M&E Portal",
        "login_required": "Please enter the portal password to continue.",
        "password_label": "Portal Password",
        "access_granted": "Access granted.",
        "access_denied": "Incorrect password.",
        "sidebar_lang": "Language / Ururimi / Langue",
        "nav_title": "Navigation",
        "nav_submit": "Submit Report",
        "nav_view": "View Reports & Analytics",
        "form_header": "Weekly Activity & M&E Report",
        "staff_name": "Staff Full Name",
        "department": "Department",
        "activities": "Key Activities Performed",
        "challenges": "Challenges Faced",
        "next_steps": "Next Week's Priorities",
        "submit_btn": "Submit Report",
        "success_msg": "Report successfully saved to Neon database!",
        "view_header": "Submitted Reports & Analytics",
        "filter_dept": "Filter by Department",
        "all": "All",
        "download_csv": "Download Data as CSV",
        "no_data": "No reports found yet."
    },
    "Français": {
        "title": "Centre Urumuri Jésuite (JUC)",
        "subtitle": "Portail du Personnel et Suivi-Évaluation",
        "login_required": "Veuillez entrer le mot de passe du portail pour continuer.",
        "password_label": "Mot de passe du portail",
        "access_granted": "Accès autorisé.",
        "access_denied": "Mot de passe incorrect.",
        "sidebar_lang": "Langue / Language / Ururimi",
        "nav_title": "Navigation",
        "nav_submit": "Soumettre un rapport",
        "nav_view": "Consulter les rapports et analyses",
        "form_header": "Rapport Hebdomadaire d'Activités & M&E",
        "staff_name": "Nom complet du membre du personnel",
        "department": "Département",
        "activities": "Activités clés réalisées",
        "challenges": "Défis rencontrés",
        "next_steps": "Priorités pour la semaine prochaine",
        "submit_btn": "Soumettre le rapport",
        "success_msg": "Rapport enregistré avec succès dans la base de données Neon !",
        "view_header": "Rapports soumit & Analyses",
        "filter_dept": "Filtrer par département",
        "all": "Tous",
        "download_csv": "Télécharger les données en CSV",
        "no_data": "Aucun rapport trouvé pour le moment."
    },
    "Kinyarwanda": {
        "title": "Ikigo cya Yezu Urumuri (JUC)",
        "subtitle": "Urubuga rw'Abakozi n'igenzura (M&E)",
        "login_required": "Nyamuneka shyiramo ijambo ry'ibanga kugira ngo ukomeze.",
        "password_label": "Ijambo ry'ibanga ry'urubuga",
        "access_granted": "Wemerewe kwinjira.",
        "access_denied": "Ijambo ry'ibanga si ryo.",
        "sidebar_lang": "Ururimi / Language / Langue",
        "nav_title": "Gushakisha",
        "nav_submit": "Tanga Raporo",
        "nav_view": "Reba Raporo n'isesurabumenyi",
        "form_header": "Raporo y'icyumweru n'ibikorwa",
        "staff_name": "Amazina y'umukozi",
        "department": "Ishami (Department)",
        "activities": "Ibikorwa by'ingenzi byakozwe",
        "challenges": "Ingorane zahuye n'akazi",
        "next_steps": "Iby'ibanze mu cyumweru gitaha",
        "submit_btn": "Ohereza Raporo",
        "success_msg": "Raporo yabitse neza muri database ya Neon!",
        "view_header": "Raporo zashyizweho n'Isesurabumenyi",
        "filter_dept": "Hitamo Ishami",
        "all": "Byose",
        "download_csv": "Kuramo Amakuru nka CSV",
        "no_data": "Nta raporo iraboneka."
    }
}

# --- BARRE LATÉRALE (LANGUE ET AUTHENTIFICATION) ---
st.sidebar.image("https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=800&q=80", use_container_width=True)
st.sidebar.markdown("---")

selected_lang = st.sidebar.selectbox("Langue / Language / Ururimi", ["Français", "English", "Kinyarwanda"])
t = translations[selected_lang]

st.sidebar.markdown("---")
st.sidebar.subheader(t["login_required"])
password_input = st.sidebar.text_input(t["password_label"], type="password")

# Vérification du mot de passe du portail
if password_input != "JUC2026Secure":
    st.warning(t["login_required"])
    st.stop()

# --- EN-TÊTE DE L'APPLICATION ---
st.title(f"🔥 {t['title']}")
st.subheader(t['subtitle'])
st.markdown("---")

# Navigation du portail
navigation = st.sidebar.radio(t["nav_title"], [t["nav_submit"], t["nav_view"]])

# Liste officielle des 7 départements
departments_list = [
    "Administration",
    "Finance",
    "Program management",
    "Project office",
    "Communication office",
    "Front Desk",
    "Monitoring and Evaluation"
]

# --- SECTION 1 : SOUMISSION DE RAPPORT ---
if navigation == t["nav_submit"]:
    st.header(t["form_header"])
    
    with st.form("juc_report_form"):
        staff_name = st.text_input(t["staff_name"])
        department = st.selectbox(t["department"], departments_list)
        activities = st.text_area(t["activities"])
        challenges = st.text_area(t["challenges"])
        next_steps = st.text_area(t["next_steps"])
        
        submitted = st.form_submit_button(t["submit_btn"])
        
        if submitted:
            if not staff_name or not activities:
                st.error("Veuillez remplir au moins votre nom et les activités réalisées.")
            elif engine is None:
                st.error("Erreur critique : La connexion à la base de données Neon est absente.")
            else:
                try:
                    with engine.connect() as conn:
                        query = text("""
                            INSERT INTO juc_reports (date, staff_name, department, activities, challenges, next_steps)
                            VALUES (:date, :staff_name, :department, :activities, :challenges, :next_steps)
                        """)
                        conn.execute(query, {
                            "date": datetime.now(),
                            "staff_name": staff_name,
                            "department": department,
                            "activities": activities,
                            "challenges": challenges,
                            "next_steps": next_steps
                        })
                        conn.commit()
                    st.success(t["success_msg"])
                except Exception as e:
                    st.error(f"Erreur lors de l'enregistrement : {e}")

# --- SECTION 2 : CONSULTATION ET ANALYSE ---
elif navigation == t["nav_view"]:
    st.header(t["view_header"])
    
    if engine is None:
        st.error("Erreur critique : La connexion à la base de données Neon est absente.")
    else:
        try:
            df = pd.read_sql("SELECT * FROM juc_reports ORDER BY date DESC", engine)
            
            if df.empty:
                st.info(t["no_data"])
            else:
                # Filtre par département
                selected_dept = st.selectbox(t["filter_dept"], [t["all"]] + departments_list)
                
                if selected_dept != t["all"]:
                    filtered_df = df[df["department"] == selected_dept]
                else:
                    filtered_df = df
                
                # Affichage des statistiques et graphique rapide
                st.metric(label="Total Rapports", value=len(filtered_df))
                
                dept_counts = df["department"].value_counts()
                st.bar_chart(dept_counts)
                
                st.markdown("### Données détaillées")
                st.dataframe(filtered_df, use_container_width=True)
                
                # Bouton de téléchargement CSV
                csv_data = filtered_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label=t["download_csv"],
                    data=csv_data,
                    file_name='juc_m_e_reports.csv',
                    mime='text/csv',
                )
        except Exception as e:
            st.error(f"Erreur lors de la lecture des données : {e}")
