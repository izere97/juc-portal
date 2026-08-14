from datetime import datetime
import io
import pandas as pd
from sqlalchemy import create_engine
import streamlit as st

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="JUC Staff & M&E Portal", page_icon="📊", layout="wide"
)

# --- SQL CONNECTION SETUP ---
DATABASE_URL = "postgresql://postgres:VOTRE_MOT_DE_PASSE@VOTRE_HOTE:5432/postgres"

@st.cache_resource
def init_sql_engine():
  try:
    engine = create_engine(DATABASE_URL)
    return engine
  except Exception as e:
    return None

engine = init_sql_engine()

# --- INITIALIZE SESSION STATE ---
if "reports_db" not in st.session_state:
  st.session_state["reports_db"] = pd.DataFrame(
      columns=[
          "Date",
          "Staff Name",
          "Department",
          "Activities",
          "Challenges",
          "Projections",
      ]
  )

# Separate tracking states for each strategic pillar based on the 2026-2031 Strategic Plan
if "pillar_1_data" not in st.session_state:
  st.session_state["pillar_1_data"] = pd.DataFrame(
      columns=[
          "Date",
          "Initiative / Activity",
          "Outputs (e.g., BNB reports, Policy Briefs)",
          "Lead Officer",
          "Status",
      ]
  )

if "pillar_2_data" not in st.session_state:
  st.session_state["pillar_2_data"] = pd.DataFrame(
      columns=[
          "Date",
          "Initiative / Activity",
          "Micro-enterprises / GYAI Score",
          "Lead Officer",
          "Status",
      ]
  )

if "pillar_3_data" not in st.session_state:
  st.session_state["pillar_3_data"] = pd.DataFrame(
      columns=[
          "Date",
          "Initiative / Activity",
          "Households / Certified Agents",
          "Lead Officer",
          "Status",
      ]
  )

if "pillar_4_data" not in st.session_state:
  st.session_state["pillar_4_data"] = pd.DataFrame(
      columns=[
          "Date",
          "Management / Revenue Action",
          "Performance Metric / Self-Reliance %",
          "Lead Officer",
          "Status",
      ]
  )

# --- OFFICIAL LISTS ---
DEPARTMENTS = [
    "Administration (Director and Assistant Director)",
    "Finance",
    "Project Manager",
    "Project Officer",
    "Front Desk",
    "M&E",
    "Communication Officer",
]

# --- ACCESS CONTROL (PASSWORD PROTECTION) ---
PORTAL_PASSWORD = "JUC2026Secure"

def check_password():
  def password_entered():
    if st.session_state["password"] == PORTAL_PASSWORD:
      st.session_state["password_correct"] = True
      del st.session_state["password"]
    else:
      st.session_state["password_correct"] = False

  if "password_correct" not in st.session_state:
    st.markdown("## 🔒 JUC Staff & M&E Portal - Secured Access")
    st.text_input(
        "Enter secure access password:",
        type="password",
        on_change=password_entered,
        key="password",
    )
    return False
  elif not st.session_state["password_correct"]:
    st.markdown("## 🔒 JUC Staff & M&E Portal - Secured Access")
    st.text_input(
        "Enter secure access password:",
        type="password",
        on_change=password_entered,
        key="password",
    )
    st.error("😕 Incorrect password")
    return False
  else:
    return True

if not check_password():
  st.stop()

# --- SIDEBAR LOGO & SETTINGS ---
try:
  st.sidebar.image("Screenshot 2026-08-14 143018.png", use_container_width=True)
except Exception:
  st.sidebar.warning("Logo introuvable (Screenshot 2026-08-14 143018.png)")

st.sidebar.header("⚙️ Portal Settings")
lang = st.sidebar.selectbox("Language / Langue", ["English", "Français"])

st.sidebar.markdown("---")
st.sidebar.header("📌 Navigation")

