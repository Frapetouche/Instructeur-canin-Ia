import tempfile
import cv2
import google.generativeai as genai
import numpy as np
import streamlit as st

# Configuration de l'API Gemini (assurez-vous d'avoir configuré votre clé API dans les secrets Streamlit ou via st.sidebar)
# st.secrets["GOOGLE_API_KEY"] doit être défini
if "GOOGLE_API_KEY" in st.secrets:
  genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

st.title("🐕 Assistant Canin - Expertise Comportementale Multimodale")
st.write(
    "Téléchargez une courte vidéo pour croiser une analyse cinétique locale et"
    " une analyse experte par IA Vision de la posture de votre chien."
)

uploaded_video = st.file_uploader(
    "Choisissez une vidéo (MP4, MOV, AVI)", type=["mp4", "mov", "avi"]
)

if uploaded_video is not None:
  tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
  tfile.write(uploaded_video.read())
  tfile.close()

  # 1. Analyse cinétique OpenCV traditionnelle
  vidcap = cv2.VideoCapture(tfile.name)
  success, image1 = vidcap.read()

  motion_scores = []
  frames_analyzed = 0
  frame_skip = 5

  if success:
    gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    frame_count = 0
    while True:
      success, image2 = vidcap.read()
      if not success:
        break

      frame_count += 1
      if frame_count % frame_skip != 0:
        continue

      gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
      diff = cv2.absdiff(gray1, gray2)
      motion_scores.append(np.mean(diff))
      gray1 = gray2
      frames_analyzed += 1

  vidcap.release()

  if frames_analyzed > 0:
    avg_motion = np.mean(motion_scores)
    motion_variance = np.var(motion_scores)
  else:
    avg_motion = 0
    motion_variance = 0

  # 2. Analyse contextuelle avancée via Gemini (IA Vision vidéo)
  ai_analysis = None
  with st.spinner(
      "Analyse éthologique cinétique et vision IA de la séquence en cours..."
  ):
    try:
      # Upload du fichier vidéo vers l'API Gemini File API
      video_file = genai.upload_file(path=tfile.name)

      # Attente que le fichier soit traité par l'API
      import time

      while video_file.state.name == "PROCESSING":
        time.sleep(2)
        video_file = genai.get_file(video_file.name)

      if video_file.state.name == "FAILED":
        raise ValueError("Le traitement de la vidéo par l'IA a échoué.")

      # Utilisation du modèle multimodal Gemini pour analyser le comportement canin
      model = genai.GenerativeModel("gemini-2.5-flash")
      prompt = (
          "Agis en tant qu'éthologue canin expert. Visionne cette vidéo de chien"
          " et analyse précisément : 1) Les signaux d'apaisement ou de stress"
          " (regard, gueule, posture corporelle, queue). 2) Le niveau émotionnel"
          " global. Fournis une synthèse claire, professionnelle et bienveillante"
          " en français."
      )

      response = model.generate_content([video_file, prompt])
      ai_analysis = response.text

      # Nettoyage du fichier sur les serveurs Google après analyse
      genai.delete_file(video_file.name)

    except Exception as e:
      ai_analysis = (
          "Analyse IA indisponible (Vérifiez votre clé API Gemini ou le format"
          f" de la vidéo). Erreur : {str(e)}"
      )

    # Logique cinétique de secours/complément
    if avg_motion < 1.5:
      etat = "État de repos ou de vigilance passive"
      conseil = "Laissez-le tranquille, son équilibre émotionnel est stable."
    elif avg_motion > 7.0 and motion_variance > 15.0:
      etat = "Agitation intense / Montée d'adrénaline"
      conseil = (
          "Prévoyez une transition calme ou un exercice de flairage pour l'aider"
          " à redescendre en pression."
      )
    elif avg_motion > 5.0:
      etat = "Activité exploratoire ou dynamique"
      conseil = (
          "C'est une phase saine de dépense physique et mentale. Pensez à"
          " l'hydrater."
      )
    else:
      etat = "Attention focalisée / Statu quo interactif"
      conseil = "Regardez s'il cherche le contact visuel ; il attend une guidance."

    st.success("Analyse éthologique multimodale réussie !")
    st.video(tfile.name)

    st.markdown("### 📊 Bilan Comportemental Avancé (Hybride OpenCV + IA)")

    with st.container(border=True):
      st.markdown(f"**Diagnostic cinétique évalué :** {etat}")
      st.divider()
      st.markdown("**Analyse Posturale & Éthologique (IA Vision) :**")
      st.write(ai_analysis)
      st.divider()
      st.markdown(f"**Recommandation d'expert :** *\"{conseil}\"*")

else:
  st.info("Téléchargez une vidéo de votre chien pour lancer l'analyse experte.")
    
