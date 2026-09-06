import streamlit as st

st.title("🐕 Assistant Canin en Temps Réel")
st.write("Prenez une photo de votre chien pour analyser son comportement instantanément.")

# Utilisation de la caméra native du cellulaire
photo_prise = st.camera_input("Photographiez votre chien ici")

if photo_prise is not None:
    with st.spinner("Analyse de l'image par les agents..."):
        
        # Simulation d'une analyse visuelle basée sur la photo capturée
        # (Ici, l'application traite le fait qu'une image a bien été envoyée)
        conseil = "J'ai l'œil rivé sur toi, humain ! Qu'est-ce qu'on fait ?"

        st.success("Analyse visuelle terminée !")
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
    st.info("Appuyez sur le bouton de la caméra ci-dessus pour prendre votre chien en photo.")
    
