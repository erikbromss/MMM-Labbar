#import sys
#import os
#root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
#sys.path.insert(0, root_dir)
#ys.path.insert(0, os.path.join(root_dir, "models"))

#from utils import load_radiative_forcing
#rfdf = load_radiative_forcing()

labels = ['Time (year)', 'RF CO2 (W/m2)', 'RF aerosols (W/m2)', 'RF other than CO2 and aerosols (W/m2)']

def total_radiative_forcing(rf_df, s=1.0):
    """
    rf_df         : DataFrame från radiativeForcingRCP45.csv
    s             : aerosol-skalningsfaktor, default 1.0
    """
    rf_aerosol = rf_df["RF aerosols (W/m2)"].to_numpy() * s
    rf_other   = rf_df["RF other than CO2 and aerosols (W/m2)"].to_numpy()
    rf_co2 = rf_df['RF CO2 (W/m2)'].to_numpy() 

    rf_total = rf_co2 + rf_aerosol + rf_other
    return rf_total


