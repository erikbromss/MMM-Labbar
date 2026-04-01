import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def load_emissions():
    """Laddar utsläppsdata från utslappRCP45.csv.
    
    Returns:
        years  : lista med år [int]
        emissions: lista med CO2-utsläpp [GtC/år]
    """
    df = pd.read_csv(os.path.join(DATA_DIR, "utslappRCP45.csv"))
    years = df["Time (year)"].tolist()
    emissions = df["CO2 Emissions  (CO2 GtC/yr)"].tolist()
    return years, emissions


def load_concentrations():
    """Laddar CO2-koncentrationsdata från koncentrationerRCP45.csv.

    Returns:
        years        : lista med år [int]
        concentrations: lista med CO2-koncentrationer [ppm]
    """
    df = pd.read_csv(os.path.join(DATA_DIR, "koncentrationerRCP45.csv"))
    years = df["Time (year)"].tolist()
    concentrations = df["CO2ConcRCP45 (ppm CO2) "].tolist()
    return years, concentrations


def load_radiative_forcing():
    """Laddar radiativ forcing-data från radiativeForcingRCP45.csv.
    Används i Del 2 och Del 3.

    Returns:
        df: DataFrame med alla kolumner
    """
    return pd.read_csv(os.path.join(DATA_DIR, "radiativeForcingRCP45.csv"))


def load_nasa_giss():
    """Laddar NASA GISS temperaturanomalier.
    Används i uppgift 11.

    Returns:
        df: DataFrame med alla kolumner
    """
    return pd.read_csv(os.path.join(DATA_DIR, "NASA_GISS.csv"))


def to_ppm(b1):
    """Konverterar atmosfäriskt kolinnehåll till CO2-koncentration.

    Args:
        b1: lista eller array med atmosfärens kolinnehåll [GtC]

    Returns:
        lista med CO2-koncentration [ppm]
    """
    return [x * 0.469 for x in b1]