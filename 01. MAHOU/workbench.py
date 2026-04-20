import os
import requests
from urllib.parse import quote

user = "JGMERAS"
password = "M1j3kMICrdmxlRFVY0g1"

base_url = "http://10.19.16.125"
download_path = "/fga/MtoDocumentosTr/DescargaFicheroSubestado"

ruta = r"\\toucifs02.em.co.gxo.com\share_IBE_CIFS\Exchange\Backup\202604\1084\BackIn\I1084_2604060640566425040000-8411327000017@SEDEB2B.COM-SM-90807314-3183-11F1-B388-CB7583D1557E"

# Codificar correctamente
ruta_codificada = quote(ruta)

url = f"{base_url}{download_path}?nombrefichero={ruta_codificada}"

session = requests.Session()
session.headers.update({"User-Agent":"Mozilla/5.0",})

# 1. Entrar en la URL preotegida para que el servidor nos redirija al login
r1 = session.get(url, allow_redirects=True, timeout=30)
print("Paso 1:",r1.status_code, r1.url)

# 2. Construir la URL de login
login_url = r1.url

payload = {
    "Nombre": user,
    "password": password,
    "ActualizarPassword": "False",
    "Agenda": "False",
    "Error": "",
    "Login": "Aceptar",
}

headers = {
    "Refer": r1.url,
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

# 3. Enviar login
r2 = session.post(login_url, data=payload, headers=headers, allow_redirects=True, timeout=30)
print("Paso 2:", r2.status_code, r2.url)

# 4. Intentar la descarga otra vez con la sesión autorizada
r3 = session.get(url, stream=True, timeout=60)
print("Paso 3:", r3.status_code)
print("Content-Type:", r3.headers.get("Content-Type"))
print("Content-Disposition:", r3.headers.get("Content-Disposition"))

# 5. Comprobar si sigue devolviendo html
content_type = (r3.headers.get("Content-Type") or "").lower()

if r3.status_code == 200 and "text/html" not in content_type:
    filename = "ejemplo.edi"

    #probar capturar el nombre que manda el server
    content_disposition = r3.headers.get("Content-Disposition", "")
    if "filename" in content_disposition:
        filename = content_disposition.split("filename=")[-1].strip().strip('"')
    
    with open(filename, "wb") as f:
            for chunk in r3.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    
    
    print(f"Archivo guardado como {filename}")
else:
     #Guardamos la respuesta
    with open("error_response.html", "w", encoding="utf-8") as f:
        f.write(r3.text)
        print("Se ha guardado la respuesta HTML de error en 'error_response.html'")
    
    print("La descarga falló. Se obtuvo una respuesta HTML de error." )
    print("Se ha guardado la respuesta en 'error_response.html'")
          
    
