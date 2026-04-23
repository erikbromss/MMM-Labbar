import numpy as np
import matplotlib.pyplot as plt
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.biosphere import B1_0, B2_0, B3_0, NPP0, ALPHA_21, ALPHA_23, ALPHA_31, npp 
from models.oceans import impuls, m0

def combined_ocean_biosphere(years, antro_emissions, beta = 0.35, k = 3.06e-3):
    """
    Task 6: Integrerad modell biosfär + hav.
    
    Argument: 
        years: Array med år - varje element är ett år
        antro_emissions: Array med mänskliga utsläpp som nu ska bearbetas innan de åker in i ekv. 8
        beta: C02-gödslingsparameter
        k: havets mättnadsgrad
    """

    n = len(years)

    #Initiera för biosfär
    b2 = np.zeros(n)
    b3 = np.zeros(n)
    b2[0] = B2_0
    b3[0] = B3_0

    #M(t) - kolmängd i box 1 = atmosfär
    m_atmos = np.zeros(n)
    m_atmos[0] = m0 #600 GtC

    # "Effektiva utläpp" som faktiskt går till havet: 
    # U(t) = U_antro(t) - Netto_upptag_bios(t)
    u_eff = np.zeros(n)

    #Generera tidsdata 
    for t in range(0, n-1):
        
        # Först beräkna NPP för rådande stund t, sen förändring
        # i biosfärens boxar

        npp_t = npp(beta, m_atmos[t])

        db2 = npp_t - (ALPHA_23 + ALPHA_21) * b2[t]
        db3 = ALPHA_23 * b2[t] - ALPHA_31 * b3[t]

        b2[t+1] = b2[t] + db2
        b3[t+1] = b3[t] + db3

        # Ta nu fram biosfärens nettoupptag:
        # NPP = flödet från atmosfär in i biosfär,
        # alpha_xy = respirationsflöde från box x in i box y 
        
        netto_bio_upptag = npp_t - (ALPHA_21 * b2[t] + ALPHA_31 * b3[t])

        u_eff[t] = antro_emissions[t] - netto_bio_upptag # utsläpp som faktiskt når atmosfär/hav-systemet

        # Havsupptaget - som task 4 fast byt U mot U_eff
        # m(t) = m0 + sum_{t_tilde = 0}^{t} u_eff(t_tilde)*I(t-t_tilde, u_cum)

        ucum_t = np.sum(u_eff[:t+1]) # Kumulativa effektiva utsläpp till hav/bio fram till snu 
        
        #uppdatera mängd kol i atmosfären

        m_next = m0
        for t_tilde in range(t + 1):
            dt = (t + 1) - t_tilde
            m_next += u_eff[t_tilde] * impuls(dt, ucum_t, k)
        
        m_atmos[t+1] = m_next

    return m_atmos, b2, b3
