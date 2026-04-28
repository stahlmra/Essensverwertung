import json
import streamlit as st

# KI IMPORTS
import tensorflow as tf
import numpy as np
from PIL import Image


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
# 2. KI MODELL LADEN
# =========================

model = tf.keras.models.load_model("keras_model.h5", compile=False)

with open("labels.txt", "r") as f:
    labels = [line.strip() for line in f.readlines()]


# =========================
# 3. ZUTATENLISTE
# =========================

alle_zutaten = (
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
# 4. STREAMLIT UI
# =========================

st.title("🍽️ Rezept Finder App")

# =========================
# 📸 KI BILD ERKENNUNG
# =========================

st.subheader("📸 Zutaten per Bild erkennen")

uploaded_files = st.file_uploader(
    "Lade bis zu 3 Bilder hoch",
    type=["jpg", "png"],
    accept_multiple_files=True
)

erkannte_zutaten = []

if uploaded_files:

    if len(uploaded_files) > 3:
        st.warning("Maximal 3 Bilder erlaubt")

    for uploaded_file in uploaded_files[:3]:

        image = Image.open(uploaded_file)
        st.image(image, caption="Dein Bild", use_column_width=True)

        img = image.resize((224, 224))
        img_array = np.array(img)
        img_array = np.expand_dims(img_array, axis=0) / 255.0

        prediction = model.predict(img_array)
        index = np.argmax(prediction)

        zutat = labels[index].strip().capitalize()

        if zutat not in erkannte_zutaten:
            erkannte_zutaten.append(zutat)

    st.success(f"Erkannt: {', '.join(erkannte_zutaten)}")


# =========================
# 5. MANUELLE AUSWAHL
# =========================

manuelle_auswahl = st.multiselect(
    "🥗 Wähle deine Zutaten:",
    alle_zutaten
)

auswahl = list(set(manuelle_auswahl + erkannte_zutaten))

# 👉 HIER EINBAUEN
if erkannte_zutaten:
    st.info("🔄 Zutaten wurden aus Bildern hinzugefügt – Rezepte werden aktualisiert")

# =========================
# 6. MATCHING
# =========================

def berechne_score(rezept, user_zutaten):
    return sum(1 for z in rezept["ingredients"] if z in user_zutaten)


# =========================
# 7. REZEPTE BEWERTEN
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


# sortieren
ergebnisse = sorted(ergebnisse, key=lambda x: x["score"], reverse=True)


# =========================
# 8. AUSGABE
# =========================

st.subheader("🍝 Passende Rezepte")

if not auswahl:
    st.info("Bitte wähle Zutaten aus 😊")

else:
    for r in ergebnisse:
        if r.get("score", 0) > 0:

            st.write("------")
            st.write(f"🍽️ **{r.get('name', 'Unbekannt')}**")
            st.write("⭐ Treffer:", r.get("score", 0))
            st.write("⏱️ Zeit:", r.get("time", "?"), "Min")
            st.write("🌱 vegetarisch:", "Ja" if r.get("vegetarian") else "Nein")

            st.write(f"📂 {r.get('category', 'Keine Angabe')} | 📊 {r.get('difficulty', 'Keine Angabe')}")
            st.write("📝", r.get("description", "Keine Beschreibung"))

            st.write("👨‍🍳 Schritte:")
            for step in r.get("steps", []):
                st.write("-", step)

            fehlend = [
                z for z in r.get("ingredients", [])
                if z not in auswahl
            ]
            st.write("❌ fehlt:", fehlend)

            ingredients = r.get("ingredients", [])
            if ingredients:
                st.progress(r.get("score", 0) / len(ingredients))
            else:
                st.progress(0)
