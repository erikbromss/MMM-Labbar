import numpy as np

# =============================================================================
# BIOSFÄRENS KOLCYKEL — BOXMODELL
# =============================================================================
#
# TRE BOXAR (pre-industriella storlekar):
#   B1 = Atmosfär           600 GtC
#   B2 = Biomassa ovan mark  600 GtC
#   B3 = Mark/rötter        1500 GtC
#
# PRE-INDUSTRIELLA FLÖDEN (GtC/år), från Figur 2:
#   F21 = 60  (B2 → B1, respiration från biomassa)
#   F31 = 15  (B3 → B1, respiration från mark)
#   F23 = 45  (B2 → B3, litterfall till mark)
#   NPP0 = 60 (B1 → B2, fotosyntes, pre-industriellt)
#
# KOEFFICIENTER:
#   alpha_21 = 60 / 600  = 0.100
#   alpha_31 = 15 / 1500 = 0.010
#   alpha_23 = 45 / 600  = 0.075
#
# DIFFERENTIALEKVATIONER (forward Euler, dt = 1 år):
#   dB1/dt = alpha_31*B3 + alpha_21*B2 - NPP + U
#   dB2/dt = NPP - alpha_23*B2 - alpha_21*B2
#   dB3/dt = alpha_23*B2 - alpha_31*B3
# =============================================================================

# Pre-industriella startvärden [GtC]
B1_0 = 600.0
B2_0 = 600.0
B3_0 = 1500.0
NPP0 = 60.0

# Flödeskoefficienter [1/år]
ALPHA_21 = 15.0 / B2_0
ALPHA_31 = 45.0 / B3_0
ALPHA_23 = 45.0 / B2_0


def npp(beta, b1):
    """Nettoprimärproduktion (NPP) — fotosyntes med logaritmiskt CO2-beroende.

    Args:
        beta: CO2-gödslingsparameter, referensvärde 0.35, intervall 0.1 - 0.8 
        b1  : atmosfärens kolinnehåll vid aktuellt tidssteg [GtC]

    Returns:
        NPP [GtC/år]
    """
    return NPP0 * (1 + beta * np.log(b1 / B1_0))


def forward_euler(beta, u):
    """Löser biosfärens boxmodell med forward Euler (dt = 1 år).

    Args:
        beta: CO2-gödslingsparameter [-]
        u   : lista med antropogena utsläpp per år [GtC/år],
              där u[0] motsvarar startårets utsläpp.

    Returns:
        b1, b2, b3: tidsserier av kolinnehåll i varje box [GtC].
                    Varje lista har längden len(u) + 1 (inkl. startvärde).
    """
    b1 = [B1_0]
    b2 = [B2_0]
    b3 = [B3_0]

    for i in range(len(u)):
        current_npp = npp(beta, b1[i])
        b1.append(b1[i] + ALPHA_31*b3[i] + ALPHA_21*b2[i] - current_npp + u[i])
        b2.append(b2[i] + current_npp - ALPHA_23*b2[i] - ALPHA_21*b2[i])
        b3.append(b3[i] + ALPHA_23*b2[i] - ALPHA_31*b3[i])

    return b1, b2, b3