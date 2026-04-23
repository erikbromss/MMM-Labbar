import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import sys
import os


root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, "models"))

from models.biosphere import B1_0 # Hittas nu eftersom models/ lagts till i path
from models.biosphere_and_oceans import combined_ocean_biosphere



from utils import load_emissions, load_concentrations, to_ppm
years, emissions = load_emissions()
_, concentrations = load_concentrations()

# Have base case beta = 0.35, k = 3.06e-3 and
# look at what happens at half values and double values

beta_base = 0.35
k_base = 3.06e-3

beta_scenarios = [beta_base * 0.5, beta_base, beta_base * 2]
beta_labels = ['Halverat Beta (0.175)', 'Basfall (0.35)', 'Dubblerat Beta (0.7)']

styles = ['-', '--', ':']
k_scenarios = [k_base * 0.5, k_base, k_base * 2]
k_labels = ['Halverat K (0.0015)', 'Basfall (0.003)', 'Dubblerat K (0.006)']

fig, (ax1, ax2) = plt.subplots(1, 2, figsize = (15, 6))

# Plotta varierande Beta

for b, label in zip(beta_scenarios, beta_labels):
    m_atm, _, _ = combined_ocean_biosphere(years, emissions, beta = b, k = k_base)
    konc_atm = to_ppm(m_atm)
    ax1.plot(years, konc_atm, label = label)

ax1.plot(years, concentrations, 'k--', label = 'Reference Concentrations (RCP45) ', alpha = 0.5)
ax1.set_title('Sensitivity Analysis: Biosphere Beta')
ax1.set_ylabel('C02 Atmospheric Concentration (ppm)')
ax1.set_xlabel('Year')
ax1.legend()
ax1.grid(True)

for i, (k_val, label) in enumerate(zip(k_scenarios, k_labels)):
    m_atm, _, _ = combined_ocean_biosphere(years, emissions, beta = beta_base, k = k_val)
    konc_atm = to_ppm(m_atm)
    ax2.plot(years, konc_atm, label = label, linestyle = styles[i], linewidth = 2)

ax2.plot(years, concentrations, 'k--', label = "Reference Concentrations (RCP45)", alpha = 0.5)
ax2.set_title('Sensitivity Analysis: Ocean K-factor')
ax2.set_ylabel('CO2 Concentration (ppm)')
ax2.legend()
ax2.grid(True)
#ax2.set_xlim(2000, 2100)
#ax2.set_ylim(350, 600) # Justera beroende på dina ppm-värden

plt.tight_layout()
plt.show()

# --- Explanation of results --- 

# Beta styr koldioxidgödslingen. 
# Högt beta - biosfären binder mer koldioxid i växter, stammar, jord etc. 
# Detta bromsar ökningen av CO2 i atmosfren markant. 
# Lågt beta - växtlighet mindre påverkad av extra koldioxid i atmosfären. 
# så mindre antropogena utsläpp binds i växtlighet och mark.
# Därmed ökar halten CO2 i atmosfären. 


# K styr hur snabbt havet blir "mättat" på koldioxid.
# Högt k simulerar ett hav som snabbt blir fullt. Därmed 
# därmed försämras dess förmåga att binda C02 tidigare och 
# en större andel av utsläppen stannar då kvar i luften. 
# Lågt k ger motsatsen. Haven har god förmåga att absorbera koldioxid, 
# och det länge. Trots att vi vräker ut utsläpp. Därmed blir 
# C02-atmosfärskoncentrationskurvan mycket flackare. 

# Beta har en större påverkan på kort sikt än vad k har.
# Biosfären reagerar "direkt" på den nuvarande koncentrationen i atmosfären
# och är en relativt snabb feedback loop jämfört med havet. 
# Haven styrs av kumulativa utsläpp och det tar tid att vända eller mätta det, 
# men när det väl händer är effekten svårare att stoppa. Därför
# divergerar havskurvorna först efter "lång tid" och ser ut att sammanfalla i början
# av tidshorizonten, medans biosfärkurvorna divergerar snabbare. 

# Basfall beta = 0.35, k = 0.00306 ligger väldigt nära
# referensdata så det verkar vara en god approximation av
# verkligheten. 



