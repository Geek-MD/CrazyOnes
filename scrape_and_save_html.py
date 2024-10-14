import os
import requests
import yaml

# Leer el archivo hreflang_links.yaml
with open("html/hreflang_links.yaml", "r") as yaml_file:
    hreflangs = yaml.safe_load(yaml_file)

# Crear el directorio 'html' si no existe
os.makedirs("html", exist_ok=True)

# Scraping de cada URL y guardado en archivos HTML
for hreflang, url in hreflangs.items():
    file_path = f"html/{hreflang}.html"
    
    try:
        # Hacer la solicitud a la URL
        response = requests.get(url)
        response.raise_for_status()  # Asegurarse de que la solicitud fue exitosa
        new_content = response.text

        # Verificar si el archivo ya existe
        if os.path.exists(file_path):
            # Leer el contenido existente del archivo
            with open(file_path, "r", encoding="utf-8") as html_file:
                old_content = html_file.read()

            # Comparar el contenido nuevo con el existente
            if old_content == new_content:
                print(f"No changes for {file_path}. Skiping...")
                continue  # Saltar al siguiente si no hay cambios

        # Guardar el nuevo contenido en el archivo HTML si no existe o si ha cambiado
        with open(file_path, "w", encoding="utf-8") as html_file:
            html_file.write(new_content)

        print(f"Stored: {file_path}")

    except requests.exceptions.RequestException as e:
        print(f"Error when downloading {url}: {e}")
