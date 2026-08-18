import base64
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine, text
import streamlit as st

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="JUC Staff & M&E Portal", page_icon="📚", layout="wide"
)

# --- CONNEXION NEON (BASE DE DONNÉES) ---
DATABASE_URL = st.secrets.get("DATABASE_URL")
engine = create_engine(DATABASE_URL) if DATABASE_URL else None


# --- CRÉATION DE LA TABLE ---
def create_table_if_not_exists():
  if engine is None:
    return
  try:
    with engine.connect() as conn:
      conn.execute(
          text("""
                CREATE TABLE IF NOT EXISTS juc_reports (
                    id SERIAL PRIMARY KEY,
                    date TIMESTAMP,
                    staff_name TEXT,
                    report_type TEXT,
                    category TEXT,
                    sub_category TEXT,
                    details TEXT,
                    document_name TEXT
                );
            """)
      )
      conn.commit()
  except Exception as e:
    st.error(f"Erreur d'initialisation de la base de données : {e}")


if engine:
  create_table_if_not_exists()

# --- PERSONNALISATION DU BACKGROUND AVEC VOS PHOTOS ---
st.sidebar.subheader("🖼️ Apparence de l'application")
bg_file = st.sidebar.file_uploader(
    "Choisir une photo de fond (JPG, PNG)", type=["jpg", "jpeg", "png"]
)

