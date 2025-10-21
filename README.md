# Calcolatore Prezzi MakerWorld 3DmArts (Playwright)

## Installazione e pubblicazione su Streamlit Cloud

1. Crea un repository GitHub, ad esempio `makerworld-calcolatore-playwright`.
2. Carica tutti i file presenti in questo pacchetto.
3. Su Streamlit Cloud, assicurati che la app installi Playwright e Chromium:
   - Aggiungi questo comando prima di deploy: `playwright install`
4. Vai su https://share.streamlit.io e accedi con il tuo account GitHub.
5. Clicca su 'New app', seleziona il repository e il branch.
6. Streamlit genererà la tua pagina pubblica.

## Funzionalità

- Inserisci un link MakerWorld con uno o più oggetti.
- Estrazione automatica di peso (g) e tempo di stampa usando Playwright (headless browser).
- Possibilità di modificare manualmente i valori se non vengono trovati automaticamente.
- Calcolo prezzo singolo e totale in base a:
  - Costo macchina: 0,60 €/h
  - Costo materiale: 0,015 €/g
  - Margine: 35%
- Download CSV del preventivo.
