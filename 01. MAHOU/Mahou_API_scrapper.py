import requests
import time

BASE_URL = "https://www.mahou-sanmiguel.com"
SEARCH_API = f"{BASE_URL}/ccstoreui/v1/search"
PRODUCT_API = f"{BASE_URL}/ccstoreui/v1/products"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

SEARCH_TERM = "maestra"  # Puedes cambiar por "mah" para ampliar

def buscar_productos(search_term, offset=0):
    params = {
        "q": search_term,
        "offset": offset,
        "limit": 24  # máximo visible
    }
    resp = requests.get(SEARCH_API, headers=HEADERS, params=params, verify=False)
    data = resp.json()
    items = data.get("records", [])
    return [item.get("productId") for item in items]

def obtener_info_producto(product_ids):
    ids = ",".join(product_ids)
    resp = requests.get(f"{PRODUCT_API}?productIds={ids}", headers=HEADERS, verify=False)
    return resp.json()

def main():
    offset = 0
    encontrados = []
    while True:
        print(f"🔎 Buscando productos (offset={offset})...")
        ids = buscar_productos(SEARCH_TERM, offset)
        if not ids:
            break

        data = obtener_info_producto(ids)
        for prod in data.get("items", []):
            pid = prod.get("id")
            name = prod.get("displayName")
            desc = prod.get("description", "")
            full = f"{name} {desc}".lower()
            if "4839" in full:
                print(f"✅ Encontrado código 4839: {name} -> ID: {pid}")
                encontrados.append((pid, name))

        offset += 24
        time.sleep(1)

    if encontrados:
        print("\n🚀 Resultados encontrados:")
        for pid, name in encontrados:
            print(f" - {name} (productId: {pid})")
    else:
        print("\n❌ No se encontró el código 4839 en los productos.")

if __name__ == "__main__":
    main()
