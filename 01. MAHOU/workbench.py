import pyodbc
import os
import pandas as pd

def con_dsn():
    dsns = pyodbc.dataSources()

    print("DSN encontrados: ")
    for nombre, driver in dsns.items():
        print(f"- {nombre}: {driver}")

    for dsn in dsns:
        try:
            conn = pyodbc.connect(f"DSN={dsn};Trusted_Connection=Yes;")
            print(f"✅ Conectado a: {dsn}")
            break
        except:

            pass

def leer_excel(archivo):
    df = pd.read_excel(archivo,
    usecols = ["Fecha Expedición", "Tipo Doc", "Nº Documento", "On Time", "Observaciones"]
    )
    df_filtrado = df[df["Tipo Doc"] != "REC"]
    df_filtrado = df_filtrado.rename(columns={"Nº Documento": "AlbaranDoc"})
    df_filtrado["AlbaranDoc"] = df_filtrado["AlbaranDoc"].astype(str).str.strip()
    
    #return df_filtrado
    print(df_filtrado)

leer_excel(r"C:\Users\jgmeras\OneDrive - GXO\Escritorio\KPIS Transporte MSM.xlsx")