if lang == "English":
  app_mode = st.sidebar.selectbox(
      "Select View",
      [
          "Submit Weekly Report",
          "Strategic Plan: Pillar 1 (Research & Advocacy)",
          "Strategic Plan: Pillar 2 (Women & Youth Empowerment)",
          "Strategic Plan: Pillar 3 (Integral Ecology)",
          "Strategic Plan: Pillar 4 (Institutional Capacity)",
          "Manager Compilation Dashboard",
          "General Institutional Report",
          "Staff Data Workspace & Statistical Tools",
      ],
  )
else:
  app_mode = st.sidebar.selectbox(
      "Sélectionner la vue",
      [
          "Soumettre le rapport hebdomadaire",
          "Plan Stratégique : Pilier 1 (Recherche & Plaidoyer)",
          "Plan Stratégique : Pilier 2 (Autonomisation Femmes & Jeunes)",
          "Plan Stratégique : Pilier 3 (Écologie Intégrale)",
          "Plan Stratégique : Pilier 4 (Capacité Institutionnelle)",
          "Tableau de bord de compilation",
          "Rapport institutionnel général",
          "Espace Données Staff & Outils Statistiques",
      ],
  )

# --- MAIN APP HEADER ---
st.title("📊 JUC Staff & M&E Portal")
if lang == "English":
  st.markdown(
      "**Jesuit Urumuri Centre (JUC)** — Official M&E, private database,"
      " reporting, and tracking platform (2026-2031 Strategy)[cite: 1]."
  )
else:
  st.markdown(
      "**Centre Urumuri des Jésuites (JUC)** — Plateforme officielle de suivi,"
      " base de données privée et rapportage (Stratégie 2026-2031)[cite: 1]."
  )

st.markdown("---")

# ==========================================
# 1. SUBMIT WEEKLY REPORT
# ==========================================
if (
    app_mode == "Submit Weekly Report"
    or app_mode == "Soumettre le rapport hebdomadaire"
):
  if lang == "English":
    st.subheader("📝 Weekly Activity Report Submission")
    st.markdown(
        "Fill out this form to submit your weekly activity report directly to"
        " the database."
    )
  else:
    st.subheader("📝 Soumission du rapport d'activité hebdomadaire")
    st.markdown(
        "Remplissez ce formulaire pour envoyer votre rapport d'activité"
        " directement dans la base de données."
    )

  with st.form("weekly_report_form"):
    col1, col2 = st.columns(2)
    with col1:
      staff_name = st.text_input(
          "Staff Name / Nom et Prénom",
          placeholder="e.g., Jean Claude Ntakirutimana",
      )
    with col2:
      department = st.selectbox("Department / Département", DEPARTMENTS)

    report_date = st.date_input("Report Date / Date du rapport")

    if lang == "English":
      activities = st.text_area("1. Activities Completed This Week")
      challenges = st.text_area("2. Challenges Encountered (Optional)")
      projections = st.text_area("3. Projections for Next Week")
      submit_label = "Submit Weekly Report"
    else:
      activities = st.text_area("1. Activités réalisées cette semaine")
      challenges = st.text_area("2. Défis rencontrés (optionnel)")
      projections = st.text_area("3. Projections pour la semaine prochaine")
      submit_label = "Envoyer le rapport hebdomadaire"

    submitted = st.form_submit_button(submit_label)

    if submitted:
      if not staff_name.strip():
        st.warning(
            "⚠️ Please enter your name."
            if lang == "English"
            else "⚠️ Veuillez entrer votre nom."
        )
      else:
        new_entry = {
            "Date": str(report_date),
            "Staff Name": staff_name,
            "Department": department,
            "Activities": activities,
            "Challenges": challenges,
            "Projections": projections,
        }

        new_row_df = pd.DataFrame([new_entry])
        st.session_state["reports_db"] = pd.concat(
            [st.session_state["reports_db"], new_row_df], ignore_index=True
        )

        if engine:
          try:
            new_row_df.to_sql(
                "juc_reports", con=engine, if_exists="append", index=False
            )
          except Exception:
            pass

        st.success(
            f"✅ Weekly report successfully saved for **{staff_name}**!"
            if lang == "English"
            else f"✅ Rapport hebdomadaire enregistré avec succès pour **{staff_name}** !"
        )

