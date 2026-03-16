import sqlite3
import pandas as pd

#Conectar a la base de datos (y si no crearla)
conn = sqlite3.connect(r'C:\Users\jgmeras\Documents\Python Scripts\5. PROYECTOS\Carteles\img_database.db')
c = conn.cursor()

#Crear tabla
# c.execute('''CREATE TABLE IF NOT EXISTS imagenes
#              (id INTEGER PRIMARY KEY AUTOINCREMENT,
#              la TEXT,
#              imagen BLOB)''')

#c.execute('''SELECT * FROM imagenes''')
#print(c.fetchall())

#Insertar datos
with open(r'C:\Users\jgmeras\Documents\Python Scripts\5. PROYECTOS\Carteles\img_database.db', 'rb') as f:
    imagen = f.read()

# Ruta al archivo Excel
excel_file_path = r'C:\Users\jgmeras\Documents\Python Scripts\5. PROYECTOS\Carteles\articulos_img.xlsx'

# Leer el archivo Excel
df = pd.read_excel(excel_file_path)    

# Insertar datos en la tabla 'articulos'
for index, row in df.iterrows():
    c.execute("INSERT INTO imagenes (la, imagen) VALUES (?, ?)", (row['la'], row['imagen']))


#c.execute("INSERT INTO imagenes (la, imagen) VALUES (?, ?)", (la, imagen))

#Guardar cambios
# conn.commit()

#Cerrar conexión
# conn.close()

#Leer datos
# c.execute("SELECT * FROM imagenes")
# datos = c.fetchall()
# for dato in datos:
#     print(dato)

conn.commit()
