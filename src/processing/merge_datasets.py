"""
Aquest script combina els datasets generats per les dues tècniques de scraping
(BeautifulSoup i Selenium) en un únic dataset consolidat. El procés inclou:

1. Carregar els datasets des dels fitxers CSV.
2. Combinar els datasets en un DataFrame únic.
3. Eliminar registres duplicats basant-se en la columna 'artist_url' per assegurar
   que cada artista apareix només una vegada.
4. Guardar el dataset final net i consolidat en un nou fitxer CSV.
5. Proporcionar un informe detallat del nombre de registres analitzats, el nombre
   de duplicats eliminats i el nombre final de registres nítids en el dataset consolidat.
"""

import os
import pandas as pd

def merge_datasets(path_bs4, path_sel, output_path):
    """
    Combina els datasets de BeautifulSoup i Selenium, elimina duplicats i guarda
    el resultat.
    
    Args:
        path_bs4 (str): Ruta al fitxer CSV generat per BeautifulSoup.
        path_sel (str): Ruta al fitxer CSV generat per Selenium.
        output_path (str): Ruta on es guardarà el dataset combinat i net.
    
    Returns:
        None: El dataset combinat es guarda en un fitxer CSV a la ruta especificada.
    """
    # Carregar els datasets
    df1 = pd.read_csv(path_bs4)
    df2 = pd.read_csv(path_sel)

    # Combinar els datasets
    raw_merged_df = pd.concat([df1, df2], ignore_index=True)

    # Guardar el dataset combinat
    raw_merged_df.to_csv(output_path, index=False)
    print(f"Datasets combinats i guardats a: {output_path}")

    initial_count = len(raw_merged_df)
    clean_df = raw_merged_df.drop_duplicates(subset=['artist_url'], keep='first')
    final_count = len(clean_df)

    output_directory = os.path.dirname(output_path)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    clean_df.to_csv(output_path, index=False, encoding='utf-8')

    # Informe final
    print("[+] Informe de tancament del Pipeline:")
    print(f"    - Registres totals analitzats: {initial_count}")
    print(f"    - Registres duplicats eliminats: {initial_count - final_count}")
    print(f"    - Dataset final consolidat: {final_count} registres nítids.")
    print(f"[+] Fitxer generat amb èxit a: {output_path}")


if __name__ == "__main__":
    FILE_BS4 = "data/artists_bs4.csv"
    FILE_SEL = "data/artists_selenium.csv"
    FINAL_CSV = "data/artists_merged.csv"

    merge_datasets(FILE_BS4, FILE_SEL, FINAL_CSV)