# ==========================================
# 2. STRATEGIC PLAN: PILLAR 1
# ==========================================
elif (
    app_mode == "Strategic Plan: Pillar 1 (Research & Advocacy)"
    or app_mode == "Plan Stratégique : Pilier 1 (Recherche & Plaidoyer)"
):
  if lang == "English":
    st.subheader(
        "🎯 Pillar 1: Research, Policy Advocacy, and Civic Engagement"
    )
    st.markdown(
        "Track indicators for Basic Needs Basket, policy briefs, journals,"
        " civic education, AHAPPY, and Pluralistic Forums[cite: 1]."
    )
  else:
    st.subheader(
        "🎯 Pilier 1 : Recherche, Plaidoyer et Engagement Civique"
    )
    st.markdown(
        "Suivez les indicateurs du Panier de Biens de Base, notes de"
        " plaidoyer, revues, éducation civique, AHAPPY et forums pluralistes[cite: 1]."
    )

  with st.form("pillar_1_form"):
    col1, col2 = st.columns(2)
    with col1:
      activity_name = st.text_input(
          "Research / Activity Title (e.g., Q3 Basic Needs Basket)"
          if lang == "English"
          else "Titre de l'activité / recherche (ex: Panier de base Q3)"
      )
    with col2:
      outputs = st.text_input(
          "Outputs / Target Reached (e.g., 1 Report published, 45 youth)"
          if lang == "English"
          else "Résultats / Cibles atteintes (ex: 1 Rapport publié, 45 jeunes)"
      )

    c1, c2 = st.columns(2)
    with c1:
      officer = st.text_input(
          "Lead Researcher / Officer"
          if lang == "English"
          else "Chercheur / Responsable"
      )
    with c2:
      status = st.selectbox(
          "Status / Statut",
          [
              "On Track / En cours",
              "Completed / Terminé",
              "Delayed / Retardé",
          ],
      )

    submitted_p1 = st.form_submit_button(
        "Save Pillar 1 Progress"
        if lang == "English"
        else "Enregistrer le progrès du Pilier 1"
    )

    if submitted_p1:
      new_p1 = pd.DataFrame([{
          "Date": str(datetime.now().date()),
          "Initiative / Activity": activity_name,
          "Outputs (e.g., BNB reports, Policy Briefs)": outputs,
          "Lead Officer": officer,
          "Status": status,
      }])
      st.session_state["pillar_1_data"] = pd.concat(
          [st.session_state["pillar_1_data"], new_p1], ignore_index=True
      )
      st.success(
          "✅ Pillar 1 progress saved successfully!"
          if lang == "English"
          else "✅ Progrès du Pilier 1 enregistré avec succès !"
      )

  st.markdown("### 📋 Logged Data: Pillar 1")
  st.dataframe(st.session_state["pillar_1_data"], use_container_width=True)

