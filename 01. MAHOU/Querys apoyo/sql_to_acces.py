import inspect
import pandas as pd
import pyodbc
from sqlalchemy import create_engine
import urllib


query = """



"""


def export_sql_to_access(query_or_table: str, sql_engine: str, access_path: str, access_table: str, if_exists: str):
    """
    Exporta datos desde una base SQL (SQL Server, MySQL o PostgreSQL) hacia una base de datos Access (.accdb).

    Parámetros:
    -----------
    query_or_table : str
        Consulta SQL completa o nombre de tabla a exportar.
    sql_engine : str
        Cadena de conexión SQLAlchemy, por ejemplo:
        - SQL Server:  "mssql+pyodbc://usuario:pwd@SERVIDOR/DB?driver=ODBC+Driver+17+for+SQL+Server"
        - MySQL:       "mysql+pymysql://usuario:pwd@localhost/DB"
        - PostgreSQL:  "postgresql+psycopg2://usuario:pwd@localhost/DB"
    access_path : str
        Ruta completa del archivo Access (.accdb)
    access_table : str
        Nombre de la tabla destino en Access.
    if_exists : str
        Comportamiento si la tabla ya existe: "replace", "append" o "fail"
    """

    print("🔹 Conectando a la base de datos SQL...")
    sql_conn = create_engine(sql_engine)

    # Detectar si es consulta o nombre de tabla
    if "select" in query_or_table.lower():
        df = pd.read_sql(query_or_table, sql_conn)
    else:
        df = pd.read_sql_table(query_or_table, sql_conn)

    print(f"✅ Datos obtenidos: {len(df)} filas, {len(df.columns)} columnas")

    # Crear conexión a Access mediante SQLAlchemy
    access_conn_str = (
        f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};"
        f"DBQ={access_path};"
    )
    odbc_conn_str = urllib.parse.quote_plus(access_conn_str)
    access_engine = create_engine(f"access+pyodbc:///?odbc_connect={odbc_conn_str}")

    print(f"📤 Exportando a Access → Tabla: {access_table}")
    if access_table in inspect(access_engine).get_table_names():
        mode = "append"
    else:
        mode = "replace"
    df.to_sql(access_table, con=access_engine, if_exists=mode, index=False)
    print("✅ Exportación completada correctamente.")


if __name__ == "__main__":
    # ⚙️ Configuración 
    sql_engine_str = (
        "mssql+pyodbc://@XGA_PROD"
        
    )

    export_sql_to_access(
        query_or_table=query,
        sql_engine=sql_engine_str,
        access_path=r"C:\ruta\a\destino.accdb",
        access_table="Ventas",
        if_exists="append"
    )
