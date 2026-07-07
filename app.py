import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
import tempfile

# ============================================================
# CONFIGURAZIONE PAGINA
# ============================================================
st.set_page_config(
    page_title="Gestione Finanze - Fiat 500",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

FILE_DATI = "dati_salvadanaio.csv"
COLONNE_BASE = ["Data", "Tipo", "Categoria", "Importo"]


def get_data_file_path():
    cwd_file = os.path.join(os.getcwd(), FILE_DATI)
    temp_file = os.path.join(tempfile.gettempdir(), FILE_DATI)

    if os.path.exists(cwd_file):
        return cwd_file
    if os.path.exists(temp_file):
        return temp_file
    if os.access(os.getcwd(), os.W_OK):
        return cwd_file
    return temp_file

# Palette cromatica coerente
COLOR_PRIMARY = "#EC4899"       
COLOR_BG_HEADER = "#FBCFE8"     
COLOR_TEXT_HEADER = "#831843"   
COLOR_ENTRATA = "#059669"       
COLOR_USCITA = "#E11D48"        
COLOR_NEUTRAL_DARK = "#374151"
COLOR_NEUTRAL_MED = "#6B7280"
COLOR_BG_CARD = "#FFF5F7"       

# ============================================================
# STILE CUSTOM (CSS injection)
# ============================================================
st.markdown(
    f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
        }}

        .app-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1.6rem 2rem;
            border-radius: 18px;
            background: linear-gradient(135deg, {COLOR_BG_HEADER} 0%, #FCE7F3 100%);
            border-left: 8px solid {COLOR_PRIMARY};
            color: {COLOR_TEXT_HEADER};
            margin-bottom: 1.6rem;
            box-shadow: 0 4px 6px -1px rgba(244, 63, 94, 0.1);
        }}
        .header-text h1 {{
            margin: 0;
            font-weight: 800;
            font-size: 1.9rem;
            letter-spacing: -0.5px;
            color: {COLOR_TEXT_HEADER};
        }}
        .header-text p {{
            margin: 0.3rem 0 0 0;
            opacity: 0.9;
            font-size: 0.95rem;
        }}
        .header-car {{
            font-size: 3.5rem;
            margin-left: 1rem;
            animation: bounce 2s infinite;
        }}
        
        @keyframes bounce {{
            0%, 100% {{ transform: translateY(0); }}
            50% {{ transform: translateY(-5px); }}
        }}

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
        }}

        div[data-testid="stMetric"] {{
            background: white;
            border: 1px solid #FCE7F3;
            border-radius: 14px;
            padding: 1rem 1.2rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
        }}

        .stButton button, div[data-testid="stForm"] button {{
            border-radius: 10px;
            font-weight: 600;
            background-color: {COLOR_PRIMARY} !important;
            color: white !important;
            border: none !important;
            width: 100%;
        }}
        .stButton button:hover, div[data-testid="stForm"] button:hover {{
            background-color: #DB2777 !important;
        }}

        .btn-delete button {{
            background-color: #EF4444 !important;
        }}

        section[data-testid="stSidebar"] {{
            background-color: #FFF1F2;
            border-right: 1px solid #FCE7F3;
        }}
        
        div[data-testid="stForm"] {{
            border: none !important;
            padding: 0 !important;
            background: transparent !important;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# HEADER CON FIAT 500
# ============================================================
st.markdown(
    """
    <div class="app-header">
        <div class="header-text">
            <h1>🌸 Gestione Finanze Condivisa 🚗</h1>
            <p>I tuoi dati, tracciati in tempo reale (e fondo cassa per la nuova Fiat 500!).</p>
        </div>
        <div class="header-car">🚗💨</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# CARICAMENTO E SALVATAGGIO DATI
# ============================================================
def normalizza_dati(df):
    if df is None or df.empty:
        return pd.DataFrame(columns=COLONNE_BASE)

    df = df.copy()
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
    df["Importo"] = pd.to_numeric(df["Importo"], errors="coerce").fillna(0.0)
    return df.dropna(subset=["Data"]).reset_index(drop=True)


def carica_dati():
    file_path = get_data_file_path()
    if not os.path.exists(file_path):
        return pd.DataFrame(columns=COLONNE_BASE)
    try:
        df = pd.read_csv(file_path)
        return normalizza_dati(df)
    except Exception:
        return pd.DataFrame(columns=COLONNE_BASE)


def salva_dati(df):
    file_path = get_data_file_path()
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        df.to_csv(file_path, index=False)
        return True
    except Exception as e:
        st.error(f"⚠️ Errore nel salvataggio: {e}")
        return False

if "df_totale" not in st.session_state:
    st.session_state.df_totale = carica_dati()
else:
    st.session_state.df_totale = normalizza_dati(st.session_state.df_totale)

df_totale = st.session_state.df_totale

# ============================================================
# FORM DI INSERIMENTO (Risolto ed Evitato il Freeze)
# ============================================================
with st.container():
    st.markdown('<div class="card-block">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">✨ Nuova Transazione</div>', unsafe_allow_html=True)

    # Fuori dal form mettiamo il selettore del tipo per permettere il cambio dinamico delle categorie
    col_t1, col_t2 = st.columns([1, 3])
    with col_t1:
        tipo = st.selectbox("Tipo", ["Entrata", "Uscita"], key="input_tipo")
        
    # Mappatura pulita delle categorie in base al tipo selezionato
    if tipo == "Uscita":
        lista_categorie = ["Benzina", "Università", "Pagamento Macchina", "Spese Generiche"]
    else:
        lista_categorie = ["Stipendio/Paghetta", "Altro"]

    # Iniziamo il form per i restanti dati della transazione
    with st.form(key="form_transazione", clear_on_submit=True):
        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            data = st.date_input("Data", datetime.today(), key="input_data")
        with col2:
            categoria = st.selectbox("Categoria", lista_categorie, key="input_cat")
        with col3:
            importo = st.number_input("Importo (€)", min_value=0.0, step=0.01, format="%.2f", key="input_importo")

        submit_button = st.form_submit_button(label="💖 Aggiungi al Registro")

        if submit_button:
            if importo > 0:
                nuova_riga = pd.DataFrame([{
                    "Data": pd.to_datetime(data).strftime("%Y-%m-%d"),
                    "Tipo": tipo,
                    "Categoria": categoria,
                    "Importo": importo,
                }])

                df_aggiornato = pd.concat([df_totale, nuova_riga], ignore_index=True)
                df_aggiornato = normalizza_dati(df_aggiornato)
                if salva_dati(df_aggiornato):
                    st.session_state.df_totale = df_aggiornato
                    df_totale = df_aggiornato
                    st.toast("Transazione registrata con successo!", icon="🌸")
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
        st.caption("I grafici storici mostrano l'andamento completo, i KPI mostrano il mese selezionato.")

    df_mese = df_totale[df_totale["Mese"] == mese_selezionato]
    entrate = df_mese[df_mese["Tipo"] == "Entrata"]["Importo"].sum()
    uscite = df_mese[df_mese["Tipo"] == "Uscita"]["Importo"].sum()
    netto = entrate - uscite

    # --- KPI STATS ---
    st.markdown(f'<div class="card-title">📊 Analisi Mensile — {mese_selezionato}</div>', unsafe_allow_html=True)
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric(label="🟢 Entrate", value=f"{entrate:,.2f} €")
    kpi2.metric(label="🔴 Uscite", value=f"{uscite:,.2f} €")
    kpi3.metric(label="🌸 Risparmio Netto", value=f"{netto:,.2f} €")

    st.divider()

    # --- ROW GRAFICI 1: DISTRIBUZIONE ---
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.markdown('<div class="card-block">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">🍰 Spaccato Uscite del Mese</div>', unsafe_allow_html=True)
        df_uscite = df_mese[df_mese["Tipo"] == "Uscita"]
        if not df_uscite.empty:
            fig_torta = px.pie(
                df_uscite, values="Importo", names="Categoria", hole=0.5,
                template="plotly_white", color_discrete_sequence=px.colors.sequential.RdPu_r
            )
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
        fig_linea.update_traces(line=dict(color=COLOR_PRIMARY, width=3), fill="tozeroy", fillcolor="rgba(236, 72, 153, 0.08)")
        fig_linea.update_layout(margin=dict(t=15, b=15, l=15, r=15), xaxis_title=None)
        st.plotly_chart(fig_linea, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # --- ROW GRAFICI 2: ULTERIORI STORICI ---
    st.markdown('<div class="card-block">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📊 Storico Globale dei Volumi e delle Categorie</div>', unsafe_allow_html=True)
    col_g3, col_g4 = st.columns(2)
    
    with col_g3:
        df_barre = df_totale.groupby(["Mese", "Tipo"])["Importo"].sum().reset_index()
        fig_barre = px.bar(
            df_barre, x="Mese", y="Importo", color="Tipo", barmode="group", template="plotly_white",
            color_discrete_map={"Entrata": COLOR_ENTRATA, "Uscita": COLOR_USCITA}
        )
        fig_barre.update_layout(margin=dict(t=15, b=15, l=15, r=15), xaxis_title=None)
        st.plotly_chart(fig_barre, use_container_width=True)
        
    with col_g4:
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
            st.info("Nessuna uscita memorizzata finora.")
    st.markdown("</div>", unsafe_allow_html=True)

    # --- TABELLA RECENTI ---
    st.markdown('<div class="card-block">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📋 Registro Transazioni Completo</div>', unsafe_allow_html=True)
    
    df_visualizzazione = df_totale.copy().sort_values(by="Data", ascending=False)
    df_visualizzazione["ID"] = df_visualizzazione.index
    
    st.dataframe(
        df_visualizzazione, use_container_width=True, hide_index=True,
        column_config={
            "ID": st.column_config.NumberColumn("🆔 ID"),
            "Data": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
            "Importo": st.column_config.NumberColumn("Importo", format="€ %.2f"),
            "Mese": None,
        },
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # --- SEZIONE ELIMINAZIONE RIGA ---
    st.markdown('<div class="card-block">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">⚙️ Gestione ed Eliminazione Errori</div>', unsafe_allow_html=True)
    col_del1, col_del2 = st.columns([3, 1])
    with col_del1:
        id_da_eliminare = st.number_input("Inserisci il numero 🆔 ID della transazione da rimuovere:", min_value=0, max_value=int(df_totale.index.max()) if int(df_totale.index.max()) > 0 else 0, step=1, key="delete_id")
    with col_del2:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        st.markdown('<div class="btn-delete">', unsafe_allow_html=True)
        conferma_elimina = st.button("🗑️ Elimina Riga", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    if conferma_elimina:
        if id_da_eliminare in df_totale.index:
            df_post_eliminazione = df_totale.drop(index=id_da_eliminare)
            df_post_eliminazione = normalizza_dati(df_post_eliminazione)
            if salva_dati(df_post_eliminazione):
                st.session_state.df_totale = df_post_eliminazione
                df_totale = df_post_eliminazione
                st.toast("Transazione eliminata!", icon="🗑️")
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.info("Il database è vuoto. Inserisci la prima transazione per iniziare!")