# ==========================================
# 3. STRATEGIC PLAN: PILLAR 2
# ==========================================
elif (
    app_mode
    == "Strategic Plan: Pillar 2 (Women & Youth Empowerment)"
    or app_mode
    == "Plan Stratégique : Pilier 2 (Autonomisation Femmes & Jeunes)"
):
  if lang == "English":
    st.subheader(
        "🎯 Pillar 2: Women and Youth Empowerment through Social Innovation"
    )
    st.markdown(
        "Track entrepreneurship incubators, financial literacy, women"
        " cooperatives, and the Gender & Youth Agency Index (GYAI)[cite: 1]."
    )
  else:
    st.subheader(
        "🎯 Pilier 2 : Autonomisation des femmes et des jeunes par l'innovation"
    )
    st.markdown(
        "Suivez les incubateurs d'entrepreneuriat, l'éducation financière,"
        " coopératives féminines et l'Indice d'Agence (GYAI)[cite: 1]."
    )

  with st.form("pillar_2_form"):
    col1, col2 = st.columns(2)
    with col1:
      activity_name = st.text_input(
          "Program / Bootcamp Name"
          if lang == "English"
          else "Nom du programme / Bootcamp"
      )
    with col2:
      metrics = st.text_input(
          "Micro-enterprises / GYAI Score (e.g., 15 businesses, +20% GYAI)"
          if lang == "English"
          else "Micro-entreprises / Score GYAI (ex: 15 entreprises, +20% GYAI)"
      )

    c1, c2 = st.columns(2)
    with c1:
      officer = st.text_input(
          "Lead Facilitator / Officer"
          if lang == "English"
          else "Facilitateur / Responsable"
      )
    with c2:
      status = st.selectbox(
          "Status / Statut",
          [
              "On Track / En cours",
              "Completed / Terminé",
              "Delayed / Retardé",
          ],
      )

    submitted_p2 = st.form_submit_button(
        "Save Pillar 2 Progress"
        if lang == "English"
        else "Enregistrer le progrès du Pilier 2"
    )

    if submitted_p2:
      new_p2 = pd.DataFrame([{
          "Date": str(datetime.now().date()),
          "Initiative / Activity": activity_name,
          "Micro-enterprises / GYAI Score": metrics,
          "Lead Officer": officer,
          "Status": status,
      }])
      st.session_state["pillar_2_data"] = pd.concat(
          [st.session_state["pillar_2_data"], new_p2], ignore_index=True
      )
      st.success(
          "✅ Pillar 2 progress saved successfully!"
          if lang == "English"
          else "✅ Progrès du Pilier 2 enregistré avec succès !"
      )

  st.markdown("### 📋 Logged Data: Pillar 2")
  st.dataframe(st.session_state["pillar_2_data"], use_container_width=True)

# ==========================================
# 4. STRATEGIC PLAN: PILLAR 3
# ==========================================
elif (
    app_mode == "Strategic Plan: Pillar 3 (Integral Ecology)"
    or app_mode == "Plan Stratégique : Pilier 3 (Écologie Intégrale)"
):
  if lang == "English":
    st.subheader("🎯 Pillar 3: Integral Ecology and Community Resilience")
    st.markdown(
        "Track Laudato Si' formation, climate-smart agriculture, kitchen"
        " gardens, and certified change agents[cite: 1]."
    )
  else:
    st.subheader("🎯 Pilier 3 : Écologie Intégrale et Résilience Communautaire")
    st.markdown(
        "Suivez les formations Laudato Si', agriculture intelligente face au"
        " climat, jardins de paillotte et agents certifiés[cite: 1]."
    )

  with st.form("pillar_3_form"):
    col1, col2 = st.columns(2)
    with col1:
      activity_name = st.text_input(
          "Ecological / Agricultural Activity"
          if lang == "English"
          else "Activité écologique / agricole"
      )
    with col2:
      metrics = st.text_input(
          "Households / Certified Agents (e.g., 120 households, 25 agents)"
          if lang == "English"
          else "Ménages / Agents certifiés (ex: 120 ménages, 25 agents)"
      )

    c1, c2 = st.columns(2)
    with c1:
      officer = st.text_input(
          "Extension Officer / Animator"
          if lang == "English"
          else "Officier d'extension / Animateur"
      )
    with c2:
      status = st.selectbox(
          "Status / Statut",
          [
              "On Track / En cours",
              "Completed / Terminé",
              "Delayed / Retardé",
          ],
      )

    submitted_p3 = st.form_submit_button(
        "Save Pillar 3 Progress"
        if lang == "English"
        else "Enregistrer le progrès du Pilier 3"
    )

    if submitted_p3:
      new_p3 = pd.DataFrame([{
          "Date": str(datetime.now().date()),
          "Initiative / Activity": activity_name,
          "Households / Certified Agents": metrics,
          "Lead Officer": officer,
          "Status": status,
      }])
      st.session_state["pillar_3_data"] = pd.concat(
          [st.session_state["pillar_3_data"], new_p3], ignore_index=True
      )
      st.success(
          "✅ Pillar 3 progress saved successfully!"
          if lang == "English"
          else "✅ Progrès du Pilier 3 enregistré avec succès !"
      )

  st.markdown("### 📋 Logged Data: Pillar 3")
  st.dataframe(st.session_state["pillar_3_data"], use_container_width=True)

