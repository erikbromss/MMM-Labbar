import numpy as np

def rf(C_t, C_t0 = 278.05):
    """
    Återger radiative forcing som funktion av 
    en viss concentration C_t = C(t) (ppm) koldioxid i 
    atmosfären vid en viss tidpunkt t.

    Argument:
        C_t: CO2-koncentrationen i atmosfären vid tid t C(t)
        C_t0: Referenskoncentration - 280 är pre-industriellt värde

    Returns:
        Radiative forcing 
    """
    return 5.35 * np.log(C_t/C_t0)

def scale(rf_other_tot, s = 1):
    """
    Arguments:
        rf_other_tot: The total sum of all individual OTHER RF contributions
        s: scalar scale factor, default value s = 1 
    
    Returns: 
        rf_other_tot * s"""
    
    return rf_other_tot * s
