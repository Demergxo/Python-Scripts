import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

# URL de la página que quieres analizar
url = "http://10.19.16.125/fga/MenuPrincipal/MenuPrincipal?UltimoLogin=10%2F21%2F2025%2008%3A23%3A52"

# 1️⃣ Obtener el HTML de la página
resp = requests.get(url)
html = resp.text

# 2️⃣ Extraer todos los links de la página
soup = BeautifulSoup(html, "html.parser")
links = [a.get("href") for a in soup.find_all("a") if a.get("href")]

# 3️⃣ Intentar acceder a cada link y ver si devuelve JSON
for link in links:
    full_url = urljoin(url, link)  # Hace que los links relativos sean absolutos
    try:
        r = requests.get(full_url, timeout=3)
        # Revisamos si el contenido es JSON
        if "application/json" in r.headers.get("Content-Type", ""):
            print(f"[JSON API encontrada] {full_url}")
    except Exception as e:
        continue
