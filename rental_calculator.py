import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import math
# Configurazione della pagina
st.set_page_config(
    page_title="Analisi Redditività Immobile",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizzato per rendere l'app più professionale
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    .comparison-positive {
        color: #28a745;
        font-weight: bold;
    }
    .comparison-negative {
        color: #dc3545;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Titolo principale
st.markdown('<h1 class="main-header">Analisi Redditività Immobile</h1>', unsafe_allow_html=True)
st.markdown("### Confronto tra Affitto Breve e Affitto Tradizionale")

# ============================================================================
# SIDEBAR - INPUTS
# ============================================================================

st.sidebar.header("Parametri dell'Immobile")

st.sidebar.markdown("---")
st.sidebar.subheader("Dati Base")

# Input per affitti brevi
prezzo_notte = st.sidebar.number_input(
    "Prezzo medio per notte (€)",
    min_value=50.0,
    max_value=1000.0,
    value=185.0,
    step=5.0,
    help="Prezzo che carichi per notte su piattaforme come Booking/Airbnb"
)

notti_prenotate_mese = st.sidebar.number_input(
    "Notti prenotate al mese",
    min_value=1,
    max_value=30,
    value=26,
    step=1,
    help="Stima realistica del numero di notti che riesci ad affittare"
)

permanenza_media = st.sidebar.number_input(
    "Permanenza media (notti)",
    min_value=1.0,
    max_value=30.0,
    value=3.0,
    step=0.5,
    help="Quante notti in media rimangono i tuoi ospiti",
    disabled = True
)

spese_pulizia = st.sidebar.number_input(
    "Spese di pulizia per cambio ospite (€)",
    min_value=0.0,
    max_value=200.0,
    value=50.0,
    step=5.0,
    help="Quanto paghi per pulire tra un ospite e l'altro",
    disabled = False
)

st.sidebar.markdown("---")
st.sidebar.subheader(" Costi e Commissioni")

commissione_piattaforme = st.sidebar.slider(
    "Commissione piattaforme (%)",
    min_value=0.0,
    max_value=30.0,
    value=15.0,
    step=0.5,
    help="Booking/Airbnb di solito prendono 12-18%",
    disabled = True
)

commissione_gestione = st.sidebar.slider(
    "Commissione di gestione (%)",
    min_value=0.0,
    max_value=40.0,
    value=20.0,
    step=1.0,
    help="Percentuale che prende l'agenzia per gestire tutto",
    disabled = True

)

iva_percentuale = st.sidebar.radio(
    "IVA al 10% o 22% a seconda del regime",
    options = [10,22],
    index = 0,
    horizontal = True
    disabled = True
)

st.sidebar.markdown("---")
st.sidebar.subheader("Calcolo tasse")

condominio_fittizio = st.sidebar.number_input(
    "rimborso spese (€)",
    min_value=0.0,
    max_value=1000.0,
    value=300.0,
    step=50.0,
    help = " Rimborso per le spese di condominio e utenze"
)

IRPEF = st.sidebar.slider(
    "Aliquota IRPEF(%)",
    min_value=0.0,
    max_value=50.0,
    value=33.0,
    step=1.0,
    help="IRPEF marginale"
)

st.sidebar.markdown("---")
st.sidebar.subheader("Spese Fisse Mensili")

condominio = st.sidebar.number_input(
    "Condominio mensile (€)",
    min_value=0.0,
    max_value=1000.0,
    value=100.0,
    step=10.0
)

utenze_mensili = st.sidebar.number_input(
    "Utenze medie mensili (€)",
    min_value=0.0,
    max_value=500.0,
    value=150.0,
    step=10.0,
    help="Luce, gas, acqua, internet, rifiuti"
)

noleggio_biancheria = st.sidebar.number_input(
    "Noleggio biancheria per cambio (€)",
    min_value=0.0,
    max_value=100.0,
    value=25.0,
    step=5.0,
    disabled = True
)

pulizie_stanza = st.sidebar.number_input(
    "Pulizie appartamento (€)",
    min_value=0.0,
    max_value=100.0,
    value=25.0,
    step=5.0,
    disabled = True
)

st.sidebar.markdown("---")
st.sidebar.subheader("Confronto Affitto Tradizionale")

canone_affitto_tradizionale = st.sidebar.number_input(
    "Canone affitto tradizionale mensile (€)",
    min_value=0.0,
    max_value=5000.0,
    value=1200.0,
    step=50.0,
    help="Quanto potresti prendere con un affitto normale"
)

tasse_affitto_tradizionale = st.sidebar.slider(
    "Tasse su affitto tradizionale (%)",
    min_value=0.0,
    max_value=50.0,
    value=21.0,
    step=1.0,
    help="Cedolare secca 21% o IRPEF marginale"
)

# ============================================================================
# CALCOLI AFFITTO BREVE
# ============================================================================

# Calcolo numero di ingressi (check-in)
ingressi = math.ceil(notti_prenotate_mese / permanenza_media)

# Ricavi lordi 
ricavi_affitti = prezzo_notte * notti_prenotate_mese
spese_pulizia_incassate = spese_pulizia * ingressi
fatturato_lordo = ricavi_affitti + spese_pulizia_incassate

# Costi
iva = fatturato_lordo * (iva_percentuale / 100)
commissioni_piattaforme = fatturato_lordo * (commissione_piattaforme / 100)
costo_pulizie = pulizie_stanza * ingressi
costo_biancheria = noleggio_biancheria * ingressi
spese_fisse_mensili = (condominio + utenze_mensili) 

# Fatturato al netto di IVA e commissioni piattaforme
fatturato_netto = fatturato_lordo - iva - commissioni_piattaforme

# Commissione gestione (calcolata sul fatturato netto)
costo_gestione = fatturato_lordo * (commissione_gestione / 100)

# Utile netto per il proprietario (PRIMA delle tasse IRPEF personali)
utile_netto_pretax = (fatturato_netto - costo_gestione - costo_pulizie - 
                     costo_biancheria)

#Afitto tassato con l'IRPEF
affitto_tassato = utile_netto_pretax-condominio_fittizio

tasse = (IRPEF/100)*affitto_tassato

#utile netto

utile_netto_breve = utile_netto_pretax - tasse - spese_fisse_mensili

# ============================================================================
# CALCOLI AFFITTO TRADIZIONALE
# ============================================================================

# Ricavi mensili affitto tradizionale
ricavi_tradizionale = canone_affitto_tradizionale 

# Costi (nel tradizionale il proprietario paga condominio e manutenzione ordinaria)
# Le utenze solitamente sono a carico dell'inquilino
costi_tradizionale = 0   # Solo condominio, utenze le paga l'inquilino

# Tasse
tasse_tradizionale = ricavi_tradizionale * (tasse_affitto_tradizionale / 100)

# Utile netto tradizionale
utile_netto_tradizionale = ricavi_tradizionale - costi_tradizionale - tasse_tradizionale

# Differenza
differenza_utile = utile_netto_breve - utile_netto_tradizionale
percentuale_guadagno = ((utile_netto_breve / utile_netto_tradizionale) - 1) * 100 if utile_netto_tradizionale > 0 else 0

# ============================================================================
# VISUALIZZAZIONE RISULTATI
# ============================================================================

# Layout a tre colonne per i KPI principali
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label=" Utile Netto Mensile Affitto Breve",
        value=f"€ {utile_netto_breve:,.0f}",
        delta=None
    )

with col2:
    st.metric(
        label=" Utile Netto Mensile Affitto Tradizionale",
        value=f"€ {utile_netto_tradizionale:,.0f}",
        delta=None
    )

with col3:
    delta_color = "normal" if percentuale_guadagno > 0 else "inverse"
    st.metric(
        label=" Guadagno Extra con Affitto Breve",
        value=f"{percentuale_guadagno:+.1f}%",
        delta=f"{differenza_utile:+,.0f} € vs tradizionale"
    )

st.markdown("---")

# ============================================================================
# DETTAGLIO AFFITTO BREVE
# ============================================================================

st.subheader(" Dettaglio Affitto Breve")

col_left, col_right = st.columns(2)

with col_left:
    st.markdown("####  Ricavi")
    ricavi_data = {
        "Voce": [
            "Ricavi da affitti",
            "Spese pulizia incassate",
            "Fatturato lordo",
            "IVA",
            "Commissioni piattaforme",
            "Fatturato netto"
        ],
        "Importo (€)": [
            f"{ricavi_affitti:,.0f}",
            f"{spese_pulizia_incassate:,.0f}",
            f"{fatturato_lordo:,.0f}",
            f"-{iva:,.0f}",
            f"-{commissioni_piattaforme:,.0f}",
            f"{fatturato_netto:,.0f}"
        ]
    }
    st.dataframe(pd.DataFrame(ricavi_data), hide_index=True, use_container_width=True)
    
    st.info(f"""
    **Dettagli operativi:**
    - Notti prenotate: {notti_prenotate_mese} notti/mese
    - Numero di ingressi: {ingressi} check-in
    - Tasso di occupazione: {(notti_prenotate_mese/30)*100:.1f}%
    - Ricavo medio per prenotazione: € {(ricavi_affitti/ingressi):,.0f}
    """)

with col_right:
    st.markdown("#### Costi")
    costi_data = {
        "Voce": [
            "Commissione gestione",
            "Pulizie",
            "Noleggio biancheria",
            "Condominio mensile",
            "Utenze mensili",
            "Totale costi"
        ],
        "Importo (€)": [
            f"{costo_gestione:,.0f}",
            f"{costo_pulizie:,.0f}",
            f"{costo_biancheria:,.0f}",
            f"{condominio :,.0f}",
            f"{utenze_mensili :,.0f}",
            f"{(costo_gestione + costo_pulizie + costo_biancheria + spese_fisse_mensili):,.0f}"
        ]
    }
    st.dataframe(pd.DataFrame(costi_data), hide_index=True, use_container_width=True)
    
    # ROI semplificato
    costi_totali = costo_gestione + costo_pulizie + costo_biancheria + spese_fisse_mensili
    margine_netto = (utile_netto_breve / fatturato_lordo * 100) if costi_totali > 0 else 0
    
    st.success(f"""
    **Riepilogo:**
    - Fatturato netto: € {fatturato_netto:,.0f}
    - Costi totali: € {costi_totali:,.0f}
    - Tasse: € {tasse:,.0f}
    - **Utile netto: € {utile_netto_breve:,.0f}**
    - Margine netto (%): {margine_netto:.1f}%
    """)

st.markdown("---")

# ============================================================================
# GRAFICI COMPARATIVI
# ============================================================================

st.subheader(" Analisi Comparativa")

tab1, tab2 = st.tabs([" Confronto Utili", " Proiezione Mensile"])

with tab1:
    # Grafico a barre confronto utili
    fig_confronto = go.Figure()
    
    fig_confronto.add_trace(go.Bar(
        name='Affitto Breve',
        x=['Ricavi Mensili', 'Costi Mensili', 'Utile Netto'],
        y=[fatturato_netto, costo_gestione + costo_pulizie + costo_biancheria + spese_fisse_mensili, utile_netto_pretax],
        marker_color='#1f77b4',
        text=[f"€{fatturato_netto:,.0f}", 
              f"€{(costo_gestione + costo_pulizie + costo_biancheria + spese_fisse_mensili):,.0f}",
              f"€{utile_netto_breve:,.0f}"],
        textposition='outside'
    ))
    
    fig_confronto.add_trace(go.Bar(
        name='Affitto Tradizionale',
        x=['Ricavi Mensili', 'Costi Mensili', 'Utile Netto'],
        y=[ricavi_tradizionale, costi_tradizionale + tasse_tradizionale, utile_netto_tradizionale],
        marker_color='#ff7f0e',
        text=[f"€{ricavi_tradizionale:,.0f}", 
              f"€{(costi_tradizionale + tasse_tradizionale):,.0f}",
              f"€{utile_netto_tradizionale:,.0f}"],
        textposition='outside'
    ))
    
    fig_confronto.update_layout(
        title="Confronto Finanziario Mensile",
        barmode='group',
        height=500,
        yaxis_title="Euro (€)",
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_confronto, use_container_width=True)
    
    if differenza_utile > 0:
        st.success(f"""
         **L'affitto breve genera € {differenza_utile:,.0f} in più al mese** 
        rispetto all'affitto tradizionale ({percentuale_guadagno:+.1f}% in più)
        """)
    else:
        st.warning(f"""
        ⚠️ **L'affitto tradizionale sarebbe più conveniente** di € {abs(differenza_utile):,.0f} al mese
        ({percentuale_guadagno:.1f}% in meno con affitto breve)
        """)



with tab2:
    # Proiezione mensile
    mesi = ['Gen', 'Feb', 'Mar', 'Apr', 'Mag', 'Giu', 'Lug', 'Ago', 'Set', 'Ott', 'Nov', 'Dic']
    
    utile_mensile_breve_y = utile_netto_breve 
    utile_mensile_trad = utile_netto_tradizionale
    
    # Cumulativo
    cumulativo_breve = [utile_mensile_breve_y * (i+1) for i in range(12)]
    cumulativo_trad = [utile_mensile_trad * (i+1) for i in range(12)]
    
    fig_proiezione = go.Figure()
    
    fig_proiezione.add_trace(go.Scatter(
        x=mesi,
        y=cumulativo_breve,
        name='Affitto Breve',
        mode='lines+markers',
        line=dict(color='#1f77b4', width=3),
        fill='tonexty',
        hovertemplate='€%{y:.1f}<extra></extra>'  
    ))

    fig_proiezione.add_trace(go.Scatter(
        x=mesi,
        y=cumulativo_trad,
        name='Affitto Tradizionale',
        mode='lines+markers',
        line=dict(color='#ff7f0e', width=3),
        fill='tozeroy',
        hovertemplate='€%{y:.1f}<extra></extra>'  
    ))
    
    fig_proiezione.update_layout(
        title="Accumulo Utile Netto nell'Anno",
        xaxis_title="Mese",
        yaxis_title="Utile Cumulativo (€)",
        height=500,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_proiezione, use_container_width=True)
    
    st.info(f"""
    **Utili mensili medi:**
    - Affitto Breve: € {utile_netto_breve:,.0f}/mese
    - Affitto Tradizionale: € {utile_netto_tradizionale:,.0f}/mese
    - Differenza: € {(utile_netto_breve- utile_netto_tradizionale):,.0f}/mese

   
""")

# ============================================================================
# NOTE E DISCLAIMER
# ============================================================================

st.markdown("---")
st.markdown("###  Note Importanti")

with st.expander("ℹ️ Clicca per leggere le note sul calcolo"):
    st.markdown("""
    **Affitto Breve:**
    - La gesione prevede che gli incassi ed i pagamenti siano gestiti da DREAMNEST
    - DREAMNEST riconosce un canone di locazione nettato dei costi dell'attività
    - Le tasse dipendono dal tuo scaglione IRPEF
    
    **Affitto Tradizionale:**
    - Si assume cedolare secca o IRPEF marginale come indicato
    - Il condominio e le utenze sono generalmente a carico dell'inquilino
    - Rischio di morosità e periodi di vuoto non considerati
    
    **Assunzioni:**
    - I prezzi e i tassi di occupazione sono stime e possono variare
    - La stagionalità può influenzare significativamente i risultati
    - I costi di manutenzione straordinaria non sono inclusi
    - La gestione professionale riduce il tempo/stress del proprietario
    """)

# Footer
st.markdown("---")
st.caption(" Analisi generata il " + datetime.now().strftime("%d/%m/%Y alle %H:%M"))
