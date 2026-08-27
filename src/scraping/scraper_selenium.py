"""
Aquest mòdul implementa l'arquitectura d'extracció dinàmica de dades mitjançant 
Selenium. Proporciona una classe 'ScraperSelenium' que utilitza un controlador 
de navegador per navegar per les pàgines web i extreure informació de manera 
dinàmica, especialment útil per a pàgines que carreguen contingut mitjançant 
JavaScript.
"""


import time
import re
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.scraping.scraping_utils import (
    parse_number,
    get_scrape_date,
    clean_text,
)

def initialize_selenium_engine():
    """
    Inicialitza el motor de Selenium amb les opcions adequades per a l'extracció 
    de dades.
    
    Retorna:
        webdriver.Chrome: Una instància del controlador de Chrome configurada.
    """
    options = Options()
    # Configurem les opcions del navegador per a una extracció més eficient i menys intrusiva
    # options.add_argument("--headless")
    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")
    options.add_argument("disable-dev-shm-usage")
    options.add_argument("no-sandbox")
    options.add_argument("disable-blink-features=AutomationControlled")

    try:
        driver = webdriver.Chrome(options=options)
        target_url = "https://www.last.fm/"
        driver.get(target_url)
        print(f"Driver initialized and navigated to {target_url}")
        return driver
    except WebDriverException as e:
        print(f"Error initializing Selenium engine: {e}")
        return None

def bypass_legal_waf(driver):
    """
    Localitza i accepta el bàner de cookies si està present. Això és important
    per evitar bloquejos de WAF legals que poden impedir l'accés a la pàgina.

    Args:
        driver (webdriver.Chrome): El controlador de Selenium que s'utilitza
                                per navegar per la pàgina.
    """
    try:
        # Espera fins que aparegui el botó d'acceptació de cookies i fes clic
        wait = WebDriverWait(driver, 5)
        accept_button = wait.until(
            EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
        )
        accept_button.click()
        print("Cookies Acceptades.")
        time.sleep(1.5)  # Espera un moment després d'acceptar les cookies
    except WebDriverException as e:
        print(f"Error accepting cookies: {e}")

def get_latest_release_url(driver, max_urls=1000):
    """
    Navega de forma sistemàtica per les pàgines de 'New Releases' per
    generar una cua massiva d'URLs d'artistes.

    Args:
        driver (webdriver.Chrome): El controlador de Selenium configurat.
        max_urls (int): El llindar màxim d'URLs úniques a recollir.

    Retorna:
        list: Una llista de cadenes (strings) amb les URLs absolutes dels
            perfils d'artista trobats.
    """
    all_urls = []
    page = 1
    wait = WebDriverWait(driver, 10)

    # Busquem els enllaços dins de la secció 'The Latest Releases'
    while len(all_urls) < max_urls:  # Limitem a max_urls per evitar sobrecàrrega
        target_url = f"https://www.last.fm/music/+releases/out-now/popular?page={page}"
        driver.get(target_url)

        try:
            artist_elements = wait.until(
                EC.presence_of_all_elements_located((
                    By.CSS_SELECTOR, ".resource-list--release-list-item-artist a"
                ))
            )
            page_urls = [el.get_attribute("href") for el in artist_elements]

            for url in page_urls:
                if url not in all_urls and len(all_urls) < max_urls:
                    all_urls.append(url)

            if not page_urls:
                print("No more artist URLs found, stopping pagination.")
                break

            page += 1
            time.sleep(1.5)  # Espera un moment abans de carregar la següent pàgina

        except WebDriverException as e:
            print(f"   [!] Error a la pàgina {target_url}: {e}")
            break

    return all_urls

def get_system_metadata(driver):
    """
    Aquesta funció captura les metadades de traçabilitat de l'extracció.
    Args:
        driver (webdriver.Chrome): El controlador de Selenium que s'utilitza
                                per navegar per la pàgina.

    Retorna:
        dict: Un diccionari amb les metadades del sistema, com la data d'extracció
        i l'URL actual.
    """
    system_data = {
        # URL absoluta del perfil actual
        "artist_url": driver.current_url,
        # Etiqueta de l'origen de la dada
        "scraped_from": "crawler_network",
        # Data i hora de l'extracció
        "scraped_date": get_scrape_date(),
    }

    return system_data

