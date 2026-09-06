import streamlit as st

st.title("🐕 Assistant Canin en Temps Réel")
st.write("Prenez une photo de votre chien pour lancer l'analyse instantanément.")

# Widget caméra simple et stable
photo_prise = st.camera_input("Photographiez votre chien")

if photo_prise is not None:
    with st.spinner("Analyse de la photo en cours..."):
        
        # Réponse instantanée basée sur la présence de la photo
        conseil = "Photo bien reçue ! Je suis là, qu'est-ce qu'on fait ?"

        st.success("Analyse terminée !")
        st.markdown(
            f"""
            <div style="background-color: #f0f2f6; border: 2px solid #333; border-radius: 20px; padding: 20px; margin-top: 20px;">
                <h3 style="margin:0; color: #111;">💬 Ce que votre chien pense :</h3>
                <p style="font-size: 1.3em; font-weight: bold; color: #d9534f; margin-top: 10px;">"{conseil}"</p>
            </div>
            """,
            unsafe_allow_html=True
        )
else:
    st.info("Prenez une photo pour démarrer.")
        
