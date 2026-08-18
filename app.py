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
        "English": {"title": "JUC Portal", "weekly": "Weekly Report", "strat": "Strategic Pillar Report", "dept": "Department", "submit": "Submit", "lang": "Language", "pillar": "Strategic Pillar", "dash": "📊 Dashboard", "admin": "⚙️ Admin"},
        "Français": {"title": "Portail JUC", "weekly": "Rapport Hebdomadaire", "strat": "Rapport par Pilier Stratégique", "dept": "Département", "submit": "Soumettre", "lang": "Langue", "pillar": "Pilier Stratégique", "dash": "📊 Tableau de Bord", "admin": "⚙️ Admin"},
        "Kinyarwanda": {"title": "Urubuga JUC", "weekly": "Raporo y'icyumweru", "strat": "Raporo y'Inkingi z'Ingamba", "dept": "Ishami", "submit": "Ohereza", "lang": "Ururimi", "pillar": "Inkingi y'Ingamba", "dash": "📊 Imbonerahamwe", "admin": "⚙️ Ubuyobozi"},
        "Dutch": {"title": "JUC Portaal", "weekly": "Wekelijks Rapport", "strat": "Strategisch Pijler Rapport", "dept": "Afdeling", "submit": "Indienen", "lang": "Taal", "pillar": "Strategische Pijler", "dash": "📊 Dashboard", "admin": "⚙️ Beheer"},
        "Italian": {"title": "Portale JUC", "weekly": "Rapporto Settimanale", "strat": "Rapporto Pilastro Strategico", "dept": "Dipartimento", "submit": "Invia", "lang": "Lingua", "pillar": "Pilastro Strategico", "dash": "📊 Dashboard", "admin": "⚙️ Admin"},
        "Spanish": {"title": "Portal JUC", "weekly": "Informe Semanal", "strat": "Informe de Pilar Estratégico", "dept": "Departamento", "submit": "Enviar", "lang": "Idioma", "pillar": "Pilar Estratégico", "dash": "📊 Panel", "admin": "⚙️ Panel"}
    }

# --- INITIALISATION ---
if "lang" not in st.session_state: st.session_state.lang = "English"
trans = get_translations()
engine = create_engine(st.secrets["DATABASE_URL"]) if "DATABASE_URL" in st.secrets else None

# --- CHARGEMENT AUTOMATIQUE DE L'IMAGE DE FOND ---
# Utilisez un nom simple sans caractères spéciaux comme 'background.jpg'
default_bg_name = "background.jpg"

if "bg_base64" not in st.session_state or not st.session_state.bg_base64:
    if os.path.exists(default_bg_name):
        with open(default_bg_name, "rb") as image_file:
            st.session_state.bg_base64 = base64.b64encode(image_file.read()).decode()
    else:
        st.session_state.bg_base64 = ""

# --- CRÉATION AUTOMATIQUE DE LA TABLE ---
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

