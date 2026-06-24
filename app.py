import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# Configurazione della pagina per i dispositivi mobili
st.set_page_config(page_title="Gestione Finanze", layout="wide")

st.title("💰 Gestione Entrate e Uscite Condivisa")
st.write("I dati sono salvati in tempo reale e visibili da qualsiasi dispositivo.")

# Nome del file in cui verranno salvati i dati stabilmente
FILE_DATI = "dati_salvadanaio.csv"

# Funzione per caricare i dati
def carica_dati():
    if os.path.exists(FILE_DATI):
        try:
            df = pd.read_csv(FILE_DATI)
            df['Data'] = pd.to_datetime(df['Data'])
            return df
        except Exception:
            pass
    # Se il file non esiste o è vuoto, crea la struttura di base
    return pd.DataFrame(columns=['Data', 'Tipo', 'Categoria', 'Importo'])

# Funzione per salvare i dati
def salva_dati(df):
    df.to_csv(FILE_DATI, index=False)

# Carichiamo i dati all'avvio
df_totale = carica_dati()

# --- FORM DI INSERIMENTO ---
st.header("📌 Inserisci Nuova Transazione")

col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

with col1:
    data = st.date_input("Data", datetime.today())
with col2:
    tipo = st.selectbox("Tipo", ["Entrata", "Uscita"])
with col3:
    if tipo == "Uscita":
        categoria = st.selectbox("Categoria", ["Benzina", "Università", "Pagamento Macchina", "Spese Generiche"])
    else:
        categoria = st.selectbox("Categoria", ["Stipendio/Paghetta", "Altro"])
with col4:
    importo = st.number_input("Importo (€)", min_value=0.0, step=0.01, format="%.2f")

if st.button("Aggiungi Transazione", use_container_width=True):
    if importo > 0:
        nuova_riga = pd.DataFrame([{
            'Data': pd.to_datetime(data).strftime('%Y-%m-%d'),
            'Tipo': tipo,
            'Categoria': categoria,
            'Importo': importo
        }])
        
        df_aggiornato = pd.concat([df_totale, nuova_riga], ignore_index=True)
        salva_dati(df_aggiornato)
        st.success("Transazione salvata con successo!")
        st.rerun()
    else:
        st.error("L'importo deve essere maggiore di zero.")

# Visualizzazione dei dati e grafici
if not df_totale.empty:
    df_totale['Data'] = pd.to_datetime(df_totale['Data'])
    df_totale['Mese'] = df_totale['Data'].dt.to_period('M').astype(str)
    
    # --- DASHBOARD PRINCIPALE ---
    st.divider()
    st.header("📊 Resoconto Finanziario")
    
    mesi_disponibili = sorted(df_totale['Mese'].unique(), reverse=True)
    mese_selezionato = st.selectbox("Seleziona il mese da analizzare:", mesi_disponibili)
    
    df_mese = df_totale[df_totale['Mese'] == mese_selezionato]
    
    entrate = df_mese[df_mese['Tipo'] == 'Entrata']['Importo'].sum()
    uscite = df_mese[df_mese['Tipo'] == 'Uscita']['Importo'].sum()
    netto = entrate - uscite
    
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric(label="🟢 Entrate Totali", value=f"{entrate:.2f} €")
    kpi2.metric(label="🔴 Uscite Totali", value=f"{uscite:.2f} €")
    kpi3.metric(label="⚖️ Netto Rimasto", value=f"{netto:.2f} €", delta=f"{netto:.2f} €")
    
    st.divider()
    
    # --- GRAFICI ---
    col_grafico1, col_grafico2 = st.columns(2)
    
    with col_grafico1:
        st.subheader("🍰 Spaccato Uscite (Mese Corrente)")
        df_uscite = df_mese[df_mese['Tipo'] == 'Uscita']
        if not df_uscite.empty:
            fig_torta = px.pie(df_uscite, values='Importo', names='Categoria', hole=0.4,
                               color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig_torta, use_container_width=True)
        else:
            st.info("Nessuna uscita registrata in questo mese.")
            
    with col_grafico2:
        st.subheader("📈 Crescita del Netto nel Tempo")
        df_storico = df_totale.groupby(['Mese', 'Tipo'])['Importo'].sum().unstack(fill_value=0)
        if 'Entrata' not in df_storico.columns: df_storico['Entrata'] = 0
        if 'Uscita' not in df_storico.columns: df_storico['Uscita'] = 0
        
        df_storico['Netto Mensile'] = df_storico['Entrata'] - df_storico['Uscita']
        df_storico['Risparmio Cumulativo'] = df_storico['Netto Mensile'].cumsum()
        df_storico = df_storico.reset_index()
        
        fig_linea = px.line(df_storico, x='Mese', y='Risparmio Cumulativo', markers=True,
                            labels={'Risparmio Cumulativo': 'Saldo Totale (€)'},
                            title="Andamento del patrimonio totale")
        st.plotly_chart(fig_linea, use_container_width=True)

    # --- TABELLA RECENTI ---
    st.subheader("📋 Registro Transazioni (Tutte)")
    st.dataframe(df_totale.sort_values(by='Data', ascending=False), use_container_width=True)
else:
    st.info("Il database è vuoto. Inserisci la prima transazione per iniziare a salvare i dati!")
