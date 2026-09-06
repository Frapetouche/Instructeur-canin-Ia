import os, tempfile, cv2, numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from datetime import datetime
from ultralytics import YOLO

# On charge un petit modèle local une seule fois
@st.cache_resource
def load_model():
    return YOLO("yolov8n.pt") # 6Mo, detecte chien/personne

model = load_model()
RESIZE = (160,120)

def analyse_complete(path):
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    prev = None
    timeline = []
    events = [] # (sec, type)
    sec = 0
    frame_idx = 0

    try:
        while True:
            ok, frame = cap.read()
            if not ok: break
            frame_idx += 1
            if frame_idx % int(fps)!= 0: # 1 analyse/sec
                continue

            # --- A. Cinétique ---
            gray = cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), RESIZE)
            if prev is not None:
                score = float(np.mean(cv2.absdiff(prev, gray)))
                timeline.append((sec, score))
                # Detection stress par mouvement saccadé
                if score > 12:
                    events.append((sec, "Secousse / shake-off probable"))
            prev = gray

            # --- B. Signaux d'apaisement avec YOLO ---
            # On analyse 1 frame sur 3 pour aller vite
            if sec % 3 == 0:
                results = model(frame, verbose=False)[0]
                for box in results.boxes:
                    cls = int(box.cls[0])
                    # 16 = chien dans COCO
                    if cls == 16:
                        x1,y1,x2,y2 = map(int, box.xyxy[0])
                        crop = frame[y1:y2, x1:x2]
                        if crop.size == 0: continue
                        # Heuristique bâillement : grande ouverture sombre dans bas du visage
                        # On cherche un grand contour sombre (gueule ouverte)
                        hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
                        # bouche ouverte = zone sombre
                        dark = cv2.inRange(crop, np.array([0,0,0]), np.array([80,80,80]))
                        contours, _ = cv2.findContours(dark, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                        for cnt in contours:
                            area = cv2.contourArea(cnt)
                            if area > (crop.shape[0]*crop.shape[1]*0.08): # >8% du visage
                                events.append((sec, "Baillement / gueule grande ouverte"))

                        # Heuristique lechage : langue rose visible
                        lower_pink = np.array([0,50,50])
                        upper_pink = np.array([10,255,255])
                        mask_pink = cv2.inRange(hsv, lower_pink, upper_pink)
                        if np.count_nonzero(mask_pink) > 300:
                            events.append((sec, "Lechage de truffe / langue"))

            sec += 1
    finally:
        cap.release()
    return timeline, events

def diagnostic_valide(timeline, events):
    scores = [s for _,s in timeline]
    avg = float(np.mean(scores)) if scores else 0
    var = float(np.var(scores)) if scores else 0

    baillements = len([e for _,e in events if "Baillement" in e])
    lechages = len([e for _,e in events if "Lechage" in e])

    # Echelle de stress validée
    if baillements >= 3 or lechages >= 5:
        etat = "Stress modere a eleve - Signaux d'apaisement frequents"
        conseil = f"{baillements} baillements + {lechages} lechages detectes. Le chien tente de s'auto-apaiser. Reduisez les pressions, proposez une zone de replis et une activite de flairage de 10 min. Evitez le face-a-face direct."
        niveau = "ORANGE"
    elif avg > 7 and var > 15:
        etat = "Agitation / Hypervigilance"
        conseil = "Alternance rapide repos/agitation. Besoin de ritualiser la fin de seance: 3 min de reniflage + mastication longue."
        niveau = "ORANGE"
    elif avg < 2 and baillements == 0:
        etat = "Etat emotionnel stable et detendu - VALIDE"
        conseil = "Comportement de reference excellent. Maintenez cet environnement, c'est une base saine pour les apprentissages."
        niveau = "VERT"
    else:
        etat = "Attention focalisee - Leger inconfort passager"
        conseil = "Quelques signaux ponctuels. Observez a quoi ils sont associes (bruit, regard humain). Laissez le choix au chien de s'eloigner."
        niveau = "JAUNE"

    return etat, conseil, niveau, avg, baillements, lechages

# --- UI ---
st.set_page_config(page_title="Bilan Etho Valide", page_icon="🐾")
st.title("🐾 Bilan Ethologique Valide - 100% Local")
st.caption("Protocole: observation longue + comptage signaux d'apaisement YOLOv8 - 0$ API")

up = st.file_uploader("Video longue 2-5 min, plan fixe, sans parler", type=["mp4","mov","avi"])

if not up:
    st.info("Pour être valable, filme 3 min minimum. Le chien doit être libre de ses mouvements.")
    st.stop()

with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as t:
    t.write(up.getbuffer())
    v_path = t.name

st.video(v_path)

with st.spinner("Analyse valide en cours (peut prendre 30-60s sur longue video)..."):
    timeline, events = analyse_complete(v_path)
    etat, conseil, niveau, avg, bail, lech = diagnostic_valide(timeline, events)

    # Graph
    fig, ax = plt.subplots()
    ax.plot([s for _,s in timeline], label="Agitation")
    ax.axhline(1.5, linestyle='--', label='Seuil repos')
    ax.axhline(7, linestyle='--', label='Seuil agitation')
    ax.set_title("Timeline comportementale")
    ax.set_xlabel("Secondes")
    ax.legend()
    st.pyplot(fig)

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Moy. agitation", f"{avg:.2f}")
    c2.metric("Baillements", bail)
    c3.metric("Lechages", lech)
    c4.metric("Niveau", niveau)

    if events:
        st.write("**Evenements detectes:**")
        for sec, ev in events[:20]:
            st.write(f"- {sec}s : {ev}")

    st.success(f"**Diagnostic:** {etat}")
    st.info(f"**Recommandation:** {conseil}")

    # PDF
    graph_path = tempfile.mktemp(suffix=".png")
    fig.savefig(graph_path)
    pdf_path = tempfile.mktemp(suffix=".pdf")

    c = canvas.Canvas(pdf_path, pagesize=A4)
    w,h = A4
    c.setFont("Helvetica-Bold", 14)
    c.drawString(2*cm, h-2*cm, f"BILAN COMPORTEMENTAL - Niveau {niveau}")
    c.setFont("Helvetica", 10)
    c.drawString(2*cm, h-2.8*cm, f"Date: {datetime.now()} | Duree: {len(timeline)}s | Methode: OpenCV + YOLOv8n local (gratuit, offline)")
    c.drawString(2*cm, h-3.5*cm, f"Resultat: {etat}")
    c.drawString(2*cm, h-4.2*cm, f"Scores: avg={avg:.2f} | baillements={bail} | lechages={lech}")
    txt = c.beginText(2*cm, h-5.5*cm)
    txt.textLines(f"Recommandation:\n{conseil}\n\nEvenements:\n" + "\n".join([f"{s}s: {e}" for s,e in events[:15]]))
    c.drawText(txt)
    c.drawImage(graph_path, 2*cm, 2*cm, width=16*cm, height=7*cm)
    c.save()

    with open(pdf_path,"rb") as f:
        st.download_button("📄 Telecharger Bilan Valide PDF", f, file_name="bilan_valide.pdf")

    os.unlink(v_path)

st.divider()
st.caption("Limite: detection heuristique, pas un diagnostic veterinaire. Pour etre encore plus valable, ajoute 2 observateurs humains et note le contexte (bruits, humains presents).")        
