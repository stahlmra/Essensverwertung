import json
import streamlit as st

import tensorflow as tf
import numpy as np
from PIL import Image


# =========================
# 0. NORMALISIERUNG (NEU)
# =========================

def norm(x):
    return x.lower().strip()


# =========================
# 1. DATEN LADEN
# =========================

def load_json(file):
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)


exotisch = load_json("exotisch.json")
fluessigkeiten = load_json("fluessigkeiten.json")
gemueseobst = load_json("gemueseobst.json")
gewuerze = load_json("gewuerze.json")
halbfertig = load_json("halbfertig.json")
suesswaren = load_json("sueßwaren.json")
tiefkuehl = load_json("tiefkuehl.json")
tierisch = load_json("tierisch.json")
verarbeitet = load_json("verarbeitet.json")

recipes = load_json("recipes.json")


# =========================
# 2. ZUTATENPOOL
# =========================

alle_zutaten_raw = (
    exotisch +
    fluessigkeiten +
    gemueseobst +
    gewuerze +
    halbfertig +
    suesswaren +
    tiefkuehl +
    tierisch +
    verarbeitet
)


# =========================
# 3. KI MODELL
# =========================

model = tf.keras.models.load_model("keras_model.h5", compile=False)

with open("labels.txt", "r") as f:
    labels = [line.strip() for line in f.readlines()]


# =========================
# 4. UI
# =========================

st.title("🍽️ Rezept Finder App")

uploaded_files = st.file_uploader(
    "Lade bis zu 3 Bilder hoch",
    type=["jpg", "png"],
    accept_multiple_files=True
)

erkannte_zutaten = []


# =========================
# 5. KI ERKENNUNG
# =========================

if uploaded_files:

    for uploaded_file in uploaded_files[:3]:

        image = Image.open(uploaded_file)
        st.image(image, use_column_width=True)

        img = image.resize((224, 224))
        img_array = np.array(img)
        img_array = np.expand_dims(img_array, axis=0) / 255.0

        prediction = model.predict(img_array)[0]

        index = np.argmax(prediction)
        confidence = prediction[index]

        THRESHOLD = 0.80

        if confidence >= THRESHOLD:
            zutat = norm(labels[index])

            if zutat not in erkannte_zutaten:
                erkannte_zutaten.append(zutat)
        else:
            st.write("🤖 Keine sichere Zutat erkannt")


# =========================
# 6. KI OUTPUT
# =========================

if erkannte_zutaten:
    st.subheader("🤖 KI ERKANNT")

    for z in erkannte_zutaten:
        st.write(z)


# =========================
# 7. MANUELLE AUSWAHL
# =========================

manuelle_auswahl = st.multiselect(
    "🥗 Wähle deine Zutaten:",
    alle_zutaten_raw
)

auswahl = [norm(z) for z in (manuelle_auswahl + erkannte_zutaten)]


# =========================
# 8. SCORE (FIXED)
# =========================

def berechne_score(rezept, user_zutaten):

    rezept_zutaten = [norm(z) for z in rezept.get("ingredients", [])]
    user = [norm(z) for z in user_zutaten]

    score = 0

    for rz in rezept_zutaten:
        for uz in user:

            if rz == uz:
                score += 1
                break

            if uz in rz or rz in uz:
                score += 0.8
                break

    return score


# =========================
# 9. REZEPTE
# =========================

ergebnisse = []

for rezept in recipes:
    score = berechne_score(rezept, auswahl)

    ergebnisse.append({
        "name": rezept.get("name"),
        "score": score,
        "time": rezept.get("time"),
        "vegetarian": rezept.get("vegetarian"),
        "ingredients": rezept.get("ingredients"),
        "category": rezept.get("category"),
        "difficulty": rezept.get("difficulty"),
        "description": rezept.get("description"),
        "steps": rezept.get("steps")
    })


ergebnisse = sorted(ergebnisse, key=lambda x: x["score"], reverse=True)


# =========================
# 10. OUTPUT
# =========================

st.markdown("---")
st.subheader("🍝 Passende Rezepte")

if not auswahl:
    st.info("Bitte wähle Zutaten aus 😊")

else:
    found = False

    for r in ergebnisse:

        if r.get("score", 0) >= 1:
            found = True

            st.write("------")
            st.write(f"🍽️ **{r.get('name')}**")
            st.write("⭐ Treffer:", round(r.get("score", 0), 1))
            st.write("⏱️ Zeit:", r.get("time"), "Min")
            st.write("🌱 vegetarisch:", "Ja" if r.get("vegetarian") else "Nein")

            st.write(f"📂 {r.get('category')} | 📊 {r.get('difficulty')}")
            st.write("📝", r.get("description"))

            st.write("👨‍🍳 Schritte:")
            for step in r.get("steps", []):
                st.write("-", step)

            fehlend = [
                z for z in r.get("ingredients", [])
                if norm(z) not in auswahl
            ]
            st.write("❌ fehlt:", fehlend)

            ingredients = r.get("ingredients", [])
            if ingredients:
                st.progress(r.get("score", 0) / len(ingredients))
            else:
                st.progress(0)

    if not found:
        st.warning("Keine passenden Rezepte gefunden – versuche mehr oder andere Zutaten 👍")
