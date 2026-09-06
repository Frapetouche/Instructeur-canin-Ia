import streamlit as st
from crewai import Agent, Crew, Process, Task

st.set_page_title("Assistant Canin IA")
st.title("🐕 Assistant Canin en Temps Réel")
st.write("Analysez le comportement de votre chien instantanément.")

description_situation = st.text_area(
    "Que fait votre chien en ce moment ?", 
    placeholder="Ex: Il fixe la porte, les oreilles dressées..."
)

if st.button("Lancer l'analyse des agents"):
    if description_situation:
        with st.spinner("Les agents IA analysent la situation..."):
            
            vision_agent = Agent(
                role="Expert en Perception Canine",
                goal="Analyser les signaux corporels et les indices décrits.",
                backstory="Spécialiste en éthologie et lecture des micro-signaux chez le chien.",
                verbose=False
            )

            behavior_agent = Agent(
                role="Analyste du Comportement",
                goal="Traduire les signaux en état émotionnel ou besoin précis.",
                backstory="Éducateur canin expert en décodage des besoins (faim, stress, attention).",
                verbose=False
            )

            advisory_agent = Agent(
                role="Conseiller Mobile",
                goal="Rédiger une bulle de dialogue courte et percutante pour le propriétaire.",
                backstory="Expert en communication directe et bienveillante.",
                verbose=False
            )

            task_1 = Task(
                description=f"Analysez cette situation : {description_situation}",
                expected_output="Rapport des signaux corporels.",
                agent=vision_agent
            )
            
            task_2 = Task(
                description="Déterminez l'état émotionnel et le besoin immédiat du chien.",
                expected_output="Diagnostic comportemental.",
                agent=behavior_agent
            )

            task_3 = Task(
                description="Rédigez une phrase très courte, style bulle de bande dessinée (ex: 'J'ai faim là !'), prête à être affichée.",
                expected_output="Une phrase courte en français.",
                agent=advisory_agent
            )

            crew = Crew(
                agents=[vision_agent, behavior_agent, advisory_agent],
                tasks=[task_1, task_2, task_3],
                process=Process.sequential,
                verbose=False
            )

            result = crew.kickoff()

            st.success("Analyse terminée !")
            st.markdown(
                f"""
                <div style="background-color: #f0f2f6; border: 2px solid #333; border-radius: 20px; padding: 20px; margin-top: 20px;">
                    <h3 style="margin:0; color: #111;">💬 Ce que votre chien pense :</h3>
                    <p style="font-size: 1.2em; font-weight: bold; color: #d9534f; margin-top: 10px;">"{result}"</p>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.warning("Veuillez d'abord entrer une description.")
          
