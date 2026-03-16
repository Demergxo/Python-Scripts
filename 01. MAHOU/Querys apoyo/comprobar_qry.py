from sqlalchemy import create_engine, text
import pandas as pd

# ===============================================
# ⚙️ CONFIGURACIÓN DE CONEXIÓN
# ===============================================
# Ejemplo de conexión ODBC (ajústalo a tu caso)
# engine = create_engine(
#     "mssql+pyodbc://usuario:contraseña@NombreDSN"
#     "?driver=ODBC+Driver+17+for+SQL+Server"
# )

# Si ya tienes tu 'engine' definido en otro módulo, impórtalo:
# from conexion import engine

# ===============================================
# 🧩 NOMBRE DE LA VISTA A CONSULTAR
# ===============================================
# Usando un DSN ODBC
engine = create_engine("mssql+pyodbc://jgmeras:AloveraMSM25$@XGA_PROD")

nombre_vista = "QRYKPIServicio"  # <- cambia aquí el nombre exacto

# ===============================================
# 🔍 Paso 1: Buscar si existe en la base actual
# ===============================================
consulta = text("""
SELECT 
    DB_NAME() AS base,
    s.name AS esquema,
    o.name AS objeto,
    o.type_desc AS tipo,
    OBJECTPROPERTY(o.object_id, 'IsEncrypted') AS encriptada
FROM sys.objects o
JOIN sys.schemas s ON o.schema_id = s.schema_id
WHERE o.name = :nombre
""")

df = pd.read_sql(consulta, con=engine, params={"nombre": nombre_vista})

if df.empty:
    print(f"⚠️ No se encontró '{nombre_vista}' en la base actual.")
    print("🔎 Buscando en otras bases accesibles...\n")

    # ===============================================
    # 🔄 Paso 2: Buscar en todas las bases del servidor
    # ===============================================
    buscar_todas = text("""
    DECLARE @nombre NVARCHAR(255) = :nombre;
    EXEC sp_MSforeachdb '
        USE [?];
        SELECT
            DB_NAME() AS base,
            s.name AS esquema,
            o.name AS objeto,
            o.type_desc AS tipo,
            OBJECTPROPERTY(o.object_id, ''IsEncrypted'') AS encriptada
        FROM sys.objects o
        JOIN sys.schemas s ON o.schema_id = s.schema_id
        WHERE o.name = ''' + @nombre + ''''
    """)

    try:
        df_all = pd.read_sql(buscar_todas, engine, params={"nombre": nombre_vista})
        if df_all.empty:
            print("❌ No se encontró la vista en ninguna base accesible con tus credenciales.")
            exit()
        else:
            print("✅ Se encontró en otra base:")
            print(df_all)
            base_encontrada = df_all.iloc[0]["base"]
            esquema = df_all.iloc[0]["esquema"]
            encriptada = df_all.iloc[0]["encriptada"]
    except Exception as e:
        print("⚠️ No se pudieron consultar todas las bases (falta de permisos).")
        print(e)
        exit()

else:
    fila = df.iloc[0]
    base_encontrada = fila["base"]
    esquema = fila["esquema"]
    encriptada = fila["encriptada"]

    print(f"✅ Se encontró '{nombre_vista}' en la base [{base_encontrada}], esquema [{esquema}]")
    print(f"Tipo: {fila['tipo']}")
    print(f"Encriptada: {'Sí 🔒' if encriptada else 'No 🟢'}\n")

# ===============================================
# 🧾 Paso 3: Obtener definición si no está encriptada
# ===============================================
if encriptada: #type:ignore
    print(f"🔒 La vista '{nombre_vista}' está encriptada. No se puede ver su definición SQL.")
else:
    try:
        consulta_def = text(f"""
        SELECT definition
        FROM [{base_encontrada}].sys.sql_modules
        WHERE object_id = OBJECT_ID('{base_encontrada}.{esquema}.{nombre_vista}');
        """)
        df_def = pd.read_sql(consulta_def, engine)
        if df_def.empty or df_def.iloc[0, 0] is None:
            print("⚠️ No se pudo obtener el texto de la vista.")
            print("   → Es posible que falten permisos (VIEW DEFINITION) o que la vista no tenga módulo asociado.")
        else:
            definicion = df_def.iloc[0, 0]
            print("🧾 Definición SQL de la vista:\n")
            print(definicion)

            # 💾 Guardar en archivo
            archivo = f"{nombre_vista}.sql"
            with open(archivo, "w", encoding="utf-8") as f:
                f.write(definicion)
            print(f"\n✅ Guardado en archivo: {archivo}")
    except Exception as e:
        print("❌ Error al intentar leer la definición:")
        print(e)
