import numpy as np
# --- Task 3 --- 

# List fractions and relaxation time constans as provided in Table 1 

As = [0.113, 0.213, 0.258, 0.273, 0.143]
tau0s = [2.0, 12.2, 50.4, 243.3, np.inf]

k = 3.06*10**(-3)

# Definiera impulsfunktionen

def impuls(t: float, ucum: float):

    tauis = [tau0 * (1+k*ucum) for tau0 in tau0s]

    I = 0
    for i in range(len(As)):
        I += As[i] * np.exp(-t / tauis[i])
    
    return I 

# --- Task 4 --- 

m0 = 600 #GtC

def m(years, emissions): 
    """
    Beräknar M(t) enligt ekv. 8. 
    years: lista med år
    emissions: array med utsläpp U(t) för varje år
    """

    M = np.zeros(len(years))

    # Tau beror på summan av utsläpp fram tills t_tilde - 1
    
    ucum = np.cumsum(emissions)
    
    for t_idx in range(len(years)):

        total_carbon_at_t = m0

        for t_tilde_idx in range(t_idx + 1):

            dt = years[t_idx] - years[t_tilde_idx] # tid sedan specifikt utsläpp

            u_tilde = emissions[t_tilde_idx] # vad det ustläppet var (U(t))

            # Kumulativa utsläpp FRAM till det året t_tilde-1

            ucum_at_tilde = ucum[t_tilde_idx-1] if t_tilde_idx > 0 else 0

            andel_kvar = impuls(dt, ucum_at_tilde)

            total_carbon_at_t += andel_kvar * u_tilde


        M[t_idx] = total_carbon_at_t
    
    return M
    

    

