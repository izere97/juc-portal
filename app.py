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
      conn.execute(
          text("""
                CREATE TABLE IF NOT EXISTS juc_reports (
                    id SERIAL PRIMARY KEY,
                    date TIMESTAMP,
                    staff_name TEXT,
                    pillar TEXT,
                    core_activity TEXT,
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
      "Veuillez entrer le mot de passe du portail (JUC2026Secure) dans la barre"
      " latérale pour continuer."
  )
  st.stop()

# --- NAVIGATION ---
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "Navigation",
    ["Soumettre un Rapport", "Dashboard & Analyses", "Gestion des Données"],
)

# --- PILIERS STRATÉGIQUES ET ACTIVITÉS (Basés sur le plan stratégique) ---
pillars_activities = {
    (
        "Pillar 1: Research, Policy Advocacy and Civic Engagement"
    ): [  #
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

# --- SECTION 1 : SOUMISSION DE RAPPORT ---
if menu == "Soumettre un Rapport":
  st.header("📚 JUC - Soumission de Rapport par Pilier Stratégique")

  with st.form("juc_strategic_form"):
    staff_name = st.text_input("Nom complet du membre du personnel")
    selected_pillar = st.selectbox(
        "Sélectionner le Pilier Stratégique", list(pillars_activities.keys())
    )
    selected_activity = st.selectbox(
        "Activité Clé associée", pillars_activities[selected_pillar]
    )

    details = st.text_area(
        "Détails du rapport, progrès et observations sur le terrain"
    )

    # Option d'upload de document
    uploaded_doc = st.file_uploader(
        "Joindre un document justificatif (PDF, Word, Image)",
        type=["pdf", "docx", "jpg", "png"],
    )

    submitted = st.form_submit_button("Soumettre le Rapport")

    if submitted:
      if not staff_name or not details:
        st.error(
            "Veuillez remplir au moins votre nom et les détails du rapport."
        )
      elif engine is None:
        st.error("Erreur de connexion à la base de données Neon.")
      else:
        try:
          doc_name = uploaded_doc.name if uploaded_doc else "Aucun document"
          with engine.connect() as conn:
            query = text("""
                            INSERT INTO juc_reports (date, staff_name, pillar, core_activity, details, document_name)
                            VALUES (:date, :staff_name, :pillar, :core_activity, :details, :document_name)
                        """)
            conn.execute(
                query,
                {
                    "date": datetime.now(),
                    "staff_name": staff_name,
                    "pillar": selected_pillar,
                    "core_activity": selected_activity,
                    "details": details,
                    "document_name": doc_name,
                },
            )
            conn.commit()
          st.success(
              "Rapport enregistré avec succès dans la base de données Neon !"
          )
        except Exception as e:
          st.error(f"Erreur lors de l'enregistrement : {e}")

# --- SECTION 2 : DASHBOARD & ANALYSES ---
elif menu == "Dashboard & Analyses":
  st.header("📊 Tableau de Bord & Suivi M&E")

  if engine is None:
    st.error("Erreur de connexion à la base de données.")
  else:
    try:
      df = pd.read_sql("SELECT * FROM juc_reports ORDER BY date DESC", engine)

      if df.empty:
        st.info(
            "Aucun rapport enregistré pour le moment. Commencez par soumettre un"
            " rapport !"
        )
      else:
        st.metric(label="Nombre total de rapports", value=len(df))

        # Graphique par pilier
        st.markdown("### Répartition par Pilier Stratégique")
        pillar_counts = df["pillar"].value_counts()
        st.bar_chart(pillar_counts)

        st.markdown("### Historique détaillé des rapports")
        st.dataframe(df, use_container_width=True)

        # Bouton de téléchargement CSV
        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Télécharger les données en CSV",
            data=csv_data,
            file_name="juc_strategic_reports.csv",
            mime="text/csv",
        )
    except Exception as e:
      st.error(f"Erreur lors de la lecture des données : {e}")

# --- SECTION 3 : GESTION DES DONNÉES (SUPPRESSION) ---
elif menu == "Gestion des Données":
  st.header("⚙️ Gestion et Nettoyage des Données")
  st.warning(
      "⚠️ Attention : L'action ci-dessous supprime définitivement l'ensemble"
      " des rapports enregistrés dans la base de données."
  )

  if st.button("🗑️ SUPPRIMER TOUTES LES DONNÉES", type="primary"):
    try:
      with engine.connect() as conn:
        conn.execute(text("DELETE FROM juc_reports"))
        conn.commit()
      st.success(
          "Toutes les données ont été supprimées de la base de données avec"
          " succès."
      )
    except Exception as e:
      st.error(f"Erreur lors de la suppression : {e}")