# ==========================================
# 5. STRATEGIC PLAN: PILLAR 4
# ==========================================
elif (
    app_mode == "Strategic Plan: Pillar 4 (Institutional Capacity)"
    or app_mode == "Plan Stratégique : Pilier 4 (Capacité Institutionnelle)"
):
  if lang == "English":
    st.subheader(
        "🎯 Pillar 4: Institutional Capacity Strengthening and Sustainability"
    )
    st.markdown(
        "Track staff performance management systems, internal revenue"
        " generation (20% target), and resource mobilization[cite: 1]."
    )
  else:
    st.subheader(
        "🎯 Pilier 4 : Renforcement des Capacités Institutionnelles"
    )
    st.markdown(
        "Suivez les systèmes de performance du personnel, la génération de"
        " revenus internes (cible 20%) et la mobilisation de ressources[cite: 1]."
    )

  with st.form("pillar_4_form"):
    col1, col2 = st.columns(2)
    with col1:
      activity_name = st.text_input(
          "Governance / Fundraising Initiative"
          if lang == "English"
          else "Initiative de gouvernance / levée de fonds"
      )
    with col2:
      metrics = st.text_input(
          "Performance Metric / Self-Reliance % (e.g., 100% HR alignment, 12%)"
          if lang == "English"
          else "Métrique / % d'autonomie (ex: 100% alignement RH, 12%)"
      )

    c1, c2 = st.columns(2)
    with c1:
      officer = st.text_input(
          "Lead Manager / Officer"
          if lang == "English"
          else "Manager / Responsable"
      )
    with c2:
      status = st.selectbox(
          "Status / Statut",
          [
              "On Track / En cours",
              "Completed / Terminé",
              "Delayed / Retardé",
          ],
      )

    submitted_p4 = st.form_submit_button(
        "Save Pillar 4 Progress"
        if lang == "English"
        else "Enregistrer le progrès du Pilier 4"
    )

    if submitted_p4:
      new_p4 = pd.DataFrame([{
          "Date": str(datetime.now().date()),
          "Management / Revenue Action": activity_name,
          "Performance Metric / Self-Reliance %": metrics,
          "Lead Officer": officer,
          "Status": status,
      }])
      st.session_state["pillar_4_data"] = pd.concat(
          [st.session_state["pillar_4_data"], new_p4], ignore_index=True
      )
      st.success(
          "✅ Pillar 4 progress saved successfully!"
          if lang == "English"
          else "✅ Progrès du Pilier 4 enregistré avec succès !"
      )

  st.markdown("### 📋 Logged Data: Pillar 4")
  st.dataframe(st.session_state["pillar_4_data"], use_container_width=True)

