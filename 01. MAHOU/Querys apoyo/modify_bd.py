import os
import sqlite3

DB_FILE = "usuarios.db"

def mod_tablas(conn: sqlite3.Connection):
    c = conn.cursor()
    
    c.execute("ALTER TABLE usuarios ADD COLUMN must_change_pwd INTEGER DEFAULT 0;")
    conn.commit()

def main():
    # Conectar o crear DB
    conn = sqlite3.connect(DB_FILE)
    mod_tablas(conn)

    conn.close()


if __name__ == "__main__":
    main()
