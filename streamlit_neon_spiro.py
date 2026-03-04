import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.collections import LineCollection  # TÄMÄ PUUTTUU TODENNÄKÖISESTI
import streamlit.components.v1 as components
import matplotlib

# macOS/Server-varmistus
matplotlib.use('Agg')

# Asetetaan otsikko
st.title("Neon Spirograph Simulator")

# --- PARAMETRIT (Voit nyt säätää näitä Streamlitin liukusäätimillä!) ---
R = 1.5
r_sis = st.sidebar.slider("Inner Radius", 0.1, 1.0, 0.5)
r_ulk = st.sidebar.slider("Outer Radius", 0.1, 1.5, 0.8)
keltainen_vauhti = st.sidebar.slider("Yellow Speed", 1.0, 20.0, 10.0)
aikakerroin = 0.025

# --- 2. ALUSTUS (KIRKKAAT VÄRIT) ---
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(12, 8), facecolor='black')
ax.set_facecolor('black')
ax.set_aspect('equal')
# 1. Lisätään grid (ruudukko)
ax.grid(True, which='both', color='#444444', linestyle=':', linewidth=1.0, ) #alpha=0.5)

# 2. Säädetään akseleiden viivojen väri ja paksuus (spines)
for spine in ax.spines.values():
    spine.set_edgecolor('#666666') # Harmaa akseliviiva
    spine.set_linewidth(1.5)       # Viivan paksuus

# 3. Säädetään numeroiden ja merkkiasteikon (ticks) väri
ax.tick_params(axis='both', colors='#888888', labelsize=10)
ax.axis('on') # oli off, kokeillan on

# Kehikot (Ympyrät) - Säädä näitä ohuemmiksi/vaaleammiksi tarvittaessa
iso_kehä, = ax.plot([], [], color='#96D7FF', lw=1.0, ) # alpha=0.5) 
sisä_kehä, = ax.plot([], [], color='white', lw=1.2, ls='--', alpha=0.9) 
ulko_kehä, = ax.plot([], [], color='white', lw=1.2, alpha=0.5) 

# Jäljet (Neon-värit)
iso_rata, = ax.plot([], [], color='#00FFFF', lw=2.0, ls='--', alpha=0.6) # Syaani aalto
ulko_jälki, = ax.plot([], [], color='#FFD700', lw=1.0, alpha=1.0)        # Kulta

# Punainen liukuväri
sisä_jälki_coll = LineCollection([], cmap='Reds', lw=2.5, alpha=1.0)
ax.add_collection(sisä_jälki_coll)

# --- UUDET: Varret ja Kynäpisteet ---
piste_iso, = ax.plot([], [], 'o', color='#00FFFF', markersize=7) # Syaani keskipiste
varsi_sisä, = ax.plot([], [], color='#FF3333', ls=':', lw=1.0, ) # alpha=0.7)
varsi_ulko, = ax.plot([], [], color='#FFD700', ls=':', lw=1.0, ) ## alpha=0.7)
piste_sisä, = ax.plot([], [], 'ro', markersize=5) # Punainen piste
piste_ulko, = ax.plot([], [], 'o', color='#FFD700', markersize=5) # Keltainen piste

# Säilöt
x_mid_t, y_mid_t = [], []
x_sis_t, y_sis_t = [], []
x_ulko_t, y_ulko_t = [], []

def update(frame):
    t = frame * aikakerroin
    cx_i = R * t
    cy_i = R + aalto_amp * np.sin(aalto_freq * t)
    
    # Sisäympyrä
    off_s = R - r_sis
    cx_s, cy_s = cx_i + off_s * np.sin(t), cy_i + off_s * np.cos(t)
    px_s = cx_s + d_sis * np.cos(-(R/r_sis) * t)
    py_s = cy_s + d_sis * np.sin(-(R/r_sis) * t)
    
    # Ulkoympyrä
    off_u = R + r_ulk
    cx_u, cy_u = cx_i + off_u * np.sin(t), cy_i + off_u * np.cos(t)
    px_u = cx_u + d_ulk * np.cos(keltainen_vauhti * t)
    py_u = cy_u + d_ulk * np.sin(keltainen_vauhti * t)
    
    # Tallennus
    x_mid_t.append(cx_i); y_mid_t.append(cy_i)
    x_sis_t.append(px_s); y_sis_t.append(py_s)
    x_ulko_t.append(px_u); y_ulko_t.append(py_u)
    if len(x_mid_t) > hännän_pituus:
        for l in [x_mid_t, y_mid_t, x_sis_t, y_sis_t, x_ulko_t, y_ulko_t]: l.pop(0)

    # Päivitykset: Kehät
    theta = np.linspace(0, 2*np.pi, 50)
    iso_kehä.set_data(cx_i + R*np.cos(theta), cy_i + R*np.sin(theta))
    sisä_kehä.set_data(cx_s + r_sis*np.cos(theta), cy_s + r_sis*np.sin(theta))
    ulko_kehä.set_data(cx_u + r_ulk*np.cos(theta), cy_u + r_ulk*np.sin(theta))
    
    # Päivitykset: Jäljet
    iso_rata.set_data(x_mid_t, y_mid_t)
    ulko_jälki.set_data(x_ulko_t, y_ulko_t)
    
    # Päivitykset: Varret ja Pisteet
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

    ax.set_xlim(cx_i - 10, cx_i + 10)
    ax.set_ylim(-3, 7)

    # Muista lisätä piste_iso myös return-listaan funktion loppuun:
    return iso_kehä, sisä_kehä, ulko_kehä, iso_rata, ulko_jälki, sisä_jälki_coll, varsi_sisä, varsi_ulko, piste_sisä, piste_ulko, piste_iso

# --- MUUTOS LOPPUUN: ---
# Sen sijaan että tallennat tiedostoon, palautetaan animaatio HTML-muodossa
ani = FuncAnimation(fig, update, frames=400, interval=30, blit=True)

# Muunnetaan animaatio HTML-koodiksi ja näytetään se Streamlitissä
components.html(ani.to_jshtml(), height=800)
