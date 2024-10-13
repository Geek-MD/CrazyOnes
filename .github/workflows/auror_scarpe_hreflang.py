import requests
from bs4 import BeautifulSoup
import yaml

# URL a scrapear
url = "https://support.apple.com/en-us/100100"

# Hacer la solicitud
response = requests.get(url)
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
