import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.collections import LineCollection
import streamlit.components.v1 as components
import matplotlib

# Pakotetaan matplotlib käyttämään 'Agg'-backendia (tärkeä pilvipalveluissa)
matplotlib.use('Agg')

# 1. Poistetaan ylämarginaali ja optimoidaan tila
st.markdown("""
    <style>
        /* Poistaa tyhjän tilan sivun yläreunasta */
        .block-container {
            padding-top: 0rem;
            padding-bottom: 0rem;
            margin-top: -5rem; /* Nostaa sisältöä ylöspäin */
        }
        /* Piilottaa Streamlitin oman yläpalkin jos haluat */
        # header {visibility: hidden;}
        /* Siirtää sisällön vasempaan reunaan */
        .main .block-container {
            max-width: 95%;
            padding-left: 2rem;
            margin-left: 0;
        }
        /* Poistaa soittimen ympäriltä turhia reunoja */
        iframe {
            display: block;
            margin-left: 0;
        }
    </style>
""", unsafe_allow_html=True)
st.set_page_config(layout="wide")

st.title("🛰️ Neon Spirograph")

# --- ASETUKSET (Määrittele nämä koodin yläosassa) ---
frames_lkm = 350       # Kuinka monta kuvaa lasketaan (pituus)
aikakerroin = 0.035    # Kuinka paljon aika siirtyy per kuva (tarkkuus)
interval_ms = 30       # Kuinka monta millisekuntia kuvien välillä on (nopeus)

# --- 1. SIDEBAR-SÄÄTIMET (Määritellään muuttujat ennen käyttöä) ---
st.sidebar.header("Parameters")
R = st.sidebar.slider("Main Circle Radius (R)", 0.5, 2.0, 1.2)
r_sis = st.sidebar.slider("Inner Circle Radius", 0.1, 1.0, 0.5)
r_ulk = st.sidebar.slider("Outer Circle Radius", 0.1, 1.5, 0.8)
aalto_amp = st.sidebar.slider("Wave Amplitude", 0.0, 2.0, 1.0)
aalto_freq = st.sidebar.slider("Wave Frequency", 0.1, 3.0, 1.2)
keltainen_vauhti = st.sidebar.slider("Yellow Tracer Speed", 1.0, 20.0, 10.0)

# Kiinteät parametrit
d_sis, d_ulk = 0.4, 0.7
aikakerroin = 0.035 # alkuperäinen 0.025
hännän_pituus = 1000 # pidennetty 300 -> 1000

# --- 2. ALUSTUS ---
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(14, 7))
ax.set_aspect('equal')
ax.grid(True, which='both', color='#444444', linestyle=':', linewidth=0.5, alpha=0.5) # ax.grid(True, which='both', color='#444444', linestyle=':', linewidth=0.5, alpha=0.5)

# 3. Säädetään numeroiden ja merkkiasteikon (ticks) väri
ax.tick_params(axis='both', colors='#888888', labelsize=10)
ax.axis('on') # oli off, kokeillaan on

# Luodaan artistit (kuten aiemmin)
iso_kehä, = ax.plot([], [], color='#96D7FF', lw=1.0)
sisä_kehä, = ax.plot([], [], color='white', lw=1.2, ls='--', alpha=0.9)
ulko_kehä, = ax.plot([], [], color='white', lw=1.2, alpha=0.5)
iso_rata, = ax.plot([], [], color='#00FFFF', lw=2.0, ls='--', alpha=0.6)
ulko_jälki, = ax.plot([], [], color='#FFD700', lw=1.0)
sisä_jälki_coll = LineCollection([], cmap='Reds', lw=2.5)
ax.add_collection(sisä_jälki_coll)
piste_iso, = ax.plot([], [], 'o', color='#00FFFF', markersize=6)
varsi_sisä, = ax.plot([], [], color='#FF3333', ls=':', lw=1.0)
varsi_ulko, = ax.plot([], [], color='#FFD700', ls=':', lw=1.0)
piste_sisä, = ax.plot([], [], 'ro', markersize=5)
piste_ulko, = ax.plot([], [], 'o', color='#FFD700', markersize=5)

# Säilöt datalle
x_mid_t, y_mid_t = [], []
x_sis_t, y_sis_t = [], []
x_ulko_t, y_ulko_t = [], []