def get_header_data(driver):
    """
    Aquesta funció captura les dades de la capçalera del perfil de l'artista, com
    el nom i el gènere.

    Args:
        driver (webdriver.Chrome): El controlador de Selenium que s'utilitza
                                per navegar per la pàgina.

    Retorna:
        dict: Un diccionari amb les dades de la capçalera del perfil de l'artista,
        com el nom i el gènere.
    """
    wait = WebDriverWait(driver, 8)

    header_data = {
        # Nom de l'artista (per defecte "N/A" si no es pot localitzar)
        "artist_name": "N/A",
        # Nombre de listeners (per defecte 0 si no es pot localitzar)
        "listeners": 0,
        # Nombre de scrobbles (per defecte 0 si no es pot localitzar)
        "scrobbles": 0,
    }

    try:
        # Intentem localitzar el nom de l'artista
        artist_name_element = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".header-new-title"))
        )
        header_data["artist_name"] = artist_name_element.text.strip()

        # Extreurem les metriques de listeners i scrobbles
        stats_elements = driver.find_elements(
            By.CSS_SELECTOR, ".header-new-content abbr"
        )

        if len(stats_elements) >= 2:
            header_data["listeners"] = parse_number(
                stats_elements[0].get_attribute("title")
            )
            header_data["scrobbles"] = parse_number(
                stats_elements[1].get_attribute("title")
            )

    except WebDriverException as e:
        print(f"Error getting header data: {e}")

    return header_data

def get_deep_data(driver):
    """
    Aquesta funció captura les dades més profundes del perfil de l'artista,
    com la biografia i les etiquetes.

    Args:
        driver (webdriver.Chrome): El controlador de Selenium que s'utilitza
                                per navegar per la pàgina.
    Retorna:
        dict: Un diccionari amb les dades més profundes del perfil de l'artista,
        com la biografia i les etiquetes.
    """

    deep_data = {
        # Biografia de l'artista (per defecte "N/A" si no es pot localitzar)
        "bio": "N/A",
        # Llista d'etiquetes associades a l'artista (per defecte "N/A" si no es pot localitzar)
        "tags": "N/A",
        # Llista d'artistes similars (per defecte "N/A" si no es pot localitzar)
        "similar_artists": "N/A",
        # Cançó més popular de l'artista (per defecte "N/A" si no es pot localitzar)
        "top_track": "N/A",
        # Posició de l'artista en el rànquing global (per defecte 0 si no es pot localitzar)
        "rank": None,
        # Data de la darrera publicació de l'artista (per defecte "N/A" si no es pot localitzar)
        "latest_release_date": None,
        # Edat de l'artista (per defecte "N/A" si no es pot localitzar)
        "age": None,
    }

    # Desplaça fins al final de la pàgina per carregar contingut dinàmic
    driver.execute_script("window.scrollTo(0, 500);")
    time.sleep(1)  # Espera un moment per assegurar que el contingut s'ha carregat

    selectors = {
        "bio": [
                "div[itemprop='description']",
                ".wiki-content",
                ".wiki-block-inner-2",
                ".wiki-block",
                ".wiki-node-content"
        ],
        "age": [
                ".catalogue-metadata",
                ".wiki-container",
                ".metadata-column"
        ]
    }

    # Intentem localitzar la biografia de l'artista utilitzant diversos selectors per
    # maximitzar les possibilitats d'èxit
    for selector in selectors["bio"]:
        try:
            element = driver.find_elements(By.CSS_SELECTOR, selector)
            if element:  # Si la llista no està buida
                text = clean_text(element[0].get_attribute("textContent"))
                if len(text) > 20:
                    deep_data["bio"] = text[:500]
                    break
        except NoSuchElementException:
            continue

    # Extracció de les etiquetes
    try:
        tag_elements = driver.find_elements(By.CSS_SELECTOR, ".tag a")
        if tag_elements:
            deep_data["tags"] = "| ".join(
                [clean_text(tag.text) for tag in tag_elements[:5]]
            )

    except NoSuchElementException:
        pass

    # Extreurem els artistes similars i URLs associats
    try:
        similar_elements = driver.find_elements(
            By.CSS_SELECTOR, ".artist-similar-artists-item-name a"
        )
        # Limitem a les 10 primeres per evitar sobrecàrrega de dades
        if similar_elements:
            deep_data["similar_artists"] = "| ".join(
                [clean_text(artist.text) for artist in similar_elements[:10]]
            )

            deep_data["_similar_urls"] = [
                artist.get_attribute("href") for artist in similar_elements[:10]
            ]

    except NoSuchElementException:
        pass

    # Extreurem les cançons més populars de l'artista
    try:
        top_track_element = driver.find_element(By.CSS_SELECTOR, ".chartlist-name a")
        if top_track_element:
            deep_data["top_track"] = clean_text(top_track_element.text)
    except NoSuchElementException:
        pass

    # Extreurem l'edat de l'artista o els anys d'activitat
    try:
        for selector in selectors["age"]:
            age_elements = driver.find_element(By.CSS_SELECTOR, selector)
            if age_elements:
                age_text = age_elements.get_attribute("textContent").lower()
                age_match = re.search(r"age\s+(\d+)|(\d+)\s+years", (age_text))
                if age_match:
                    deep_data["age"] = int(age_match.group(1) or age_match.group(2))
                    break

    except NoSuchElementException:
        pass

    # Extreurem la posició de l'artista en el rànquing global
    try:
        rank_elements = driver.find_elements(
            By.CSS_SELECTOR, ".header-new-chart-position-desktop"
        )

        if rank_elements:
            rank_text = rank_elements[0].get_attribute("textContent").strip()
            rank_match = re.sub(r"[^\d]", "", rank_text)
            if rank_match:
                deep_data["rank"] = int(rank_match)
    except NoSuchElementException:
        pass

    # Extreurem la data de la darrera publicació de l'artista
    try:
        release_element = driver.find_element(
            By.CSS_SELECTOR, ".header-metadata-tnew-display"
        )
        if release_element:
            text = release_element.get_attribute("textContent").strip()
            if re.search(r'\d{4}', text):
                deep_data["latest_release_date"] = text
    except NoSuchElementException:
        pass

    return deep_data


