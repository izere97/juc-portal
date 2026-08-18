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
            conn.execute(text("ALTER TABLE juc_reports ADD COLUMN IF NOT EXISTS completed_activities TEXT;"))
            conn.execute(text("ALTER TABLE juc_reports ADD COLUMN IF NOT EXISTS pending_issues TEXT;"))
            conn.execute(text("ALTER TABLE juc_reports ADD COLUMN IF NOT EXISTS challenges TEXT;"))
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
        background: rgba(255, 255, 258, 0.98) !important;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(226, 232, 240, 1);
    }}
    .bubble-card {{
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 2px solid #cbd5e1;
        border-radius: 20px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-bottom: 20px;
    }}
    .bubble-admin {{
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        border: 2px solid #3b82f6;
        border-radius: 25px;
        padding: 25px;
        text-align: center;
        box-shadow: 0 6px 16px rgba(59, 130, 246, 0.15);
        margin-bottom: 25px;
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
                with engine.connect() as conn:
                    conn.execute(text("""
                        INSERT INTO juc_reports (
                            submission_date, staff_name, report_type, category, sub_category, 
                            completed_activities, pending_issues, challenges
                        ) 
                        VALUES (
                            :sub_date, :n, 'Weekly', :c, :sub, 
                            :comp, :pend, :chal
                        )
                    """), {
                        "sub_date": submission_date,
                        "n": staff_name, 
                        "c": dept, 
                        "sub": "JUC weekly report",
                        "comp": completed_activities,
                        "pend": pending_issues,
                        "chal": challenges
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
            completed_activities = st.text_area("Progress Details / Activités réalisées", key="p1_det")
            pending_issues = st.text_area("Pending / Projections semaine prochaine", key="p1_pend")
            challenges = st.text_area("Challenges / Défis", key="p1_chal")
            if st.form_submit_button(t["submit"]):
                if engine:
                    with engine.connect() as conn:
                        conn.execute(text("""
                            INSERT INTO juc_reports (
                                submission_date, staff_name, report_type, category, sub_category, 
                                completed_activities, pending_issues, challenges
                            ) VALUES (:sub_date, :n, 'Strategic', :c, :sub, :comp, :pend, :chal)
                        """), {
                            "sub_date": submission_date, "n": staff_name, "c": chosen_pillar, "sub": f"{selected_activity} | Metrics: {quantitative_metrics} | Ben: {beneficiaries}",
                            "comp": completed_activities, "pend": pending_issues, "chal": challenges
                        })
                        conn.commit()
                    st.success("Submitted successfully!")
    elif chosen_pillar.startswith("Pillar 2"):
        with st.form("form_pillar_2"):
            staff_name = st.text_input("Full Name / Nom complet", key="p2_name")
            submission_date = st.date_input("Submission Date", value=date.today(), key="p2_date")
            selected_activity = st.selectbox("Core Activity", ["Obj 2.1 - Social innovation incubation", "Obj 2.1 - Financial literacy"], key="p2_act")
            quantitative_metrics = st.text_input("Quantitative Metrics", key="p2_qm")
            beneficiaries = st.text_input("Beneficiaries", key="p2_ben")
            completed_activities = st.text_area("Progress Details / Activités réalisées", key="p2_det")
            pending_issues = st.text_area("Pending / Projections semaine prochaine", key="p2_pend")
            challenges = st.text_area("Challenges / Défis", key="p2_chal")
            if st.form_submit_button(t["submit"]):
                if engine:
                    with engine.connect() as conn:
                        conn.execute(text("""
                            INSERT INTO juc_reports (
                                submission_date, staff_name, report_type, category, sub_category, 
                                completed_activities, pending_issues, challenges
                            ) VALUES (:sub_date, :n, 'Strategic', :c, :sub, :comp, :pend, :chal)
                        """), {
                            "sub_date": submission_date, "n": staff_name, "c": chosen_pillar, "sub": f"{selected_activity} | Metrics: {quantitative_metrics} | Ben: {beneficiaries}",
                            "comp": completed_activities, "pend": pending_issues, "chal": challenges
                        })
                        conn.commit()
                    st.success("Submitted successfully!")
    elif chosen_pillar.startswith("Pillar 3"):
        with st.form("form_pillar_3"):
            staff_name = st.text_input("Full Name / Nom complet", key="p3_name")
            submission_date = st.date_input("Submission Date", value=date.today(), key="p3_date")
            selected_activity = st.selectbox("Core Activity", ["Obj 3.1 - Climate change awareness", "Obj 3.2 - Sustainable agriculture"], key="p3_act")
            quantitative_metrics = st.text_input("Quantitative Metrics", key="p3_qm")
            beneficiaries = st.text_input("Beneficiaries", key="p3_ben")
            completed_activities = st.text_area("Progress Details / Activités réalisées", key="p3_det")
            pending_issues = st.text_area("Pending / Projections semaine prochaine", key="p3_pend")
            challenges = st.text_area("Challenges / Défis", key="p3_chal")
            if st.form_submit_button(t["submit"]):
                if engine:
                    with engine.connect() as conn:
                        conn.execute(text("""
                            INSERT INTO juc_reports (
                                submission_date, staff_name, report_type, category, sub_category, 
                                completed_activities, pending_issues, challenges
                            ) VALUES (:sub_date, :n, 'Strategic', :c, :sub, :comp, :pend, :chal)
                        """), {
                            "sub_date": submission_date, "n": staff_name, "c": chosen_pillar, "sub": f"{selected_activity} | Metrics: {quantitative_metrics} | Ben: {beneficiaries}",
                            "comp": completed_activities, "pend": pending_issues, "chal": challenges
                        })
                        conn.commit()
                    st.success("Submitted successfully!")
    elif chosen_pillar.startswith("Pillar 4"):
        with st.form("form_pillar_4"):
            staff_name = st.text_input("Full Name / Nom complet", key="p4_name")
            submission_date = st.date_input("Submission Date", value=date.today(), key="p4_date")
            selected_activity = st.selectbox("Core Activity", ["Obj 4.1 - Staff capacity building", "Obj 4.2 - Corporate partnerships"], key="p4_act")
            quantitative_metrics = st.text_input("Quantitative Metrics", key="p4_qm")
            beneficiaries = st.text_input("Beneficiaries", key="p4_ben")
            completed_activities = st.text_area("Progress Details / Activités réalisées", key="p4_det")
            pending_issues = st.text_area("Pending / Projections semaine prochaine", key="p4_pend")
            challenges = st.text_area("Challenges / Défis", key="p4_chal")
            if st.form_submit_button(t["submit"]):
                if engine:
                    with engine.connect() as conn:
                        conn.execute(text("""
                            INSERT INTO juc_reports (
                                submission_date, staff_name, report_type, category, sub_category, 
                                completed_activities, pending_issues, challenges
                            ) VALUES (:sub_date, :n, 'Strategic', :c, :sub, :comp, :pend, :chal)
                        """), {
                            "sub_date": submission_date, "n": staff_name, "c": chosen_pillar, "sub": f"{selected_activity} | Metrics: {quantitative_metrics} | Ben: {beneficiaries}",
                            "comp": completed_activities, "pend": pending_issues, "chal": challenges
                        })
                        conn.commit()
                    st.success("Submitted successfully!")

# --- 3. DASHBOARD SOUS FORME DE BULLES (ORGANIGRAMME / RÉSEAU & DÉTAILS WORD) ---
elif menu == t["dash"]:
    st.header(t["dash"])
    st.markdown("Vue d'ensemble et consultation détaillée par département/pilier avec option de téléchargement Word.")
    
    if engine:
        try:
            df = pd.read_sql("SELECT * FROM juc_reports", engine)
            
            # --- SOMMET : BULLE ADMIN ---
            st.markdown("""
                <div class="bubble-admin">
                    <h3>🏛️ Administration & Direction</h3>
                    <p>Supervision générale et pilotage institutionnel</p>
                </div>
            """, unsafe_allow_html=True)
            
            # --- NIVEAU INTERMÉDIAIRE : LES 3 COLONNES ---
            col_left, col_mid, col_right = st.columns(3)
            
            with col_left:
                st.markdown("""
                    <div class="bubble-card">
                        <h4>💼 Finance & Admin</h4>
                        <p>Gestion financière & Opérations</p>
                    </div>
                """, unsafe_allow_html=True)
                fin_count = len(df[df['category'] == 'Finance']) if not df.empty and 'category' in df.columns else 0
                st.metric("Rapports Finance", fin_count)
            
            with col_mid:
                st.markdown("""
                    <div class="bubble-card">
                        <h4>📊 Program Management</h4>
                        <p>Coordination des programmes & M&E</p>
                    </div>
                """, unsafe_allow_html=True)
                prog_count = len(df[df['category'].str.contains('Program|Monitoring', case=False, na=False)]) if not df.empty and 'category' in df.columns else 0
                st.metric("Rapports Programmes", prog_count)
            
            with col_right:
                st.markdown("""
                    <div class="bubble-card">
                        <h4>🎯 Piliers Stratégiques</h4>
                        <p>Piliers 1, 2, 3 & 4</p>
                    </div>
                """, unsafe_allow_html=True)
                strat_count = len(df[df['report_type'] == 'Strategic']) if not df.empty and 'report_type' in df.columns else 0
                st.metric("Rapports Piliers", strat_count)

            st.markdown("---")
            
            # --- SECTION DÉTAILS PAR DÉPARTEMENT / PILIER ---
            st.subheader("🔍 Consultation détaillée par entité")
            if not df.empty:
                all_categories = df['category'].dropna().unique().tolist()
                selected_cat_view = st.selectbox("Filtrer par Département ou Pilier pour voir les détails :", all_categories)
                
                filtered_df = df[df['category'] == selected_cat_view]
                st.markdown(f"### Rapports pour : **{selected_cat_view}**")
                
                for index, row in filtered_df.iterrows():
                    with st.expander(f"👤 {row.get('staff_name', 'N/A')} — Date: {row.get('submission_date', 'N/A')} ({row.get('sub_category', '')})"):
                        st.markdown(f"**✅ Activités réalisées :**\n{row.get('completed_activities', 'N/A')}")
                        st.markdown(f"**⏳ Projections / En attente :**\n{row.get('pending_issues', 'N/A')}")
                        st.markdown(f"**⚠️ Défis rencontrés :**\n{row.get('challenges', 'N/A')}")
                
                st.markdown("---")
                
                # --- GÉNÉRATEUR DE DOCUMENT WORD (.DOCX) ---
                st.subheader("📥 Exporter le rapport au format Word")
                
                if st.button("Générer le document Word (.docx) pour cette sélection"):
                    doc = Document()
                    doc.add_heading(f"Rapport JUC - {selected_cat_view}", 0)
                    doc.add_paragraph(f"Date de génération : {date.today().strftime('%Y-%m-%d')}")
                    doc.add_paragraph(f"Nombre total de soumissions : {len(filtered_df)}")
                    doc.add_heading("Détail des activités", level=1)
                    
                    for index, row in filtered_df.iterrows():
                        p = doc.add_paragraph()
                        p.add_run(f"Collaborateur : {row.get('staff_name', 'N/A')}").bold = True
                        p.add_run(f"\nDate : {row.get('submission_date', 'N/A')}\n")
                        p.add_run(f"Activités réalisées :\n{row.get('completed_activities', 'N/A')}\n")
                        p.add_run(f"Projections :\n{row.get('pending_issues', 'N/A')}\n")
                        p.add_run(f"Défis :\n{row.get('challenges', 'N/A')}\n\n")
                    
                    # Sauvegarde en mémoire tampon
                    buffer = io.BytesIO()
                    doc.save(buffer)
                    buffer.seek(0)
                    
                    st.download_button(
                        label=f"📥 Télécharger le Word pour {selected_cat_view}",
                        data=buffer,
                        file_name=f"JUC_Rapport_{selected_cat_view.replace(' ', '_')}_{date.today()}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True
                    )
            else:
                st.info("Aucune donnée enregistrée pour le moment.")
                
        except Exception as e:
            st.error(f"Erreur lors du chargement des bulles : {e}")

# --- 4. ADMIN ---
elif menu == t["admin"]:
    st.header(t["admin"])
    if engine:
        try:
            df = pd.read_sql("SELECT id, submission_date, staff_name, report_type, category, completed_activities, pending_issues, challenges FROM juc_reports ORDER BY submission_date DESC", engine)
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
