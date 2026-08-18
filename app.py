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

# --- CRÉATION AUTOMATIQUE DE LA TABLE ---
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
                    sub_category TEXT,
                    details TEXT
                );
            """))
            conn.commit()
    except Exception as e:
        st.error(f"Erreur d'initialisation de la base de données : {e}")

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

# --- 1. RAPPORT HEBDOMADAIRE (Conforme au Mémo) ---
if menu == t["weekly"]:
    st.header(t["weekly"])
    st.info("Conformément au mémo de la direction, veuillez soumettre votre rapport d'activités pour la semaine ainsi que vos projections pour la semaine prochaine[cite: 2].")
    
    with st.form("weekly_memo_form"):
        staff_name = st.text_input("Full Name / Nom complet")
        dept = st.selectbox(t["dept"], ["Administration", "Finance", "Program management", "Project office", "Communication office", "Front Desk", "Monitoring and Evaluation"])
        
        completed_activities = st.text_area("Activities completed for the week ending on Friday / Activités réalisées cette semaine")
        pending_issues = st.text_area("Projection of pending issues to be completed or initiated next week / Projections et dossiers en attente pour la semaine prochaine")
        
        doc = st.file_uploader("Upload supporting document / Document justificatif", type=['pdf', 'jpg', 'png'])
        
        if st.form_submit_button(t["submit"]):
            if not staff_name or not completed_activities:
                st.error("Please fill in your name and completed activities.")
            elif engine:
                combined_details = f"Accomplished: {completed_activities} || Pending/Next week: {pending_issues}"
                with engine.connect() as conn:
                    conn.execute(text("""
                        INSERT INTO juc_reports (date, staff_name, report_type, category, sub_category, details) 
                        VALUES (:date, :n, 'Weekly', :c, :sub, :d)
                    """), {
                        "date": datetime.now(),
                        "n": staff_name, 
                        "c": dept, 
                        "sub": "Weekly Memo Report",
                        "d": combined_details
                    })
                    conn.commit()
                st.success("Weekly report submitted successfully!")

# --- 2. RAPPORT PAR PILIER STRATÉGIQUE (Plan 2026-2031) ---
elif menu == t["strat"]:
    st.header(t["strat"])
    st.markdown("Rapports alignés sur les quatre piliers stratégiques et leurs activités clés (2026–2031)[cite: 1].")

    # Dictionnaire des piliers et activités du Plan Stratégique
    pillars_data = {
        "Pillar 1: Research, Policy Advocacy and Civic Engagement": [
            "Basic Needs Basket Updates",
            "Policy Briefs & Research Reports",
            "Social Justice Conferences",
            "Civic Education & Life-skills training (AHAPPY / Drug abuse prevention)",
            "Pluralistic Governance Forums"
        ],
        "Pillar 2: Women & Youth Empowerment through Social Innovation and Entrepreneurship": [
            "Social Innovation Incubation Bootcamps",
            "Financial Literacy Training",
            "Women's Empowerment Cooperatives",
            "Gender and Youth Agency Index (GYAI) Assessment"
        ],
        "Pillar 3: Integral Ecology and Community Resilience": [
            "Climate Change Awareness Campaigns",
            "Laudato Si' Formation & Ecological Retreats",
            "Sustainable Agriculture & Climate-Smart Farming",
            "Kitchen Gardens & Nutrition Programs"
        ],
        "Pillar 4: Institutional Capacity Strengthening and Sustainability": [
            "Staff Development & Performance Management",
            "Financial Resource Mobilization & CSR",
            "Governance & M&E Systems Strengthening",
            "Internal Income-Generating Activities"
        ]
    }

    with st.form("strategic_report_form"):
        staff_name = st.text_input("Full Name / Nom complet")
        selected_pillar = st.selectbox(t["pillar"], list(pillars_data.keys()))
        selected_activity = st.selectbox("Core Activity / Activité clé", pillars_data[selected_pillar])
        
        details = st.text_area("Detailed Progress, Metrics & Observations / Détails des progrès, indicateurs et observations")
        doc = st.file_uploader("Upload monitoring document / Document de suivi", type=['pdf', 'jpg', 'png'])
        
        if st.form_submit_button(t["submit"]):
            if not staff_name or not details:
                st.error("Please fill in all mandatory fields.")
            elif engine:
                with engine.connect() as conn:
                    conn.execute(text("""
                        INSERT INTO juc_reports (date, staff_name, report_type, category, sub_category, details) 
                        VALUES (:date, :n, 'Strategic', :c, :sub, :d)
                    """), {
                        "date": datetime.now(),
                        "n": staff_name, 
                        "c": selected_pillar, 
                        "sub": selected_activity,
                        "d": details
                    })
                    conn.commit()
                st.success("Strategic report submitted successfully!")

# --- 3. DASHBOARD ---
elif menu == t["dash"]:
    st.header(t["dash"])
    if engine:
        try:
            df = pd.read_sql("SELECT * FROM juc_reports ORDER BY date DESC", engine)
            if df.empty:
                st.info("No reports recorded yet.")
            else:
                st.metric(label="Total Reports", value=len(df))
                st.dataframe(df, use_container_width=True)
                
                # Option de téléchargement CSV
                csv_data = df.to_csv(index=False).encode("utf-8")
                st.download_button("Download Data as CSV", data=csv_data, file_name="juc_reports.csv", mime="text/csv")
        except Exception as e:
            st.info("Database table initializing or empty.")

# --- 4. ADMIN ---
elif menu == t["admin"]:
    st.header(t["admin"])
    
    if engine:
        try:
            df = pd.read_sql("SELECT id, date, staff_name, report_type, category, sub_category FROM juc_reports ORDER BY date DESC", engine)
            if df.empty:
                st.info("The database is currently empty.")
            else:
                st.dataframe(df, use_container_width=True)
                
                st.subheader("Delete a specific record by ID / Supprimer un enregistrement par ID")
                report_id_to_delete = st.number_input("Enter ID to delete / Entrez l'ID à supprimer", min_value=0, step=1)
                
                if st.button("Delete Selected Row / Supprimer cette ligne"):
                    with engine.connect() as conn:
                        conn.execute(text("DELETE FROM juc_reports WHERE id = :id"), {"id": report_id_to_delete})
                        conn.commit()
                    st.success(f"Record ID {report_id_to_delete} deleted successfully.")
                    st.rerun()
        except Exception as e:
            st.info("Loading administration tools...")
                
        st.markdown("---")
        if st.button("🗑️ DELETE ALL / TOUT SUPPRIMER (Total Reset)"):
            with engine.connect() as conn:
                conn.execute(text("DELETE FROM juc_reports"))
                conn.commit()
            st.warning("Database completely cleared.")
            st.rerun()
