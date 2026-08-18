import base64
from datetime import date, datetime
import os
import pandas as pd
from sqlalchemy import create_engine, text
import streamlit as st

# --- CONFIGURATION ---
st.set_page_config(page_title="JUC Portal", layout="wide")

# --- TRADUCTIONS ---
def get_translations():
    return {
        "English": {"title": "JUC Portal", "weekly": "Weekly Report", "strat": "Strategic Pillar Report", "dept": "Department", "submit": "Submit", "lang": "Language", "pillar": "Strategic Pillar", "dash": "📊 Unified Analytics & Reports", "admin": "⚙️ Admin"},
        "Français": {"title": "Portail JUC", "weekly": "Rapport Hebdomadaire", "strat": "Rapport par Pilier Stratégique", "dept": "Département", "submit": "Soumettre", "lang": "Langue", "pillar": "Pilier Stratégique", "dash": "📊 Analyses & Rapports Unifiés", "admin": "⚙️ Admin"},
        "Kinyarwanda": {"title": "Urubuga JUC", "weekly": "Raporo y'icyumweru", "strat": "Raporo y'Inkingi z'Ingamba", "dept": "Ishami", "submit": "Ohereza", "lang": "Ururimi", "pillar": "Inkingi y'Ingamba", "dash": "📊 Isesengura Rusange", "admin": "⚙️ Ubuyobozi"},
        "Dutch": {"title": "JUC Portaal", "weekly": "Wekelijks Rapport", "strat": "Strategisch Pijler Rapport", "dept": "Afdeling", "submit": "Indienen", "lang": "Taal", "pillar": "Strategische Pijler", "dash": "📊 Gecombineerd Dashboard", "admin": "⚙️ Beheer"},
        "Italian": {"title": "Portale JUC", "weekly": "Rapporto Settimanale", "strat": "Rapporto Pilastro Strategico", "dept": "Dipartimento", "submit": "Invia", "lang": "Lingua", "pillar": "Pilastro Strategico", "dash": "📊 Dashboard Unificata", "admin": "⚙️ Admin"},
        "Spanish": {"title": "Portal JUC", "weekly": "Informe Semanal", "strat": "Informe de Pilar Estratégico", "dept": "Departamento", "submit": "Enviar", "lang": "Idioma", "pillar": "Pilar Estratégico", "dash": "📊 Panel Unificado", "admin": "⚙️ Panel"}
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

# --- CRÉATION & MISE À JOUR AUTOMATIQUE DE LA TABLE ---
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
                    details TEXT
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
    .stApp {{
        background-image: {bg_css} !important;
        background-size: cover !important;
        background-position: center center !important;
        background-repeat: no-repeat !important;
        background-attachment: fixed !important;
    }}
    .main .block-container {{
        background: rgba(255, 255, 255, 0.93);
        padding: 2.5rem;
        border-radius: 15px;
        backdrop-filter: blur(8px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }}
    div[data-testid="stForm"] {{
        background: rgba(255, 255, 255, 0.98) !important;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(226, 232, 240, 1);
    }}
    h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown {{
        color: #0f172a !important;
    }}
    </style>
""", unsafe_allow_html=True)

# --- SÉCURITÉ MOT DE PASSE ---
password_input = st.sidebar.text_input("Password", type="password")
if password_input != "JUC2026Secure":
    st.warning("Access Restricted. Please enter the secure password in the sidebar.")
    st.stop()

# --- NAVIGATION ---
menu = st.sidebar.radio(t["title"], [t["weekly"], t["strat"], t["dash"], t["admin"]])

# --- 1. RAPPORT HEBDOMADAIRE ---
if menu == t["weekly"]:
    st.header(t["weekly"])
    st.info("Conformément au mémo de la direction, veuillez soumettre votre rapport d'activités pour la semaine ainsi que vos projections pour la semaine prochaine.")
    
    with st.form("weekly_memo_form"):
        col1, col2 = st.columns(2)
        with col1:
            staff_name = st.text_input("Full Name / Nom complet")
        with col2:
            submission_date = st.date_input("Submission Date / Date de soumission", value=date.today())
            
        dept = st.selectbox(t["dept"], ["Administration", "Finance", "Program management", "Project office", "Communication office", "Front Desk", "Monitoring and Evaluation"])
        
        completed_activities = st.text_area("Activities completed for the week ending on Friday / Activités réalisées cette semaine")
        pending_issues = st.text_area("Projection of pending issues to be completed or initiated next week / Projections et dossiers en attente pour la semaine prochaine")
        challenges = st.text_area("Challenges Encountered / Défis rencontrés")
        
        doc = st.file_uploader("Upload supporting document / Document justificatif", type=['pdf', 'jpg', 'png', 'docx'])
        
        if st.form_submit_button(t["submit"]):
            if not staff_name or not completed_activities:
                st.error("Please fill in your name and completed activities.")
            elif engine:
                combined_details = f"Accomplished: {completed_activities} || Pending/Next week: {pending_issues} || Challenges: {challenges}"
                with engine.connect() as conn:
                    conn.execute(text("""
                        INSERT INTO juc_reports (submission_date, staff_name, report_type, category, sub_category, details) 
                        VALUES (:sub_date, :n, 'Weekly', :c, :sub, :d)
                    """), {
                        "sub_date": submission_date,
                        "n": staff_name, 
                        "c": dept, 
                        "sub": "Weekly Memo Report",
                        "d": combined_details
                    })
                    conn.commit()
                st.success("Weekly report submitted successfully!")

# --- 2. RAPPORT PAR PILIER STRATÉGIQUE ---
elif menu == t["strat"]:
    st.header(t["strat"])
    st.markdown("Veuillez sélectionner le pilier stratégique concerné pour accéder à ses objectifs et activités spécifiques.")

    chosen_pillar = st.selectbox(
        "Select Strategic Pillar / Sélectionnez le Pilier Stratégique",
        [
            "Pillar 1: Research, Policy Advocacy and Civic Engagement",
            "Pillar 2: Women & Youth Empowerment through Social Innovation and Entrepreneurship",
            "Pillar 3: Integral Ecology and Community Resilience",
            "Pillar 4: Institutional Capacity Strengthening and Sustainability"
        ]
    )
    st.markdown("---")

    if chosen_pillar.startswith("Pillar 1"):
        with st.form("form_pillar_1"):
            staff_name = st.text_input("Full Name / Nom complet", key="p1_name")
            submission_date = st.date_input("Submission Date", value=date.today(), key="p1_date")
            selected_activity = st.selectbox("Core Activity", ["Obj 1.1 - Publication Basic Needs Basket", "Obj 1.2 - Youth Life-skills", "Obj 1.3 - AHAPPY Program"], key="p1_act")
            quantitative_metrics = st.text_input("Quantitative Metrics", key="p1_qm")
            beneficiaries = st.text_input("Beneficiaries", key="p1_ben")
            details = st.text_area("Progress Details", key="p1_det")
            challenges = st.text_area("Challenges", key="p1_chal")
            if st.form_submit_button(t["submit"]):
                if engine:
                    with engine.connect() as conn:
                        conn.execute(text("INSERT INTO juc_reports (submission_date, staff_name, report_type, category, sub_category, details) VALUES (:sub_date, :n, 'Strategic', :c, :sub, :d)"),
                                     {"sub_date": submission_date, "n": staff_name, "c": chosen_pillar, "sub": selected_activity, "d": f"Metrics: {quantitative_metrics} | Beneficiaries: {beneficiaries} || {details}"})
                        conn.commit()
                    st.success("Submitted successfully!")
    elif chosen_pillar.startswith("Pillar 2"):
        with st.form("form_pillar_2"):
            staff_name = st.text_input("Full Name / Nom complet", key="p2_name")
            submission_date = st.date_input("Submission Date", value=date.today(), key="p2_date")
            selected_activity = st.selectbox("Core Activity", ["Obj 2.1 - Social innovation incubation", "Obj 2.1 - Financial literacy"], key="p2_act")
            quantitative_metrics = st.text_input("Quantitative Metrics", key="p2_qm")
            beneficiaries = st.text_input("Beneficiaries", key="p2_ben")
            details = st.text_area("Progress Details", key="p2_det")
            if st.form_submit_button(t["submit"]):
                if engine:
                    with engine.connect() as conn:
                        conn.execute(text("INSERT INTO juc_reports (submission_date, staff_name, report_type, category, sub_category, details) VALUES (:sub_date, :n, 'Strategic', :c, :sub, :d)"),
                                     {"sub_date": submission_date, "n": staff_name, "c": chosen_pillar, "sub": selected_activity, "d": f"Metrics: {quantitative_metrics} | Beneficiaries: {beneficiaries} || {details}"})
                        conn.commit()
                    st.success("Submitted successfully!")
    elif chosen_pillar.startswith("Pillar 3"):
        with st.form("form_pillar_3"):
            staff_name = st.text_input("Full Name / Nom complet", key="p3_name")
            submission_date = st.date_input("Submission Date", value=date.today(), key="p3_date")
            selected_activity = st.selectbox("Core Activity", ["Obj 3.1 - Climate change awareness", "Obj 3.2 - Sustainable agriculture"], key="p3_act")
            quantitative_metrics = st.text_input("Quantitative Metrics", key="p3_qm")
            beneficiaries = st.text_input("Beneficiaries", key="p3_ben")
            details = st.text_area("Progress Details", key="p3_det")
            if st.form_submit_button(t["submit"]):
                if engine:
                    with engine.connect() as conn:
                        conn.execute(text("INSERT INTO juc_reports (submission_date, staff_name, report_type, category, sub_category, details) VALUES (:sub_date, :n, 'Strategic', :c, :sub, :d)"),
                                     {"sub_date": submission_date, "n": staff_name, "c": chosen_pillar, "sub": selected_activity, "d": f"Metrics: {quantitative_metrics} | Beneficiaries: {beneficiaries} || {details}"})
                        conn.commit()
                    st.success("Submitted successfully!")
    elif chosen_pillar.startswith("Pillar 4"):
        with st.form("form_pillar_4"):
            staff_name = st.text_input("Full Name / Nom complet", key="p4_name")
            submission_date = st.date_input("Submission Date", value=date.today(), key="p4_date")
            selected_activity = st.selectbox("Core Activity", ["Obj 4.1 - Staff capacity building", "Obj 4.2 - Corporate partnerships"], key="p4_act")
            quantitative_metrics = st.text_input("Quantitative Metrics", key="p4_qm")
            beneficiaries = st.text_input("Beneficiaries", key="p4_ben")
            details = st.text_area("Progress Details", key="p4_det")
            if st.form_submit_button(t["submit"]):
                if engine:
                    with engine.connect() as conn:
                        conn.execute(text("INSERT INTO juc_reports (submission_date, staff_name, report_type, category, sub_category, details) VALUES (:sub_date, :n, 'Strategic', :c, :sub, :d)"),
                                     {"sub_date": submission_date, "n": staff_name, "c": chosen_pillar, "sub": selected_activity, "d": f"Metrics: {quantitative_metrics} | Beneficiaries: {beneficiaries} || {details}"})
                        conn.commit()
                    st.success("Submitted successfully!")

# --- 3. DASHBOARD & ANALYSES UNIFIÉES (AVEC GRAPHIQUES SÉPARÉS DÉPARTEMENTS & PILIERS) ---
elif menu == t["dash"]:
    st.header(t["dash"])
    st.markdown("Vue d'ensemble centralisée : visualisez séparément l'activité des **Départements** et des **Piliers Stratégiques** sur une seule page, prête à être téléchargée.")
    
    if engine:
        try:
            df = pd.read_sql("SELECT * FROM juc_reports ORDER BY submission_date DESC, created_at DESC", engine)
            if df.empty:
                st.info("Aucun rapport enregistré pour le moment.")
            else:
                # Métriques Globales
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Global des Rapports", len(df))
                col2.metric("Collaborateurs Actifs", df['staff_name'].nunique() if 'staff_name' in df.columns else 0)
                col3.metric("Rapports par Piliers / Départements", len(df.dropna(subset=['category'])))
                
                st.markdown("---")
                
                # --- SECTION 1 : RAPPORT HEBDOMADAIRE PAR DÉPARTEMENT ---
                st.subheader("🏢 Résumé des Départements (Rapports Hebdomadaires)")
                df_weekly = df[df['report_type'] == 'Weekly']
                
                if df_weekly.empty:
                    st.info("Aucun rapport hebdomadaire soumis pour l'instant.")
                else:
                    dept_counts = df_weekly['category'].value_counts().reset_index()
                    dept_counts.columns = ['Département', 'Nombre de Rapports']
                    st.bar_chart(dept_counts.set_index('Département'))
                
                st.markdown("---")
                
                # --- SECTION 2 : PILIERS STRATÉGIQUES ---
                st.subheader("🎯 Résumé des Piliers Stratégiques")
                df_strat = df[df['report_type'] == 'Strategic']
                
                if df_strat.empty:
                    st.info("Aucun rapport de pilier stratégique soumis pour l'instant.")
                else:
                    pillar_counts = df_strat['category'].value_counts().reset_index()
                    pillar_counts.columns = ['Pilier Stratégique', 'Nombre de Rapports']
                    st.bar_chart(pillar_counts.set_index('Pilier Stratégique'))
                
                st.markdown("---")
                
                # --- CENTRE DE TÉLÉCHARGEMENT GLOBAL ---
                st.subheader("📥 Centre de Téléchargement Global")
                st.markdown("Téléchargez l'intégralité des données (départements et piliers confondus) en un seul clic pour vos bilans.")
                
                csv_data = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="📥 Télécharger la base complète unifiée (CSV)",
                    data=csv_data,
                    file_name=f"juc_unified_reports_{date.today()}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                
                st.markdown("---")
                st.subheader("📋 Table Détaillée Globale")
                st.dataframe(df, use_container_width=True)
                
        except Exception as e:
            st.error(f"Erreur lors du chargement des analyses : {e}")

# --- 4. ADMIN ---
elif menu == t["admin"]:
    st.header(t["admin"])
    if engine:
        try:
            df = pd.read_sql("SELECT id, submission_date, staff_name, report_type, category, sub_category FROM juc_reports ORDER BY submission_date DESC", engine)
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
