"""
Aquest mòdul conté funcions utilitàries per al procés de neteja i transformació de dades.

Inclou funcions per netejar textos, convertir textos numèrics a enters, obtenir la data
d'extracció i eliminar duplicats d'una llista mantenint l'ordre original i ignorant
majúscules i minúscules.
"""
from datetime import datetime
import re
import os
import pandas as pd

def clean_text(text):
    """
    Neteja espais i salts de línea.
    """
    if text is None:
        return ""
    return " ".join(text.strip().split())


def parse_number(text):
    """
    Converteix textos numèrics de Last.fm a enter.
    Exemples:
    '1,234' -> 1234
    '12.5K' -> 12500
    '59M' -> 59000000
    '364.2M' -> 364200000
    """
    if text is None:
        return None

    cleaned = clean_text(text).replace(",", "")
    match = re.match(r"^([\d\.]+)\s*([KMB]?)$", cleaned, re.IGNORECASE)

    if not match:
        digits_only = re.sub(r"[^\d]", "", cleaned)
        return int(digits_only) if digits_only else None

    number = float(match.group(1))
    suffix = match.group(2).upper()

    multiplier = 1
    if suffix == "K":
        multiplier = 1_000
    elif suffix == "M":
        multiplier = 1_000_000
    elif suffix == "B":
        multiplier = 1_000_000_000

    return int(number * multiplier)


def get_scrape_date():
    """
    Retorna la data d'extracció en format YYYY-MM-DD.
    """
    return datetime.now().strftime("%Y-%m-%d")

def duplicates(item_list):
    """
    Elimina duplicats d'una llista mantenint l'ordre original, 
    ignorant majúscules i minúscules.
    """
    seen = set()
    result = []

    for i in item_list:
        if i.lower() not in seen:
            seen.add(i.lower())
            result.append(i)

    return result


def load_existing_urls(csv_path):
    """
    Carrega les URLs ja existents al dataset.
    """
    if not os.path.exists(csv_path):
        return set()

    df = pd.read_csv(csv_path)

    if "artist_url" not in df.columns:
        return set()

    return set(df["artist_url"].dropna())
