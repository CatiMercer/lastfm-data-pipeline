"""
Aquest script és el punt d'entrada principal per a l'extracció de dades d'artistes
musicals. Permet a l'usuari triar entre dos motors de scraping (BeautifulSoup o Selenium)
i especificar el nombre d'artistes a extreure. Els resultats es guarden en un fitxer CSV,
i l'usuari té l'opció de consolidar els datasets generats en un únic fitxer CSV final.
"""

import csv
import os
import pandas as pd
import time
from src.scraping.scraper_bs import get_artist_links, scrape_artist
from src.scraping.scraper_selenium import scrape_with_selenium
from src.processing.merge_datasets import merge_datasets
from src.scraping.scraping_utils import load_existing_urls

def ask_engine():
    """
    Gestiona la selecció del motor de scraping per part de l'usuari.

    Returns:
        str: "bs4" per BeautifulSoup o "selenium" per Selenium.
    """
    while True:
        print("\nEscull el motor de scraping:")
        print("1. BeautifulSoup")
        print("2. Selenium")
        option = input("Opció (1/2): ").strip()

        if option == "1":
            return "bs4"

        if option == "2":
            return "selenium"

        print("Opció no vàlida. Torna-ho a provar.")


def ask_num_artists():
    """
    Sol·licita a l'usuari el nombre d'artistes a extreure i valida la entrada.
    
    Returns:
        int: Nombre d'artistes a extreure.
    """
    while True:
        try:
            num = int(input("Nombre d'artistes a extreure: ").strip())
            if num > 0:
                return num
            print("Introdueix un enter positiu.")
        except ValueError:
            print("Introdueix un número vàlid.")


def save_to_csv(results, output_path="data/artists.csv"):
    """
    Guarda els resultats en un fitxer CSV.

    Args:
        results (list): Llista de diccionaris amb les dades dels artistes.
        output_path (str): Ruta on es guardarà el fitxer CSV.
    """
    if not results:
        print("No s'han obtingut resultats. No es generarà cap CSV.")
        return

    new_df = pd.DataFrame(results)

    if os.path.exists(output_path):
        old_df = pd.read_csv(output_path)
        combined = pd.concat([old_df, new_df], ignore_index=True)
        combined = combined.drop_duplicates(subset=["artist_url"])
    else:
        combined = new_df

    combined.to_csv(output_path, index=False, encoding="utf-8")
    print(f"CSV actualitzat: {output_path}")


def retry_failed_artists(failed_artists, current_count, num_artists):
    """
    Torna a provar només els artistes que han fallat.
    """
    retry_results = []
    still_failed = []

    print("\n[RETRY] Reintentant artistes amb error...\n")

    for artist in failed_artists:
        try:
            data = scrape_artist(artist)

            if data:
                retry_results.append(data)
                print(f"[{current_count + len(retry_results)}/{num_artists}] {data.get('artist_name', 'Unknown artist')} (retry)")
            else:
                still_failed.append(artist)

        except Exception as e:
            print(f"[ERROR][RETRY] {artist['artist_url']}: {e}")
            still_failed.append(artist)

    return retry_results, still_failed

def run_beautifulsoup(num_artists):
    """
    Executa el procés de scraping utilitzant BeautifulSoup.

    Args:
        num_artists (int): Nombre d'artistes a extreure.

    Returns:
        list: Llista de diccionaris amb les dades dels artistes.
    """
    artists = get_artist_links(max_artists=num_artists, max_chart_pages=40,
                                max_tag_pages=40)
    results = []
    existing_urls = load_existing_urls("data/artists_bs4.csv")
    failed_artists = [] # Artistes que han donat error

    for artist in artists:
        if artist["artist_url"] in existing_urls:
            print(f"[SKIP] Ja existeix: {artist['artist_url']}")
            continue
        try:
            data = scrape_artist(artist)

            if data:
                results.append(data)
                print(f"[{len(results)}/{num_artists}] {data.get('artist_name', 'Unknown')}")
            else:
                print(f"[ERROR] No s'han pogut extreure dades de: {artist['artist_url']}")
                failed_artists.append(artist)

        except Exception as e:
            print(f"Error amb {artist['artist_url']}: {e}")
            failed_artists.append(artist)
            continue
    
    print(f"[INFO] Total d'artistes extrets correctament: {len(results)}")
    print(f"[INFO] Total amb error: {len(failed_artists)}")

    if failed_artists:
        retry = input("Vols tornar a provar de descarregar els artistes amb error? (s/n): ").strip().lower()

        if retry == "s":
            retry_results, still_failed = retry_failed_artists(failed_artists, len(results), num_artists)
            results.extend(retry_results)

            print(f"\n[INFO] Després del reintent:")
            print(f"[INFO] Total extrets correctament: {len(results)}")
            print(f"[INFO] Total que encara fallen: {len(still_failed)}")

    return results

def run_selenium_batched(total_artists, batch_size=100):
    """
    Executa el procés de scraping utilitzant Selenium en lots.

    Args:
        total_artists (int): Nombre total d'artistes a extreure.
        batch_size (int): Nombre d'artistes a extreure per lot.

    Returns:
        list: Llista de diccionaris amb les dades dels artistes.
    """
    batches = total_artists // batch_size
    remainder = total_artists % batch_size
    total_batches = batches + (1 if remainder > 0 else 0)

    all_results = []

    print(f"\n [INFO] Iniciant scraping amb Selenium en {total_batches} lots...")

    for batch in range(total_batches + 1):
        if batch == total_batches and remainder > 0:
            current_batch_size = remainder
        else:
            current_batch_size = batch_size

        batch_data = scrape_with_selenium(current_batch_size)

        if batch_data:
            all_results.extend(batch_data)
            checkpoint_path = f"data/selenium_checkpoint_lote_{batch + 1}.csv"
            save_to_csv(all_results, checkpoint_path)
            print(f"[INFO] Lot {batch + 1}/{total_batches} completat. Checkpoint guardat a: {checkpoint_path}")

        if batch < total_batches:
            cooldown_time = 5
            time.sleep(cooldown_time)

    return all_results

def main():
    """
    Punt d'entrada principal de l'script.
    """
    engine = ask_engine()
    num_artists = ask_num_artists()
    os.makedirs("data", exist_ok=True)

    if engine == "bs4":
        results = run_beautifulsoup(num_artists)
        save_to_csv(results, "data/artists_bs4.csv")

    elif engine == "selenium":
        results = run_selenium_batched(num_artists)
        save_to_csv(results, "data/artists_selenium.csv")

    print("\n[?] Vols consolidar els datasets generats? (s/n)")
    consolidate = input("Opció (s/n): ").strip().lower()
    if consolidate == "s":
        merge_datasets(
            "data/artists_bs4.csv", "data/artists_selenium.csv", "data/artists_merged.csv"
        )

if __name__ == "__main__":
    main()
