import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import matplotlib.pyplot as plt
from models.biosphere import forward_euler
from utils import load_emissions, load_concentrations, to_ppm

# -----------------------------------------------------------------------------
# Ladda data
# -----------------------------------------------------------------------------
years, emissions = load_emissions()
_, concentrations = load_concentrations()

# -----------------------------------------------------------------------------
# Task 1: Kör biosfärmodellen och jämför med RCP45-koncentrationer
# -----------------------------------------------------------------------------
b1, b2, b3 = forward_euler(beta=0.35, u=emissions)

# Bygg tidsserie som matchar b1 (ett år längre än emissions pga startvärde)
model_years = list(range(years[0], years[0] + len(b1)))
b1_ppm = to_ppm(b1)

plt.figure()
plt.plot(model_years, b1_ppm, color="r", label="Modell (endast biosfär)")
plt.plot(years, concentrations, color="g", label="RCP45 koncentrationsdata")
plt.xlabel("År")
plt.ylabel("CO2-koncentration (ppm)")
plt.title("Task 1: Atmosfärisk CO2 — modell vs data")
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()

# Förväntat resultat: modellen överskattar koncentrationen eftersom havsupptag
# saknas. Havet absorberar en betydande andel av antropogena utsläpp varför avsaknad
# av dettas effekt på ustläppen medför högre koncentrationer av CO2 i atmosfären. 

# -----------------------------------------------------------------------------
# Task 2: Testa olika beta-värden
# -----------------------------------------------------------------------------
betas = [0.1, 0.35, 0.8]

fig, axes = plt.subplots(1, 3, figsize=(14, 4))
titles = ["Atmosfär B1 (ppm)", "Biomassa B2 (GtC)", "Mark B3 (GtC)"]

for beta in betas:
    b1, b2, b3 = forward_euler(beta=beta, u=emissions)
    model_years = list(range(years[0], years[0] + len(b1)))
    axes[0].plot(model_years, to_ppm(b1), label=f"β = {beta}")
    axes[1].plot(model_years, b2, label=f"β = {beta}")
    axes[2].plot(model_years, b3, label=f"β = {beta}")

axes[0].plot(years, concentrations, "k--", label="RCP45 data")

for ax, title in zip(axes, titles):
    ax.set_title(title)
    ax.set_xlabel("År")
    ax.legend()
    ax.grid()

plt.suptitle("Task 2: Effekt av CO2-gödslingsparameter β")
plt.tight_layout()
plt.show()

# Förväntat resultat:
#   Högre β → mer fotosyntes per extra CO2-enhet → mer kol binds i B2 och B3
#   → lägre B1. Lägre β ger motsatt effekt — biosfären absorberar mindre.