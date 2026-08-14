import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="JUC Staff & M&E Portal", page_icon="📊", layout="wide")

# --- CONNEXION À LA BASE DE DONNÉES (SUPABASE AVEC SSL) ---
@st.cache_resource
def init_connection():
    try:
        db_url = st.secrets["DATABASE_URL"]
        # Ajoute automatiquement le paramètre SSL requis par Supabase en production cloud
        if "?" not in db_url:
            db_url += "?sslmode=require"
        elif "sslmode" not in db_url:
            db_url += "&sslmode=require"
            
        engine = create_engine(db_url)
        return engine
    except Exception as e:
        st.error(f"Erreur de connexion à la base de données : {e}")
        return None

engine = init_connection()

# --- INITIALISATION DES TABLES DANS POSTGRESQL ---
def init_tables():
    if engine:
        try:
            with engine.begin() as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS rapports_hebdo (
                        staff_name TEXT,
                        department TEXT,
                        report_date TEXT,
                        activities TEXT,
                        challenges TEXT,
                        projections TEXT
                    )
                """)
        except Exception as e:
            st.warning(f"Note sur l'initialisation de la table : {e}")

init_tables()

# --- PROTECTION PAR MOT DE PASSE ---
PASSWORD = "JUC2026Secure"

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔐 JUC Portal - Connexion Sécurisée")
    pwd_input = st.text_input("Entrez le mot de passe d'accès :", type="password")
    if st.button("Se connecter"):
        if pwd_input == PASSWORD:
            st.session_state["authenticated"] = True
            st.success("Accès autorisé !")
            st.rerun()
        else:
            st.error("Mot de passe incorrect.")
    st.stop()

# --- APPLICATION PRINCIPALE ---
st.image("Screenshot 2026-08-14 143018.png", width=200)
st.title("Juc Staff & M&E Portal (2026-2031)")

menu = st.sidebar.selectbox("Navigation", ["Rapport Hebdomadaire", "Visualiser les Rapports", "Espace de Données"])

if menu == "Rapport Hebdomadaire":
    st.header("📝 Soumission du Rapport Hebdomadaire")
    
    with st.form("weekly_form"):
        staff_name = st.text_input("Staff Name / Nom et Prénom")
        department = st.text_input("Department / Département", value="M&E")
        report_date = st.date_input("Report Date")
        activities = st.text_area("1. Activities Completed This Week")
        challenges = st.text_area("2. Challenges Encountered (Optional)")
        projections = st.text_area("3. Projections for Next Week")
        
        submitted = st.form_submit_button("Envoyer le rapport")
        
        if submitted:
            if staff_name and activities:
                new_data = pd.DataFrame([{
                    "staff_name": staff_name,
                    "department": department,
                    "report_date": str(report_date),
                    "activities": activities,
                    "challenges": challenges,
                    "projections": projections
                }])
                
                # Sauvegarde permanente dans PostgreSQL
                try:
                    if engine:
                        new_data.to_sql("rapports_hebdo", con=engine, if_exists="append", index=False)
                        st.success("Rapport enregistré en permanence dans la base de données !")
                    else:
                        st.error("Base de données non connectée.")
                except Exception as e:
                    st.error(f"Erreur lors de l'enregistrement : {e}")
            else:
                st.warning("Veuillez remplir au moins votre nom et les activités réalisées.")

elif menu == "Visualiser les Rapports":
    st.header("📂 Historique des Rapports (Persistant)")
    
    if engine:
        try:
            df_saved = pd.read_sql("SELECT * FROM rapports_hebdo", con=engine)
            if not df_saved.empty:
                st.dataframe(df_saved, use_container_width=True)
            else:
                st.info("Aucun rapport enregistré pour le moment.")
        except Exception as e:
            st.warning("La table est vide ou en cours de création.")

elif menu == "Espace de Données":
    st.header("📊 Data Workspace")
    st.write("Gérez vos données et effectuez vos analyses ici.")
    
    if engine:
        try:
            df_saved = pd.read_sql("SELECT * FROM rapports_hebdo", con=engine)
            if not df_saved.empty:
                csv = df_saved.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Télécharger les rapports en CSV",
                    data=csv,
                    file_name='juc_rapports_hebdo.csv',
                    mime='text/csv',
                )
        except:
            pass
