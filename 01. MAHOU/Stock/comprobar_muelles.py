from sqlalchemy import create_engine, text #type:ignore
import pandas as pd
from datetime import datetime

import shutil
from tabulate import tabulate
from colorama import init, Fore, Style

import re

PATRON_MUELLE = re.compile(r"^(DE|CA|CP)00\d{3}00$")
PATRON_T_MUELLES = re.compile(r"^(DE|CA|CP)")

def pedir_muelle():
    while True:
        muelle = input("Introduzca código de muelle (DE00XXX00): ").strip().upper()
        if PATRON_MUELLE.fullmatch(muelle):
            return muelle
        print(centrar("❌ Formato incorrecto. Debe ser DE00 + 3 números + 00 (ej: DE0005500)", Fore.RED))

def todos_muelles():
    while True:
        muelles = input("Introduzca zona de muelles: ").strip().upper()
        if PATRON_T_MUELLES.match(muelles):
            return muelles
        print(centrar("❌ Formato incorrecto. Debe ser DE | CA | CP", Fore.RED))

init(autoreset=True)

date = datetime.now().strftime("%Y%m%d%H%M%S")

def centrar(texto, color=Fore.CYAN):
    ancho = shutil.get_terminal_size().columns
    return color + texto.center(ancho) + Style.RESET_ALL

def hora():
    hora = datetime.now().strftime("%H:%M:%S")
    return hora

print(f"Hora de inicio: {hora()}")

# --- CONEXIÓN SQLALCHEMY ---

def comprobar_1_muelle():

    muelle = pedir_muelle()

    engine = create_engine("mssql+pyodbc://@XGA_PROD")

    # --- QUERY SQL (rango de fechas) ---
    query = text("""
        SELECT *
        FROM (
            SELECT
                CONCAT(ZonaUbicacion, PasilloUbicacion, HuecoUbicacion, NivelUbicacion) AS [Ubicacion],
                CodigoProdClte AS [Referencia],
                NombreProdClte AS [Descripción],
                CantidadActualPalet AS [Cantidad],
                SSCCPalet AS [SSCC]
            FROM vUbicacionesProducto
            WHERE ID_Cliente = 944
            AND ID_Almacen = 221
        ) AS sub
        WHERE Ubicacion LIKE :muelle
    """)

    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params={"muelle": muelle})
   

    # --- EJECUTAR CONSULTA ---
    print(centrar(f"🔍 Revisando muelle {muelle}...", Fore.YELLOW))

    if df.empty:
        print(centrar("⚠️ No se han encontrado resultados", Fore.RED))
        return

    tabla = tabulate(
        df, #type: ignore
        headers="keys",
        tablefmt="fancy_grid",
        showindex=False,
        stralign="center",
        numalign="center"
    )

# Centramos cada línea de la tabla respecto al ancho de terminal
    ancho = shutil.get_terminal_size().columns
    for linea in tabla.split("\n"):
        print(linea.center(ancho))

    print(centrar(f"✅ Consulta finalizada a las {hora()}", Fore.CYAN))


if __name__ == "__main__":  
    comprobar_1_muelle()
    
def comprobar_todos_los_muelles():

    amuelle = todos_muelles()
    
    engine = create_engine("mssql+pyodbc://@XGA_PROD")

    # --- QUERY SQL (rango de fechas) ---
    query = text("""
        SELECT *
        FROM (
            SELECT
                CONCAT(ZonaUbicacion, PasilloUbicacion, HuecoUbicacion, NivelUbicacion) AS [Ubicacion],
                CodigoProdClte AS [Referencia],
                NombreProdClte AS [Descripción],
                CantidadActualPalet AS [Cantidad],
                SSCCPalet AS [SSCC]
            FROM vUbicacionesProducto
            WHERE ID_Cliente = 944
            AND ID_Almacen = 221
        ) AS sub
        WHERE ZonaUbicacion = :muelle
    """)

    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params={"muelle": amuelle})
       
    # --- EXPORTAR ---
    nombre_archivo = f"muelles_{date}.xlsx"
    df.to_excel(nombre_archivo, index=False)

    print(f"✅ Archivo generado correctamente: {nombre_archivo}")

    print(f"Hora de fin: {hora()}")
    engine.dispose()
    
if __name__ == "__main__":  
    comprobar_1_muelle()
  