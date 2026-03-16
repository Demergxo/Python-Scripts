from sqlalchemy import create_engine, text

# ===============================================
# ⚙️ CONFIGURACIÓN DE CONEXIÓN
# ===============================================
# Conéctate a cualquier base accesible, por ejemplo tu base principal
engine = create_engine("mssql+pyodbc://@XGA_PROD")#?driver=ODBC+Driver+17+for+SQL+Server

# Bases dentro de XGA/dbo a las que tienes acceso
bases_permitidas = [
    "vClientes",
    "vDocumentoConsulta",
    "vDocumentos",
    "vDocumentosExtraccion",
    "vDocumentosObsLogisticas",
    "vlnfDocsTrans",
    "vPendientesDistribucion"
    # ... agrega aquí todas las que sabes que puedes consultar
]

# Archivo de salida
archivo_encontradas = "bases_con_registro.txt"

# ===============================================
# 🔹 Revisar solo el esquema dbo en cada base
# ===============================================
bases_encontradas = []

with engine.connect() as conn:
    for base in bases_permitidas:
        try:
            # Tablas que tengan ambas columnas en dbo
            tablas = conn.execute(text(f"""
                SELECT TABLE_NAME
                FROM [{base}].INFORMATION_SCHEMA.COLUMNS
                WHERE COLUMN_NAME IN ('ID_Cliente', 'AlbaranDoc')
                  AND TABLE_SCHEMA = 'dbo'
                GROUP BY TABLE_NAME
                HAVING COUNT(DISTINCT COLUMN_NAME) = 2
            """)).fetchall()

            for (tabla,) in tablas:
                query = text(f"""
                    SELECT TOP 1 1
                    FROM [{base}].[dbo].[{tabla}]
                    WHERE ID_Cliente = 944 AND AlbaranDoc = '15352933'
                """)
                result = conn.execute(query).fetchone()
                if result:
                    bases_encontradas.append(base)
                    print(f"✅ Registro encontrado en la base: {base}, tabla: dbo.{tabla}")
                    break  # No necesitamos seguir buscando en esta base

        except Exception as e:
            print(f"⚠️ Error en base {base}: {e}")
            continue

# ===============================================
# 🔹 Guardar resultados en TXT
# ===============================================
with open(archivo_encontradas, "w") as f_out:
    for b in bases_encontradas:
        f_out.write(f"{b}\n")

print(f"\n✅ Proceso completado. Bases con registro guardadas en {archivo_encontradas}")