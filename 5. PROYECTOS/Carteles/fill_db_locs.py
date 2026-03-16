import pandas as pd
import sqlite3

# Ruta al archivo Excel
excel_file_path = r'C:\Users\jgmeras\Documents\Python Scripts\5. PROYECTOS\Carteles\localizaciones.xlsx'

# Leer el archivo Excel
df = pd.read_excel(excel_file_path)
print(df.columns)

# Conectar a la base de datos SQLite
db_path = r'C:\Users\jgmeras\Documents\Python Scripts\5. PROYECTOS\Carteles\localizaciones.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Insertar datos en la tabla 'articulos'
for index, row in df.iterrows():
    cursor.execute('''
                   INSERT INTO localizaciones (seccion, pasillo, columna, nivel, ubicacion)
                   VALUES (?, ?, ?, ?, ?)
                   ''', (row['seccion'], row['pasillo'], row['columna'], row['nivel'], row['ubicacion']))

# Confirmar los cambios
conn.commit()

# Cerrar la conexión
conn.close()


