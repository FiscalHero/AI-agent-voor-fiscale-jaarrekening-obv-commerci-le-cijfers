import streamlit as st
import pandas as pd

st.set_page_config(page_title="AI Fiscale Jaarrekening", layout="centered")
st.title("🤖 AI Agent voor Fiscale Jaarrekening")
st.write("""
Upload een CSV met minimaal de kolommen:
- Grootboekrekening
- Bedrag (EUR)
""")

uploaded = st.file_uploader("Upload hier je bestand (.csv)", type=["csv"])

if uploaded:
    try:
        df = pd.read_csv(uploaded)
        st.write("Ingelezen data:")
        st.dataframe(df)
        # Validatie
        if not {"Grootboekrekening","Bedrag (EUR)"}.issubset(df.columns):
            st.error("CSV mist 'Grootboekrekening' of 'Bedrag (EUR)'")
        else:
            # Classificatie
            def bepaal_posttype(txt):
                t = str(txt).lower()
                if "representatie" in t: return "Representatiekosten"
                if "auto" in t:           return "Autokosten"
                if "huur" in t:           return "Huisvestingskosten"
                return "Overige kosten"
            df['Categorie'] = df['Grootboekrekening'].apply(bepaal_posttype)
            st.write("Classificatie per rij:")
            st.dataframe(df[['Grootboekrekening','Categorie']])
            # Correcties
            def corrigeer(r):
                b, c = r['Bedrag (EUR)'], r['Categorie']
                if c == "Representatiekosten":
                    return b * 0.8
                if c == "Autokosten":
                    return b * 0.9
                return b
            df['Fiscaal aftrekbaar'] = df.apply(corrigeer, axis=1)
            st.write("Resultaat met fiscale correcties:")
            st.dataframe(df)
            # Download link
            st.download_button("Download resultaat als CSV", df.to_csv(index=False), "fiscale_correctie.csv")
    except Exception as e:
        st.error(f"Fout: {e}")
