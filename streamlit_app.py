import streamlit as st
import pandas as pd

# Helper voor toelichting op de regels
fiscale_toelichting = """
**Regels gebruikt in deze tool:**

- _Representatiekosten_: 80% aftrekbaar (art. 3.14 Wet IB 2001)
- _Autokosten (benzine/diesel)_: 90% aftrekbaar, tenzij privégebruik → correctie
- _Autokosten (elektrisch)_: 100% aftrekbaar tot €2.100 bijtelling, daarna 90%
- _Huisvestingskosten_: volledig aftrekbaar (tenzij gemengd gebruik)
- _Boetes_: niet aftrekbaar
- _Kosten eigen woning_: niet aftrekbaar voor VPB/IB-ondernemer
- _Overige bedrijfskosten_: volledig aftrekbaar tenzij anders wettelijk bepaald
"""

def bepaal_posttype(naam):
    t = naam.lower()
    if "representatie" in t:         return "Representatiekosten"
    if "auto" in t and "elektr" in t: return "Autokosten elektrisch"
    if "auto" in t:                  return "Autokosten"
    if "huur" in t:                  return "Huisvestingskosten"
    if "boete" in t:                 return "Boetes"
    if "eigen woning" in t:          return "Kosten eigen woning"
    if "personeel" in t:             return "Personeelskosten"
    if "afschrijving" in t:          return "Afschrijvingen"
    return "Overige kosten"

def fiscale_correctie(row):
    b, c = row['Bedrag (EUR)'], row['Categorie']
    toel = ""
    if c == "Representatiekosten":
        toel = "80% aftrekbaar"
        return b*0.8, b*0.2, toel
    if c == "Autokosten elektrisch":
        # Simpel voorbeeld: boven €2.100 beperkt aftrekbaar (stelregel)
        if b > 2100:
            toel = "100% aftrekbaar tot €2.100, rest 90%"
            aftrekbaar = 2100 + (b-2100)*0.9
            return aftrekbaar, b-aftrekbaar, toel
        else:
            toel = "100% aftrekbaar"
            return b, 0, toel
    if c == "Autokosten":
        toel = "90% aftrekbaar (rest privégebruik of bijtelling)"
        return b*0.9, b*0.1, toel
    if c == "Boetes":
        toel = "Niet aftrekbaar (art. 3.14 Wet IB)"
        return 0, b, toel
    if c == "Huisvestingskosten":
        toel = "Volledig aftrekbaar"
        return b, 0, toel
    if c == "Kosten eigen woning":
        toel = "Niet aftrekbaar in VPB"
        return 0, b, toel
    # etc. (je kunt uitbreiden met meer posten)
    toel = "Volledig aftrekbaar"
    return b, 0, toel

st.set_page_config(page_title="AI Fiscale Jaarrekening", layout="centered")
st.title("🤖 AI Agent voor Fiscale Jaarrekening")
st.write("Upload je CSV (Grootboekrekening, Bedrag (EUR)) en zie de fiscale correcties.")
st.markdown(fiscale_toelichting)

uploaded = st.file_uploader("📂 Kies je CSV-bestand", type=["csv"])
if uploaded:
    df = pd.read_csv(uploaded)
    if not {"Grootboekrekening","Bedrag (EUR)"}.issubset(df.columns):
        st.error("CSV mist 'Grootboekrekening' of 'Bedrag (EUR)'")
    else:
        df["Categorie"] = df["Grootboekrekening"].apply(bepaal_posttype)
        res = df.apply(lambda row: fiscale_correctie(row), axis=1, result_type='expand')
        df["Fiscaal aftrekbaar"], df["Correctie"], df["Toelichting"] = res[0], res[1], res[2]
        st.success("✅ Fiscale berekening voltooid!")
        st.dataframe(df)

        # Downloadknop
        csv = df.to_csv(index=False).encode()
        st.download_button(
            "Download resultaat als CSV",
            csv,
            "fiscale_jaarrekening_resultaat.csv",
            "text/csv",
            key='download-csv'
        )
