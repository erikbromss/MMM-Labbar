# =============================================================================
# BIOSFÄRENS KOLCYKEL — BOXMODELL
# =============================================================================
#
# TRE BOXAR (pre-industriella storlekar):
#   B1 = Atmosfär          600 GtC
#   B2 = Biomassa ovan mark 600 GtC
#   B3 = Mark/rötter       1500 GtC
#
# PRE-INDUSTRIELLA FLÖDEN (GtC/år), från Figur 2:
#   F21 = 60  (B2 → B1, respiration från biomassa)
#   F31 = 15  (B3 → B1, respiration från mark)
#   F12 = 60  (B1 → B2, fotosyntes / NPP₀)  <-- OBS: se NPP nedan
#   F23 = 45  (B2 → B3, litterfall till mark)
#
# LINJÄRA KOEFFICIENTER (fraktion av Bi som flödar till Bj per år):
#   α_ij = F_ij,0 / B_i,0      (antas konstanta oavsett boxstorlek)
#
#   alpha_21 = 60 / 600  = 0.100   (B2 → B1)
#   alpha_31 = 15 / 1500 = 0.010   (B3 → B1)
#   alpha_23 = 45 / 600  = 0.075   (B2 → B3)
#
# FOTOSYNTES / NET PRIMARY PRODUCTION (NPP):
#   Ej linjär — beror logaritmiskt på atmosfärens CO₂-halt (CO₂-gödslingseffekt).
#
#   NPP = NPP0 * (1 + β * ln(B1 / B1_0))
#
#   NPP0 = 60 GtC/år  (pre-industriellt värde)
#   β    = 0.35       (CO₂-gödslingsparameter, osäkert intervall 0.1–0.8)
#   B1_0 = 600 GtC    (pre-industriell atmosfär)
#
# DIFFERENTIALEKVATIONER (forward Euler, tidssteg 1 år):
#
#   dB1/dt = alpha_31*B3 + alpha_21*B2 - NPP + U
#   dB2/dt = NPP - alpha_23*B2 - alpha_21*B2
#   dB3/dt = alpha_23*B2 - alpha_31*B3
#
#   U = antropogena utsläpp [GtC/år]  (läs från utslappRCP45.csv)
#
# OMVANDLING atmosfärsmassa → koncentration:
#   pCO2 [ppm] = B1 [GtC] * 0.469
#
# =============================================================================
# TASK 1
# =============================================================================
# 1. Implementera boxmodellen ovan med forward Euler (dt = 1 år).
# 2. Driva modellen med utsläppsdata från utslappRCP45.csv.
# 3. Beräkna pCO2 = B1 * 0.469 och plotta mot tid.
# 4. Jämför med koncentrationerRCP45.csv — förväntad avvikelse eftersom
#    havsupptag EJ ingår ännu (läggs till i uppg. 3–6).
# 5. Testa olika β-värden (uppg. 2) och observera effekten på B1, B2, B3.
# =============================================================================
import numpy as np

def npp(beta = 0.35, b1 = 600):
    """Returns Net Primary Production of biomass resulting from photosynthesis
       modeled with a logarithmic dependency on the present day carbon content
       of the atmosphere (box 1). 
       
       Parameters: 
       
       beta: CO2 Fertilization Factor - reference value of 0.35 but presumed to range
             between 0.1 - 0.8 [no unit]
       
       b1:   present day carbon content of the atmosphere [GtC]
       
       
       """
    npp0 = 60 #[GtC]
    b10 = 600

    return npp0 * (1 + beta*np.log(b1/b10) )


def forward_euler(beta, b1, time):

    b1 = [600]
    b2 = [600]
    b3 = [1500]

    alpha_21 = 60 / 600 
    alpha_31 = 15 / 1500 
    alpha_23 = 45 / 600  
    
    for i in range(time):
        b1 = alpha_31 * b3[i] + alpha_21 - npp(beta, b1) + b1_new
        b2= npp(beta, b1)- alpha_23 * b2[i] - alpha_21 * b2[i]
        b3 = alpha_23 * b2[i] - alpha_31 * b3[i]






