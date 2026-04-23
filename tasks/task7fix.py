import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import sys
import os

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, "models"))

from models.biosphere import B1_0, B2_0, B3_0
from models.biosphere_and_oceans import combined_ocean_biosphere

from utils import load_emissions, load_concentrations, to_ppm

years, emissions = load_emissions()
_, concentrations = load_concentrations()

# Basfall och scenarion för beta och k
beta_base = 0.35
k_base = 3.06e-3

beta_scenarios = [beta_base * 0.5, beta_base, beta_base * 2]
beta_labels    = ['β = 0.175 (halverat)', 'β = 0.35 (basfall)', 'β = 0.70 (dubblerat)']

k_scenarios = [k_base * 0.5, k_base, k_base * 2]
k_labels    = ['k = 0.00153 (halverat)', 'k = 0.00306 (basfall)', 'k = 0.00612 (dubblerat)']

# Pre-industriella referensvärden för att visa förändring [GtC]
M0_atm  = B1_0    # 600 GtC atmosfär
M0_bio  = B2_0    # 600 GtC biomassa
M0_mark = B3_0    # 1500 GtC mark


def compute_ocean_stock(m_atmos, u_eff_cumulative):
    """
    Havets kolinnehåll = kumulativa effektiva utsläpp som INTE finns kvar i atmosfären.
    M_ocean(t) = sum(u_eff[0..t]) - (m_atmos(t) - M0_atm)
    """
    return u_eff_cumulative - (m_atmos - M0_atm)


def run_scenario(beta, k):
    """Kör modellen och returnerar tidsserier för alla fyra reservoarer [GtC]."""
    m_atm, b2, b3 = combined_ocean_biosphere(years, emissions, beta=beta, k=k)

    # Rekonstruera u_eff (nödvändigt för havets kolinnehåll)
    # Lättast: hav = kumulativa effektiva utsläpp - atmosfärs-ökning
    # Kumulativa effektiva utsläpp ≈ kumulativa antropogena utsläpp - nettoupptagning i biosfären
    # Men biosfärens nettoupptagning = (B2+B3 - B2_0 - B3_0) förändring, dvs:
    # Netto_bio_kum(t) = (b2[t] - B2_0) + (b3[t] - B3_0)
    # => u_eff_kum(t) = kum_antro(t) - netto_bio_kum(t)
    kum_antro   = np.cumsum(emissions)
    delta_bio   = (b2 - B2_0) + (b3 - B3_0)   # totalt nettoupptag i biosfären [GtC]
    u_eff_kum   = kum_antro - delta_bio

    m_ocean = compute_ocean_stock(m_atm, u_eff_kum)

    return m_atm, b2, b3, m_ocean


# ── Figur 1: Absoluta kolmängder, basfall ──────────────────────────────────────
m_atm, b2, b3, m_ocean = run_scenario(beta_base, k_base)

fig0, axes0 = plt.subplots(2, 2, figsize=(13, 9))
fig0.suptitle('Kolinnehåll i de fyra reservoarerna — basfall (β=0.35, k=0.00306)', fontsize=13)

ax = axes0[0, 0]
ax.plot(years, m_atm, color='steelblue')
ax.axhline(M0_atm, color='gray', linestyle='--', alpha=0.6, label='Pre-industriellt')
ax.set_title('Atmosfär (Box 1)')
ax.set_ylabel('Kolinnehåll [GtC]')
ax.legend()
ax.grid(True)

ax = axes0[0, 1]
ax.plot(years, b2, color='forestgreen')
ax.axhline(M0_bio, color='gray', linestyle='--', alpha=0.6, label='Pre-industriellt')
ax.set_title('Biomassa ovan mark (Box 2)')
ax.set_ylabel('Kolinnehåll [GtC]')
ax.legend()
ax.grid(True)

ax = axes0[1, 0]
ax.plot(years, b3, color='saddlebrown')
ax.axhline(M0_mark, color='gray', linestyle='--', alpha=0.6, label='Pre-industriellt')
ax.set_title('Mark / rötter (Box 3)')
ax.set_ylabel('Kolinnehåll [GtC]')
ax.set_xlabel('År')
ax.legend()
ax.grid(True)

ax = axes0[1, 1]
ax.plot(years, m_ocean, color='navy')
ax.axhline(0, color='gray', linestyle='--', alpha=0.6, label='Pre-industriellt (0 extra GtC)')
ax.set_title('Hav (kumulativt nettoupptag)')
ax.set_ylabel('Extra kolinnehåll [GtC]')
ax.set_xlabel('År')
ax.legend()
ax.grid(True)

