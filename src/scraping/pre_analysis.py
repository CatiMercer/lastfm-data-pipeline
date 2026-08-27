"""
Aquest script realitza una anàlisi prèvia del lloc web de Last.fm per avaluar
la seva idoneïtat per al projecte de web scraping. Es comproven diversos aspectes
com el fitxer robots.txt, el sitemap, la grandària estimada del lloc, les tecnologies
utilitzades i el propietari del domini. Aquesta anàlisi ajudarà a determinar si el lloc
és adequat per a l'extracció de dades i si hi ha restriccions que cal tenir en compte.
"""
import requests
import builtwith
import whois


def check_robots():
    """
    Comprova el fitxer robots.txt del lloc web.
    """
    print("\n--- ROBOTS.TXT ---")
    url = "https://www.last.fm/robots.txt"

    # Afegim un timeout de 10 segons per evitar que el script es pengi
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()  # Assegura que la resposta és 200 OK
        print(r.text[:500])
    except requests.exceptions.RequestException as e:
        print(f"Error al accedir a robots.txt: {e}")


def check_sitemap():
    """
    Comprova el sitemap del lloc web.
    """

    print("\n--- SITEMAP ---")
    url = "https://www.last.fm/sitemap-index-secure.xml"

    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()  # Assegura que la resposta és 200 OK
        print(r.text[:500])  # només els primers caràcters
    except requests.exceptions.RequestException as e:
        print(f"Error al accedir al sitemap: {e}")


def check_size():
    """
    Comprova la grandària estimada del lloc web.
    """
    print("\n--- GRANDARIA ESTIMADA ---")
    print("Comprovació manual a Google: site:last.fm")
    print("Conclusió: gran dimensió")


def check_technology():
    """
    Comprova les tecnologies utilitzades pel lloc web.
    """
    print("\n--- TECNOLOGIA ---")
    tech = builtwith.builtwith("https://www.last.fm")
    print(tech)


def check_owner():
    """
    Comprova el propietari del lloc web.
    """
    print("\n--- PROPIETARI ---")
    print(whois.whois('https://www.last.fm/'))


def main():
    """Executa totes les comprovacions d'anàlisi prèvia."""
    check_robots()
    check_sitemap()
    check_size()
    check_technology()
    check_owner()


if __name__ == "__main__":
    main()
