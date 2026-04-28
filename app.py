import json
import streamlit as st

# 👉 NEU: KI IMPORTS
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

# 👉 NEU: MODELL LADEN
model = tf.keras.models.load_model("keras_model.h5", compile=False)

with open("labels.txt", "r") as f:
    labels = [line.strip() for line in f.readlines()]


# =========================
# 2. ALLE ZUTATEN ZUSAMMENFÜHREN
# =========================

alle_zutaten = (
    exotisch
    + fluessigkeiten
    + gemueseobst
    + gewuerze
    + halbfertig
    + suesswaren
    + tiefkuehl
    + tierisch
    + verarbeitet
)


# =========================
# 3. STREAMLIT UI
# =========================

st.title("🍽️ Rezept Finder App")

# 👉 NEU: BILD ERKENNUNG
st.subheader("📸 Zutaten per Bild erkennen")

uploaded_file = st.file_uploader("Lade ein Bild hoch", type=["jpg", "png"])

erkannte_zutat = None

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Dein Bild", use_column_width=True)

    img = image.resize((224, 224))
    img_array = np.array(img)
    img_array = np.expand_dims(img_array, axis=0) / 255.0

    prediction = model.predict(img_array)
    index = np.argmax(prediction)

    erkannte_zutat = labels[index].strip()
    erkannte_zutat = erkannte_zutat.capitalize()

    st.success(f"Erkannt: {erkannte_zutat}")


auswahl = st.multiselect(
    "🥗 Wähle deine Zutaten:",
    alle_zutaten
)

# 👉 NEU: erkannte Zutat hinzufügen
if erkannte_zutat:
    if erkannte_zutat not in auswahl:
        auswahl.append(erkannte_zutat)


# =========================
# 4. MATCHING-LOGIK
# =========================

def berechne_score(rezept, user_zutaten):
    rezept_zutaten = rezept["ingredients"]

    treffer = 0

    for zutat in rezept_zutaten:
        if zutat in user_zutaten:
            treffer += 1

    return treffer


# =========================
# 5. REZEPTE BEWERTEN
# =========================

ergebnisse = []

for rezept in recipes:
    score = berechne_score(rezept, auswahl)

    # 👉 NEU: ALLE FELDER ÜBERNEHMEN
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


# sortieren (beste zuerst)
ergebnisse = sorted(ergebnisse, key=lambda x: x["score"], reverse=True)


# =========================
# 6. ERGEBNISSE ANZEIGEN
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
            st.write("⏱️ Zeit:", r.get("time", "?" ), "Min")
            st.write("🌱 vegetarisch:", "Ja" if r.get("vegetarian", False) else "Nein")

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
