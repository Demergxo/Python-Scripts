import sqlite3
import pandas as pd

# Ruta del archivo SQLite
ruta_db = r"C:\Users\jgmeras\Documents\Python Scripts\Aplicaciones\Querys_xga\clientes.db"

# Conectarse a la base de datos
conn = sqlite3.connect(ruta_db)
cursor = conn.cursor()

# 1️⃣ Obtener la lista de tablas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tablas = [fila[0] for fila in cursor.fetchall()]

print(f"Tablas encontradas: {tablas}\n")

# 2️⃣ Mostrar los 5 primeros registros de cada tabla
for tabla in tablas:
    print(f"📋 Tabla: {tabla}")
    try:
        df = pd.read_sql_query(f"SELECT * FROM {tabla} LIMIT 5;", conn)
        if df.empty:
            print("   (sin registros)")
        else:
            print(df)
    except Exception as e:
        print(f"   ⚠️ Error leyendo la tabla {tabla}: {e}")
    print("-" * 60)

# Cerrar conexión
conn.close()
