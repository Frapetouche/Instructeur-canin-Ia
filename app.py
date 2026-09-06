import streamlit as st

st.title("🐕 Assistant Canin en Temps Réel")
st.write("Prenez une photo de votre chien pour déclencher l'analyse immédiatement.")

# Utilisation d'un compteur dans la mémoire de session pour réinitialiser à chaque nouvelle photo
if "photo_count" not in st.session_state:
    st.session_state.photo_count = 0

def reset_analysis():
    st.session_state.photo_count += 1

# Le widget de caméra déclenche un changement d'état à chaque nouvelle prise
photo_prise = st.camera_input("Photographiez votre chien", on_change=reset_analysis, key=f"cam_{st.session_state.photo_count}")

if photo_prise is not None:
    with st.spinner("Analyse de la nouvelle photo en cours..."):
        
        # Réponse générée instantanément pour chaque nouvelle prise
        conseil = "Nouvelle photo détectée ! Je me demande bien ce que tu prépares..."

        st.success("Analyse mise à jour !")
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
    st.info("Prenez une photo pour lancer l'analyse des agents.")
        
