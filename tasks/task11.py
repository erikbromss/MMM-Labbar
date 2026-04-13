import sys
import os
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, "models"))

from utils import load_emissions, to_ppm, load_nasa_giss, load_radiative_forcing
from models.biosphere_and_oceans import combined_ocean_biosphere
from models.energy_balance import rf
from task10 import energybalance
from task9 import other_aerosol_total_rf as rftot

import numpy as np
import matplotlib.pyplot as plt

# Ladda utsläpp och år, samt filtrera ut datan
# till intervallet 1765 -> 2024

years, emissions = load_emissions()
filtered_years = [y for y in years if 1765 <= y <= 2024]
filtered_emissions = emissions[:len(filtered_years)]

m_atm, _, _ = combined_ocean_biosphere(filtered_years, filtered_emissions)

konc_co2_modell = to_ppm(m_atm)

rfdf = load_radiative_forcing()

rf_c02 = np.array([rf(x) for x in konc_co2_modell])
rf_aerosol_and_other = np.array(rftot(rfdf)[:len(filtered_years)])
rf_total = rf_c02 + rf_aerosol_and_other

dT1, dT2 = energybalance(rf_total)
dT1 = dT1[1:]

# plot(filtered_years, dT1) = model global mean temp increase from 1765 -> 2024

start_idx = filtered_years.index(1951)
end_idx = filtered_years.index(1980)

ref_period_temps = dT1[start_idx : end_idx + 1]
medel_ref = np.mean(ref_period_temps)

dT1_adjusted = dT1 - medel_ref

nasa_data = load_nasa_giss()
nasa_years = nasa_data['Land-Ocean Temperature Index (C)'][1:].tolist()
nasa_temps = nasa_data['Unnamed: 1'][1:].tolist()

nasa_start_idx = nasa_years.index('1880')
nasa_end_idx = nasa_years.index('2019')

filtered_nasa_temps = nasa_temps[nasa_start_idx : nasa_end_idx + 1]
filtered_nasa_years = nasa_years[nasa_start_idx : nasa_end_idx + 1]

filtered_nasa_temps = [float(y) for y in filtered_nasa_temps]
filtered_nasa_years = [int(y) for y in filtered_nasa_years]

#print(len(filtered_nasa_temps)) = 140

model_start_idx = filtered_years.index(1880)
model_end_idx = filtered_years.index(2019)

filtered_model_temps = dT1_adjusted[model_start_idx : model_end_idx + 1]

print(len(filtered_nasa_temps), len(filtered_model_temps), len(filtered_nasa_years))

fig, axs = plt.subplots(1, 2, figsize = (12, 6))
axs[0].plot(filtered_years, dT1_adjusted, label = 'Model MGSTI')
axs[0].set_title('MGSTI (1765-2024) Relative Mean 1951-1980')
axs[0].set_ylabel('Temperature Increase (Celsius)')
axs[0].set_xlabel('Year')
axs[0].grid()
axs[0].legend()

axs[1].plot(filtered_nasa_years, filtered_nasa_temps, label = 'NASA temperature anomalies')
axs[1].plot(filtered_nasa_years, filtered_model_temps, label = 'Model temperatures')
axs[1].set_title('Model vs. NASA: MGSTI (1880-2019) Relative Mean 1951-1980')
axs[1].set_ylabel('Temperature Increase (Celsius)')
axs[1].set_xlabel('Year')
axs[1].grid()
axs[1].legend()

plt.tight_layout()
plt.show()

# --- 11a) --- 

# Referensperioden bestämmer nollpunkten för 
# temperaturanomalin. Du subtreherar medelvärdet av 
# den perioden från hela tidsserien. Det förskjuter hela kurvan vertikalt 
# utan att ändra trenden eller formen. Om man väljer en varm 
# referensperiod, ex 1981-2010 ser tidigare temperaturer låga ut och den totala 
# uppvärmningen ser mindre ut. Väljer du istället en kall period ser uppvärmningen större ut. 
# Därmed vill man välja "pre-industrial times" som referensperiod om målet är att analysera 
# utvecklingen sedan den tidsperioden

# --- 11b) ---