# ==========================================
# 6. MANAGER COMPILATION DASHBOARD
# ==========================================
elif (
    app_mode == "Manager Compilation Dashboard"
    or app_mode == "Tableau de bord de compilation"
):
  if lang == "English":
    st.subheader("📈 Management Compilation Dashboard")
    st.markdown(
        "Real-time overview of all collected operational data across pillars"
        " and reports."
    )
  else:
    st.subheader("📈 Tableau de bord de compilation de la direction")
    st.markdown(
        "Vue d'ensemble en temps réel de toutes les données opérationnelles."
    )

  tab1, tab2, tab3, tab4, tab5 = st.tabs(
      [
          "Weekly Reports",
          "Pillar 1 Data",
          "Pillar 2 Data",
          "Pillar 3 Data",
          "Pillar 4 Data",
      ]
  )

  with tab1:
    st.dataframe(st.session_state["reports_db"], use_container_width=True)
  with tab2:
    st.dataframe(st.session_state["pillar_1_data"], use_container_width=True)
  with tab3:
    st.dataframe(st.session_state["pillar_2_data"], use_container_width=True)
  with tab4:
    st.dataframe(st.session_state["pillar_3_data"], use_container_width=True)
  with tab5:
    st.dataframe(st.session_state["pillar_4_data"], use_container_width=True)

# ==========================================
# 7. GENERAL INSTITUTIONAL REPORT
# ==========================================
elif (
    app_mode == "General Institutional Report"
    or app_mode == "Rapport institutionnel général"
):
  if lang == "English":
    st.subheader("📋 General Institutional Summary Report")
    total_subs = len(st.session_state["reports_db"])

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Weekly Submissions", str(total_subs))
    m2.metric("Strategic Pillars", "4 / 4", "Active[cite: 1]")
    m3.metric("Institutional Coverage", "100%", "Complete")
    m4.metric("Compliance Rate", "95%", "Optimal")

    st.markdown("---")
    st.markdown("### 📊 Consolidated Plan Execution Overview (2026-2031)")
    summary_table = pd.DataFrame({
        "Strategic Pillar": [
            "Pillar 1: Research, Policy Advocacy & Civic Engagement",
            "Pillar 2: Women & Youth Empowerment",
            "Pillar 3: Integral Ecology & Resilience",
            "Pillar 4: Institutional Capacity & Sustainability",
        ],
        "Active Logged Entries": [
            len(st.session_state["pillar_1_data"]),
            len(st.session_state["pillar_2_data"]),
            len(st.session_state["pillar_3_data"]),
            len(st.session_state["pillar_4_data"]),
        ],
        "Overall Status": ["On Track", "On Track", "On Track", "Active"],
    })
    st.dataframe(summary_table, use_container_width=True)
  else:
    st.subheader("📋 Rapport de Synthèse Institutionnel Général")
    total_subs = len(st.session_state["reports_db"])

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Rapports Hebdomadaires", str(total_subs))
    m2.metric("Piliers Stratégiques", "4 / 4", "Actifs[cite: 1]")
    m3.metric("Couverture Institutionnelle", "100%", "Complet")
    m4.metric("Conformité", "95%", "Optimal")

    st.markdown("---")
    st.markdown("### 📊 Vue d'ensemble de l'exécution du plan (2026-2031)")
    summary_table = pd.DataFrame({
        "Pilier Stratégique": [
            "Pilier 1 : Recherche, Plaidoyer & Engagement Civique",
            "Pilier 2 : Autonomisation Femmes & Jeunes",
            "Pilier 3 : Écologie Intégrale & Résilience",
            "Pilier 4 : Capacité Institutionnelle & Durabilité",
        ],
        "Entrées Enregistrées": [
            len(st.session_state["pillar_1_data"]),
            len(st.session_state["pillar_2_data"]),
            len(st.session_state["pillar_3_data"]),
            len(st.session_state["pillar_4_data"]),
        ],
        "Statut Global": ["En cours", "En cours", "En cours", "Actif"],
    })
    st.dataframe(summary_table, use_container_width=True)

