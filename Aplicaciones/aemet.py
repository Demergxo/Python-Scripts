import requests
import json
import datetime


API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJqYXZpZXIuZ2FyY2lhLW1lcmFzLXBhbGFjaW9zQGd4by5jb20iLCJqdGkiOiIyZmIwMTYzZi0wY2EwLTRmOGEtYTZjYi00NzU5MmYzZDJmNzYiLCJpc3MiOiJBRU1FVCIsImlhdCI6MTc3MjAyODE0NSwidXNlcklkIjoiMmZiMDE2M2YtMGNhMC00ZjhhLWE2Y2ItNDc1OTJmM2QyZjc2Iiwicm9sZSI6IiJ9.QQ0B1wtraCTe7FcTIwSlW7yaG7BN0xYPngjmItJgtRI"

ccaa = "clm"

provincia = "19" # Guadalajara
api_url = f"https://opendata.aemet.es/opendata//api/prediccion/provincia/manana/{provincia}"       



# Añadir encabezados
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0"
}
def get_predict(api_url, headers, API_KEY):

      
    # fecha = datetime.datetime.now().strftime("%Y-%m-%d")
    # sufix = f"/api/prediccion/provincia/hoy/{provincia}/elaboracion/{fecha}"
    # url_full = api_url + sufix
    request = requests.get(api_url, headers=headers, params={"api_key": API_KEY}, timeout=30)
    request.raise_for_status()
    info = request.json()


    # comprobar estado
    estado = info.get("estado")
    if estado and estado != 200:
        raise RuntimeError(f"AEMET devolvió estado {estado}: {info.get('descripcion')}")

    data_url = info["datos"] 

    # descargar el recurso real
    # Primero SIN api_key adicional; si falla, probamos con api_key
    r_data = requests.get(data_url, headers=headers, timeout=60)
    if r_data.status_code >= 400 or not r_data.text.strip():
        r_data = requests.get(data_url, headers=headers, params={"api_key": API_KEY}, timeout=60)
    r_data.raise_for_status()

    content_type = r_data.headers.get("Content-Type", "").lower()

    # Intentar parsear como JSON solo si es JSON o si el texto empieza por '[' o '{'
    text = r_data.text.strip()
    is_probably_json = ("application/json" in content_type) or text[:1] in ("[", "{")


    if is_probably_json:
        try:
            prediccion = r_data.json()
        except ValueError:
            prediccion = text  # no era JSON válido, nos quedamos el texto
    else:
        prediccion = text  # puede ser XML o texto normalizado

    #print("Content-Type:", content_type)
    #print("Tipo de resultado:", type(prediccion))
    return prediccion

prediccion = get_predict(api_url, headers, API_KEY)

print(str(prediccion))

print("\n")
print("*"*32)
print("\n")

api_url = "https://opendata.aemet.es/opendata/api/prediccion/nacional/medioplazo"

prediccion = get_predict(api_url, headers, API_KEY)

print(str(prediccion))


print("\n")
print("*"*32)
print("\n")