import sqlite3

conn = sqlite3.connect(r'C:\Users\jgmeras\Documents\Python Scripts\5. PROYECTOS\Carteles\artículos.db')
cursor = conn.cursor()
cursor.execute('ALTER TABLE articulos DROP COLUMN mp')

conn.close()