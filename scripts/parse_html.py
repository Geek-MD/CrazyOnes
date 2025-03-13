import os
import json
from bs4 import BeautifulSoup

# Directorios de trabajo
HTML_DIR = "html"
JSON_DIR = "json"

# Asegurar que el directorio json existe
os.makedirs(JSON_DIR, exist_ok=True)

def parse_html(file_path):
    """Parsea una tabla en un archivo HTML y devuelve su contenido en formato JSON."""
    with open(file_path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "lxml")

    # Buscar la tabla dentro del contenedor con clase "table-wrapper gb-table"
    table = soup.select_one(".table-wrapper .gb-table")
    if not table:
        print(f"No se encontró la tabla en {file_path}")
        return []

    rows = table.find_all("tr")[1:]  # Omitir la primera fila (header)
    
    data = []
    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 3:
            continue  # Omitir filas sin suficientes columnas

        update_name = cols[0].get_text(strip=True)
        update_link = cols[0].find("a")["href"] if cols[0].find("a") else None
        description = cols[1].get_text(strip=True)
        update_date = cols[2].get_text(strip=True)

        data.append({
            "update_name": update_name,
            "update_link": update_link,
            "description": description,
            "update_date": update_date
        })

    return data

def main():
    """Procesa todos los archivos HTML y guarda su contenido en JSON."""
    for filename in os.listdir(HTML_DIR):
        if filename.endswith(".html"):
            html_path = os.path.join(HTML_DIR, filename)
            json_path = os.path.join(JSON_DIR, filename.replace(".html", ".json"))

            parsed_data = parse_html(html_path)
            if parsed_data:
                with open(json_path, "w", encoding="utf-8") as json_file:
                    json.dump(parsed_data, json_file, indent=4, ensure_ascii=False)

                print(f"✅ Procesado: {filename} → {json_path}")
            else:
                print(f"⚠️ Sin datos: {filename}")

if __name__ == "__main__":
    main()
