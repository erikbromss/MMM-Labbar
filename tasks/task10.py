import sys
import os
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, "models"))

import numpy as np
from models.biosphere_and_oceans import combined_ocean_biosphere
from utils import load_emissions, load_radiative_forcing, to_ppm
from task9 import total_radiative_forcing
import matplotlib.pyplot as plt

years, emissions = load_emissions()

m_atm, _, _ = combined_ocean_biosphere(years, emissions)
rfdf = load_radiative_forcing()

konc_modell = to_ppm(m_atm)
rftot = total_radiative_forcing(rfdf)

def energybalance(rftot, c1 = 6.77, c2 = 270.6, lam = 0.8, k = 0.5):

    #Initialize (Pre-Industrial) data for RF, delta_T1, delta_T2
    
    
    delta_T1_0 = 0
    delta_T2_0 = 0

    delta_T1 = [delta_T1_0]
    delta_T2 = [delta_T2_0]

    for t in range(0, len(rftot)):
        
        delta_T1_t = delta_T1[t] + (rftot[t] - (delta_T1[t] / lam ) - k * (delta_T1[t] - delta_T2[t])) / c1
        delta_T2_t = delta_T2[t] + (k * (delta_T1[t] - delta_T2[t])) / c2

        delta_T1.append(delta_T1_t)
        delta_T2.append(delta_T2_t)
    
    return delta_T1, delta_T2

# --- 10a) ---
n_years = 2500
rftot_step = np.ones(n_years)
rftot_step[0] = 0  

T1, T2 = energybalance(rftot_step)

print(T1[-1], T2[-1]) #Should both equal RF * LAMDA = 0.8

# see that it takes a very long while for them to reach equillibrium, 2500 years and t2 is still .03 degrees celsius off
# makes sense as dT2 grows as k(T1-T2)/c2 and c2 is huge, and T1-T2 is very small as we approach equilibrium state 
# but they do approach 0.8 deg celsius! ok :) 

t = np.arange(len(T1))

# Plot
plt.figure()
plt.plot(t, T1, label="Delta T1 (snabb box)")
plt.plot(t, T2, label="Delta T2 (djuphav)")

# Jämviktslinje
plt.axhline(0.8, linestyle="--", label="Teoretisk jämvikt (0.8 grader Celsius)")

plt.xlabel("Tid (år)")
plt.ylabel("Temperaturförändring (Celsius)")
plt.title("Temperaturrespons på step forcing (1 W/m²)")
plt.legend()
plt.grid()

plt.show()

# --- 10b) --- 

def efolding_time(T, lambda_val):
    T_eq = lambda_val # since RF = 1 from idx 1 
    threshold = 0.632 * T_eq
    
    for t, temp in enumerate(T):
        if temp >= threshold:
            return t
    return None

lambdas = [0.5, 0.8, 1.1, 1.3]
kappas = [0.2, 0.5, 1.0]

results = []

for lam in lambdas:
    for k in kappas:
        rftot_step = np.ones(5000)
        rftot_step[0] = 0
        
        T1, T2 = energybalance(rftot_step, lam=lam, k=k)
        
        tau1 = efolding_time(T1, lam)
        tau2 = efolding_time(T2, lam)
        
        results.append((lam, k, tau1, tau2))

for r in results:
    print(f"lambda={r[0]}, kappa={r[1]} → tau1={r[2]}, tau2={r[3]}")

import matplotlib.pyplot as plt
from collections import defaultdict #AI hjälp att organisera results för plotting 

tau1_dict = defaultdict(list)
tau2_dict = defaultdict(list)
kappa_dict = defaultdict(list)

for lam, k, tau1, tau2 in results:
    tau1_dict[lam].append(tau1)
    tau2_dict[lam].append(tau2)
    kappa_dict[lam].append(k)

plt.figure()
for lam in sorted(tau1_dict.keys()):
    kappas = kappa_dict[lam]
    tau1_vals = tau1_dict[lam]
    
    
    kappas, tau1_vals = zip(*sorted(zip(kappas, tau1_vals)))
    
    plt.plot(kappas, tau1_vals, marker='o', label=f"λ={lam}")

plt.xlabel("κ (exchange coefficient)")
plt.ylabel("τ₁ (years)")
plt.title("E-folding time (surface temperature)")
plt.legend()
plt.grid()
plt.show()

plt.figure()
for lam in sorted(tau2_dict.keys()):
    kappas = kappa_dict[lam]
    tau2_vals = tau2_dict[lam]
    
    kappas, tau2_vals = zip(*sorted(zip(kappas, tau2_vals)))
    
    plt.plot(kappas, tau2_vals, marker='o', label=f"λ={lam}")

plt.xlabel("κ (exchange coefficient)")
plt.ylabel("τ₂ (years)")
plt.title("E-folding time (deep ocean temperature)")
plt.legend()
plt.grid()
plt.show()

# The results show that the exchange coefficient κ strongly controls
# the transient response of the system. A larger κ reduces the e-folding time
#  of the deep ocean temperature, as heat is transferred more efficiently from the surface
#  to the deeper layers. However, this also slows down the surface temperature response,
#  since energy is continuously redistributed into the deep ocean, increasing τ₁.

# Conversely, a small κ allows the surface temperature to respond rapidly to radiative forcing,
#  resulting in a short τ₁, but leads to a very slow equilibration of the deep ocean, reflected
#  in large τ₂ values.

# Increasing the climate sensitivity parameter λ increases the equilibrium temperature and
#  therefore slightly increases the e-folding times, since the system must undergo a larger temperature adjustment.