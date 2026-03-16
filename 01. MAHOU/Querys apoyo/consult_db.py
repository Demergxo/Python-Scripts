import os
import sqlite3
import pandas as pd

DB_FILE = r"C:\Users\jgmeras\Documents\Python Scripts\Aplicaciones\Querys_xga\clientes.db"                         # Nombre de la base de datos SQLite
TABLE_NAME = "direcciones_clientes"             # Nombre de la tabla en SQLite

def mod_tablas(conn: sqlite3.Connection):
    c = conn.cursor()
    
    # Opcional: mostrar los primeros registros insertados
    consulta = f"SELECT * FROM {TABLE_NAME} LIMIT 5"
    resultado = pd.read_sql_query(consulta, conn)
    print("\nEjemplo de los primeros registros:")
    print(resultado)
    conn.commit()

def main():
    # Conectar o crear DB
    conn = sqlite3.connect(DB_FILE)
    mod_tablas(conn)

    conn.close()


if __name__ == "__main__":
    main()
