import streamlit as st
import numpy as np
from PIL import Image

st.title("🐕 Assistant Canin en Temps Réel")
st.write("Prenez une photo de votre chien pour déclencher une vraie analyse visuelle.")

# Utilisation d'un identifiant dynamique (clé unique) pour forcer le rechargement du widget à chaque prise
if "camera_key" not in st.session_state:
    st.session_state.camera_key = 0

photo_prise = st.camera_input("Photographiez votre chien", key=f"cam_{st.session_state.camera_key}")

if photo_prise is not None:
    with st.spinner("Analyse de la nouvelle photo en cours..."):
        
        # Lecture réelle de l'image capturée par la caméra
        image = Image.open(photo_prise)
        
        # Analyse basique de la couleur dominante ou de la taille pour varier la réponse
        img_array = np.array(image)
        luminosite = np.mean(img_array)
        
        # Logique dynamique selon l'image reçue
        if luminosite < 80:
            conseil = "Il fait un peu sombre par ici... Je me repose ou j'essaie de deviner dans le noir !"
        elif luminosite > 180:
            conseil = "Oouh c'est très lumineux ! On est dehors au soleil ? Je veux courir !"
        else:
            conseil = "Photo bien reçue et analysée ! Je suis tout près de toi, qu'est-ce qu'on fait ?"

        st.success("Analyse de la photo réussie !")
        st.markdown(
            f"""
            <div style="background-color: #f0f2f6; border: 2px solid #333; border-radius: 20px; padding: 20px; margin-top: 20px;">
                <h3 style="margin:0; color: #111;">💬 Ce que votre chien pense :</h3>
                <p style="font-size: 1.3em; font-weight: bold; color: #d9534f; margin-top: 10px;">"{conseil}"</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Bouton pour effacer et reprendre une autre photo instantanément
        if st.button("Prendre une autre photo"):
            st.session_state.camera_key += 1
            st.rerun()
else:
    st.info("Prenez une photo pour lancer l'analyse.")
        
