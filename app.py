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
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

FILE_DATI = "dati_salvadanaio.csv"
COLONNE_BASE = ["Data", "Tipo", "Categoria", "Importo"]

# Palette cromatica coerente per l'intera dashboard
COLOR_ENTRATA = "#10B981"   # smeraldo
COLOR_USCITA = "#F43F5E"    # corallo/crimson
COLOR_PRIMARY = "#4F46E5"   # indaco (accento)
COLOR_NEUTRAL_DARK = "#1E293B"
COLOR_NEUTRAL_MED = "#64748B"
COLOR_BG_CARD = "#FFFFFF"

# ============================================================
# STILE CUSTOM (CSS injection) — card, tipografia, spaziature
# ============================================================
st.markdown(
    f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
        }}

        /* Header principale */
        .app-header {{
            padding: 1.6rem 2rem;
            border-radius: 18px;
            background: linear-gradient(135deg, {COLOR_PRIMARY} 0%, #6366F1 100%);
            color: white;
            margin-bottom: 1.6rem;
        }}
        .app-header h1 {{
            margin: 0;
            font-weight: 800;
            font-size: 1.9rem;
            letter-spacing: -0.5px;
        }}
        .app-header p {{
            margin: 0.3rem 0 0 0;
            opacity: 0.9;
            font-size: 0.95rem;
        }}

        /* Card generiche per raggruppare contenuti */
        .card-block {{
            background: {COLOR_BG_CARD};
            border: 1px solid #E2E8F0;
            border-radius: 16px;
            padding: 1.4rem 1.6rem;
            margin-bottom: 1.4rem;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
        }}
        .card-title {{
            font-weight: 700;
            font-size: 1.05rem;
            color: {COLOR_NEUTRAL_DARK};
            margin-bottom: 0.8rem;
        }}

        /* KPI metric cards */
        div[data-testid="stMetric"] {{
            background: {COLOR_BG_CARD};
            border: 1px solid #E2E8F0;
            border-radius: 14px;
            padding: 1rem 1.2rem;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
        }}
        div[data-testid="stMetricLabel"] {{
            font-weight: 600;
            color: {COLOR_NEUTRAL_MED};
        }}

        /* Bottone principale */
        .stButton button {{
            border-radius: 10px;
            font-weight: 600;
            background-color: {COLOR_PRIMARY};
            color: white;
            border: none;
        }}
        .stButton button:hover {{
            background-color: #4338CA;
            color: white;
        }}

        section[data-testid="stSidebar"] {{
            background-color: #F8FAFC;
            border-right: 1px solid #E2E8F0;
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
        <h1>💰 Gestione Entrate e Uscite Condivisa</h1>
        <p>I dati sono salvati in tempo reale e visibili da qualsiasi dispositivo.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# CARICAMENTO DATI (con cache e gestione errori esplicita)
# ============================================================
@st.cache_data(show_spinner=False)
def carica_dati():
    """Carica i dati dal CSV. Ritorna sempre un DataFrame con lo schema corretto."""
    if not os.path.exists(FILE_DATI):
        return pd.DataFrame(columns=COLONNE_BASE)

    try:
        df = pd.read_csv(FILE_DATI)
    except pd.errors.EmptyDataError:
        # File presente ma vuoto: nessun errore, semplicemente nessun dato
        return pd.DataFrame(columns=COLONNE_BASE)
    except (pd.errors.ParserError, OSError) as e:
        st.error(f"⚠️ Il file dati risulta corrotto o illeggibile: {e}")
        return pd.DataFrame(columns=COLONNE_BASE)

    # Verifica integrità dello schema
    colonne_mancanti = [c for c in COLONNE_BASE if c not in df.columns]
    if colonne_mancanti:
        st.error(f"⚠️ Il file dati non ha la struttura attesa (colonne mancanti: {colonne_mancanti}).")
        return pd.DataFrame(columns=COLONNE_BASE)

    try:
        df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
        df["Importo"] = pd.to_numeric(df["Importo"], errors="coerce").fillna(0.0)
    except Exception as e:
        st.error(f"⚠️ Errore nella conversione dei tipi di dato: {e}")
        return pd.DataFrame(columns=COLONNE_BASE)

    return df.dropna(subset=["Data"])


def salva_dati(df):
    """Salva i dati su CSV e invalida la cache per ricaricare i dati aggiornati."""
    try:
        df.to_csv(FILE_DATI, index=False)
        carica_dati.clear()  # invalida la cache dopo la scrittura
        return True
    except OSError as e:
        st.error(f"⚠️ Impossibile salvare il file: {e}")
        return False


df_totale = carica_dati()

# ============================================================
# FORM DI INSERIMENTO (dentro una card)
# ============================================================
with st.container():
    st.markdown('<div class="card-block">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📌 Inserisci Nuova Transazione</div>', unsafe_allow_html=True)

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

    if st.button("➕ Aggiungi Transazione", use_container_width=True):
        if importo > 0:
            nuova_riga = pd.DataFrame([{
                "Data": pd.to_datetime(data).strftime("%Y-%m-%d"),
                "Tipo": tipo,
                "Categoria": categoria,
                "Importo": importo,
            }])

            df_aggiornato = pd.concat([df_totale, nuova_riga], ignore_index=True)
            if salva_dati(df_aggiornato):
                st.toast("Transazione salvata con successo!", icon="✅")
                st.rerun()
        else:
            st.error("L'importo deve essere maggiore di zero.")

    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# DASHBOARD PRINCIPALE
# ============================================================
if not df_totale.empty:
    df_totale["Mese"] = df_totale["Data"].dt.to_period("M").astype(str)
    mesi_disponibili = sorted(df_totale["Mese"].unique(), reverse=True)

    # --- FILTRO MESE NELLA SIDEBAR ---
    with st.sidebar:
        st.markdown("### 🗓️ Filtri")
        mese_selezionato = st.selectbox("Seleziona il mese da analizzare:", mesi_disponibili)
        st.caption("Il filtro si applica a KPI e grafico a torta. Lo storico resta completo.")

    df_mese = df_totale[df_totale["Mese"] == mese_selezionato]

    entrate = df_mese[df_mese["Tipo"] == "Entrata"]["Importo"].sum()
    uscite = df_mese[df_mese["Tipo"] == "Uscita"]["Importo"].sum()
    netto = entrate - uscite

    # --- KPI ---
    st.markdown(f'<div class="card-title">📊 Resoconto Finanziario — {mese_selezionato}</div>', unsafe_allow_html=True)
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric(label="🟢 Entrate Totali", value=f"{entrate:,.2f} €")
    kpi2.metric(label="🔴 Uscite Totali", value=f"{uscite:,.2f} €")
    kpi3.metric(label="⚖️ Netto Rimasto", value=f"{netto:,.2f} €", delta=f"{netto:,.2f} €")

    st.divider()

    # --- GRAFICI ---
    col_grafico1, col_grafico2 = st.columns(2)

    with col_grafico1:
        st.markdown('<div class="card-block">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">🍰 Spaccato Uscite (Mese Corrente)</div>', unsafe_allow_html=True)
        df_uscite = df_mese[df_mese["Tipo"] == "Uscita"]
        if not df_uscite.empty:
            fig_torta = px.pie(
                df_uscite,
                values="Importo",
                names="Categoria",
                hole=0.55,
                template="plotly_white",
                color_discrete_sequence=px.colors.sequential.Reds_r,
            )
            fig_torta.update_traces(
                textposition="inside",
                textinfo="percent+label",
                marker=dict(line=dict(color="white", width=2)),
            )
            fig_torta.update_layout(
                margin=dict(t=10, b=10, l=10, r=10),
                legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
                showlegend=True,
            )
            st.plotly_chart(fig_torta, use_container_width=True)
        else:
            st.info("Nessuna uscita registrata in questo mese.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_grafico2:
        st.markdown('<div class="card-block">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📈 Crescita del Netto nel Tempo</div>', unsafe_allow_html=True)
        df_storico = df_totale.groupby(["Mese", "Tipo"])["Importo"].sum().unstack(fill_value=0)
        if "Entrata" not in df_storico.columns:
            df_storico["Entrata"] = 0
        if "Uscita" not in df_storico.columns:
            df_storico["Uscita"] = 0

        df_storico["Netto Mensile"] = df_storico["Entrata"] - df_storico["Uscita"]
        df_storico["Risparmio Cumulativo"] = df_storico["Netto Mensile"].cumsum()
        df_storico = df_storico.reset_index().sort_values("Mese")

        fig_linea = px.line(
            df_storico,
            x="Mese",
            y="Risparmio Cumulativo",
            markers=True,
            template="plotly_white",
            labels={"Risparmio Cumulativo": "Saldo Totale (€)"},
            line_shape="spline",
        )
        fig_linea.update_traces(
            line=dict(color=COLOR_PRIMARY, width=3, smoothing=1.1),
            marker=dict(size=7, color=COLOR_PRIMARY),
            fill="tozeroy",
            fillcolor="rgba(79, 70, 229, 0.08)",
        )
        fig_linea.update_layout(
            margin=dict(t=10, b=10, l=10, r=10),
            xaxis_title=None,
        )
        st.plotly_chart(fig_linea, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # --- TABELLA RECENTI ---
    st.markdown('<div class="card-block">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📋 Registro Transazioni (Tutte)</div>', unsafe_allow_html=True)
    st.dataframe(
        df_totale.sort_values(by="Data", ascending=False),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Data": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
            "Tipo": st.column_config.TextColumn("Tipo"),
            "Categoria": st.column_config.TextColumn("Categoria"),
            "Importo": st.column_config.NumberColumn("Importo", format="€ %.2f"),
            "Mese": None,  # colonna tecnica, non mostrata
        },
    )
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.info("Il database è vuoto. Inserisci la prima transazione per iniziare a salvare i dati!")