# --- 3. UPDATE-FUNKTIO ---
def update(frame):
    # Käytetään parametreja, jotka on määritelty yläpuolella
    t = frame * aikakerroin
    cx_i = R * t
    cy_i = R + aalto_amp * np.sin(aalto_freq * t)
    
    # Laskenta (sama kuin aiemmin)
    off_s = R - r_sis
    cx_s, cy_s = cx_i + off_s * np.sin(t), cy_i + off_s * np.cos(t)
    px_s = cx_s + d_sis * np.cos(-(R/r_sis) * t)
    py_s = cy_s + d_sis * np.sin(-(R/r_sis) * t)
    
    off_u = R + r_ulk
    cx_u, cy_u = cx_i + off_u * np.sin(t), cy_i + off_u * np.cos(t)
    px_u = cx_u + d_ulk * np.cos(keltainen_vauhti * t)
    py_u = cy_u + d_ulk * np.sin(keltainen_vauhti * t)
    
    # Datan päivitys
    x_mid_t.append(cx_i); y_mid_t.append(cy_i)
    x_sis_t.append(px_s); y_sis_t.append(py_s)
    x_ulko_t.append(px_u); y_ulko_t.append(py_u)
    
    if len(x_mid_t) > hännän_pituus:
        for l in [x_mid_t, y_mid_t, x_sis_t, y_sis_t, x_ulko_t, y_ulko_t]: l.pop(0)

    # Piirto-objektien päivitys
    theta = np.linspace(0, 2*np.pi, 50)
    iso_kehä.set_data(cx_i + R*np.cos(theta), cy_i + R*np.sin(theta))
    sisä_kehä.set_data(cx_s + r_sis*np.cos(theta), cy_s + r_sis*np.sin(theta))
    ulko_kehä.set_data(cx_u + r_ulk*np.cos(theta), cy_u + r_ulk*np.sin(theta))
    iso_rata.set_data(x_mid_t, y_mid_t)
    ulko_jälki.set_data(x_ulko_t, y_ulko_t)
    varsi_sisä.set_data([cx_s, px_s], [cy_s, py_s])
    varsi_ulko.set_data([cx_u, px_u], [cy_u, py_u])
    piste_sisä.set_data([px_s], [py_s])
    piste_ulko.set_data([px_u], [py_u])
    piste_iso.set_data([cx_i], [cy_i])
    
    if len(x_sis_t) > 2:
        points = np.array([x_sis_t, y_sis_t]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
        sisä_jälki_coll.set_segments(segments)
        sisä_jälki_coll.set_array(np.linspace(0, 1, len(segments)))

    ax.set_xlim (-2, 25) # (cx_i - 15, cx_i + 4)
    ax.set_ylim(-3, 7)
    # Asetetaan näkyvä ruudukko
    ax.grid(True, which='both', color='#555555', linestyle='--', linewidth=0.5)
    # Varmistetaan, että ruudukko on piirrosten takana (zorder)
    ax.set_axisbelow(True) 
    
    # Akselien rajat kuvakaappauksen perusteella (0 -> 25)
    ax.set_xlim(-2, 25)
    ax.set_ylim(-3, 7)
    
    return iso_kehä, sisä_kehä, ulko_kehä, iso_rata, ulko_jälki, sisä_jälki_coll, varsi_sisä, varsi_ulko, piste_sisä, piste_ulko, piste_iso

# --- 4. ANIMAATION GENERONTIA ---
# Pienennetään frames määrää ja lisätään nappula
with st.sidebar:
    render_button = st.button("🚀 Render Animation")

if render_button:
    with st.spinner("Generating high-quality animation..."):
        # 150 framea riittää nyt kattamaan pitkän matkan, koska aikakerroin on suurempi
        ani = FuncAnimation(fig, update, frames=frames_lkm, interval=interval_ms, blit=True)
        # JSHTML-soitin tarvitsee tilaa napeille, pidetään height korkeana
        components.html(ani.to_jshtml(), height=800, width=1200)
else:
    st.write("### Start: adjust the sliders and press Render")
    # Näytetään vaikka staattinen kuva alkajaisiksi
    update(0)
    st.pyplot(fig)
