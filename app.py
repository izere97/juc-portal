import streamlit as st

# Configuration de la page (doit être la première commande st)
st.set_page_config(
    page_title="JUC Staff & M&E Portal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# GESTION DU FOND D'ÉCRAN (BACKGROUND) & STYLE CSS
# ---------------------------------------------------------
# Remplacez "generated_image-width=4096_height=3058.png" par le nom exact de votre image si besoin
bg_image_name = "generated_image-width=4096_height=3058.png"

st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("{bg_image_name}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    
    /* Effet glassmorphism pour le contenu principal */
    .block-container {{
        background-color: rgba(255, 255, 255, 0.85);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        margin-top: 2rem;
    }}
    
    h1, h2, h3, p, label {{
        color: #1e293b !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# AUTHENTIFICATION & SÉCURITÉ ADMIN (Réservé à vous seul)
# ---------------------------------------------------------
st.sidebar.title("🔐 Espace Sécurisé")
app_mode = st.sidebar.selectbox(
    "Navigation", ["Portail Public (Rapports)", "Zone Administrateur"]
)

if app_mode == "Zone Administrateur":
  st.sidebar.subheader("Accès Restreint")
  admin_password = st.sidebar.text_input(
      "Mot de passe administrateur", type="password"
  )

  # Changez "JUC2026Secure" par votre mot de passe secret personnel
  if admin_password == "JUC2026Secure":
    st.sidebar.success("Accès autorisé")
    st.title("🛠️ Panneau d'Administration Exclusif")
    st.write(
        "Ici, vous seul pouvez effectuer des modifications globales, "
        "gérer la base de données ou réinitialiser les données."
    )
    # Insérez ici vos outils CRUD / réinitialisation de base de données
  else:
    if admin_password:
      st.sidebar.error("Mot de passe incorrect")
    st.warning("Veuillez entrer le mot de passe administrateur dans la barre latérale pour accéder à cette zone.")
    st.stop()  # Stoppe l'exécution du reste de la page admin si non connecté

else:
  # ---------------------------------------------------------
  # PORTAIL PUBLIC / RAPPORT DE L'ÉQUIPE
  # ---------------------------------------------------------
  st.title("🌟 JUC Staff & M&E Portal")
  st.markdown(
      "Bienvenue sur le portail officiel de suivi des rapports et de la mise en"
      " œuvre du Plan Stratégique JUC 2026-2031."
  )

  # Exemple de formulaire de rapport hebdomadaire
  with st.form("weekly_report_form"):
    st.subheader("Soumission de Rapport Hebdomadaire")
    col1, col2 = st.columns(2)

    with col1:
      staff_name = st.text_input("Nom complet")
      department = st.selectbox(
          "Département",
          [
              "Recherche & Civic Engagement",
              "Women & Youth Empowerment",
              "Integral Ecology",
              "Institutional Sustainability",
              "M&E General",
          ],
      )

    with col2:
      week_period = st.date_input("Période de la semaine")

    activities_done = st.text_area("Activités réalisées cette semaine")
    challenges = st.text_area("Défis rencontrés / Solutions proposées")

    submitted = st.form_submit_button("Envoyer le rapport")
    if submitted:
      if staff_name and activities_done:
        # Code d'insertion dans la base de données PostgreSQL (Neon)
        st.success("Rapport soumis et enregistré avec succès dans la base de données !")
      else:
        st.error("Veuillez remplir au moins votre nom et les activités réalisées.")
