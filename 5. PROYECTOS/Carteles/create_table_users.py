from hashlib import sha256
import sqlite3
from base64 import b64encode
import os

user_pc = os.environ['USERNAME']

user = "admin"
passw = "Hastalaseta"
salt = "df^%kTZBnirXv6Yc&#65Ki"
user_salt = user + salt
passw_salt = passw + salt


user_data = user_salt.encode('utf-8')
passw_data = passw_salt.encode('utf-8')

user_hash = sha256(user_data).hexdigest()
passw_hash = sha256(passw_data).hexdigest()
#print(f"user: {user_hash}\npass: {passw_hash}")

# Conectar a la base de datos
conexion = sqlite3.connect(f'C:\\Users\\{user_pc}\\Documents\\Python Scripts\\5. PROYECTOS\\Carteles\\usuarios.db')   

# Crear cursor para ejecutar comando SQL
cursor = conexion.cursor()

# Crear una tabla
# cursor.execute('''
#                CREATE TABLE IF NOT EXISTS usuarios (
#                    id INTEGER PRIMARY KEY AUTOINCREMENT,
#                    usuario TEXT,
#                    contraseña TEXT
                                      
#                )
#             ''')
#cursor.execute("INSERT INTO usuarios (usuario, contraseña) VALUES (?,?)", (user_hash, passw_hash))
cursor.execute("SELECT * FROM usuarios")
resultado = cursor.fetchall()
for fila in resultado:
    print(fila)

#id_eliminar = 1 
# cursor.execute("DELETE FROM usuarios WHERE id = ?", (id_eliminar,))

# Cerrar la conexión a la base de datos 'artículos.db'
conexion.commit()
conexion.close()