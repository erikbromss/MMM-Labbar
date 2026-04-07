import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import matplotlib.pyplot as plt
from utils import load_emissions, load_concentrations, to_ppm
from models.biosphere_and_oceans import combined_ocean_biosphere
years, emissions = load_emissions()
_, concentrations = load_concentrations()

m_atm, b2_biomass, b3_soil = combined_ocean_biosphere(years, emissions)

# Task 6: Beräkna C02-koncentrationerna från utsläppRCP45 via kombinerad
# biosfär + hav + atmosfär modell. 
# Jämför sedan modellens koncentrationer med de i koncentrationerRCP45
# och justera beta så att modellen stämmer hyggligt med datan

konc_atm_modell = to_ppm(m_atm) #koncentrationer från kolinnehåll från modell körd på utsläppRCP45 (se utils)


plt.figure()
plt.plot(years, konc_atm_modell, label = 'Model C02-concentration in Atmosphere')
plt.plot(years, concentrations, label = 'Reference C02-concentration data (RCP45)')
plt.grid(True)
plt.xlabel('Year')
plt.ylabel('Atmospheric C02 Concentration (ppm)')
plt.title('Ocean/Biosphere Model: Atmospheric C02 Concentration Comparison')
plt.legend() 
plt.show()



