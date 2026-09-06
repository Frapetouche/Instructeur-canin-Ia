import tempfile
import cv2
import numpy as np
import streamlit as st

st.title("🐕 Assistant Canin - Expertise Comportementale Avancée")
st.write(
    "Téléchargez une courte vidéo pour analyser la cinétique, la régularité et"
    " les indices posturaux de votre chien."
)

uploaded_video = st.file_uploader(
    "Choisissez une vidéo (MP4, MOV, AVI)", type=["mp4", "mov", "avi"]
)

if uploaded_video is not None:
  tfile = tempfile.NamedTemporaryFile(delete=False)
  tfile.write(uploaded_video.read())

  vidcap = cv2.VideoCapture(tfile.name)
  success, image1 = vidcap.read()

  motion_scores = []
  frames_analyzed = 0

  if success:
    gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    while True:
      success, image2 = vidcap.read()
      if not success:
        break
      gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
      diff = cv2.absdiff(gray1, gray2)
      motion_scores.append(np.mean(diff))
      gray1 = gray2
      frames_analyzed += 1

  if frames_analyzed > 0:
    avg_motion = np.mean(motion_scores)
    # Calcul de la variance pour détecter l'erraticité (pics de stress vs mouvement fluide)
    motion_variance = np.var(motion_scores)
  else:
    avg_motion = 0
    motion_variance = 0

  with st.spinner(
      "Analyse éthologique et cinétique de la séquence en cours..."
  ):
    # Logique experte combinant intensité et régularité du mouvement
    if avg_motion < 1.5:
      etat = "État de repos ou de vigilance passive"
      analyse_experte = (
          "Le chien présente une très faible cinétique. Si les muscles sont"
          " souples et la respiration lente, il s'agit d'un repos récupérateur"
          " (sommeil paradoxal ou calme profond). Attention toutefois à"
          " surveiller une éventuelle posture de figement si le corps est"
          " rigide."
      )
      conseil = (
          "Laissez-le tranquille, son équilibre émotionnel est stable."
      )
    elif avg_motion > 7.0 and motion_variance > 15.0:
      etat = "Agitation intense / Montée d'adrénaline"
      analyse_experte = (
          "Forte intensité couplée à une forte variance : les mouvements sont"
          " saccadés et imprévisibles. Cela traduit souvent une excitation"
          " débordante (jeu, attente d'une récompense) ou une décharge émotionnelle"
          " suite à un pic de stress."
      )
      conseil = (
          "Prévoyez une transition calme ou un exercice de flairage pour l'aider"
          " à redescendre en pression."
      )
    elif avg_motion > 5.0:
      etat = "Activité exploratoire ou dynamique"
      analyse_experte = (
          "Mouvement soutenu mais régulier. Le chien est engagé dans une action"
          " physique structurée (course, interaction, résolution de"
          " problème)."
      )
      conseil = (
          "C'est une phase saine de dépense physique et mentale. Pensez à"
          " l'hydrater."
      )
    else:
      etat = "Attention focalisée / Statu quo interactif"
      analyse_experte = (
          "Activité modérée et stable. Le chien est en position d'écoute active"
          " ou d'observation (attente d'instruction, analyse olfactive ou"
          " visuelle de son environnement)."
      )
      conseil = "Regardez s'il cherche le contact visuel ; il attend une guidance."

    st.success("Analyse éthologique réussie !")
    st.video(uploaded_video)

    st.markdown(
        f"""
        <div style="background-color: #f0f2f6; border: 2px solid #333; border-radius: 20px; padding: 20px; margin-top: 20px;">
            <h3 style="margin:0; color: #111;">📊 Bilan Comportemental (Expert) :</h3>
            <p style="font-size: 1.1em; color: #333; margin-top: 10px;"><b>Diagnostic évalué :</b> {etat}</p>
            <p style="font-size: 1.05em; color: #444; margin-top: 5px;"><b>Lecture éthologique :</b> {analyse_experte}</p>
            <hr style="border: 0; border-top: 1px solid #ccc; margin: 15px 0;">
            <p style="font-size: 1.2em; font-weight: bold; color: #d9534f; margin: 0;">Recommandation : "{conseil}"</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
  st.info("Téléchargez une vidéo de votre chien pour lancer l'analyse experte.")
      
