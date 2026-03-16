
"""
crear_bd.py

Script para crear la base de datos SQLite usada por la app de login,
generar la clave Fernet (key.key) y añadir el primer usuario.

Campos en tabla usuarios:
 - username (TEXT) -> CIFRADO con Fernet
 - password (TEXT) -> HASH SHA-256
 - administrador (INTEGER) -> 1 (true) / 0 (false)

Tabla seguridad:
 - id (INTEGER PK)
 - intentos (INTEGER)
 - bloqueado_hasta (REAL)

Uso:
  python crear_bd.py
  (o)
  python crear_bd.py --username admin --password 1234 --admin 1
"""

import os
import argparse
import sqlite3
import hashlib
from cryptography.fernet import Fernet
import getpass
from datetime import datetime

DB_FILE = "usuarios.db"
KEY_FILE = "key.key"


def generar_clave_si_no_existe():
    if not os.path.exists(KEY_FILE):
        clave = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(clave)
        print(f"[+] Clave generada y guardada en '{KEY_FILE}'. CONSÉRVALA: si la pierdes, NO podrás descifrar los usuarios.")
    else:
        print(f"[i] Clave existente encontrada en '{KEY_FILE}'.")


def cargar_fernet():
    with open(KEY_FILE, "rb") as f:
        key = f.read()
    return Fernet(key)


def hash_password(pwd: str) -> str:
    return hashlib.sha256(pwd.encode("utf-8")).hexdigest()


def crear_tablas(conn: sqlite3.Connection):
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        administrador INTEGER DEFAULT 0
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS seguridad (
        id INTEGER PRIMARY KEY,
        intentos INTEGER DEFAULT 0,
        bloqueado_hasta REAL DEFAULT 0
    )
    """)
    c.execute("INSERT OR IGNORE INTO seguridad (id) VALUES (1)")
    conn.commit()


def usuario_existe(conn: sqlite3.Connection, fernet: Fernet, username_plain: str) -> bool:
    c = conn.cursor()
    c.execute("SELECT username FROM usuarios")
    filas = c.fetchall()
    for (u_cifrado,) in filas:
        try:
            u_desc = fernet.decrypt(u_cifrado.encode()).decode()
        except Exception:
            # si no se puede descifrar, saltar
            continue
        if u_desc == username_plain:
            return True
    return False


def insertar_usuario(conn: sqlite3.Connection, fernet: Fernet, username_plain: str, pwd_plain: str, admin_flag: int):
    u_cifrado = fernet.encrypt(username_plain.encode()).decode()
    pwd_hash = hash_password(pwd_plain)
    c = conn.cursor()
    c.execute("INSERT INTO usuarios (username, password, administrador) VALUES (?, ?, ?)",
              (u_cifrado, pwd_hash, int(bool(admin_flag))))
    conn.commit()


def main():
    parser = argparse.ArgumentParser(description="Crear DB e insertar primer usuario (cifrado + hash).")
    parser.add_argument("--username", "-u", help="Usuario (opcional).")
    parser.add_argument("--password", "-p", help="Contraseña (opcional).")
    parser.add_argument("--admin", "-a", type=int, choices=[0, 1], default=0,
                        help="1 si es administrador, 0 si no (por defecto 0).")
    args = parser.parse_args()

    generar_clave_si_no_existe()
    fernet = cargar_fernet()

    # Conectar o crear DB
    conn = sqlite3.connect(DB_FILE)
    crear_tablas(conn)

    # Obtener username y password (interactivo si no pasan por args)
    if args.username:
        username = args.username
    else:
        username = input("Introduce el nombre de usuario a crear: ").strip()
        while not username:
            username = input("Usuario vacío. Introduce el nombre de usuario: ").strip()

    if args.password:
        password = args.password
    else:
        # usar getpass para no mostrar la contraseña en pantalla
        password = getpass.getpass("Introduce la contraseña: ").strip()
        password2 = getpass.getpass("Confirma la contraseña: ").strip()
        while not password or password != password2:
            print("Las contraseñas no coinciden o están vacías. Vuelve a intentarlo.")
            password = getpass.getpass("Introduce la contraseña: ").strip()
            password2 = getpass.getpass("Confirma la contraseña: ").strip()

    admin_flag = args.admin
    if args.admin not in (0, 1):
        # si no se pasó por args, pedir interactivo
        resp = input("¿Es administrador? (s/n) [n]: ").strip().lower()
        admin_flag = 1 if resp in ("s", "si", "y", "yes") else 0

    # Comprobar si ya existe el usuario
    if usuario_existe(conn, fernet, username):
        print(f"[!] El usuario '{username}' ya existe en la base de datos. Abortando.")
        conn.close()
        return

    # Insertar usuario
    insertar_usuario(conn, fernet, username, password, admin_flag)
    print(f"[+] Usuario '{username}' creado correctamente. Administrador={admin_flag}")

    # Mostrar resumen (sin mostrar la contraseña)
    print("Resumen:")
    print(f" - Base de datos: {DB_FILE}")
    print(f" - Clave: {KEY_FILE} (mantenla segura)")
    print(f" - Usuario: {username}")
    print(f" - Administrador: {admin_flag}")

    conn.close()


if __name__ == "__main__":
    main()
