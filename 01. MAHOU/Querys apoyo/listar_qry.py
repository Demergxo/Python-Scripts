from sqlalchemy import create_engine, text
import pandas as pd
import os

# ===============================================
# ⚙️ CONFIGURACIÓN DE CONEXIÓN
# ===============================================
engine = create_engine("mssql+pyodbc://@XGA_PROD")

# Carpeta para exportar los Excel
carpeta_salida = "export_columns"
os.makedirs(carpeta_salida, exist_ok=True)

# ===============================================
# 🔍 Paso 1: Obtener todas las vistas
# ===============================================WHERE o.type = 'V'
consulta_vistas = text("""
SELECT
    DB_NAME() AS base,
    s.name AS esquema,
    o.name AS vista
FROM sys.objects o
JOIN sys.schemas s ON o.schema_id = s.schema_id

ORDER BY base, esquema, vista
""")

df_vistas = pd.read_sql(consulta_vistas, engine)

if df_vistas.empty:
    print("⚠️ No se encontraron vistas en la base actual.")
    exit()

# ===============================================
# 🔍 Paso 2: Obtener columnas, tipos y descripciones
# ===============================================
for _, fila in df_vistas.iterrows():
    base = fila["base"]
    esquema = fila["esquema"]
    vista = fila["vista"]

    print(f"\n🔹 Procesando vista: [{base}].[{esquema}].[{vista}]")

    consulta_columnas = text(f"""
    SELECT 
        c.name AS columna,
        t.name AS tipo,
        c.max_length,
        c.precision,
        c.scale,
        ep.value AS descripcion
    FROM [{base}].sys.columns c
    JOIN [{base}].sys.types t ON c.user_type_id = t.user_type_id
    LEFT JOIN [{base}].sys.extended_properties ep 
        ON ep.major_id = c.object_id 
        AND ep.minor_id = c.column_id
        AND ep.name = 'MS_Description'
    WHERE c.object_id = OBJECT_ID('{esquema}.{vista}')
    ORDER BY c.column_id
    """)

    try:
        df_col = pd.read_sql(consulta_columnas, engine)
        if df_col.empty:
            print("   ⚠️ No se encontraron columnas o no hay permisos.")
            continue

        # Mapear longitud y precisión según tipo
        def tipo_legible(row):
            tipo = row['tipo'].upper()
            if tipo in ['CHAR', 'NCHAR', 'VARCHAR', 'NVARCHAR']:
                return f"{tipo}({row['max_length']})"
            elif tipo in ['DECIMAL', 'NUMERIC']:
                return f"{tipo}({row['precision']},{row['scale']})"
            else:
                return tipo

        df_col['tipo_completo'] = df_col.apply(tipo_legible, axis=1)
        df_col = df_col[['columna', 'tipo_completo', 'descripcion']]

        # Guardar Excel
        archivo = os.path.join(carpeta_salida, f"{vista}_columns.xlsx")
        df_col.to_excel(archivo, index=False)
        print(f"   ✅ Guardado en: {archivo}")
    except Exception as e:
        print(f"   ⚠️ Error al procesar columnas: {e}")

print(f"\n✅ Proceso completado. Archivos guardados en {os.path.abspath(carpeta_salida)}")
