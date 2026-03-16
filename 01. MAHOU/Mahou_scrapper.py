import requests
from bs4 import BeautifulSoup
import time

BASE_URL = "https://www.mahou-sanmiguel.com"
SEARCH_URL = f"{BASE_URL}/tienda/resultados-busqueda"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0"
}

# Cambia esto por el nombre general del producto (ej: "maestra")
SEARCH_TERM = "mahou"

def get_search_results(page=0):
    params = {
        "q": SEARCH_TERM,
        "lang": "es_ES",
        "start": page * 12  # 12 productos por página
    }
    response = requests.get(SEARCH_URL, headers=HEADERS, params=params, verify=False)
    soup = BeautifulSoup(response.text, "html.parser")
    product_links = []

    for a in soup.select("a.product_link"):
        href = a.get("href")
        if href:
            full_url = BASE_URL + href #type:ignore
            product_links.append(full_url)

    return product_links

def check_code_in_product(url, code="4839"):
    response = requests.get(url, headers=HEADERS, verify=False)
    if code in response.text:
        print(f"✅ Encontrado el código {code} en: {url}")
        return True
    return False

def main():
    page = 0
    all_found = []
    while True:
        print(f"🔍 Buscando página {page+1}...")
        links = get_search_results(page)

        if not links:
            break

        for link in links:
            print(f"Revisando {link}")
            if check_code_in_product(link):
                all_found.append(link)

            time.sleep(0.5)  # Para no sobrecargar el servidor

        page += 1

    if all_found:
        print("\n🚀 Productos con el código encontrado:")
        for url in all_found:
            print(url)
    else:
        print("\n❌ No se encontró el código en los productos.")

if __name__ == "__main__":
    main()
