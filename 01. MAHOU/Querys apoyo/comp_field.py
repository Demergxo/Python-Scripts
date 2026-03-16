import sqlite3
import pandas as pd
import os

# Ruta a tu base de datos SQLite
db_path = "clientes.db"  # cámbiala por la tuya

# Nombre del archivo de salida
excel_path = "export_sqlite.xlsx"

# =======================================
# 1️⃣ Conexión a la base de datos
# =======================================
if not os.path.exists(db_path):
    print(f"❌ No se encontró la base de datos en {db_path}")
else:
    print(f"✅ Conectando a {db_path}...")
    conn = sqlite3.connect(db_path)

    # =======================================
    # 2️⃣ Obtener las tablas disponibles
    # =======================================
    tablas = pd.read_sql_query(
        "SELECT name FROM sqlite_master WHERE type='table';", conn
    )["name"].tolist()

    print(f"📋 Tablas encontradas: {tablas}")

    # =======================================
    # 3️⃣ Crear el Excel y exportar cada tabla
    # =======================================
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        for tabla in tablas:
            print(f"➡ Exportando tabla: {tabla}")

            # Cargar los datos de la tabla
            df = pd.read_sql_query(f"SELECT * FROM {tabla}", conn)

            # Si existe la columna AlbaranDoc, la renombramos
            if "AlbaranDoc" in df.columns:
                df = df.rename(columns={"AlbaranDoc": "Nº Documento"})
                print("   🏷 Columna 'AlbaranDoc' renombrada a 'Nº Documento'")

            # Mostrar si Transporte está presente
            if "Transporte" in df.columns:
                print("   🚚 Columna 'Transporte' detectada correctamente")
            else:
                print("   ⚠ La columna 'Transporte' NO está en esta tabla")

            # Exportar la tabla a una hoja del Excel
            df.to_excel(writer, sheet_name=tabla[:31], index=False)

        print(f"✅ Exportación completada: {excel_path}")

    conn.close()
