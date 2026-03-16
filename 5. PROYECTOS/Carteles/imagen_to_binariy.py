import sqlite3
from datetime import datetime
import os

user_pc = os.environ['USERNAME']

date = datetime.now().date()

def convertir_imagen_a_binario(ruta_imagen):
    with open(ruta_imagen, 'rb') as imagen:
        contenido = imagen.read()
    return contenido

def insertar_imagen_en_db(ruta_imagen, db_path, la):
    contenido = convertir_imagen_a_binario(ruta_imagen)
    
    conexion = sqlite3.connect(db_path)
    cursor = conexion.cursor()
    
    cursor.execute("INSERT INTO imagenes (la, imagen) VALUES (?, ?)", (la, contenido,))
    
    conexion.commit()
    conexion.close()
    
def recuperar_imagen_desde_db(db_path, la):
    conexion = sqlite3.connect(db_path)
    cursor = conexion.cursor()

    cursor.execute("SELECT imagen FROM imagenes WHERE la = ?", (la, ))
    imagen = cursor.fetchone()
    name_tmp = f'{date}_imagen_test.jpg'

    path= os.path.join('C:', os.sep , 'Users', user_pc, 'Documents', 'Python Scripts', '5. PROYECTOS', 'Carteles', name_tmp)    
    
    with open(path, 'wb') as archivo:
        archivo.write(imagen[0])  # Escribir la imagen en el archivo
    
    conexion.close()

    return imagen

ruta_imagen = os.path.join('C:', os.sep, 'Users', user_pc, 'Documents', 'Python Scripts', '5. PROYECTOS', 'Carteles', 'pocion.png')
db_path = os.path.join('C:', os.sep, 'Users', user_pc, 'Documents', 'Python Scripts', '5. PROYECTOS', 'Carteles', 'img_database.db')

#ruta_imagen = r'C:/Users/jgmeras/Documents/Python Scripts/5. PROYECTOS/Carteles/pocion.png'
#db_path = r'C:/Users/jgmeras/Documents/Python Scripts/5. PROYECTOS/Carteles/img_database.db'
la = 'test'

#insertar_imagen_en_db(ruta_imagen, db_path, la)
recuperar_imagen_desde_db(db_path, la)