def scrape_with_selenium(max_artists_to_scrape, urls_list=[], seen_urls=set()):
    """
    Funció principal que gestiona el procés d'extracció de dades utilitzant Selenium.

    Args:
        max_artists_to_scrape (int): El nombre màxim d'artistes que es volen escrapejar.
    Retorna:
        list: Una llista de diccionaris, on cada diccionari conté les dades d'un artista.
    """
    driver = initialize_selenium_engine()
    if not driver:
        return []

    try:
        bypass_legal_waf(driver)

        if len(urls_list) == 0:
            urls_list.extend(get_latest_release_url(driver, max_urls=1000))
        # seen_urls = set()
        dataset_final = []

        while len(urls_list) > 0 and len(dataset_final) < max_artists_to_scrape:
            url = urls_list.pop(0)

            if url in seen_urls:
                continue

            try:
                driver.get(url)
                time.sleep(1.5)

                seen_urls.add(url)

                header_data = get_header_data(driver)

                count = len(dataset_final) + 1
                total = max_artists_to_scrape
                name = header_data.get("artist_name", "N/A")
                print(f"[{count}/{total}] {name}")

                deep_data = get_deep_data(driver)

                registre_artista = {}
                registre_artista.update(get_system_metadata(driver))
                registre_artista.update(header_data)
                registre_artista.update(deep_data)

                new_urls = registre_artista.get("_similar_urls", [])
                if isinstance(new_urls, list):
                    for new_url in new_urls:
                        if new_url not in seen_urls and new_url not in urls_list:
                            urls_list.append(new_url)

                registre_artista.pop("_similar_urls", None)
                dataset_final.append(registre_artista)

                time.sleep(2)

            except WebDriverException as e:
                print(f"    [!] Avís: Error al carregar la pàgina de l'artista. Error: {e}")
                continue

        return dataset_final

    finally:
        driver.quit()