# Application du fond d'écran plein écran sécurisé
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

    if chosen_pillar == "Pillar 1: Research, Policy Advocacy and Civic Engagement":
        st.subheader("Pillar 1: Research, Policy Advocacy and Civic Engagement")
        with st.form("form_pillar_1"):
            col1, col2 = st.columns(2)
            with col1:
                staff_name = st.text_input("Full Name / Nom complet", key="p1_name")
            with col2:
                submission_date = st.date_input("Submission Date / Date de soumission", value=date.today(), key="p1_date")
                
            selected_activity = st.selectbox(
                "Core Activity / Activité clé",
                [
                    "Obj 1.1 - Quarterly publication of the Basic Needs Basket",
                    "Obj 1.1 - Policy briefs, research reports, and semestrial journal",
                    "Obj 1.1 - Hosting annual social justice conferences",
                    "Obj 1.1 - JUC Policy Forum (public op-eds, policy roundtables, media briefs)",
                    "Obj 1.2 - Life-skills training on drug abuse and sexual morality",
                    "Obj 1.2 - Leadership training programs for youth",
                    "Obj 1.2 - Public dialogues on governance, ethics, and citizenship",
                    "Obj 1.2 - Peace and constitutional literacy programs",
                    "Obj 1.2 - Annual Pluralistic Governance Forums",
                    "Obj 1.3 - African Jesuit AIDS Network HIV/AIDS Youth Prevention Program (AHAPPY)",
                    "Obj 1.3 - Value-based education and sexual/reproductive health awareness",
                    "Obj 1.3 - Drug abuse prevention campaigns"
                ],
                key="p1_act"
            )
            
            col3, col4 = st.columns(2)
            with col3:
                quantitative_metrics = st.text_input("Quantitative Metrics (participants count, reports count)", key="p1_qm")
            with col4:
                beneficiaries = st.text_input("Target Group / Beneficiaries", key="p1_ben")
                
            details = st.text_area("Detailed Progress & Qualitative Achievements", key="p1_det")
            challenges = st.text_area("Implementation Challenges", key="p1_chal")
            recommendations = st.text_area("Recommendations", key="p1_rec")
            doc = st.file_uploader("Upload monitoring document", type=['pdf', 'jpg', 'png', 'docx'], key="p1_doc")
            
            if st.form_submit_button(t["submit"]):
                if not staff_name or not details:
                    st.error("Please fill in all mandatory fields (Name and Details).")
                elif engine:
                    full_details = f"Metrics: {quantitative_metrics} | Beneficiaries: {beneficiaries} || Progress: {details} || Challenges: {challenges} || Recommendations: {recommendations}"
                    with engine.connect() as conn:
                        conn.execute(text("""
                            INSERT INTO juc_reports (submission_date, staff_name, report_type, category, sub_category, details) 
                            VALUES (:sub_date, :n, 'Strategic', :c, :sub, :d)
                        """), {
                            "sub_date": submission_date,
                            "n": staff_name, 
                            "c": "Pillar 1: Research, Policy Advocacy and Civic Engagement", 
                            "sub": selected_activity,
                            "d": full_details
                        })
                        conn.commit()
                    st.success("Pillar 1 report submitted successfully!")

    elif chosen_pillar == "Pillar 2: Women & Youth Empowerment through Social Innovation and Entrepreneurship":
        st.subheader("Pillar 2: Women & Youth Empowerment through Social Innovation and Entrepreneurship")
        with st.form("form_pillar_2"):
            col1, col2 = st.columns(2)
            with col1:
                staff_name = st.text_input("Full Name / Nom complet", key="p2_name")
            with col2:
                submission_date = st.date_input("Submission Date / Date de soumission", value=date.today(), key="p2_date")
                
            selected_activity = st.selectbox(
                "Core Activity / Activité clé",
                [
                    "Obj 2.1 - Social innovation incubation bootcamps",
                    "Obj 2.1 - Financial literacy training workshops",
                    "Obj 2.1 - Targeted women's empowerment cooperatives",
                    "Obj 2.1 - Gender and Youth Agency Index (GYAI) Assessment & Monitoring"
                ],
                key="p2_act"
            )
            
            col3, col4 = st.columns(2)
            with col3:
                quantitative_metrics = st.text_input("Quantitative Metrics (participants count, reports count)", key="p2_qm")
            with col4:
                beneficiaries = st.text_input("Target Group / Beneficiaries", key="p2_ben")
                
            details = st.text_area("Detailed Progress & Qualitative Achievements", key="p2_det")
            challenges = st.text_area("Implementation Challenges", key="p2_chal")
            recommendations = st.text_area("Recommendations", key="p2_rec")
            doc = st.file_uploader("Upload monitoring document", type=['pdf', 'jpg', 'png', 'docx'], key="p2_doc")
            
            if st.form_submit_button(t["submit"]):
                if not staff_name or not details:
                    st.error("Please fill in all mandatory fields (Name and Details).")
                elif engine:
                    full_details = f"Metrics: {quantitative_metrics} | Beneficiaries: {beneficiaries} || Progress: {details} || Challenges: {challenges} || Recommendations: {recommendations}"
                    with engine.connect() as conn:
                        conn.execute(text("""
                            INSERT INTO juc_reports (submission_date, staff_name, report_type, category, sub_category, details) 
                            VALUES (:sub_date, :n, 'Strategic', :c, :sub, :d)
                        """), {
                            "sub_date": submission_date,
                            "n": staff_name, 
                            "c": "Pillar 2: Women & Youth Empowerment", 
                            "sub": selected_activity,
                            "d": full_details
                        })
                        conn.commit()
                    st.success("Pillar 2 report submitted successfully!")

    elif chosen_pillar == "Pillar 3: Integral Ecology and Community Resilience":
        st.subheader("Pillar 3: Integral Ecology and Community Resilience")
        with st.form("form_pillar_3"):
            col1, col2 = st.columns(2)
            with col1:
                staff_name = st.text_input("Full Name / Nom complet", key="p3_name")
            with col2:
                submission_date = st.date_input("Submission Date / Date de soumission", value=date.today(), key="p3_date")
                
            selected_activity = st.selectbox(
                "Core Activity / Activité clé",
                [
                    "Obj 3.1 - Climate change awareness campaigns",
                    "Obj 3.1 - Laudato Si’ formation programs",
                    "Obj 3.1 - Ecological retreats and reflections",
                    "Obj 3.2 - Sustainable agriculture training",
                    "Obj 3.2 - Kitchen gardens and nutrition programs",
                    "Obj 3.2 - Climate-smart farming projects"
                ],
                key="p3_act"
            )
            
            col3, col4 = st.columns(2)
            with col3:
                quantitative_metrics = st.text_input("Quantitative Metrics (participants count, reports count)", key="p3_qm")
            with col4:
                beneficiaries = st.text_input("Target Group / Beneficiaries", key="p3_ben")
                
            details = st.text_area("Detailed Progress & Qualitative Achievements", key="p3_det")
            challenges = st.text_area("Implementation Challenges", key="p3_chal")
            recommendations = st.text_area("Recommendations", key="p3_rec")
            doc = st.file_uploader("Upload monitoring document", type=['pdf', 'jpg', 'png', 'docx'], key="p3_doc")
            
            if st.form_submit_button(t["submit"]):
                if not staff_name or not details:
                    st.error("Please fill in all mandatory fields (Name and Details).")
                elif engine:
                    full_details = f"Metrics: {quantitative_metrics} | Beneficiaries: {beneficiaries} || Progress: {details} || Challenges: {challenges} || Recommendations: {recommendations}"
                    with engine.connect() as conn:
                        conn.execute(text("""
                            INSERT INTO juc_reports (submission_date, staff_name, report_type, category, sub_category, details) 
                            VALUES (:sub_date, :n, 'Strategic', :c, :sub, :d)
                        """), {
                            "sub_date": submission_date,
                            "n": staff_name, 
                            "c": "Pillar 3: Integral Ecology", 
                            "sub": selected_activity,
                            "d": full_details
                        })
                        conn.commit()
                    st.success("Pillar 3 report submitted successfully!")

    elif chosen_pillar == "Pillar 4: Institutional Capacity Strengthening and Sustainability":
        st.subheader("Pillar 4: Institutional Capacity Strengthening and Sustainability")
        with st.form("form_pillar_4"):
            col1, col2 = st.columns(2)
            with col1:
                staff_name = st.text_input("Full Name / Nom complet", key="p4_name")
            with col2:
                submission_date = st.date_input("Submission Date / Date de soumission", value=date.today(), key="p4_date")
                
            selected_activity = st.selectbox(
                "Core Activity / Activité clé",
                [
                    "Obj 4.1 - Staff capacity-building and development",
                    "Obj 4.1 - Performance management implementation",
                    "Obj 4.1 - Establishing distinct departments with demarcated duties",
                    "Obj 4.1 - Consolidating monitoring and advisory boards",
                    "Obj 4.2 - Building corporate partnerships",
                    "Obj 4.2 - Designing diversified fundraising plans",
                    "Obj 4.2 - Establishing internal income-generating projects"
                ],
                key="p4_act"
            )
            
            col3, col4 = st.columns(2)
            with col3:
                quantitative_metrics = st.text_input("Quantitative Metrics (participants count, reports count)", key="p4_qm")
            with col4:
                beneficiaries = st.text_input("Target Group / Beneficiaries", key="p4_ben")
                
            details = st.text_area("Detailed Progress & Qualitative Achievements", key="p4_det")
            challenges = st.text_area("Implementation Challenges", key="p4_chal")
            recommendations = st.text_area("Recommendations", key="p4_rec")
            doc = st.file_uploader("Upload monitoring document", type=['pdf', 'jpg', 'png', 'docx'], key="p4_doc")
            
            if st.form_submit_button(t["submit"]):
                if not staff_name or not details:
                    st.error("Please fill in all mandatory fields (Name and Details).")
                elif engine:
                    full_details = f"Metrics: {quantitative_metrics} | Beneficiaries: {beneficiaries} || Progress: {details} || Challenges: {challenges} || Recommendations: {recommendations}"
                    with engine.connect() as conn:
                        conn.execute(text("""
                            INSERT INTO juc_reports (submission_date, staff_name, report_type, category, sub_category, details) 
                            VALUES (:sub_date, :n, 'Strategic', :c, :sub, :d)
                        """), {
                            "sub_date": submission_date,
                            "n": staff_name, 
                            "c": "Pillar 4: Institutional Capacity", 
                            "sub": selected_activity,
                            "d": full_details
                        })
                        conn.commit()
                    st.success("Pillar 4 report submitted successfully!")

# --- 3. DASHBOARD ---
elif menu == t["dash"]:
    st.header(t["dash"])
    if engine:
        try:
            df = pd.read_sql("SELECT * FROM juc_reports ORDER BY submission_date DESC, created_at DESC", engine)
            if df.empty:
                st.info("No reports recorded yet.")
            else:
                st.metric(label="Total Reports", value=len(df))
                st.dataframe(df, use_container_width=True)
                
                csv_data = df.to_csv(index=False).encode("utf-8")
                st.download_button("Download Data as CSV", data=csv_data, file_name="juc_reports.csv", mime="text/csv")
        except Exception as e:
            st.info("Database table initializing or empty.")

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
            
