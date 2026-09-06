Le fichier Python corrigé complet — prêt à copier-coller dans votre repo GitHub :

```python
import os
import time
import tempfile
import logging
import cv2
import numpy as np
import google.generativeai as genai
import streamlit as st
from concurrent.futures import ThreadPoolExecutor

# --- Configuration ---
logging.basicConfig(level=logging.INFO)
MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100 Mo
FRAME_SKIP = 5
MAX_WAIT_SEC = 300  # timeout Gemini
RESIZE_DIM = (160, 120)  # sous-échantillonnage pour accélérer OpenCV

PROMPT_ETHOLOGUE = (
    "Agis en tant qu'éthologue canin expert. Visionne cette vidéo de chien "
    "et analyse précisément : 1) Les signaux d'apaisement ou de stress "
    "(regard, gueule, posture corporelle, queue). 2) Le niveau émotionnel "
    "global. Fournis une synthèse claire, professionnelle et bienveillante "
    "en français."
)

# --- Vérification de la clé API ---
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("⚠️ Configuration manquante : GOOGLE_API_KEY non défini dans les secrets Streamlit.")
    st.stop()
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])


# --- Fonctions métier ---
def analyse_cinetique(path):
    """Analyse du mouvement via OpenCV, sur frames sous-échantillonnées."""
    cap = cv2.VideoCapture(path)
    success, frame1 = cap.read()
    if not success:
        cap.release()
        return 0.0, 0.0
    gray1 = cv2.resize(cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY), RESIZE_DIM)
    scores = []
    count = 0
    while True:
        success, frame2 = cap.read()
        if not success:
            break
        count += 1
        if count % FRAME_SKIP != 0:
            continue
        gray2 = cv2.resize(cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY), RESIZE_DIM)
        scores.append(float(np.mean(cv2.absdiff(gray1, gray2))))
        gray1 = gray2
    cap.release()
    if not scores:
        return 0.0, 0.0
    return float(np.mean(scores)), float(np.var(scores))


def analyse_gemini(path):
    """Upload + analyse Gemini Vision, avec nettoyage garanti du fichier."""
    video_file = None
    try:
        video_file = genai.upload_file(path=path)
        elapsed = 0
        while video_file.state.name == "PROCESSING" and elapsed < MAX_WAIT_SEC:
            time.sleep(5)
            elapsed += 5
            video_file = genai.get_file(video_file.name)
        if video_file.state.name != "ACTIVE":
            raise RuntimeError("Traitement IA échoué ou expiré.")
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content([video_file, PROMPT_ETHOLOGUE])
        return response.text, None
    except Exception as e:
        logging.exception("Erreur Gemini")
        return None, str(e)
    finally:
        if video_file:
            try:
                genai.delete_file(video_file.name)
            except Exception:
                logging.warning("Suppression du fichier Gemini échouée.")


def diagnostic_cinetique(avg_motion, motion_variance):
    """Retourne (état, conseil) selon les scores de mouvement."""
    if avg_motion < 1.5:
        return ("État de repos ou de vigilance passive",
                "Laissez-le tranquille, son équilibre émotionnel est stable.")
    if avg_motion > 7.0 and motion_variance > 15.0:
        return ("Agitation intense / Montée d'adrénaline",
                "Prévoyez une transition calme ou un exercice de flairage "
                "pour l'aider à redescendre en pression.")
    if avg_motion > 5.0:
        return ("Activité exploratoire ou dynamique",
                "C'est une phase saine de dépense physique et mentale. "
                "Pensez à l'hydrater.")
    return ("Attention focalisée / Statu quo interactif",
            "Regardez s'il cherche le contact visuel ; il attend une guidance.")


# --- Interface ---
st.title("🐕 Assistant Canin - Expertise Comportementale Multimodale")
st.write(
    "Téléchargez une courte vidéo pour croiser une analyse cinétique locale "
    "et une analyse experte par IA Vision de la posture de votre chien."
)

uploaded_video = st.file_uploader(
    "Choisissez une vidéo (MP4, MOV, AVI)", type=["mp4", "mov", "avi"]
)

if uploaded_video is None:
    st.info("Téléchargez une vidéo de votre chien pour lancer l'analyse experte.")
    st.stop()

# --- Limite de taille (anti-DoS) ---
if uploaded_video.size > MAX_VIDEO_SIZE:
    st.error("Vidéo trop volumineuse (max 100 Mo).")
    st.stop()

# --- Écriture par chunks sur disque (anti-OOM) ---
tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
try:
    chunk_size = 10 * 1024 * 1024  # 10 Mo
    while True:
        chunk = uploaded_video.read(chunk_size)
        if not chunk:
            break
        tfile.write(chunk)
    tfile.close()

    with st.spinner("Analyse éthologique cinétique et vision IA en cours..."):
        # OpenCV + Gemini EN PARALLÈLE
        with ThreadPoolExecutor(max_workers=2) as ex:
            future_cv = ex.submit(analyse_cinetique, tfile.name)
            future_ai = ex.submit(analyse_gemini, tfile.name)
            avg_motion, motion_variance = future_cv.result()
            ai_analysis, ai_error = future_ai.result()

    etat, conseil = diagnostic_cinetique(avg_motion, motion_variance)

    # --- Affichage ---
    if ai_analysis is not None:
        st.success("✅ Analyse éthologique multimodale réussie !")
    else:
        st.warning("⚠️ Analyse cinétique OK, mais analyse IA indisponible.")

    st.video(uploaded_video)  # évite d'exposer le chemin serveur

    st.markdown("### 📊 Bilan Comportemental Avancé (Hybride OpenCV + IA)")
    with st.container(border=True):
        st.markdown(f"**Diagnostic cinétique évalué :** {etat}")
        st.divider()
        st.markdown("**Analyse Posturale & Éthologique (IA Vision) :**")
        if ai_analysis is not None:
            st.write(ai_analysis)
        else:
            st.write(
                "Analyse IA temporairement indisponible. "
                "Vérifiez votre clé API Gemini ou le format de la vidéo."
            )
        st.divider()
        st.markdown(f"**Recommandation d'expert :** *\"{conseil}\"*")

except Exception:
    logging.exception("Erreur lors de l'analyse")
    st.error("Une erreur est survenue pendant l'analyse. Réessayez plus tard.")
finally:
    # Nettoyage GARANTI du fichier temporaire (anti-fuite disque)
    try:
        os.unlink(tfile.name)
    except OSError:
        pass