lambdas = [0.5, 0.8, 1.3] 
scalars = [0.5, 1, 2]
kappas = [0.2, 0.5, 1.0]

color_map = {0.5: 'steelblue', 1.0: 'darkorange', 2.0: 'green'}
ls_map    = {0.2: 'solid',     0.5: 'dashed',     1.0: 'dotted'}

fig, axs = plt.subplots(1, 3, figsize=(18, 5), sharey=True)

best = {}

for i, lam in enumerate(lambdas):

    best_rmse = np.inf
    best_params = None
    
    for s in scalars:
        for k in kappas:
            rf_aerosol_and_other = np.array(rftot(rfdf, s)[:len(filtered_years)])
            rf_total = rf_c02 + rf_aerosol_and_other

            T1, _ = energybalance(rf_total, lam=lam, k=k)
            T1 = np.array(T1[1:])

            medel_ref = np.mean(T1[start_idx : end_idx + 1])
            T1_adj    = T1 - medel_ref
            T1_plot   = T1_adj[model_start_idx : model_end_idx + 1]

            nasa_arr = np.array(filtered_nasa_temps, dtype=float)
            rmse = np.sqrt(np.mean((T1_plot - nasa_arr)**2))

            if rmse < best_rmse:
                best_rmse = rmse
                best_params = (s, k)


            axs[i].plot(filtered_nasa_years, T1_plot, color=color_map[s], linestyle=ls_map[k], linewidth=0.9, label=f's={s}, κ={k}')

    best[lam] = (best_params, best_rmse)
    print(f"λ={lam}: bästa s={best_params[0]}, κ={best_params[1]}, RMSE={best_rmse:.4f}")

    axs[i].plot(filtered_nasa_years, filtered_nasa_temps,
                color='black', linewidth=1,
                linestyle='solid', label='NASA', zorder=10)

    axs[i].set_title(f'λ = {lam} K·W⁻¹·m²')
    axs[i].set_xlabel('År')
    axs[i].grid(True, alpha=0.4)

axs[0].set_ylabel('Temperaturanomali (°C)')

# Gemensam legend utanför subplotsen
handles, labels = axs[0].get_legend_handles_labels()
plt.legend(handles, labels,
           loc='upper left', ncol=3, fontsize=10)

fig.suptitle('11b): MGSTI — modell vs NASA för olika λ, s och κ (gemensam legend)')
plt.tight_layout()
plt.show()

# --- 11c) ---

# Det är möjligt såklart, men försvåras
# markant (kan jag tänka mig) av att parametrarna är 
# sammanflätade, eller co-dependent på varandra. 
# Vi såg ex. i 11b) att olika kombinationer av lambda, kappa och s
# kan ge väldigt lika data, näranpassad till NASA-datan. 
# Sammanflätningen tycks ju logiskt: 
# ett högt lambda (mycket uppvärmning) kan kompenseras med
# lågt s (aerosoler kyler) eller med ett högt kappa, dvs djuphavet
# absorberar mer. 
# Omvändningen blir att lågt lambda kan kompenseras med högt s
# och lågt k. 
# Parametrarna är antagligen inte identifierbara från endast temperaturdata.
# Hade vi haft mer observationsdata, typ tusentals år snarare än 140, 
# hade vi kanske kunat separera kappa och lambda. Nu fångar vi inte
# upp mycket av de långsamma dynamikerna. 
# Dessutom tar vår modell inte in något brus som NASA datan. 
# Där finns variabilitet i temperaturförändring från saker som vulkanutbrott
# eller annat som vår modell inte tar hänsyn till. 

# Om man skulle ta en bayesiansk approach och använda flera observationer simultant, 
# ex yttemperatur + havsvärmeinnehåll (kappa känsligt) + strålningsdata
# från sattelit (känsligt för lambda) och atmosfäriska aerosolkoncentrationer (för s)
# så kan man nog få en hygglig skattning av varje enskild parameter. 
# Man kombinerar prior fördelningar (modeller etc.) för respektive parameter
# och likelihood från faktiska observationer för att 
# få smalare posteriorfördelningar, men enda såklart innehåller även dessa
# en viss osäkerhet. 









