import sys
import os

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, "models"))
import matplotlib.pyplot as plt
from models.energy_balance import rf
from models.biosphere_and_oceans import combined_ocean_biosphere as modell
from utils import load_emissions, load_concentrations, load_radiative_forcing, to_ppm

years, emissions = load_emissions()
_, concentrations = load_concentrations()
rfdata = load_radiative_forcing()

# Valde att köra på modellkoncentrationer snarare än RCP datan

m_atm, _, _ = modell(years, emissions)
konc_modell = to_ppm(m_atm)
rf_modell = [rf(x) for x in konc_modell] # modellerad radiative forcing

# Plotta rf_modell mot rfdata['CO2'] för comparison

plt.figure()
plt.plot(years, rf_modell, label = 'Model RF')
plt.plot(years, rfdata['RF CO2 (W/m2)'], label = 'Reference RF (RCP45)')
plt.grid(True)
plt.title('Model vs. Reference: Radiative forcing')
plt.ylabel('Radiative Forcing [W/m^2]')
plt.xlabel('Year')
plt.legend()
plt.show()



