import streamlit as st
import pandas as pd

def agent_block(title: str, color: str, feedback: str):
    st.markdown(
        f"""
        <div style="background-color:{color}; padding:16px; border-radius:8px; margin:16px 0;">
          <h4 style="color:white; margin:0;">{title}</h4>
          <pre style="color:white;">{feedback}</pre>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.set_page_config(page_title="AI Fiscale Jaarrekening", layout="centered")
st.title("🤖 AI Agent voor Fiscale Jaarrekening")
st.write("Upload een CSV met balans, W&V of journaalposten. De fiscale correcties en toelichtingen worden automatisch getoond.")

uploaded = st.file_uploader("📂 Kies je CSV-bestand", type=["csv"])
if uploaded:
    try:
        agent_block("📥 Inlees-agent", "#22523b", "Structuur en kolommen worden gecontroleerd…")
        df = pd.read_csv(uploaded)

        benodigde = {"Grootboekrekening", "Bedrag (EUR)"}
        if not benodigde.issubset(df.columns):
            st.error("CSV mist 'Grootboekrekening' of 'Bedrag (EUR)'")
        else:
            # Basiscategorieën
            def bepaal_categorie(row):
                gr = str(row["Grootboekrekening"]).lower()
                spec = str(row["Specificatie"]).lower() if "Specificatie" in row else ""
                if "auto" in gr:
                    if "elektrisch" in gr or "elektrisch" in spec:
                        return "Elektrische auto"
                    else:
                        return "Auto"
                if "loon" in gr or "dga" in spec:
                    return "Loonkosten"
                if "afschrijving" in gr:
                    return "Afschrijvingen"
                if "representatie" in gr:
                    return "Representatiekosten"
                if "huur" in gr:
                    return "Huur kantoorruimte"
                if "boete" in gr:
                    return "Boetes"
                if "rente" in gr:
                    return "Rente"
                if "voorraad" in gr:
                    return "Voorraad"
                if "voorziening" in gr:
                    return "Voorzieningen"
                if "verzeker" in gr:
                    return "Verzekeringen"
                if "advies" in gr:
                    return "Advieskosten"
                if "telefonie" in gr or "telefoon" in gr:
                    return "Telefonie"
                if "reiskosten" in gr or "ov" in spec:
                    return "Reiskosten"
                if "bank" in gr or "kas" in gr:
                    return "Liquide middelen"
                if "debiteur" in gr:
                    return "Debiteuren"
                if "crediteur" in gr:
                    return "Crediteuren"
                if "btw" in gr:
                    return "BTW"
                if "omzet" in gr:
                    return "Omzet"
                if "inkoop" in gr:
                    return "Inkoopkosten"
                return "Overig"

            df['Categorie'] = df.apply(bepaal_categorie, axis=1)

            # Correctie & toelichting
            toelichtingen = []
            correcties = []
            aftrekbaar = []

            for idx, row in df.iterrows():
                gr = row['Categorie']
                bedrag = row['Bedrag (EUR)']
                toel = ""
                corr = 0
                aftrek = bedrag

                # Fiscale logica
                if gr == "Representatiekosten":
                    toel = "Art. 3.15 IB: 80% aftrekbaar."
                    corr = bedrag * 0.2
                    aftrek = bedrag * 0.8
                elif gr == "Boetes":
                    toel = "Art. 3.14 IB: Niet aftrekbaar."
                    corr = bedrag
                    aftrek = 0
                elif gr == "Auto":
                    toel = "Art. 3.20 IB: Bijtelling privégebruik/90% aftrekbaar. Geen km-adm → bijtelling. Zie ook art. 13bis Wet LB."
                    corr = bedrag * 0.1
                    aftrek = bedrag * 0.9
                elif gr == "Elektrische auto":
                    toel = "Elektrische auto: 100% aftrekbaar, maar let op bijtelling. Zie art. 3.20 IB."
                    corr = 0
                    aftrek = bedrag
                elif gr == "Afschrijvingen":
                    toel = "Art. 3.30 IB: Max. afschrijving, let op restwaarde/bijtelling."
                elif gr == "Voorzieningen":
                    toel = "Art. 3.25-3.29b IB: Alleen onder voorwaarden fiscaal toegestaan."
                elif gr == "Huur kantoorruimte":
                    toel = "Art. 3.16 IB: Alleen aftrekbaar bij voldoen aan voorwaarden (thuiswerkruimte meestal niet aftrekbaar)."
                elif gr == "Loonkosten":
                    toel = "Loon DGA: Art. 12a Wet LB, gebruikelijk loonregeling."
                elif gr == "Rente":
                    toel = "Art. 10a VPB: Onzakelijke rente niet aftrekbaar."
                elif gr == "Mutatie voorraad":
                    toel = "Art. 3.25-3.29 IB: Voorraadwaardering moet fiscaal aanvaardbaar zijn."
                elif gr == "Overig":
                    toel = "Volledig aftrekbaar tenzij specifieke uitzondering geldt."
                else:
                    toel = "Volledig aftrekbaar."

                correcties.append(corr)
                aftrekbaar.append(aftrek)
                toelichtingen.append(toel)

            df["Fiscaal aftrekbaar"] = aftrekbaar
            df["Fiscale correctie"] = correcties
            df["Toelichting"] = toelichtingen

            agent_block("⚖️ Fiscale correcties", "#a14a76", "\n".join(toelichtingen))
            st.success("✅ Fiscale berekening voltooid!")
            st.dataframe(df)

            # Toelichting onder de tabel
            st.info("""
            ### Belangrijkste fiscale regels:
            - **Representatiekosten**: 80% aftrekbaar, zie art. 3.15 IB.
            - **Autokosten**: 90% aftrekbaar (benzine), bijtelling bij privégebruik, tenzij sluitende km-administratie; 100% voor elektrisch, maar let op de bijtelling. Zie art. 3.20 IB.
            - **Boetes**: Niet aftrekbaar, art. 3.14 IB.
            - **Voorzieningen**: Alleen onder strikte voorwaarden toegestaan, zie art. 3.25-3.29b IB.
            - **Huur kantoorruimte**: Thuiswerkruimte meestal niet aftrekbaar, art. 3.16 IB.
            - **DGA-loon**: Gebruiksloonregeling, art. 12a Wet LB.
            - **Overige kosten**: Volledig aftrekbaar tenzij uitzondering.
            """)
    except Exception as e:
        st.error(f"Fout bij inlezen: {e}")