plt.tight_layout()
plt.savefig('task7_basfall_absolut.png', dpi=150)
plt.show()


# ── Figur 2: Känslighetsanalys beta — förändring relativt pre-industriellt ─────
fig1, axes1 = plt.subplots(2, 2, figsize=(13, 9))
fig1.suptitle('Känslighetsanalys: β  (k = basfall)\nFörändring relativt pre-industriellt [GtC]', fontsize=13)
colors = ['tab:orange', 'tab:blue', 'tab:green']

for beta, label, color in zip(beta_scenarios, beta_labels, colors):
    m_atm, b2, b3, m_ocean = run_scenario(beta, k_base)
    axes1[0, 0].plot(years, m_atm  - M0_atm,  label=label, color=color)
    axes1[0, 1].plot(years, b2     - M0_bio,  label=label, color=color)
    axes1[1, 0].plot(years, b3     - M0_mark, label=label, color=color)
    axes1[1, 1].plot(years, m_ocean,           label=label, color=color)

titles  = ['Atmosfär (Box 1)', 'Biomassa ovan mark (Box 2)',
           'Mark / rötter (Box 3)', 'Hav (kumulativt nettoupptag)']
ylabels = ['ΔKolinnehåll [GtC]'] * 4

for i, (ax, title) in enumerate(zip(axes1.flat, titles)):
    ax.set_title(title)
    ax.set_ylabel(ylabels[i])
    ax.set_xlabel('År')
    ax.axhline(0, color='gray', linestyle='--', alpha=0.5)
    ax.legend(fontsize=8)
    ax.grid(True)

plt.tight_layout()
plt.savefig('task7_kanslighetsbeta.png', dpi=150)
plt.show()


# ── Figur 3: Känslighetsanalys k — förändring relativt pre-industriellt ────────
fig2, axes2 = plt.subplots(2, 2, figsize=(13, 9))
fig2.suptitle('Känslighetsanalys: k  (β = basfall)\nFörändring relativt pre-industriellt [GtC]', fontsize=13)

for k_val, label, color in zip(k_scenarios, k_labels, colors):
    m_atm, b2, b3, m_ocean = run_scenario(beta_base, k_val)
    axes2[0, 0].plot(years, m_atm  - M0_atm,  label=label, color=color)
    axes2[0, 1].plot(years, b2     - M0_bio,  label=label, color=color)
    axes2[1, 0].plot(years, b3     - M0_mark, label=label, color=color)
    axes2[1, 1].plot(years, m_ocean,           label=label, color=color)

for ax, title in zip(axes2.flat, titles):
    ax.set_title(title)
    ax.set_ylabel('ΔKolinnehåll [GtC]')
    ax.set_xlabel('År')
    ax.axhline(0, color='gray', linestyle='--', alpha=0.5)
    ax.legend(fontsize=8)
    ax.grid(True)

plt.tight_layout()
plt.savefig('task7_kanslighetek.png', dpi=150)
plt.show()


# ─── Förklaring av resultat ────────────────────────────────────────────────────
#
# BETA (CO2-gödslingsparameter):
#   Högt beta → biosfären binder mer kol via ökad NPP → biomassa och markboxen
#   växer snabbare → atmosfären håller mindre kol → havet behöver absorbera mindre.
#   Lågt beta → tvärtom; mindre kol binds i växtlighet → mer stannar i luften
#   och havet.
#
# K (havets mättnadskoefficient):
#   Högt k → havet mättas snabbare → impulsresponsen avtar snabbare → mer kol
#   stannar i atmosfären → atmosfärskurvan stiger brantare.
#   Lågt k → havet absorberar effektivt länge → atmosfärskurvan flackare och
#   havet samlar mer kol.
#
# BIOSFÄRENS BOXAR (B2 och B3):
#   Biomassa (B2) ökar tack vare CO2-gödsling men dämpas av ökad respiration
#   och litterfall (ALPHA_23, ALPHA_21). Mark (B3) ökar långsamt via litterfall
#   men är trögare än biomassa.
#
# JÄMFÖRELSE beta vs k:
#   Beta påverkar biosfären direkt och ger snabb divergens mellan scenarierna.
#   K styr ett kumulativt, trögare hav — skillnaderna syns tydligare sent i
#   tidshorisonten men kan inte reverseras lika lätt.