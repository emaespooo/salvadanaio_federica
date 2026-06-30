import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# ============================================================
# CONFIGURAZIONE PAGINA
# ============================================================
st.set_page_config(
    page_title="Gestione Finanze",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded",
)

FILE_DATI = "dati_salvadanaio.csv"
COLONNE_BASE = ["Data", "Tipo", "Categoria", "Importo"]

# Palette cromatica coerente: Sfumi di Rosa, Fragola, Salvia e Berry
COLOR_PRIMARY = "#EC4899"       # Rosa acceso / Magenta per accenti e pulsanti
COLOR_BG_HEADER = "#FBCFE8"     # Rosa pastello chiaro per header
COLOR_TEXT_HEADER = "#831843"   # Rosa scuro intenso per testi header
COLOR_ENTRATA = "#059669"       # Smeraldo scuro (per contrasto leggibilità su sfondo chiaro)
COLOR_USCITA = "#E11D48"        # Crimson/Rosso Fragola
COLOR_NEUTRAL_DARK = "#374151"
COLOR_NEUTRAL_MED = "#6B7280"
COLOR_BG_CARD = "#FFF5F7"       # Sfondo card rosa chiarissimo, quasi bianco

# ============================================================
# STILE CUSTOM (CSS injection) — Tema Rosa Coerente
# ============================================================
st.markdown(
    f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
        }}

        /* Header principale in rosa pastello */
        .app-header {{
            padding: 1.6rem 2rem;
            border-radius: 18px;
            background: linear-gradient(135deg, {COLOR_BG_HEADER} 0%, #FCE7F3 100%);
            border-left: 8px solid {COLOR_PRIMARY};
            color: {COLOR_TEXT_HEADER};
            margin-bottom: 1.6rem;
            box-shadow: 0 4px 6px -1px rgba(244, 63, 94, 0.1);
        }}
        .app-header h1 {{
            margin: 0;
            font-weight: 800;
            font-size: 1.9rem;
            letter-spacing: -0.5px;
            color: {COLOR_TEXT_HEADER};
        }}
        .app-header p {{
            margin: 0.3rem 0 0 0;
            opacity: 0.9;
            font-size: 0.95rem;
        }}

        /* Card con sfumatura rosa impercettibile */
        .card-block {{
            background: {COLOR_BG_CARD};
            border: 1px solid #FCE7F3;
            border-radius: 16px;
            padding: 1.4rem 1.6rem;
            margin-bottom: 1.4rem;
            box-shadow: 0 2px 4px rgba(244, 63, 94, 0.02);
        }}
        .card-title {{
            font-weight: 700;
            font-size: 1.1rem;
            color: {COLOR_TEXT_HEADER};
            margin-bottom: 0.8rem;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        /* KPI metric cards */
        div[data-testid="stMetric"] {{
            background: white;
            border: 1px solid #FCE7F3;
            border-radius: 14px;
            padding: 1rem 1.2rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
        }}
        div[data-testid="stMetricLabel"] {{
            font-weight: 600;
            color: {COLOR_NEUTRAL_MED};
        }}

        /* Bottone Rosa Principale */
        .stButton button {{
            border-radius: 10px;
            font-weight: 600;
            background-color: {COLOR_PRIMARY};
            color: white;
            border: none;
            transition: all 0.2s ease;
        }}
        .stButton button:hover {{
            background-color: #DB2777;
            color: white;
            transform: translateY(-1px);
        }}

        /* Bottone secondario/cancella */
        .btn-delete button {{
            background-color: #EF4444 !important;
        }}
        .btn-delete button:hover {{
            background-color: #DC2626 !important;
        }}

        /* Sidebar soft pink styling */
        section[data-testid="stSidebar"] {{
            background-color: #FFF1F2;
            border-right: 1px solid #FCE7F3;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# HEADER
# ============================================================
st.markdown(
    """
    <div class="app-header">
        <h1>🌸 Gestione Finanze Condivisa</h1>
        <p>I tuoi dati, tracciati in tempo reale con uno stile pulito e moderno.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# CARICAMENTO DATI (con cache)
# ============================================================
@st.cache_data(show_spinner=False)
def carica_dati():
    if not os.path.exists(FILE_DATI):
        return pd.DataFrame(columns=COLONNE_BASE)
    try:
        df = pd.read_csv(FILE_DATI)
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=COLONNE_BASE)
    except Exception as e:
        st.error(f"⚠️ Errore nel file: {e}")
        return pd.DataFrame(columns=COLONNE_BASE)

    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
    df["Importo"] = pd.to_numeric(df["Importo"], errors="coerce").fillna(0.0)
    return df.dropna(subset=["Data"])

def salva_dati(df):
    try:
        df.to_csv(FILE_DATI, index=False)
        carica_dati.clear()
        return True
    except OSError as e:
        st.error(f"⚠️ Errore nel salvataggio: {e}")
        return False

df_totale = carica_dati()

# ============================================================
# FORM DI INSERIMENTO
# ============================================================
with st.container():
    st.markdown('<div class="card-block">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">✨ Nuova Transazione</div>', unsafe_allow_html=True)

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

    if st.button("💖 Aggiungi al Registro", use_container_width=True):
        if importo > 0:
            nuova_riga = pd.DataFrame([{
                "Data": pd.to_datetime(data).strftime("%Y-%m-%d"),
                "Tipo": tipo,
                "Categoria": categoria,
                "Importo": importo,
            }])

            df_aggiornato = pd.concat([df_totale, nuova_riga], ignore_index=True)
            if salva_dati(df_aggiornato):
                st.toast("Transazione registrata!", icon="🌸")
                st.rerun()
        else:
            st.error("Inserisci un importo maggiore di zero.")
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# DASHBOARD PRINCIPALE
# ============================================================
if not df_totale.empty:
    df_totale["Mese"] = df_totale["Data"].dt.to_period("M").astype(str)
    mesi_disponibili = sorted(df_totale["Mese"].unique(), reverse=True)

    with st.sidebar:
        st.markdown("### 🌸 Opzioni e Filtri")
        mese_selezionato = st.selectbox("Mese da analizzare:", mesi_disponibili)
        st.markdown("---")
        st.caption("I grafici storici mostrano l'andamento completo, mentre la torta e i KPI si riferiscono al mese scelto.")

    df_mese = df_totale[df_totale["Mese"] == mese_selezionato]
    entrate = df_mese[df_mese["Tipo"] == "Entrata"]["Importo"].sum()
    uscite = df_mese[df_mese["Tipo"] == "Uscita"]["Importo"].sum()
    netto = entrate - uscite

    # --- KPI STATS ---
    st.markdown(f'<div class="card-title">📊 Analisi Mensile — {mese_selezionato}</div>', unsafe_allow_html=True)
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric(label="🟢 Entrate", value=f"{entrate:,.2f} €")
    kpi2.metric(label="🔴 Uscite", value=f"{uscite:,.2f} €")
    kpi3.metric(label="🌸 Risparmio Netto", value=f"{netto:,.2f} €", delta=f"{netto:,.2f} €")

    st.divider()

    # --- ROW GRAFICI 1: DISTRIBUZIONE ---
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.markdown('<div class="card-block">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">🍰 Spaccato Uscite del Mese</div>', unsafe_allow_html=True)
        df_uscite = df_mese[df_mese["Tipo"] == "Uscita"]
        if not df_uscite.empty:
            fig_torta = px.pie(
                df_uscite,
                values="Importo",
                names="Categoria",
                hole=0.5,
                template="plotly_white",
                color_discrete_sequence=px.colors.sequential.RdPu_r
            )
            fig_torta.update_traces(textposition="inside", textinfo="percent+label")
            fig_torta.update_layout(
                margin=dict(t=10, b=10, l=10, r=10),
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_torta, use_container_width=True)
        else:
            st.info("Nessuna uscita registrata questo mese.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_g2:
        st.markdown('<div class="card-block">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📈 Crescita Cumulativa del Patrimonio</div>', unsafe_allow_html=True)
        df_storico = df_totale.groupby(["Mese", "Tipo"])["Importo"].sum().unstack(fill_value=0)
        if "Entrata" not in df_storico.columns: df_storico["Entrata"] = 0
        if "Uscita" not in df_storico.columns: df_storico["Uscita"] = 0

        df_storico["Netto Mensile"] = df_storico["Entrata"] - df_storico["Uscita"]
        df_storico["Risparmio Cumulativo"] = df_storico["Netto Mensile"].cumsum()
        df_storico = df_storico.reset_index().sort_values("Mese")

        fig_linea = px.line(
            df_storico, x="Mese", y="Risparmio Cumulativo", markers=True,
            template="plotly_white", labels={"Risparmio Cumulativo": "Saldo (€)"}, line_shape="spline"
        )
        fig_linea.update_traces(
            line=dict(color=COLOR_PRIMARY, width=3),
            marker=dict(size=8, color=COLOR_PRIMARY),
            fill="tozeroy",
            fillcolor="rgba(236, 72, 153, 0.08)"
        )
        fig_linea.update_layout(margin=dict(t=15, b=15, l=15, r=15), xaxis_title=None)
        st.plotly_chart(fig_linea, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # --- ROW GRAFICI 2: COMPREHENSIVE TRANSACTION TRACKING ---
    st.markdown('<div class="card-block">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📊 Storico Globale dei Volumi e delle Categorie</div>', unsafe_allow_html=True)
    
    col_g3, col_g4 = st.columns(2)
    
    with col_g3:
        st.markdown("<p style='font-weight:600; font-size:0.95rem; color:#6B7280;'>Confronto Mensile Flussi (Entrate vs Uscite)</p>", unsafe_allow_html=True)
        df_barre = df_totale.groupby(["Mese", "Tipo"])["Importo"].sum().reset_index()
        fig_barre = px.bar(
            df_barre, x="Mese", y="Importo", color="Tipo",
            barmode="group", template="plotly_white",
            color_discrete_map={"Entrata": COLOR_ENTRATA, "Uscita": COLOR_USCITA}
        )
        fig_barre.update_layout(margin=dict(t=15, b=15, l=15, r=15), xaxis_title=None, legend_title=None)
        st.plotly_chart(fig_barre, use_container_width=True)
        
    with col_g4:
        st.markdown("<p style='font-weight:600; font-size:0.95rem; color:#6B7280;'>Distribuzione Storica delle Spese (Solo Uscite)</p>", unsafe_allow_html=True)
        df_tutte_uscite = df_totale[df_totale["Tipo"] == "Uscita"]
        if not df_tutte_uscite.empty:
            fig_cat = px.bar(
                df_tutte_uscite.groupby("Categoria")["Importo"].sum().reset_index(),
                x="Importo", y="Categoria", orientation="h", template="plotly_white",
                color="Categoria", color_discrete_sequence=px.colors.sequential.Pinkyl
            )
            fig_cat.update_layout(margin=dict(t=15, b=15, l=15, r=15), yaxis_title=None, showlegend=False)
            st.plotly_chart(fig_cat, use_container_width=True)
        else:
            st.info("Nessuna spesa storica.")
            
    st.markdown("</div>", unsafe_allow_html=True)

    # --- TABELLA RECENTI CON ID PER ELIMINAZIONE ---
    st.markdown('<div class="card-block">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📋 Registro Transazioni Completo</div>', unsafe_allow_html=True)
    
    # Prepariamo un dataframe temporaneo con l'indice visibile chiamato "ID"
    df_visualizzazione = df_totale.copy().sort_values(by="Data", ascending=False)
    df_visualizzazione["ID"] = df_visualizzazione.index
    
    st.dataframe(
        df_visualizzazione,
        use_container_width=True,
        hide_index=True,
        column_config={
            "ID": st.column_config.NumberColumn("🆔 ID", help="Usa questo numero sotto se vuoi eliminare la riga"),
            "Data": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
            "Tipo": st.column_config.TextColumn("Tipo"),
            "Categoria": st.column_config.TextColumn("Categoria"),
            "Importo": st.column_config.NumberColumn("Importo", format="€ %.2f"),
            "Mese": None,
        },
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # --- NUOVA SEZIONE: MODIFICA / ELIMINAZIONE DATI ---
    st.markdown('<div class="card-block">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">⚙️ Gestione ed Eliminazione Errori</div>', unsafe_allow_html=True)
    
    col_del1, col_del2 = st.columns([3, 1])
    
    with col_del1:
        id_da_eliminare = st.number_input(
            "Inserisci il numero 🆔 ID della transazione che vuoi rimuovere (lo trovi nella tabella sopra):",
            min_value=0,
            max_value=int(df_totale.index.max()) if not df_totale.empty else 0,
            step=1
        )
    with col_del2:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True) # Allinea il bottone al campo
        st.markdown('<div class="btn-delete">', unsafe_allow_html=True)
        conferma_elimina = st.button("🗑️ Elimina Riga", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    if conferma_elimina:
        if id_da_eliminare in df_totale.index:
            # Rimuoviamo la riga corrispondente all'indice selezionato
            df_post_eliminazione = df_totale.drop(index=id_da_eliminare)
            if salva_dati(df_post_eliminazione):
                st.toast("Transazione eliminata con successo!", icon="🗑️")
                st.rerun()
        else:
            st.error("ID non trovato. Controlla il numero nel registro.")
            
    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.info("Il database è vuoto. Inserisci la prima transazione per iniziare!")
