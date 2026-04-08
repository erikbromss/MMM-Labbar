import sys
import os
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, "models"))
 
import numpy as np
import matplotlib.pyplot as plt
 
from utils import load_emissions, load_radiative_forcing, to_ppm
from models.biosphere_and_oceans import combined_ocean_biosphere
from models.energy_balance import rf
from task9 import other_aerosol_total_rf
from task10 import energybalance

# =================================================

# Parametrar: De bästa vi fick för lambda = 0.8
# var kappa = 1, s = 1. Kunde ju testat fler värden för ännu bättre fit
# säkert men nu gör vi så här. 

LAM = 0.8
K = 1
S = 1

# Referensperiod - samma som NASA
ref_start = 1951
ref_end = 1980

# modellens tidsgränser 
hist_start = 1765
hist_end = 2024
future_end = 2200

# ===================================================
# LADDA DATA
# ===================================================

years, emissions = load_emissions()

hist_years = [y for y in years if hist_start <= y <= hist_end]
hist_emissions = emissions[:len(hist_years)]

rfdf = load_radiative_forcing()

rf_other_full = other_aerosol_total_rf(rfdf, S)
rf_other_years = rfdf['Time (year)'].tolist()

def get_rf_other(year_list):
    """Plockar ut rf_other för en given lista av år"""
    idx = [rf_other_years.index(y) for y in year_list]
    return np.array([rf_other_full[i] for i in idx])


# ===================================================
# Bygg upp olika utsläpps-scenarios
# ===================================================

emission_2024 = 10.59522 #hämtat ur utsläppCSV direkt

future_years = list(range(hist_end + 1, future_end + 1)) # 2025-2200
n_future = len(future_years)

def build_scenario(future_years, emission_2024):
    """Returnerar de tre utsläppscenarios som arrays med koncentrationsnivåer"""

    n = len(future_years)
    
    s1 = np.zeros(n) #scenario 1: linjär minskning -> noll -> negativ -> konstant
    s2 = np.zeros(n) #scenario 2: konstant
    s3 = np.zeros(n) #scenario 3: linjär ökning -> konstant

    idx_2070 = future_years.index(2070) # noll utsläpp då i scenario 1 
    idx_2100 = future_years.index(2100) # tak scenario 3, konstant scenario 1 

    rate1 = emission_2024 / (2070 - hist_end) # linkär minskning
    rate3 = emission_2024 / (2100 - hist_end)

    for j, y in enumerate(future_years):

        #scenario 1:
        if y <= 2070:
            s1[j] = emission_2024 - rate1 * (y - hist_end)
        elif y <= 2100:
            s1[j] = - rate1 * (y-2070)
        else:
            #konstant post 2100
            s1[j] = s1[future_years.index(2100)]
        
        # --- Scenario ii ---
        s2[j] = emission_2024
 
        # --- Scenario iii ---
        if y <= 2100:
            s3[j] = emission_2024 + rate3 * (y - hist_end)
        else:
            s3[j] = 2 * emission_2024
 
    return s1, s2, s3
 
s1, s2, s3 = build_scenario(future_years, emission_2024)



def run_scenario(hist_years, hist_emissions, future_years, future_emissions):
    """
    Kör combined_ocean_biosphere och energybalance för hela perioden
    1765 → FUTURE_END.
 
    Returns:
        all_years, dT1_adj
    """
    all_years = hist_years + future_years
    all_emissions = list(hist_emissions) + list(future_emissions)
 
    # Kolcykelmodell
    m_atm, _, _ = combined_ocean_biosphere(all_years, all_emissions)
    konc = to_ppm(m_atm) 
 
    # Radiativ forcing CO2
    rf_co2 = np.array([rf(c) for c in konc])
 
    rf_other = get_rf_other(all_years)
 
    rf_total = rf_co2 + rf_other
 
    # Energibalansmodell
    dT1, _ = energybalance(rf_total, lam=LAM, k=K)
    dT1 = np.array(dT1[1:])  # trimma startvärde
 
    # Justera relativt referensperioden 1951–1980
    ref_s = all_years.index(ref_start)
    ref_e = all_years.index(ref_end)
    dT1_adj = dT1 - np.mean(dT1[ref_s : ref_e + 1])
 
    return all_years, dT1_adj

years1, dT1_1 = run_scenario(hist_years, hist_emissions, future_years, s1)
years2, dT1_2 = run_scenario(hist_years, hist_emissions, future_years, s2)
years3, dT1_3 = run_scenario(hist_years, hist_emissions, future_years, s3)

# =====================================================
# Plotta utsläpps-scenarios samt temperaturprojektioner
# över (1765 - 2100)
# =====================================================

fig, axs = plt.subplots(1, 2, figsize = (14, 5))

# kör utsläpp i vänster plot
axs[0].plot(hist_years, [emission_2024] * len(hist_years), color = 'gray', linewidth = '0.8', linestyle = 'dashed', label = 'Historiska Usläpp (konstant ref.)')
axs[0].plot(future_years, s1, color = 'steelblue', label = 'Scenario 1')
axs[0].plot(future_years, s2, color = 'darkorange', label = 'Scenario 2')
axs[0].plot(future_years, s3, color = 'firebrick', label = 'Scenario 3')
axs[0].axhline(0, color = 'black', linewidth = 0.5, linestyle = '--')
axs[0].set_xlabel('År')
axs[0].set_ylabel('CO₂-utsläpp (GtC/år)')
axs[0].set_title('Utsläppsscenarier 2025-2200')
axs[0].legend(fontsize=8)
axs[0].grid(True, alpha=0.4)

# kör temperatur i höger plot 

axs[1].plot(years1, dT1_1, color = 'steelblue', label = 'Scenario 1')
axs[1].plot(years2, dT1_2, color = 'darkorange', label = 'Scenario 2')
axs[1].plot(years3, dT1_3, color = 'firebrick', label = 'Scenario 3')
axs[1].axhline(1.5, color='black', linewidth=0.8, linestyle='--', label='1.5°C (Paris)')
axs[1].axhline(2.0, color='black', linewidth=0.8, linestyle=':',  label='2.0°C (Paris)')
axs[1].axvline(2100, color='gray', linewidth=0.6, linestyle='--')
axs[1].set_xlabel('År')
axs[1].set_ylabel('Temperaturanomali (°C, relativt 1951–1980)')
axs[1].set_title('Temperaturprojektioner 1765–2200 (λ=0.8)')
axs[1].legend(fontsize=8)
axs[1].grid(True, alpha=0.4)

plt.suptitle('12a): C02-scenarerier och temperaturprojektioner')
plt.tight_layout()
plt.show()

# skriv ut tempen år 2100 för varje scenario
for name, ys, dT in [('1', years1, dT1_1), ('2', years2, dT1_2), ('3', years3, dT1_3)]:
    idx2100 = ys.index(2100)
    print(f'Scenario {name}: dT år 2100 = {dT[idx2100]:.2f} grader Celsius')

