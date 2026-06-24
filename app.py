import streamlit as pd
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Configurazione della pagina per adattarsi ai dispositivi mobili
st.set_page_config(page_title="Gestione Finanze", layout="wide")

st.title("💰 Gestione Entrate e Uscite")
st.write("Tieni traccia delle tue finanze mese per mese.")

# Inizializzazione dello stato della sessione per salvare i dati in memoria
if 'transazioni' not in st.session_state:
    st.session_state.transazioni = pd.DataFrame(columns=['Data', 'Tipo', 'Categoria', 'Importo'])

# --- FORM DI INSERIMENTO ---
st.header("📌 Inserisci Nuova Transazione")

col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

with col1:
    data = st.date_input("Data", datetime.today())
with col2:
    tipo = st.selectbox("Tipo", ["Entrata", "Uscita"])
with col3:
    if tipo == "Uscita":
        categoria = st.selectbox("Categoria", ["Benzina", "Università", "Spese Generiche"])
    else:
        categoria = st.selectbox("Categoria", ["Stipendio/Paghetta", "Altro"])
with col4:
    importo = st.number_input("Importo (€)", min_value=0.0, step=0.01, format="%.2f")

if st.button("Aggiungi Transazione", use_container_width=True):
    if importo > 0:
        nuova_riga = pd.DataFrame([{
            'Data': pd.to_datetime(data),
            'Tipo': tipo,
            'Categoria': categoria,
            'Importo': importo
        }])
        st.session_state.transazioni = pd.concat([st.session_state.transazioni, nuova_riga], ignore_index=True)
        st.success("Transazione aggiunta con successo!")
    else:
        st.error("L'importo deve essere maggiore di zero.")

# Visualizzazione dei dati se presenti
df = st.session_state.transazioni

if not df.empty:
    # Assicuriamoci che la colonna Data sia in formato datetime
    df['Data'] = pd.to_datetime(df['Data'])
    df['Mese'] = df['Data'].dt.to_period('M').astype(str)
    
    # --- DASHBOARD PRINCIPALE ---
    st.divider()
    st.header("📊 Resoconto Finanziario")
    
    # Filtro per Mese
    mesi_disponibili = sorted(df['Mese'].unique(), reverse=True)
    mese_selezionato = st.selectbox("Seleziona il mese da analizzare:", mesi_disponibili)
    
    # Dati filtrati per il mese corrente
    df_mese = df[df['Mese'] == mese_selezionato]
    
    # Calcolo metriche
    entrate = df_mese[df_mese['Tipo'] == 'Entrata']['Importo'].sum()
    uscite = df_mese[df_mese['Tipo'] == 'Uscita']['Importo'].sum()
    netto = entrate - uscite
    
    # Visualizzazione KPI
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
        # Calcolo del netto storico mese per mese
        df_storico = df.groupby(['Mese', 'Tipo'])['Importo'].sum().unstack(fill_value=0)
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
    st.dataframe(df.sort_values(by='Data', ascending=False), use_container_width=True)
else:
    st.info("Inserisci la prima transazione per vedere i grafici e il resoconto.")