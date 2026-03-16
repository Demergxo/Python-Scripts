import pandas as pd
import sqlite3
import os

# === CONFIGURACIÓN ===
EXCEL_FILE = r"C:\Users\jgmeras\OneDrive - GXO\Documents\Python Scripts\ProductosClientes.xlsx"         # Ruta al archivo Excel
SHEET_NAME = "Sheet1"                            # Nombre de la pestaña a importar
DB_FILE = "apoyo.db"                         # Nombre de la base de datos SQLite
TABLE_NAME = "maestro_msm"             # Nombre de la tabla en SQLite

# === LECTURA DEL EXCEL ===
print(f"Leyendo archivo Excel '{EXCEL_FILE}'...")
df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)

print(f"Columnas encontradas: {', '.join(df.columns)}")

# === CONEXIÓN A SQLITE ===
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# === CREAR TABLA AUTOMÁTICAMENTE SI NO EXISTE ===
# pandas puede hacerlo automáticamente al escribir el DataFrame
df.to_sql(TABLE_NAME, conn, if_exists='replace', index=False)

# === VERIFICAR RESULTADO ===
print(f"Datos insertados en la tabla '{TABLE_NAME}' de la base '{DB_FILE}'.")

# Opcional: mostrar los primeros registros insertados
consulta = f"SELECT * FROM {TABLE_NAME} LIMIT 5"
resultado = pd.read_sql_query(consulta, conn)
print("\nEjemplo de los primeros registros:")
print(resultado)

# === CERRAR CONEXIÓN ===
conn.close()
print("\n✅ Proceso completado con éxito.")