if bg_file is not None:
  encoded_img = base64.b64encode(bg_file.read()).decode()
  st.markdown(
      f"""
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(255, 255, 255, 0.9), rgba(255, 255, 255, 0.9)), url(data:image/jpeg;base64,{encoded_img});
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
      unsafe_allow_html=True,
  )

# --- AUTHENTIFICATION ---
st.sidebar.markdown("---")
password_input = st.sidebar.text_input("Mot de passe du portail", type="password")

if password_input != "JUC2026Secure":
  st.warning(
      "Veuillez entrer le mot de passe du portail (JUC2026Secure) pour"
      " continuer."
  )
  st.stop()

# --- LISTES OFFICIELLES ---
departments_list = [
    "Administration",
    "Finance",
    "Program management",
    "Project office",
    "Communication office",
    "Front Desk",
    "Monitoring and Evaluation",
]

pillars_activities = {
    (
        "Pillar 1: Research, Policy Advocacy and Civic Engagement"
    ): [  #[cite: 1]
        "Basic Needs Basket",
        "Policy Briefs & Research Reports",
        "Social Justice Conferences",
        "Civic Education & Life-skills training",
        "Pluralistic Governance Forums",
    ],
    (
        "Pillar 2: Women & Youth Empowerment through Social Innovation and"
        " Entrepreneurship"
    ): [  #[cite: 1]
        "Social Innovation Incubation Bootcamps",
        "Financial Literacy Training",
        "Women's Empowerment Cooperatives",
    ],
    "Pillar 3: Integral Ecology and Community Resilience": [  #[cite: 1]
        "Climate Change Awareness Campaigns",
        "Laudato Si' Formation & Ecological Retreats",
        "Sustainable Agriculture & Climate-Smart Farming",
        "Kitchen Gardens & Nutrition Programs",
    ],
    "Pillar 4: Institutional Capacity Strengthening and Sustainability": [  #[cite: 1]
        "Staff Development & Capacity Building",
        "Financial Resource Mobilization & CSR",
        "Governance & M&E Systems Strengthening",
    ],
}

# --- NAVIGATION SÉPARÉE ---
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "Navigation",
    [
        "📅 Rapport Hebdomadaire (Départements)",
        "🎯 Rapport par Pilier Stratégique",
        "📊 Dashboard & Analyses",
        "⚙️ Gestion des Données",
    ],
)

# --- 1. RAPPORT HEBDOMADAIRE (SÉPARÉ) ---
if menu == "📅 Rapport Hebdomadaire (Départements)":
  st.header("📅 Soumission du Rapport Hebdomadaire")
  st.markdown("Rapport d'activités spécifique aux différents départements du JUC.")

  with st.form("weekly_report_form"):
    staff_name = st.text_input("Nom complet du membre du personnel")
    department = st.selectbox("Département", departments_list)

    activities = st.text_area("Activités clés réalisées cette semaine")
    challenges = st.text_area("Défis rencontrés")
    next_steps = st.text_area("Priorités pour la semaine prochaine")

    uploaded_doc = st.file_uploader(
        "Joindre un document justificatif (PDF, Word, Image)",
        type=["pdf", "docx", "jpg", "png"],
    )

    submitted = st.form_submit_button("Soumettre le Rapport Hebdomadaire")

    if submitted:
      if not staff_name or not activities:
        st.error(
            "Veuillez remplir au moins votre nom et les activités réalisées."
        )
      elif engine is None:
        st.error("Erreur de connexion à la base de données Neon.")
      else:
        try:
          doc_name = uploaded_doc.name if uploaded_doc else "Aucun document"
          details_combined = (
              f"Défis: {challenges} | Prochaine étape: {next_steps}"
          )
          with engine.connect() as conn:
            query = text("""
                            INSERT INTO juc_reports (date, staff_name, report_type, category, sub_category, details, document_name)
                            VALUES (:date, :staff_name, :report_type, :category, :sub_category, :details, :document_name)
                        """)
            conn.execute(
                query,
                {
                    "date": datetime.now(),
                    "staff_name": staff_name,
                    "report_type": "Hebdomadaire",
                    "category": department,
                    "sub_category": "N/A",
                    "details": (
                        f"Activités: {activities} || {details_combined}"
                    ),
                    "document_name": doc_name,
                },
            )
            conn.commit()
          st.success("Rapport hebdomadaire enregistré avec succès !")
        except Exception as e:
          st.error(f"Erreur lors de l'enregistrement : {e}")

# --- 2. RAPPORT PAR PILIER STRATÉGIQUE (SÉPARÉ) ---
elif menu == "🎯 Rapport par Pilier Stratégique":
  st.header("🎯 Soumission par Pilier Stratégique (2026-2031)")
  st.markdown("Rapport aligné sur les objectifs stratégiques institutionnels[cite: 1].")

  with st.form("strategic_report_form"):
    staff_name = st.text_input("Nom complet du membre du personnel")
    selected_pillar = st.selectbox(
        "Sélectionner le Pilier Stratégique", list(pillars_activities.keys())
    )
    selected_activity = st.selectbox(
        "Activité Clé associée", pillars_activities[selected_pillar]
    )

    details = st.text_area(
        "Détails des progrès, indicateurs et observations de terrain"
    )

    uploaded_doc = st.file_uploader(
        "Joindre un document de suivi (PDF, Word, Image)",
        type=["pdf", "docx", "jpg", "png"],
    )

    submitted_strat = st.form_submit_button("Soumettre le Rapport Stratégique")

    if submitted_strat:
      if not staff_name or not details:
        st.error("Veuillez remplir les champs obligatoires.")
      elif engine is None:
        st.error("Erreur de connexion à la base de données Neon.")
      else:
        try:
          doc_name = uploaded_doc.name if uploaded_doc else "Aucun document"
          with engine.connect() as conn:
            query = text("""
                            INSERT INTO juc_reports (date, staff_name, report_type, category, sub_category, details, document_name)
                            VALUES (:date, :staff_name, :report_type, :category, :sub_category, :details, :document_name)
                        """)
            conn.execute(
                query,
                {
                    "date": datetime.now(),
                    "staff_name": staff_name,
                    "report_type": "Stratégique",
                    "category": selected_pillar,
                    "sub_category": selected_activity,
                    "details": details,
                    "document_name": doc_name,
                },
            )
            conn.commit()
          st.success("Rapport stratégique enregistré avec succès !")
        except Exception as e:
          st.error(f"Erreur lors de l'enregistrement : {e}")

# --- 3. DASHBOARD & ANALYSES ---
elif menu == "📊 Dashboard & Analyses":
  st.header("📊 Tableau de Bord Global")

  if engine is None:
    st.error("Erreur de connexion à la base de données.")
  else:
    try:
      df = pd.read_sql("SELECT * FROM juc_reports ORDER BY date DESC", engine)

      if df.empty:
        st.info("Aucun rapport enregistré pour le moment.")
      else:
        st.metric(label="Total des rapports", value=len(df))

        # Filtre par type de rapport
        report_filter = st.selectbox(
            "Filtrer par type de rapport",
            ["Tous", "Hebdomadaire", "Stratégique"],
        )
        if report_filter != "Tous":
          df_filtered = df[df["report_type"] == report_filter]
        else:
          df_filtered = df

        st.dataframe(df_filtered, use_container_width=True)

        # Bouton de téléchargement CSV
        csv_data = df_filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Télécharger les données en CSV",
            data=csv_data,
            file_name="juc_reports_export.csv",
            mime="text/csv",
        )
    except Exception as e:
      st.error(f"Erreur lors de la lecture des données : {e}")

# --- 4. GESTION DES DONNÉES ---
elif menu == "⚙️ Gestion des Données":
  st.header("⚙️ Gestion et Nettoyage des Données")
  st.warning(
      "⚠️ Attention : L'action ci-dessous supprime définitivement l'ensemble"
      " des rapports de la base de données."
  )

  if st.button("🗑️ SUPPRIMER TOUTES LES DONNÉES", type="primary"):
    try:
      with engine.connect() as conn:
        conn.execute(text("DELETE FROM juc_reports"))
        conn.commit()
      st.success("Base de données réinitialisée avec succès.")
    except Exception as e:
      st.error(f"Erreur lors de la suppression : {e}")
