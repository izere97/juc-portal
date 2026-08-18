import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="JUC Staff & M&E Portal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# 1. FOND D'ÉCRAN & STYLE CSS (Image .jpg)
# ---------------------------------------------------------
bg_image_name = "generated_image-width=4096_height=3058.jpg"

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
    .block-container {{
        background-color: rgba(255, 255, 255, 0.88);
        padding: 2.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
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
# 2. SÉCURITÉ & NAVIGATION (Restreint aux admins)
# ---------------------------------------------------------
st.sidebar.title("🔐 Navigation & Sécurité")
app_mode = st.sidebar.selectbox(
    "Mode d'accès", ["Portail Utilisateur (Rapports & Piliers)", "Zone Administrateur Exclusive"]
)

if app_mode == "Zone Administrateur Exclusive":
    st.sidebar.subheader("Identification Requise")
    admin_password = st.sidebar.text_input("Mot de passe", type="password")
    
    # Mot de passe sécurisé personnel
    if admin_password == "JUC2026Secure":
        st.sidebar.success("Accès administrateur accordé")
        st.title("🛠️ Panneau d'Administration (Gestion Globale)")
        st.write("Ici se trouvent vos outils CRUD, de suppression par ID et de réinitialisation totale de la base de données PostgreSQL.")
        # [Insérez ici vos fonctions d'administration et de gestion de base de données existantes]
    else:
        if admin_password:
            st.sidebar.error("Mot de passe incorrect")
        st.warning("Veuillez entrer votre mot de passe administrateur dans la barre latérale pour accéder à cette section.")
        st.stop()

else:
    # ---------------------------------------------------------
    # 3. VOTRE APPLICATION PRINCIPALE (Piliers & Rapports)
    # ---------------------------------------------------------
    st.title("🌟 JUC Staff & M&E Portal")
    st.markdown("Portail de suivi des rapports et de la mise en œuvre du Plan Stratégique JUC 2026-2031.")

    # (Insérez ici la suite de vos formulaires par piliers, sélecteurs de langues et intégration Neon que vous aviez mis en place)
    st.info("Votre application complète fonctionne ici avec toutes vos sections de rapports hebdomadaires et stratégiques.")
