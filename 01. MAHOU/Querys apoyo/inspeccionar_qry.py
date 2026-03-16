from sqlalchemy import create_engine, text
import pandas as pd
import os

# ===============================================
# ⚙️ CONFIGURACIÓN DE CONEXIÓN
# ===============================================
# Ejemplo con DSN ODBC configurado:
# engine = create_engine("mssql+pyodbc://usuario:contraseña@NombreDSN?driver=ODBC+Driver+17+for+SQL+Server")

# Si ya tienes el engine definido, puedes importarlo:
# from conexion import engine

# ===============================================
# 📂 Carpeta donde guardar los archivos .sql
# ===============================================
engine = create_engine("mssql+pyodbc://@XGA_PROD")
carpeta_salida = "export_views"
os.makedirs(carpeta_salida, exist_ok=True)

# ===============================================
# 🔍 Paso 1: Buscar todas las vistas que empiecen por 'qry_'
# ===============================================
print("🔎 Buscando todas las vistas que empiecen por 'qry_' en el servidor...\n")

consulta_busqueda = text("""
EXEC sp_MSforeachdb '
    USE [?];
    SELECT
        DB_NAME() AS base,
        s.name AS esquema,
        o.name AS objeto,
        OBJECTPROPERTY(o.object_id, ''IsEncrypted'') AS encriptada
    FROM sys.objects o
    JOIN sys.schemas s ON o.schema_id = s.schema_id
    WHERE o.type = ''V''
      AND o.name LIKE ''QRY%''
'
""")

try:
    df_vistas = pd.read_sql(consulta_busqueda, engine)
except Exception as e:
    print("❌ Error al obtener la lista de vistas:")
    print(e)
    exit()

if df_vistas.empty:
    print("⚠️ No se encontraron vistas 'qry_...' accesibles con tus credenciales.")
    exit()

print(f"✅ Se encontraron {len(df_vistas)} vistas.\n")

# ===============================================
# 🧩 Paso 2: Comprobar permisos y obtener definiciones
# ===============================================
for _, fila in df_vistas.iterrows():
    base = fila["base"]
    esquema = fila["esquema"]
    vista = fila["objeto"]
    encriptada = fila["encriptada"]

    print(f"🔹 [{base}].[{esquema}].[{vista}]")

    if encriptada:
        print("   🔒 Encriptada — no se puede leer la definición.")
        continue

    try:
        consulta_def = text(f"""
        SELECT definition
        FROM [{base}].sys.sql_modules
        WHERE object_id = OBJECT_ID('{base}.{esquema}.{vista}');
        """)

        df_def = pd.read_sql(consulta_def, engine)
        if df_def.empty or df_def.iloc[0, 0] is None:
            print("   🚫 Sin permiso para ver la definición (falta VIEW DEFINITION).")
        else:
            definicion = df_def.iloc[0, 0]
            archivo = os.path.join(carpeta_salida, f"{vista}.txt")
            with open(archivo, "w", encoding="utf-8") as f:
                f.write(definicion)
            print(f"   🧾 Guardado en: {archivo}")
    except Exception as e:
        print(f"   ⚠️ Error al intentar leer '{vista}': {e}")

print("\n✅ Proceso completado.")
print(f"📁 Archivos guardados en: {os.path.abspath(carpeta_salida)}")
