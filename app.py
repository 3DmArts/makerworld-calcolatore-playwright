import streamlit as st
import pandas as pd
import json
from playwright.sync_api import sync_playwright
import re

st.set_page_config(page_title="Calcolatore Prezzi MakerWorld 3DmArts", layout="wide")
st.title("Calcolatore Prezzi MakerWorld 3DmArts (Playwright)")
st.write("Versione ibrida: estrazione automatica con Playwright + modifica manuale")

# Carica configurazione
with open("config.json") as f:
    cfg = json.load(f)
COSTO_ORA = cfg["costo_macchina_per_ora"]
COSTO_MAT_G = cfg["costo_materiale_per_g"]
MARGINE = cfg["margine_percentuale"]

st.sidebar.header("Parametri")
costo_orario = st.sidebar.number_input("Costo macchina €/h", value=COSTO_ORA, step=0.01)
costo_materiale = st.sidebar.number_input("Costo materiale €/g", value=COSTO_MAT_G, step=0.001)
margine_percent = st.sidebar.number_input("Margine %", value=MARGINE, step=1)

url = st.text_input("Inserisci link MakerWorld")

def estrai_dati_playwright(url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)
            # Attendere il caricamento completo (puoi regolare timeout)
            page.wait_for_timeout(2000)
            html = page.content()
            browser.close()
            return html
    except Exception as e:
        st.error(f"Errore Playwright: {e}")
        return None

def parse_html(html):
    # Regex tempo
    time_pattern = re.compile(r'(?:(\d+)\s*h(?:ou?r)?(?:s)?\s*(?:(\d+)\s*m)?)|(?:(\d+)\s*m)', flags=re.IGNORECASE)
    times = [m for m in time_pattern.finditer(html)]
    # Regex peso
    weight_pattern = re.compile(r'(\d+)\s*(?:g|gr)', flags=re.IGNORECASE)
    weights = [m for m in weight_pattern.finditer(html)]

    rows = []
    for i in range(max(len(times), len(weights))):
        # Tempo
        if i < len(times):
            t = times[i]
            if t.group(1):
                hours = int(t.group(1))
                minutes = int(t.group(2)) if t.group(2) else 0
            else:
                hours = 0
                minutes = int(t.group(3))
        else:
            hours = 0
            minutes = 0
        tempo_str = f"{hours}h {minutes}m" if (hours or minutes) else "-"
        ore_float = hours + minutes/60
        # Peso
        grams = int(weights[i].group(1)) if i < len(weights) else 0
        rows.append({"Nome": f"Oggetto {i+1}", "Tempo": tempo_str, "Ore_float": ore_float, "Peso_g": grams})
    return pd.DataFrame(rows)

if st.button("Calcola prezzi"):
    if not url:
        st.warning("Inserisci un link.")
        st.stop()
    html = estrai_dati_playwright(url)
    if html:
        df = parse_html(html)
        st.write("Puoi modificare i valori prima del calcolo:")
        edited_df = st.data_editor(df, num_rows="dynamic")
        # Calcolo prezzo
        prezzi = []
        for _, r in edited_df.iterrows():
            prezzo = (r["Ore_float"]*costo_orario + r["Peso_g"]*costo_materiale)*(1+margine_percent/100)
            prezzi.append(round(prezzo,2))
        edited_df["Prezzo €"] = prezzi
        total = sum(prezzi)
        st.success(f"Totale preventivo: € {total:.2f}")
        st.dataframe(edited_df[["Nome","Tempo","Peso_g","Prezzo €"]], use_container_width=True)
        # Download CSV
        csv = edited_df.to_csv(index=False)
        st.download_button("Scarica CSV", data=csv, file_name="preventivo.csv", mime="text/csv")