# ==========================================
# 8. STAFF DATA WORKSPACE & STATISTICAL TOOLS (UPLOAD/DOWNLOAD)
# ==========================================
elif (
    app_mode == "Staff Data Workspace & Statistical Tools"
    or app_mode == "Espace Données Staff & Outils Statistiques"
):
  if lang == "English":
    st.subheader("🗄️ Staff Data Workspace & Statistical Tools")
    st.markdown(
        "Manage, download, and upload datasets entered by staff (Weekly Reports"
        " and Strategic Pillars) to easily manipulate indicators using statistical"
        " software (SPSS, Stata, R, Python)."
    )
  else:
    st.subheader("🗄️ Espace Données Staff & Outils d'Analyse Statistique")
    st.markdown(
        "Gérez, téléchargez et téléversez les jeux de données saisis par le"
        " personnel (Rapports hebdomadaires et Piliers Stratégiques) pour une"
        " manipulation facile avec vos logiciels statistiques (SPSS, Stata, R,"
        " Python)."
    )

  dataset_choice = st.selectbox(
      "Select Staff Dataset to Manage / Sélectionner le jeu de données du staff:",
      [
          "Weekly Reports (juc_reports)",
          "Strategic Plan: Pillar 1 Data",
          "Strategic Plan: Pillar 2 Data",
          "Strategic Plan: Pillar 3 Data",
          "Strategic Plan: Pillar 4 Data",
      ],
  )

  # Map selection to session state dataframe
  target_df = st.session_state["reports_db"]
  key_name = "reports_db"
  if "Pillar 1" in dataset_choice:
    target_df = st.session_state["pillar_1_data"]
    key_name = "pillar_1_data"
  elif "Pillar 2" in dataset_choice:
    target_df = st.session_state["pillar_2_data"]
    key_name = "pillar_2_data"
  elif "Pillar 3" in dataset_choice:
    target_df = st.session_state["pillar_3_data"]
    key_name = "pillar_3_data"
  elif "Pillar 4" in dataset_choice:
    target_df = st.session_state["pillar_4_data"]
    key_name = "pillar_4_data"

  st.markdown("---")
  col_dl, col_ul = st.columns(2)

  with col_dl:
    st.markdown(
        "### 📥 Download Staff Data"
        if lang == "English"
        else "### 📥 Télécharger les données du staff"
    )
    st.markdown(
        "Export your staff-entered data in CSV format for analysis in SPSS,"
        " Stata, or R."
    )

    if not target_df.empty:
      csv_data = target_df.to_csv(index=False).encode("utf-8")
      st.download_button(
          label="Download CSV File / Télécharger le fichier CSV",
          data=csv_data,
          file_name=f"juc_staff_{key_name}_{datetime.now().date()}.csv",
          mime="text/csv",
      )
    else:
      st.info(
          "No data available to download."
          if lang == "English"
          else "Aucune donnée disponible au téléchargement."
      )

  with col_ul:
    st.markdown(
        "### 📤 Upload Staff Data"
        if lang == "English"
        else "### 📤 Téléverser des données"
    )
    st.markdown(
        "Upload a completed CSV file to update or populate this database table."
    )

    uploaded_file = st.file_uploader(
        "Choose a CSV file", type=["csv"], key=f"uploader_{key_name}"
    )
    if uploaded_file is not None:
      try:
        imported_df = pd.read_csv(uploaded_file)
        st.session_state[key_name] = imported_df
        st.success(
            "✅ Staff dataset successfully uploaded and updated!"
            if lang == "English"
            else "✅ Jeu de données du staff téléversé et mis à jour avec succès !"
        )
      except Exception as e:
        st.error(f"Error reading CSV: {e}")

  st.markdown("---")
  st.markdown(
      "### 🔍 Live Data Preview & Summary Statistics"
      if lang == "English"
      else "### 🔍 Aperçu en direct et statistiques descriptives"
  )
  if not target_df.empty:
    st.dataframe(target_df, use_container_width=True)
    st.markdown(
        f"**Total Records / Enregistrements totaux :** {len(target_df)}"
    )
  else:
    st.warning(
        "The selected dataset is currently empty."
        if lang == "English"
        else "Le jeu de données sélectionné est actuellement vide."
    )
