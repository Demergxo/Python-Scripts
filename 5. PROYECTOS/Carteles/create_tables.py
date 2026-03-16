import sqlite3

# Conectar a la base de datos
conexion = sqlite3.connect(r'C:\Users\jgmeras\GXO\SPCABANILLAS - Cabanillas_Zooplus\6. Stock\08. Ideas, Sugerencias, Cambios\BBDD --NO TOCAR--\artículos.db')   

# Crear cursor para ejecutar comando SQL
cursor = conexion.cursor()

# Crear una tabla
# cursor.execute('''
#                CREATE TABLE IF NOT EXISTS articulos (
#                    id INTEGER PRIMARY KEY AUTOINCREMENT,
#                    la TEXT,
#                    descripcion TEXT,
#                    ean TEXT                   
#                )
#             ''')

cursor.execute('''
               SELECT * FROM articulos WHERE LA = 11111
               ''')
# Obtener los resultados de la consulta
resultados = cursor.fetchall()

# Imprimir los resultados
for fila in resultados:
    print(fila)


# # Cerrar la conexión a la base de datos 'artículos.db'
# conexion.commit()
# conexion.close()

# # Conectar a la segunda base de datos
# conexion = sqlite3.connect(r'C:\Users\jgmeras\Documents\Python Scripts\5. PROYECTOS\Carteles\localizaciones.db')
# cursor2 = conexion.cursor()

# # Crear una tabla
# cursor2.execute('''
#                CREATE TABLE IF NOT EXISTS localizaciones (
#                    id INTEGER PRIMARY KEY AUTOINCREMENT,
#                    seccion TEXT NOT NULL CHECK(seccion IN ('BIN', 'SUELO', 'RACK', 'RIAB', 'SHELVES')),
#                    pasillo TEXT,
#                    columna CHAR(3),
#                    nivel CHAR(2),
#                    ubicacion CHAR(1)
#                )
#             ''')

# # Cerrar la conexión a la base de datos 'localizaciones.db'
conexion.commit()
conexion.close()
