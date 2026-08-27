"""
Aquest script utilitza la biblioteca BeautifulSoup per realitzar web scraping al
lloc web de Last.fm. El procés inclou:

1. Descarregar la pàgina de charts de Last.fm i extreure els enllaços dels artistes
   i el seu rànquing.
2. Visitar la pàgina de cada artista i extreure informació com el nom, el nombre de
   listeners, scrobbles, tags, biografia, artistes similars, edat, data de l'últim
   llançament i la seva cançó més popular.
3. Guardar les dades extretes en un fitxer CSV.

El script també inclou gestió d'errors per manejar possibles problemes durant les
peticions HTTP i assegura que les dades es netegen i es transformen adequadament
abans de ser guardades.
"""
import time
import random
import re
import requests
from bs4 import BeautifulSoup
from utils import clean_text, parse_number, get_scrape_date, duplicates


HEADERS = {
    "User-Agent": "*",
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,image/apng,*/*;q=0.8"
    ),
    "Accept-Language": "ca-ES,ca;q=0.9,en;q=0.8",
    "Referer": "https://www.last.fm/",
    "Connection": "keep-alive",
}

BASE_URL = "https://www.last.fm"

# Crea una sessió HTTP i reutilitzable per compartir configuració
# entre totes les peticions i evitar repetir headers a cada crida.
session = requests.Session()

# Assigna a la sessió les capçaleres comunes que s'enviaran
# automàticament a totes les peticions al lloc web.
session.headers.update(HEADERS)

def get_soup(url):
    """
    Descarrega la pàgina i la converteix en un objecte BeautifulSoup.
    Retorna None si hi ha algun error en la petició.
    """
    # Bloc control d'errors
    try:
        time.sleep(random.uniform(1.5, 3.0)) # Pausa l'execució entre 1.5 i 3 seg.
        response = session.get(url, timeout=15) # Fa una petició, màxim 15 seg. esperant resposta
        response.raise_for_status() # Si la resposta és 404, 403... es gestiona com error
        return BeautifulSoup(response.text, "html.parser") # Converteix response a BeautifulSoup
    except requests.RequestException as e:
        print(f"Error en descarregar {url}: {e}")
        return None

def _add_artist_link(artists, seen, href, rank=None, source="unknown"):
    """
    Afegeix un artista a la llista si l'URL és vàlida i encara no s'ha vist.
    """
    if not href:
        return False

    if not href.startswith("/music/"):
        return False

    if "/_/" in href or "?" in href:
        return False

    full_url = BASE_URL + href

    if full_url in seen:
        return False

    seen.add(full_url)
    artists.append({
        "artist_url": full_url,
        "rank": rank,
        "scraped_from": source
    })
    return True

def get_artist_links_from_charts(artists, seen, max_artists=2000, max_pages=40):
    """
    Extreu artistes des dels charts paginats.
    """
    for page in range(1, max_pages + 1):
        url = f"{BASE_URL}/charts/weekly?page={page}" # URL completa d'on es troben els artistes.
        soup = get_soup(url) # Descarrega la pàgina

        # Si hi ha un error torna una llista buida
        if soup is None:
            continue

        added_this_page = 0

        for row in soup.find_all("tr"):
            link = row.find("a", href=True) # Cerca un enllaç dins la taula <a> </a>
            # Si no hi ha link a la fila, passa a la següent
            if not link:
                continue

            rank = None # Inicialitza rank
            rank_tag = row.find("td", class_="globalchart-rank") # Cerca la fila que conté el rank
            # converteix el rank a número
            if rank_tag:
                rank = parse_number(rank_tag.get_text())

            added = _add_artist_link(
                artists,
                seen,
                link["href"],
                rank=rank,
                source=f"charts_weekly_page_{page}"
            )
            if added:
                added_this_page += 1

            if len(artists) >= max_artists:
                print(f"[Charts] Límmit assolit: {len(artists)} artistes")
                return artists

        print(f"[Charts] Pàgina {page}: +{added_this_page} artistes | Total: {len(artists)}")

        if added_this_page == 0:
            print("[Charts] No s'han trobat artistes nous en aquesta pàgina.")
            break

    return artists

def get_artist_links_from_tags(artists, seen, max_artists=2000, tags=None, max_pages_per_tag=40):
    """
    Extreu artistes des de pàgines de tags per ampliar el conjunt inicial.
    """
    # Si no troba tags inicializem per defecte
    if tags is None:
        tags = ["pop", "rock", "indie", "electronic", "hip-hop", "reggae", "dance", "metal", "rnb", "hardcore", 
                "jazz", "alternative", "acoustic", "reggaeton", "trap", "latin"]

    # Recorre la llista de tags
    for tag in tags:
        for page in range(1, max_pages_per_tag + 1):
            url = f"{BASE_URL}/tag/{tag}/artists?page={page}"
            soup = get_soup(url)

            if soup is None:
                continue

            added_this_page = 0

            for a in soup.find_all("a", href=True):
                href = a["href"]

                added = _add_artist_link(
                    artists,
                    seen,
                    href,
                    rank=None,
                    source=f"tag_{tag}_page_{page}"
                )
                if added:
                    added_this_page += 1

                if len(artists) >= max_artists:
                    print(f"[Tags] Límit assolit: {len(artists)} artistes")
                    return artists

            print(f"[Tag: {tag}] Pàgina {page}: +{added_this_page} artistes | Total: {len(artists)}")

    return artists


def get_artist_links(max_artists=2000, max_chart_pages=40, max_tag_pages=40):
    """
    Construeix una llista d'artistes combinant diverses fonts:
    1) charts
    2) tags
    """
    artists = [] # Llista per guardar el resultat
    seen = set() # Guardarà les URLs ja vistes

    artists = get_artist_links_from_charts(artists,
                                            seen, max_artists=max_artists,
                                            max_pages=max_chart_pages)

    # Si no hi ha suficient artistes a charts les extreu de tags
    if len(artists) < max_artists:
        artists = get_artist_links_from_tags(artists,
                                            seen, max_artists=max_artists,
                                            max_pages_per_tag=max_tag_pages)

    print(f"[INFO] Total d'artistes únics trobats: {len(artists)}")
    return artists

def scrape_artist(artist_info):
    """
    Visita una pàgina d'artista i retorna un diccionari
    amb les variables que es volen extreure.
    """
    url = artist_info["artist_url"]  # URL de l'artista
    soup = get_soup(url)  # Descarrega la pàgina de l'artista

    # Si ha donat error no retorna res.
    if soup is None:
        return None

    # Dades que es volen extreure
    data = {
        "artist_url": url,
        # Si no hi ha info d'origen, marquem per defecte com a "charts"
        "scraped_from": artist_info.get("scraped_from", "charts"),
        "scraped_date": get_scrape_date(),
        "artist_name": None,
        "listeners": None,
        "scrobbles": None,
        "tags": None,
        "rank": artist_info.get("rank"),
        "latest_release_date": None,
        "similar_artists": None,
        "age": None,
        "bio": None,
        "top_track": None,
    }

    # NOM DE L'ARTISTA
    h1 = soup.find("h1", class_="header-new-title")
    if h1:
        data["artist_name"] = clean_text(h1.get_text())

    # LISTENERS I SCROBBLES
    # Llista de metadades
    metadata_items = soup.find_all("li", class_="header-metadata-tnew-item")
    # Recorre cada bloc de metadades per identificar el títol i el seu valor
    for item in metadata_items:
        # Nom de la mètrica (listeners o scrobbles)
        title_tag = item.find("h4", class_="header-metadata-tnew-title")
        # Valor de la mètrica
        value_tag = item.find("div", class_="header-metadata-tnew-display")

        # Si no troba algun dels dos valors continua
        if not title_tag or not value_tag:
            continue

        # Nateja text i passa a miníscules
        title = clean_text(title_tag.get_text()).lower()

        # Cerca l'etiqueta abbr
        abbr = value_tag.find("abbr")
        # Si troba l'etiqueta abbr i té títol com atribut
        if abbr and abbr.has_attr("title"):
            value = abbr["title"]  # valor exacte de scrobbles o listeners
        # Si no te l'etiqueta títol agafa el text abreujat
        else:
            value = value_tag.get_text()

        # Neteja el valor
        value = clean_text(value)

        # Es posa dins listeners o scrobbles segons el valor de title
        if "listener" in title:
            data["listeners"] = parse_number(value)
        elif "scrobble" in title:
            data["scrobbles"] = parse_number(value)

    # TAGS
    tag_candidates = [] # Guarda els tags trobats

    # Cerca els elements amb classe = tag
    for li in soup.find_all("li", class_="tag"):
        # Dins cada li cerca els que que estan en <a> i tenen URL
        a = li.find("a", href=True)

        # Si no hi ha continua
        if not a:
            continue

        # Extreu el text (tags) i el neteja
        text = clean_text(a.get_text())

        # L'afagim a la llista de tags
        if text:
            tag_candidates.append(text)

    # Elimna tags duplicats
    if tag_candidates:
        unique_tags = duplicates(tag_candidates)
        data["tags"] = "|".join(unique_tags[:5])

    # BIO
    bio = soup.find("div", class_="wiki-block-inner-2")
    if bio:
        data["bio"] = clean_text(bio.get_text(" ", strip=True))[:500] # Nomes cull 500 caràcters

    # TOP TRACK
    # Cerca week al títol
    head = soup.find("h4", string=lambda t: t and "week" in t.lower())
    if head:
        container = head.find_parent() # Cull el bloc que conté h4
        top_track = container.find("a", class_="link-block-target") # Cerca top_track
        # Si la troba, actualitza les dades
        if top_track:
            data["top_track"] = clean_text(top_track.get_text())

    # ARTISTES SIMILARS
    similar = []

    for h3 in soup.find_all("h3", class_="artist-similar-artists-sidebar-item-name"):
        artist = h3.find("a", href=True)
        if artist:
            name = clean_text(artist.get_text())
            if name:
                similar.append(name)

    # Elimna artistes duplicats
    if similar:

        similar_unique = duplicates(similar)
        data["similar_artists"] = "|".join(similar_unique[:5])

    # EDAT
    metadata = soup.find("dl", class_="catalogue-metadata")
    if metadata:
        for dd in metadata.find_all("dd", class_="catalogue-metadata-description"):
            text = clean_text(dd.get_text())

            # Captura age + num
            age = re.search(r"age\s+(\d+)", text.lower())
            if age:
                data["age"] = int(age.group(1)) # Collim el número
                break

    return data
