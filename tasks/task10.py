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

if __name__ == "__main__":
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

    # --- 10c) --- 

    # Analysera RF(t), dT1(t) / lam, och k * (dT1(t) - dT2(t))
    # för de olika värdena på lambda och kappa som vi använda i ovanstående uppgift. 

    # Gör det över 200 år, gäller energikonservation här? 

    n_years = 200
    rftot_step = np.ones(n_years)
    rftot_step[0] = 0
    t = np.arange(n_years)
    c1, c2 = 6.77, 270.6

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    axes[0].set_title("Utgående rymdstrålning (ΔT1/λ)")
    axes[1].set_title("Havsupptag κ·(ΔT1-ΔT2)")

    # RF plottas en gång som referens i båda subplots
    for ax in axes:
        ax.plot(t, rftot_step, color="black", linewidth=1.5, label="RF = 1 W/m²")

    colors = {0.5: "steelblue", 0.8: "darkorange", 1.1: "green", 1.3: "red"}

    for lam in lambdas:
        for k in kappas:
            T1, T2 = energybalance(rftot_step, lam=lam, k=k)
            T1, T2 = np.array(T1[:n_years]), np.array(T2[:n_years])

            rymdstrålning = T1 / lam
            havsupptag    = k * (T1 - T2)

            # Streckstil per kappa så man kan särskilja dem
            ls = {0.2: "solid", 0.5: "dashed", 1.0: "dotted"}[k]

            axes[0].plot(t, rymdstrålning, color=colors[lam], linestyle=ls, label=f"λ={lam}, κ={k}")
            axes[1].plot(t, havsupptag, color=colors[lam], linestyle=ls, label=f"λ={lam}, κ={k}")

    for ax in axes:
        ax.set_xlabel("Tid (år)")
        ax.set_ylabel("Energiflöde (W/m²)")
        ax.legend(fontsize=7, ncol=2)
        ax.grid(True)

    plt.suptitle("Energiflöden över 200 år — alla λ och κ")
    plt.tight_layout()
    plt.show()

    # --- Energikonservation (defaultparametrar) ---
    T1, T2 = energybalance(rftot_step, lam=0.8, k=0.5)
    T1, T2 = np.array(T1[:n_years]), np.array(T2[:n_years])

    rymdstrålning   = T1 / 0.8
    havsupptag      = 0.5 * (T1 - T2)
    ackumulerad     = c1 * T1 + c2 * T2
    net_flux_cumsum = np.cumsum(rftot_step - rymdstrålning)

    plt.figure()
    plt.plot(t, net_flux_cumsum, label="Kumulativ nettoinflöde (RF − strålning − hav)")
    plt.plot(t, ackumulerad,     label="Lagrad energi (C1·T1 + C2·T2)", linestyle="--")
    plt.xlabel("Tid (år)")
    plt.ylabel("Ackumulerad energi (W·yr/m²)")
    plt.title("Energikonservation (λ=0.8, κ=0.5)")
    plt.legend()
    plt.grid(True)
    plt.show()

    # Analys av resultat: 
    # Utgående rymdstrålning - beror starkt på lambda och relativt 
    # lite på kappa. Högre lambda ger lägre rymdstrålning vid en 
    # viss tidpunkt. Makes sense eftersom detta är ΔT1/λ, och 
    # ett högt lambda innebär att samma RF ger högre jämviktstemperatur, 
    # men att varje grad temperaturökning ger mindre utgående strålning. 
    # Systemet bromsar då alltså långsammare mot jämvikt. 
    # k påverkar hur snabbt rymdstrålningen når sitt slutvärde - högre k,
    # här de prickade linjerna, planar ut långsammare eftersom mer värme kontinuerligt
    # pumpas in i djuphavet och därmed hålls T1 lägre längre -> mindre 
    # utstrålad effekt. Detta ser vi genom att kolla på en given färgs olika
    # streckstilar i plotten. 

    # Havsupptag - beror tydligt av både kappa och lambda. 
    # Mönstret som syns i plotten är att upptaget ökar snabbt i början 
    # eller för små t, då T1 stiger men T2 fortfarande är låg. Dvs då vi värmer
    # box 1 (biosfär + grundhav) och djuphavet fortfarande är relativt kallt. 
    # Därefter minskar upptaget gradvis då T2 hinner ikapp T1 varpå temperaturskillnaden
    # T1-T2 krymper. 
    # Högre kappa ger ett kraftigare initialt havsupptag men också snabbare dämpning
    # av upptaget vilket syns av att de prickade linjerna har mest negativ lutning
    # då de faktiskt börjat minska relativt samma färgs streckade och heldragna linjer. 
    # Detta då värmen överförs effektivare och T2 hinner ikapp T1 snabbare. 
    # Högre lambda ger ett högre havsupptag överlag eftersom T1 tillåts bli högre
    # vilket framgår ur ekvation 10. Detta resulterar i att T1-T2 blir större och kvarstår längre. 


    # Energibalansen: 
    #I jämvikt måste havsupptaget gå mot noll (T1 = T2) och
    # rymdstrålningen mot RF = 1, vilket stämmer med plottarna. 
    # Kurvorna överlappar vilket visar att net flux RF - rymdstrålning
    # är lika med ackumulerad energi i systemet. 
    # Denna går oxå mot en jämvikt men inte förens efter flera 1000 år
    # märks det, då djuphavet fortsätter att absorbera energi
    # mycket länge, tills dess att T2 och T1 blir ungefär lika
    # med RF * lambda. Det kräver ungefär 2500 år som vi såg i 10a). 
    # Det betyder alltså att planeten tills dess fortfarande är i obalans och tar upp mer
    # energi än den strålar ut. 