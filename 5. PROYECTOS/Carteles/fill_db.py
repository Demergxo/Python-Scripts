import pandas as pd
import sqlite3

# Ruta al archivo Excel
excel_file_path = r'C:\Users\jgmeras\Documents\Python Scripts\5. PROYECTOS\Carteles\articulos.xlsx'

# Leer el archivo Excel
df = pd.read_excel(excel_file_path)
print(df.columns)

# Conectar a la base de datos SQLite
db_path = r'C:\Users\jgmeras\Documents\Python Scripts\5. PROYECTOS\Carteles\artículos.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Insertar datos en la tabla 'articulos'
for index, row in df.iterrows():
    cursor.execute('''
                   INSERT INTO articulos (la, descripcion, ean)
                   VALUES (?, ?, ?)
                   ''', (row['la'], row['descripcion'], row['ean']))

# Confirmar los cambios
conn.commit()

# Cerrar la conexión
conn.close()
