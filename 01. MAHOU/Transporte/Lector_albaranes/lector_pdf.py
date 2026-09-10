import os
import re
import pdfplumber
import pandas as pd
from datetime import datetime

# ------------------ CONFIGURACION ------------------
date = datetime.now().strftime("%Y%m%d%H%M%S")
user = os.getenv("USERNAME")
path = rf"C:\Users\{user}\OneDrive - GXO\Escritorio"

CARPETA_PDF = rf"{path}\PDFs"
CSV_SALIDA = f"resultado_{date}.csv"
# ---------------------------------------------------

# Patrones sobre el texto (una linea por campo, formato Mahou/GXO)
RE_DOC    = re.compile(r"Documento\s+([A-Z]{2}\s*\d+)\s+Fecha", re.I)
RE_PEDIDO = re.compile(r"Pedido\s+Cliente:\s*(\S+)", re.I)
RE_BULTOS = re.compile(r"Bultos\s+([\d.,]+)", re.I)

# Numero entero admitiendo separador de miles (9, 24, 1.200 ...)
RE_INT = re.compile(r"^\d{1,3}(?:\.\d{3})*$")


def a_entero(s):
    """1.200 -> 1200 ; 24 -> 24"""
    return int(s.replace(".", ""))


def suma_cantidad(pagina):
    """
    Suma la columna 'Cantidad' usando las coordenadas de las cabeceras,
    para no confundirla con 'Unidades Consumo'.
    """
    palabras = pagina.extract_words()

    cab = {w["text"]: w for w in palabras
           if w["top"] < 400 and w["text"] in ("EAN", "Cantidad", "Palets")}

    # Si la pagina no tiene la tabla estandar, devolvemos 0
    if not {"EAN", "Cantidad", "Palets"} <= set(cab):
        return 0

    x_izq = cab["EAN"]["x1"]          # limite izq de la columna Cantidad
    x_der = cab["Palets"]["x0"]       # limite der de la columna Cantidad
    y_ini = cab["Cantidad"]["top"]

    # La tabla acaba en 'Observaciones...'
    y_fin = min([w["top"] for w in palabras
                 if w["text"].startswith("Observaciones")], default=10**9)

    total = 0
    for w in palabras:
        centro = (w["x0"] + w["x1"]) / 2
        if x_izq < centro < x_der and y_ini + 3 < w["top"] < y_fin and RE_INT.match(w["text"]):
            total += a_entero(w["text"])
    return total


datos = []

for raiz, _, archivos in os.walk(CARPETA_PDF):

    for archivo in archivos:

        if not archivo.lower().endswith(".pdf"):
            continue

        ruta_pdf = os.path.join(raiz, archivo)

        try:
            with pdfplumber.open(ruta_pdf) as pdf:

                for num_pagina, pagina in enumerate(pdf.pages, start=1):

                    texto = pagina.extract_text() or ""

                    if "Pedido Cliente" not in texto or "Bultos" not in texto:
                        continue

                    

                    documento = None
                    pedido = None
                    bultos = None

                    m = RE_DOC.search(texto)
                    if m:
                        documento = m.group(1)[2:].strip()   # sin los 2 primeros caracteres

                    m = RE_PEDIDO.search(texto)
                    if m:
                        pedido = m.group(1)

                    m = RE_BULTOS.search(texto)
                    if m:
                        bultos = m.group(1)

                    total_cantidad = suma_cantidad(pagina)

                        
                    ruta_relativa = os.path.relpath(ruta_pdf, CARPETA_PDF)

                    datos.append({
                        "Ruta": ruta_relativa,
                        "Archivo": archivo,
                        "Pagina": num_pagina,
                        "Documento": documento,
                        "Pedido_Cliente": pedido,
                        "Bultos": bultos,
                        "Total_Cantidad": total_cantidad
                    })

        except Exception as e:
            print(f"Error en {archivo}: {e}")

df = pd.DataFrame(datos)
df.to_csv(CSV_SALIDA, sep=";", index=False, encoding="utf-8-sig")

print(f"CSV generado: {CSV_SALIDA}  ({len(df)} albaranes)")
