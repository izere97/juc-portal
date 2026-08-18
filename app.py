import base64
from datetime import date
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
        "Français": {"title": "Portail JUC", "weekly": "Rapport Hebdomadaire", "strat": "Rapport par Pilier Stratégique", "dept": "Département", "submit": "Soumettre", "lang": "Langue", "pillar": "Pilier Stratégique", "dash": "📊 Tableau de Bord en Bulles", "admin": "⚙️ Admin"}
    }

# --- INITIALISATION ---
if "lang" not in st.session_state: st.session_state.lang = "English"
trans = get_translations()
# Utilisation de la variable d'environnement pour la DB
engine = create_engine(st.secrets["DATABASE_URL"]) if "DATABASE_URL" in st.secrets else None

# --- UI & STYLE ---
st.markdown("""
    <style>
    .bubble-card { background: #f8fafc; border: 2px solid #cbd5e1; border-radius: 20px; padding: 20px; text-align: center; margin-bottom: 20px; }
    .bubble-admin { background: #dbeafe; border: 2px solid #3b82f6; border-radius: 25px; padding: 25px; text-align: center; margin-bottom: 25px; }
    </style>
""", unsafe_allow_html=True)

# --- SÉCURITÉ ---
password_input = st.sidebar.text_input("Password", type="password")
if password_input != "JUC2026Secure":
    st.warning("Access Restricted. Please enter the secure password in the sidebar.")
    st.stop()

# --- NAVIGATION ---
t = trans[st.session_state.lang]
menu = st.sidebar.radio("Navigation", [t["weekly"], t["strat"], t["dash"], t["admin"]])

# --- 1. & 2. LOGIQUE DES FORMULAIRES (IDENTIQUE À VOTRE VERSION) ---
# (Note : La logique d'insertion reste la même que dans le code précédent)

# --- 3. DASHBOARD AVEC EXPORT WORD ---
if menu == t["dash"]:
    st.header(t["dash"])
    
    if engine:
        df = pd.read_sql("SELECT * FROM juc_reports", engine)
        
        # Affichage des bulles
        col1, col2, col3 = st.columns(3)
        with col1: st.markdown('<div class="bubble-card"><h4>Finance</h4></div>', unsafe_allow_html=True)
        with col2: st.markdown('<div class="bubble-card"><h4>Program Mgmt</h4></div>', unsafe_allow_html=True)
        with col3: st.markdown('<div class="bubble-card"><h4>Piliers</h4></div>', unsafe_allow_html=True)

        # Consultation et Export
        if not df.empty:
            all_cats = df['category'].dropna().unique().tolist()
            selected = st.selectbox("Filtrer par catégorie :", all_cats)
            filtered_df = df[df['category'] == selected]
            
            for _, row in filtered_df.iterrows():
                with st.expander(f"{row['staff_name']} - {row['submission_date']}"):
                    st.write(f"**Activités:** {row['completed_activities']}")
                    st.write(f"**Défis:** {row['challenges']}")

            # --- GÉNÉRATEUR WORD ---
            if st.button("Générer Word pour cette sélection"):
                doc = Document()
                doc.add_heading(f"Rapport JUC : {selected}", 0)
                for _, row in filtered_df.iterrows():
                    doc.add_paragraph(f"Staff: {row['staff_name']} | Date: {row['submission_date']}")
                    doc.add_paragraph(f"Activités: {row['completed_activities']}")
                    doc.add_paragraph("---")
                
                buffer = io.BytesIO()
                doc.save(buffer)
                buffer.seek(0)
                
                st.download_button(
                    label="📥 Télécharger le rapport",
                    data=buffer,
                    file_name=f"Rapport_{selected}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
