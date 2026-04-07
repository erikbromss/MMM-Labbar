# Task 3: Recreate plot from impulse-response functions 
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import matplotlib.pyplot as plt
import numpy as np
from models.oceans import impuls, m

from utils import load_emissions, load_concentrations, to_ppm

years, emissions = load_emissions()
_, concentrations = load_concentrations()

t = np.linspace(0, 500, 1000)
ucums = [0, 140, 560, 1680]

for u in ucums:
    y = [impuls(time, u) for time in t]
    plt.plot(t, y, label = f'{u} GtC')

plt.legend()
plt.xlabel('Tid efter Utsläppspuls (år)')
plt.ylabel('Andel kvar i atmosfären')
plt.yticks(np.arange(0, 1.1, 0.1))
plt.title('Impulsrespons för CO2 beroende på tidigare kumulativa utsläpp')
plt.show()

# --- Task 4 --- 
atm_carbon_stock = m(years, emissions)
model_concentrations = to_ppm(atm_carbon_stock)


plt.plot(years, concentrations, linestyle = '--', color = 'black', label = 'Reference RCP45 Concentrations')
plt.plot(years, model_concentrations, color = 'red', label = 'Model Concentration Levels')
plt.grid()
plt.xlabel('Year')
plt.ylabel('Atmospheric Concentration of C02 (ppm)')
plt.title('Atmospheric CO2 (ppm): Ocean-only absorbtion model vs. Reference')
plt.legend()
plt.show()


# Model curve above reference data as reference data includes absorbtion from 
# both the biosphere and the ocean, resulting in less net CO2 in the atmosphere. 
# After enough time the oceans CO2 absorbtion starts combating emissions - 
# the ocean is able to absorb a lot of C02 from the atmosphere given that 
# the concentration is high enough; a point only reached after so much time has passed 
# since the industrialisation that a significant amount of past emissions have been 
# transported to deep-sea levels by the ocean. The result is a net reduction in emissions per year
# as given by our ocean-absorbtion model. 

# --- Alternativt ---: 
# Den röda kurvan vänder nedåt eftersom vi i RCP4.5 "slutar elda" snabbare än vad havet
# hinner bli mättat. Det är havets långsamma processer (djuphavsmixning) som drar
# ner halten när de årliga utsläppen inte längre räcker till för att hålla koncentrationen uppe.
# Vi tar inte här hänsyn till mättnadseffekter från biosfären
