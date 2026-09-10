import os
import re
import pdfplumber
import pandas as pd
from datetime import datetime

date = datetime.now().strftime("%Y%m%d%H%M%S")
user = os.getenv("USERNAME")
path = rf"C:\Users\{user}\OneDrive - GXO\Escritorio"


CARPETA_PDF = rf"{path}\PDFs"
CSV_SALIDA = f"resultado_{date}.csv"

datos = []

for archivo in os.listdir(CARPETA_PDF):
    if archivo.lower().endswith(".pdf"):

        ruta_pdf = os.path.join(CARPETA_PDF, archivo)

        try:
            texto = ""

            with pdfplumber.open(ruta_pdf) as pdf:
                for pagina in pdf.pages:
                    texto += (pagina.extract_text() or "") + "\n"

            pedido = None
            bultos = None

            m = re.search(r"Pedido Cliente[:\s]+(\d+)", texto, re.I)
            if m:
                pedido = m.group(1)

            m = re.search(r"Bultos[:\s]+([\d.,]+)", texto, re.I)
            if m:
                bultos = m.group(1)

            datos.append({
                "Archivo": archivo,
                "Pedido_Cliente": pedido,
                "Bultos": bultos
            })

        except Exception as e:
            print(f"Error en {archivo}: {e}")

df = pd.DataFrame(datos)
df.to_csv(CSV_SALIDA, sep=";", index=False, encoding="utf-8-sig")

print(f"CSV generado: {CSV_SALIDA}")