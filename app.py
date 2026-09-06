import streamlit as st

st.title("🐕 Assistant Canin en Temps Réel")
st.write("Analysez le comportement de votre chien instantanément.")

description_situation = st.text_area(
    "Que fait votre chien en ce moment ?", 
    placeholder="Ex: Il fixe la porte, les oreilles dressées..."
)

if st.button("Lancer l'analyse"):
    if description_situation:
        with st.spinner("Analyse du comportement en cours..."):
            
            texte_lower = description_situation.lower()
            
            if "faim" in texte_lower or "gamelle" in texte_lower or "cuisine" in texte_lower:
                conseil = "J'ai faim là ! C'est l'heure de la pâtée ?"
            elif "porte" in texte_lower or "dehors" in texte_lower or "sortir" in texte_lower:
                conseil = "Je veux aller explorer dehors ! Ouvre la porte !"
            elif "joue" in texte_lower or "balle" in texte_lower:
                conseil = "C'est l'heure de jouer ! Lance-moi ce truc !"
            else:
                conseil = "Je veille au grain, tout est sous contrôle !"

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
        st.warning("Veuillez d'abord entrer une description.")
            
