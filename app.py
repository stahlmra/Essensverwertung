import json
import streamlit as st

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

auswahl = st.multiselect(
    "🥗 Wähle deine Zutaten:",
    alle_zutaten
)


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

    ergebnisse.append({
        "name": rezept["name"],
        "score": score,
        "time": rezept["time"],
        "vegetarian": rezept["vegetarian"],
        "ingredients": rezept["ingredients"]
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

            # ⭐ Bonus: sichere Bewertung
            ingredients = r.get("ingredients", [])
            if ingredients:
                st.progress(r.get("score", 0) / len(ingredients))
            else:
                st.progress(0)
