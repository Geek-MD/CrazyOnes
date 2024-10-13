import requests
from bs4 import BeautifulSoup
import yaml

# URL a scrapear
url = "https://support.apple.com/en-us/100100"

try:
    # Hacer la solicitud
    response = requests.get(url)
    response.raise_for_status()  # Asegurarse de que no hubo error en la solicitud

    # Parsear el contenido HTML
    soup = BeautifulSoup(response.content, "html.parser")

    # Buscar todos los tags <link> con hreflang
    hreflangs = {}
    for link in soup.find_all("link", hreflang=True):
        hreflang = link.get("hreflang")
        href = link.get("href")
        hreflangs[hreflang] = href

    # Guardar en un archivo YAML
    with open("auror_hreflang_links.yaml", "w") as yaml_file:
        yaml.dump(hreflangs, yaml_file, default_flow_style=False)

    print("Successful scraping. YAML file created.")

except requests.exceptions.RequestException as e:
    print(f"Request failure: {e}")
    exit(1)
except Exception as e:
    print(f"Error with scraping o file storing: {e}")
    exit(1)
