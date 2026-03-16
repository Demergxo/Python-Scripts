import sys
sys.path.append(r"C:\PyLib")
import time
import hashlib
import sqlite3
from datetime import datetime
from PyQt6 import QtWidgets #type:ignore
from PyQt6.QtWidgets import ( #type:ignore
    QApplication, QWidget, QLineEdit, QPushButton, QLabel, QVBoxLayout, QMessageBox, QDateEdit,
    QHBoxLayout,  QCheckBox, QTableWidgetItem, QTableWidget, QErrorMessage, QTimeEdit, 
)
from PyQt6.QtCore import Qt, QLocale, QDate, QByteArray, QTime  #type:ignore
from cryptography.fernet import Fernet #type:ignore
import os
from PyQt6.QtGui import QIcon, QPixmap #type:ignore
import base64

path = os.getcwd()

DB_FILE =f"{path}\\usuarios.db"
LOG_FILE = "security.log"
KEY_FILE = f"{path}\\key.key"
MAX_INTENTOS = 5
BLOQUEO_MINUTOS = 30
print(os.getcwd())


# --- 🔑 Manejo de claves y cifrado ---
def generar_clave():
    """Genera una clave Fernet si no existe."""
    if not os.path.exists(KEY_FILE):
        clave = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(clave)


def cargar_clave():
    """Carga la clave Fernet desde el archivo."""
    return Fernet(open(KEY_FILE, "rb").read())


def cifrar_texto(texto: str) -> str:
    f = cargar_clave()
    return f.encrypt(texto.encode()).decode()


def descifrar_texto(texto_cifrado: str) -> str:
    f = cargar_clave()
    return f.decrypt(texto_cifrado.encode()).decode()


# --- Hash de contraseñas ---
def cargar_fernet():
    """Carga y devuelve un objeto Fernet (lanza excepción si falta key.key)."""
    with open(KEY_FILE, "rb") as f:
        key = f.read()
    return Fernet(key)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


# --- Inicialización de base de datos ---
def init_db():
    generar_clave()
    conn = sqlite3.connect(DB_FILE)
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

    # Crear usuario de ejemplo si no hay ninguno
    c.execute("SELECT COUNT(*) FROM usuarios")
    if c.fetchone()[0] == 0:
        usuario_cifrado = cifrar_texto("admin")
        c.execute("INSERT INTO usuarios (username, password, administrador) VALUES (?, ?, ?)",
                (usuario_cifrado, hash_password("1234"), 1))

        conn.commit()
        print("Usuario de ejemplo creado: admin / 1234")

    conn.commit()
    conn.close()


# --- Registro de eventos ---
def log_event(mensaje: str):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {mensaje}\n")

# --- Verificar bloqueo ---
def esta_bloqueado():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT bloqueado_hasta FROM seguridad WHERE id = 1")
    bloqueado_hasta = c.fetchone()[0]
    conn.close()

    if bloqueado_hasta and time.time() < bloqueado_hasta:
        return True, bloqueado_hasta
    return False, None

# --- Clase principal de Login ---
class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login Exportacion Archivos")
        self.setFixedSize(320, 220)
        # Convertir a bytes y crear QPixmap
        icon_base64 = "AAABAAEAICAAAAEAIACoEAAAFgAAACgAAAAgAAAAQAAAAAEAIAAAAAAAABAAAL1OAAC9TgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAAAGMAAABLAAAAAAAAAAAAAAADAAAAYAAAAE4AAAAAAAAAAgAAAAAAAAAQAAAAXgAAAGwAAAAlAAAAAAAAAAIAAAABAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABQAAAAAAAABbAAAAnQAAAKcAAAAuAAAAAAAAAFcAAACeAAAApgAAADMAAAAAAAAALwAAAL4AAACMAAAAewAAAMAAAABeAAAAAAAAAAIAAAAAAAAAAwAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAEAAAAAAAAAG4AAABMAAAAdgAAAD8AAAAAAAAAaQAAAFAAAABwAAAAQQAAAAAAAAC4AAAAOgAAAAAAAAAAAAAACwAAALoAAAAqAAAACwAAABIAAAAAAAAAAgAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAAAAAAAACMAAAA2AAAAkwAAAIAAAACeAAAAbwAAACgAAACQAAAAgwAAAJsAAABoAAAAXgAAAJUAAAAAAAAABwAAAAgAAAAAAAAAVwAAANEAAACYAAAApgAAAJcAAAAcAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAwAAAAAAAABHAAAAsgAAAHYAAACDAAAAiQAAAIcAAACEAAAAiAAAAIQAAACKAAAAiQAAAHsAAACtAAAAiAAAAAAAAAAEAAAAAQAAAAAAAAASAAAALwAAAAAAAAAAAAAATgAAALoAAAATAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAACAAAAAAAAAJwAAAApAAAAIAAAAAcAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAAAAAAAAD0AAACGAAAAAAAAAAQAAAAAAAAAAAAAAAEAAAAAAAAAAQAAAAMAAAAAAAAAYQAAAIQAAAAAAAAAAwAAAAAAAAAAAAAAAAAAAAEAAAAAAAAAmwAAABgAAAArAAAACwAAAAQAAAAEAAAAAAAAADYAAAAEAAAAJgAAACAAAAAAAAAAQAAAAIgAAAAAAAAABAAAAAAAAAAAAAAAAQAAAAIAAAAAAAAAAQAAAAAAAAAXAAAAnQAAAAAAAAACAAAAAAAAAAAAAAAAAAAAAgAAAAAAAACcAAAAkAAAAAAAAAAAAAAAAAAAABAAAAAxAAAAtAAAAEUAAACPAAAAfgAAACEAAABzAAAAiwAAAAAAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAAAAAAAABoAAACvAAAAAQAAAAEAAAABAAAAAAAAAAAAAAAAAAAAAQAAAAAAAACEAAAAcQAAAAAAAAAmAAAArwAAAIwAAACHAAAAiQAAAIgAAACJAAAAgAAAALEAAACNAAAAAAAAAAcAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEAAAAAAAAACgAAAJQAAACjAAAADAAAAAAAAAAAAAAAAAAAAAAAAAADAAAAAAAAAEMAAACNAAAAAAAAAJQAAABKAAAAAAAAAAIAAAAAAAAAAAAAAAIAAAAAAAAAQAAAAJEAAAAAAAAAAwAAAAsAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADAAAAAAAAAGoAAACMAAAAAAAAAAAAAAACAAAAAgAAAAAAAABTAAAAvAAAAC0AAAADAAAAogAAACAAAAAAAAAABQAAAAQAAAAEAAAABgAAAAAAAABFAAAAiQAAAB8AAACbAAAAqAAAAFcAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAEAAAADAAAABwAAAKEAAAALAAAAAAAAAAAAAAACAAAAAAAAAKQAAAAwAAAAAAAAAIgAAADRAAAAGAAAAAAAAAABAAAAAAAAAAAAAAACAAAAAAAAADUAAADLAAAApAAAADMAAAABAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAHAAAAFQAAAAAAAAANAAAAowAAAAYAAAAAAAAAbwAAAKEAAACWAAAAxwAAABMAAAAAAAAAAAAAAJgAAAAiAAAAAAAAAAEAAAAAAAAAAAAAAAIAAAAAAAAANAAAAOgAAAAWAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAACAAAAAAAAACMAAACnAAAAjwAAAI8AAABwAAAAAAAAAAwAAACpAAAAMAAAACUAAACuAAAAGgAAAAAAAAAGAAAAnQAAACEAAAAAAAAAAQAAAAAAAAAAAAAAAgAAAAAAAABBAAAAlAAAAAAAAAAGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAAAAAAAAAxAAAA0AAAACkAAAAAAAAAAAAAAGgAAAChAAAAlgAAAMwAAAAIAAAAOAAAAKkAAADLAAAAFwAAAAAAAAABAAAAAAAAAAAAAAACAAAAAAAAAEAAAACRAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAAAAwAAAAAAAABFAAAAigAAAAAAAAAAAAAAAAAAAAEAAAAAAAAAmwAAABoAAAAAAAAAAAAAAJgAAAAhAAAAAAAAAAEAAAAAAAAAAAAAAAIAAAAAAAAAQQAAAJAAAAAAAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAAAAAAAABIAAACZAAAAAAAAAAAAAAAAAAAAAQAAAAAAAACbAAAAGgAAAAAAAAAAAAAAmAAAACEAAAAAAAAAAQAAAAAAAAAAAAAAAgAAAAAAAABBAAAAkAAAAAAAAAAFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAcAAAAAAAAAHgAAAJgAAAAAAAAAAAAAAGgAAAChAAAAlgAAAMwAAAAIAAAAOAAAAKkAAADLAAAAFwAAAAAAAAABAAAAAAAAAAAAAAACAAAAAAAAAEEAAACQAAAAAAAAAAUAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAEAAAAAAAAAhwAAACUAAAB9AAAAaAAAAAAAAAAMAAAAqQAAADAAAAAlAAAArgAAABoAAAAAAAAABgAAAJ0AAAAhAAAAAAAAAAEAAAAAAAAAAAAAAAIAAAAAAAAAQgAAAIkAAAAaAAAAJAAAAAAAAAABAAAAAAAAAAAAAAAAAAAAAwAAAAAAAAA+AAAA2AAAAIMAAAAAAAAAAAAAAAAAAABvAAAAoQAAAJYAAADHAAAAEwAAAAAAAAAAAAAAmAAAACIAAAAAAAAAAQAAAAAAAAAAAAAAAgAAAAAAAABDAAAAhgAAACwAAACuAAAAAgAAAAAAAAABAAAAAAAAAAAAAAAGAAAAgQAAAKkAAAC6AAAABQAAAAAAAAAAAAAAAAAAAAAAAAACAAAAAAAAAKQAAAAwAAAAAAAAAIgAAADRAAAAGAAAAAAAAAABAAAAAAAAAAAAAAACAAAAAAAAAEEAAACTAAAAAAAAAIMAAAA3AAAAAAAAAAMAAAABAAAAAAAAAAAAAAAlAAAADAAAAIAAAAAuAAAAAAAAAAEAAAAAAAAAAgAAAAIAAAAAAAAAUwAAALwAAAAsAAAAAwAAAKIAAAAgAAAAAAAAAAUAAAAEAAAABAAAAAYAAAAAAAAAQgAAAJsAAAAcAAAAogAAABEAAAAAAAAAAQAAAAIAAAACAAAAAQAAAAMAAAAAAAAAgQAAACkAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAMAAAAAAAAAQwAAAI0AAAAAAAAAlAAAAEoAAAAAAAAAAgAAAAAAAAAAAAAAAgAAAAAAAAA1AAAA0gAAAIsAAAAzAAAAAAAAAAAAAAAaAAAACwAAAAAAAAACAAAAAAAAACAAAACWAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAAAAAAAACEAAAAcgAAAAAAAAAmAAAArwAAAIwAAACHAAAAiQAAAIgAAACJAAAAgAAAALEAAACOAAAAAAAAAAUAAAADAAAAAAAAAFMAAAClAAAAKwAAABUAAAAvAAAAnAAAADAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAnAAAAJAAAAAAAAAAAAAAAAAAAAAQAAAAMQAAALQAAABFAAAAjwAAAH4AAAAhAAAAcwAAAIwAAAAAAAAABgAAAAAAAAACAAAAAAAAAD0AAACJAAAAhwAAAMoAAAAsAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAQAAAAAAAACbAAAAGAAAACsAAAAKAAAABAAAAAQAAAAAAAAANwAAAAQAAAAmAAAAIAAAAAAAAABAAAAAiAAAAAAAAAAEAAAAAAAAAAAAAAAEAAAAAQAAAAAAAAAAAAAAnwAAABEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAAAAAAAAJwAAAApAAAAIAAAAAcAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAAAAAAAAD0AAACGAAAAAAAAAAQAAAAAAAAAIAAAAAQAAAACAAAAAAAAAFMAAACaAAAAAAAAAAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAAAAAAAARwAAALIAAAB2AAAAgwAAAIgAAACHAAAAhAAAAIgAAACEAAAAiQAAAIkAAAB7AAAArQAAAIgAAAAAAAAABgAAAAAAAAB8AAAAmgAAAFEAAACCAAAAsAAAABgAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEAAAAAAAAAJAAAADYAAACTAAAAgAAAAJ4AAABvAAAAKAAAAJAAAACFAAAAmQAAAGoAAABbAAAAlAAAAAAAAAAHAAAABwAAAAAAAAB5AAAAsQAAAEkAAAAMAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAEAAAAAAAAAG4AAABMAAAAdgAAAD8AAAAAAAAAagAAAFMAAABuAAAARQAAAAAAAACtAAAAPQAAAAAAAAAAAAAADQAAAKoAAAAiAAAAAAAAAAMAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAUAAAAAAAAAWwAAAJ0AAACnAAAALgAAAAAAAABXAAAAoAAAAKUAAAA1AAAAAAAAACMAAACqAAAAhAAAAHUAAACvAAAATgAAAAAAAAAGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEAAAAYwAAAEsAAAAAAAAAAAAAAAMAAABgAAAATwAAAAAAAAABAAAAAAAAAAgAAABGAAAAUwAAABcAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA+jFCF8oQgUvSEJglyAAkC9AAJMWQvSQkkCEkJZOAIqDJACmhiS0iSRAhAiCSLQBIgy0TQQAtIpGALSdJky0nqZMtK0mALSQhAC0LooMtBIKSLSRCECEEEoktDKTJACQEk4AqCpAhJImQvSiT0AAoE8gAJCvSEJiXyhCBL/oxQr8="
        icon_data = base64.b64decode(icon_base64)
        pixmap = QPixmap()
        pixmap.loadFromData(QByteArray(icon_data))
        # Crear QIcon y asignarlo
        self.setWindowIcon(QIcon(pixmap))
        self.setup_ui()
        init_db()

        bloqueado, hasta = esta_bloqueado()
        if bloqueado:
            self.show_bloqueado(hasta)

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label_user = QLabel("Usuario:")
        self.entry_user = QLineEdit()
        self.label_pass = QLabel("Contraseña:")
        self.entry_pass = QLineEdit()
        self.entry_pass.setEchoMode(QLineEdit.EchoMode.Password)

        self.btn_login = QPushButton("Iniciar sesión")
        self.btn_login.clicked.connect(self.login)
        self.entry_pass.returnPressed.connect(self.login)
        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.clicked.connect(self.close)

        layout.addWidget(self.label_user)
        layout.addWidget(self.entry_user)
        layout.addWidget(self.label_pass)
        layout.addWidget(self.entry_pass)
        layout.addWidget(self.btn_login)
        layout.addWidget(self.btn_cancel)

        self.setLayout(layout)

    def show_bloqueado(self, hasta):
        minutos = int((hasta - time.time()) / 60)
        QMessageBox.critical(self, "Programa Bloqueado",
                             f"El programa está bloqueado.\nIntenta de nuevo en {minutos} minutos.")
        self.entry_user.setEnabled(False)
        self.entry_pass.setEnabled(False)
        self.btn_login.setEnabled(False)

    def login(self):
        user = self.entry_user.text().strip()
        pwd = self.entry_pass.text().strip()

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()

        bloqueado, hasta = esta_bloqueado()
        if bloqueado:
            self.show_bloqueado(hasta)
            conn.close()
            return

        # Recuperamos todos los usuarios
        c.execute("SELECT username, password, administrador, must_change_pwd FROM usuarios")
        usuarios = c.fetchall()

        login_ok = False
        es_admin = 0  # Valor por defecto (no admin)

        for u_cifrado, pwd_hash, admin_flag, must_change_pwd in usuarios:
            try:
                u_descifrado = descifrar_texto(u_cifrado)
            except Exception:
                continue  # Si alguna entrada vieja no puede descifrarse

        # Comparamos usuario y contraseña
            if u_descifrado == user and pwd_hash == hash_password(pwd):
                login_ok = True
                es_admin = admin_flag

                if must_change_pwd:
                    login_ok = True  # <— aseguramos que el login está OK
                    QMessageBox.information(
                        self, 
                        "Cambio requerido",
                        "Tu contraseña es temporal. Debes cambiarla para continuar."
                    )
                    self.hide()
                    self.ventana_cambio = VentanaCambioPassword(username_cifrado=u_cifrado)
                    self.ventana_cambio.setGeometry(self.geometry())
                    self.ventana_cambio.show()
                    return

                break



        if login_ok:
            c.execute("UPDATE seguridad SET intentos = 0 WHERE id = 1")
            conn.commit()
            conn.close()
            log_event(f"Login exitoso del usuario '{user}'.")
            QMessageBox.information(self, "Éxito", "Login correcto. ¡Bienvenido!")
            self.hide()


            if es_admin == 1:
                # 🔐 Usuario administrador
                self.ventana_admin = VentanaAdmin(user)
                self.ventana_admin.setGeometry(self.geometry())
                self.ventana_admin.show()
            else:
                # 👤 Usuario normal
                self.ventana_fechas = VentanaFechas()
                self.ventana_fechas.setGeometry(self.geometry())
                self.ventana_fechas.show()
        else:
            c.execute("SELECT intentos FROM seguridad WHERE id = 1")
            intentos = c.fetchone()[0] + 1

            if intentos >= MAX_INTENTOS:
                bloqueado_hasta = time.time() + (BLOQUEO_MINUTOS * 60)
                c.execute("UPDATE seguridad SET intentos = 0, bloqueado_hasta = ? WHERE id = 1", (bloqueado_hasta,))
                conn.commit()
                conn.close()
                log_event(f"Programa bloqueado tras {MAX_INTENTOS} intentos fallidos.")
                self.show_bloqueado(bloqueado_hasta)
            else:
                c.execute("UPDATE seguridad SET intentos = ? WHERE id = 1", (intentos,))
                conn.commit()
                conn.close()
                log_event(f"Intento fallido #{intentos} con usuario '{user}'.")
                self.entry_pass.clear()
                self.entry_pass.setFocus()
                QMessageBox.warning(self, "Error",
                                    f"Usuario o contraseña incorrectos.\nIntentos: {intentos}/{MAX_INTENTOS}")

# --- Clase de Selector de Fechas ---            
class VentanaFechas(QWidget):
    def __init__(self):
        
        super().__init__()
        self.setObjectName("VentanaFechas")  # 👈 clave para volver a mostrar esta ventana
        self.setWindowTitle("Selector de Fechas")
        self.setGeometry(200, 200, 340, 260)
        # Convertir a bytes y crear QPixmap
        icon_base64 = "AAABAAEAICAAAAEAIACoEAAAFgAAACgAAAAgAAAAQAAAAAEAIAAAAAAAABAAAE0GAABNBgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAWUwuAFlMLgFZTC4DWUwuA1lMLgNZTC4DWUwuA1lMLgNZTC4DWUwuA1lMLgNZTC4DWUwuA1lMLgNZTC4DWUwuA1lMLgNZTC4DWUwuA1lMLgNZTC4DWUwuA1lMLgNZTC4DWUwuA1lMLgNZTC4DWUwuA1lMLgNZTC4DWUwuAVlMLgBZTC4AWUwuAVlMLgBZTC4AWUwuAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABdTi4AWUwuAFlMLgBZTC4BWUwuAEIzIABHOSQJLRwDPysbAEUrGwBEKxsARCsbAEQrGwBEKxsARCsbAEQrGwBELBsARS0dAEctHQBHLR0ARy0dAEctHQBHLR0ARy4dAEcrGwBHNSUIRk5AIEVGNxZGSz0cRks9HEZHORhGSToaRkk6GkVNPx5GRTYbQTEhCworGgYAY1c7AF1QM4eimon/uLKl/LOtoP+0rqD/tK6g/7SuoP+0rqD/tK6g/7SuoP+0rqD/tK6g/7SuoP+0rqD/tK6g/7SuoP+0rqD/s62f/7izpv+Xj3z/cGVL/4F3Yf92bFP/dmxT/350XP96cFj/enBY/3VqUfx4bVT/aFxBinpwWABhVDgAW04wktzZ0//////5+vr5/fz7+/38+/v9/Pv7/fz7+/38+/v9/Pv7/fz7+/38/Pv8/Pz7/Pz8+/z8/Pv8/Pz7/Pz8+/z8+/v8/Pz8/Pz8+/2UjHj9opuJ/ZCIc/2UjHj9nZaE/ZyVg/2Xj3z9jYVw+aWejv9uYkiUg3liADIiAAA4KARVubSn//T08vzd2tT/4d7Z/+He2f/f3Nf/3tvW/97b1v/e29b/4N3Y/9/c1//e29b/3tvW/97b1v/e29b/3tzX/+Hf2v/c2dP/+Pj3/6Wejf+Qh3P/iH9q/42EcP+RiXT/lIx5/4mAav+MhG/8npaF/0w+HVhENRMACwAAAAwAACWbk4H8//////X08v749/b/9/f1//39/f/////////////////5+fj//f38///////////////////////9/f3/9/f1//X08v//////wbyx/4V8Zv+Ifmn/ioFr/46Gcf+RiXX/gnli/paOe/+VjXr9FwQAJxgGAAAAAAAAAAAAAn1yW9f6+vn//////f7+/v//////sKqc/5CIdP+eloT/kol2/+ro5P+zrZ//mJB9/5iQfv+Ti3f/j4Zy/7awo////////f38///////g3dj/gHZf/4N6Y/+EemT/i4Jt/4yEb/98clr9oZmI/4Z9Z9kAAAADAAAAAH91XgRwZUsAYFQ3o+Lg2v/////7/f38///////d29X/sKqc/2BTN/+/uq//+vn4/7u2qv9NPx//ta+i/8vHvf+yrJ7/ZVk9//X08v////////////n49/+HfWj/em9X/310XP+Hfmj/hn1m/3lvV/unoZH/cWZMppyUggCAdl8DXFAyBDwtCQBDNRNpxL+0//////v9/fz////////////8/Pz/eG1V/+Ti3v///////////8O+s/+Adl//8/Pw//////+1r6H/7uzp///////8/Pz//////5yUgv9sYEX/d21U/4J5Yv99c1v/f3Vd+6egkP9VRyhsUEMjAFxPMgRZTC4DGggAAB4NADOknYz///////38/P///////Pv7//////+HfWf/vLaq///////6+fj//////8C7sP9sYUb/6Obi///////+/v3///////z8/P//////u7aq/11RM/9wZUr/e3FZ/3JnTf+Mg27+npaE/ygXADUlFAAAWUwuA1pNLwEAAAAAAAAAC4V8ZuP//////////f/////8/Pz//////6iikv+YkH7///////z8/P/7+/r//////8jEuv9tYkj/6efj///////+/v7//f39///////d29X/V0os/2RYPP9zaE//Z1xA/pyVg/+OhXDkAAAADAAAAABaTS8BWUwuAKWejQKWjnsAaF1Bs+ro5f/////8/v7+//39/f//////zsrB/3xyWv///////v7+///////7+/r//////8XAtv90aVD/+Pf2///////+/v3///////j49v9oXEH/W04w/2dbQP9jVzr8qaKT/3htVbbV0soAqaKTAllMLgBZTC4AYVQ4BEc4FwBMPh56zcnA//////v9/f3//v7+///////s6+f/b2RK//Lx7v//////6unl//Lx7//8+/v//////5uTgf+clIL///////38/P/9/f3//////4l/av9RQyT/XFAy/2peQ/usppf/W08xfV5SNQBhVDgEWUwuAFlMLgBZTC4DJRQAACsbAEKtp5j//////f38/P///////v7+//////+Adl//0c3F//////+rpJX/kop2////////////3NnT/3NoT/////////////z8+///////rqiZ/05AIP9XSiv/e3FZ/aafjv80JABEMSEAAFlMLgNZTC4AWUwuAFpNLwEAAAAAAAAAFY6Gce7/////+vr5/v/////m5OD/pp+P/2ZaPv+qo5T///////Py8P91alH/qaKT//Dv7P+im4r/dGlP///////8+/v/+vr5///////RzsX/VEYn/1BCIv6RiHT/lo577wAAABcAAAAAWU0vAVlLLgAAAAAAWUwuAP///wH9/PwAcWZMw/Lx7v/////8//////z7+//Py8L/qKGQ/8O+sv////////////X08v+knIv/h31n/4uCbP/l4t3///////7+/v/+/v7///////Tz8f9pXUL/TT8e/K2nmP9/dV7F////AP///wFZTC4AAAAAAAAAAABZTC4AZlo+BF5RMwBaTS+MpZ+Q/7u2rfu1sKb/uLOp/8O/t//EwLj/u7at/7axpv+1sKX/urWr/8O/t/+3sqj/vrqx/724r/+1sKb/t7Kn/7axp/+2saf/uLOp/2peRf9PQiP7jINw/2RYPI5wZUsAZlo+BFlMLgAAAAAAAAAAAFlMLgBYSiwDPTAWAEM2G1SHelH/u658/LCjc/+zpXX/saNz/6+hcf+ypHT/s6Z2/7KldP+xpHT/saNz/7Kldf+xpHP/sqR0/7Kl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"
        icon_data = base64.b64decode(icon_base64)
        pixmap = QPixmap()
        pixmap.loadFromData(QByteArray(icon_data))
        # Crear QIcon y asignarlo
        self.setWindowIcon(QIcon(pixmap))
                
        # Forzar español
        QLocale.setDefault(QLocale(QLocale.Language.Spanish, QLocale.Country.Spain))

        layout = QVBoxLayout()

        # --- Fecha inicio ---
        self.fecha_inicio = QDateEdit()
        self.fecha_inicio.setCalendarPopup(True)
        self.fecha_inicio.setDisplayFormat("dd/MM/yyyy")
        self.fecha_inicio.setDate(QDate.currentDate().addDays(-1))

         # --- Hora inicio ---
        self.hora_inicio = QTimeEdit()
        self.hora_inicio.setDisplayFormat("HH:mm:ss")
        self.hora_inicio.setTime(QTime(16, 25, 1))

        # --- Fecha fin ---
        self.fecha_fin = QDateEdit()
        self.fecha_fin.setCalendarPopup(True)
        self.fecha_fin.setDisplayFormat("dd/MM/yyyy")
        self.fecha_fin.setDate(QDate.currentDate())

         # --- Hora fin ---
        self.hora_fin = QTimeEdit()
        self.hora_fin.setDisplayFormat("HH:mm:ss")
        self.hora_fin.setTime(QTime(16, 25, 0))

        # --- Layout ---
        layout.addWidget(QLabel("Fecha Inicio:"))
        layout.addWidget(self.fecha_inicio)
        layout.addWidget(QLabel("Hora inicio"))
        layout.addWidget(self.hora_inicio)

        layout.addSpacing(8)

        layout.addWidget(QLabel("Fecha Fin:"))
        layout.addWidget(self.fecha_fin)
        layout.addWidget(QLabel("Hora fin"))
        layout.addWidget(self.hora_fin)

        # --- Botones ---
        boton_layout = QHBoxLayout()

        btn_limpiar = QPushButton("Limpiar")
        btn_aceptar = QPushButton("Aceptar")
        btn_salir = QPushButton("Salir")

        boton_layout.addWidget(btn_limpiar)
        boton_layout.addWidget(btn_aceptar)
        boton_layout.addWidget(btn_salir)

        layout.addLayout(boton_layout)
        self.setLayout(layout)

        # --- Conexiones ---
        btn_limpiar.clicked.connect(self.limpiar_campos)
        btn_aceptar.clicked.connect(self.aceptar_fechas)
        btn_salir.clicked.connect(QtWidgets.QApplication.quit)
    def limpiar_campos(self):
        self.fecha_inicio.setDate(QDate.currentDate().addDays(-1))
        self.hora_inicio.setTime(QTime(16, 25, 1))
        self.fecha_fin.setDate(QDate.currentDate())
        self.hora_fin.setTime(QTime(16, 25, 0))

    def aceptar_fechas(self):
        inicio = self.fecha_inicio.date().toString("yyyy-MM-dd")
        hora_inicio = self.hora_inicio.time()
        fin = self.fecha_fin.date().toString("yyyy-MM-dd")
        hora_fin = self.hora_fin.time() 
        #print(f"Fechas seleccionadas: {inicio} - {fin}")

        self.hide()

        # 🔧 Ventana independiente (sin parent)
        self.ventana_consultas = VentanaConsultas(inicio, hora_inicio, fin, hora_fin)
        self.ventana_consultas.setGeometry(self.geometry())

        # Mostrar forzando foco
        self.ventana_consultas.show()
        QtWidgets.QApplication.processEvents()
        self.ventana_consultas.raise_()
        self.ventana_consultas.activateWindow()
        self.ventana_consultas.setFocus()
                
        #print("Ventana visible?", self.ventana_consultas.isVisible())
        #print("Geometry:", self.ventana_consultas.geometry())
        #print("Parent activo?", self.isVisible())

# --- Clase que llama a las consultas ---        
class VentanaConsultas(QtWidgets.QWidget):
    def __init__(self, fecha_inicio, hora_incio, fecha_fin, hora_fin, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Selector Tareas")
        self.resize(420, 250)
        # Convertir a bytes y crear QPixmap
        icon_base64 = "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"
        icon_data = base64.b64decode(icon_base64)
        pixmap = QPixmap()
        pixmap.loadFromData(QByteArray(icon_data))
        # Crear QIcon y asignarlo
        self.setWindowIcon(QIcon(pixmap))

        self.fecha_inicio = fecha_inicio
        self.hora_inicio = hora_incio
        self.fecha_fin = fecha_fin
        self.hora_fin = hora_fin

        # --- Layout principal ---
        layout = QtWidgets.QVBoxLayout(self)

        # Labels de fecha y hora inicio
        fechas_layout = QHBoxLayout()
        label_inicio = QLabel("Fecha inicio:")
        label_inicio.setStyleSheet("font-weight: bold;")
        label_valor_inicio = QLabel(self.fecha_inicio)

        label_hinicio = QLabel("Hora inicio")
        label_hinicio.setStyleSheet("font-weight: bold;")
        label_valor_hinicio = QLabel(self.hora_inicio.toString("HH:mm:ss"))
        
        # Labels de fecha y hora fin
        label_fin = QLabel("Fecha fin:")
        label_fin.setStyleSheet("font-weight: bold;")
        label_valor_fin = QLabel(self.fecha_fin)

        label_hfin = QLabel("Hora fin:")
        label_hfin.setStyleSheet("font-weight: bold;")
        label_valor_hfin = QLabel(self.hora_fin.toString("HH:mm:ss"))

        # Crear layout y configuración
        fechas_layout.addWidget(label_inicio)
        fechas_layout.addWidget(label_valor_inicio)
        fechas_layout.addWidget(label_hinicio)
        fechas_layout.addWidget(label_valor_hinicio)
        fechas_layout.addSpacing(40)
        fechas_layout.addWidget(label_fin)
        fechas_layout.addWidget(label_valor_fin)
        fechas_layout.addWidget(label_hfin)
        fechas_layout.addWidget(label_valor_hfin)
        layout.addLayout(fechas_layout)

        layout.addSpacing(20)

        # Botones de consulta
        botones_layout = QVBoxLayout()
        self.btn_consulta1 = QPushButton("Fichero Facturación")
        self.btn_consulta1.setFixedHeight(40)
        self.btn_consulta1.setStyleSheet("text-align: left; padding-left: 20px;")
        self.btn_consulta2 = QPushButton("Fichero XPO")
        self.btn_consulta2.setFixedHeight(40)
        self.btn_consulta2.setStyleSheet("text-align: left; padding-left: 20px;")
        self.btn_consulta3 = QPushButton("Fichero DSV")
        self.btn_consulta3.setFixedHeight(40)
        self.btn_consulta3.setStyleSheet("text-align: left; padding-left: 20px;")

        botones_layout.addWidget(self.btn_consulta1)
        botones_layout.addWidget(self.btn_consulta2)
        botones_layout.addWidget(self.btn_consulta3)
        layout.addLayout(botones_layout)

        layout.addSpacing(30)

        # Botones de control (centrados)
        control_layout = QHBoxLayout()
        self.btn_atras = QPushButton("Atrás")
        self.btn_salir = QPushButton("Salir")
        control_layout.addStretch()
        control_layout.addWidget(self.btn_atras)
        control_layout.addSpacing(20)
        control_layout.addWidget(self.btn_salir)
        control_layout.addStretch()
        layout.addLayout(control_layout)

        self.setLayout(layout)

        # Conexiones
        self.btn_consulta1.clicked.connect(self.ejecutar_consulta1)
        self.btn_consulta2.clicked.connect(self.ejecutar_consulta2)
        self.btn_consulta3.clicked.connect(self.ejecutar_consulta3)
        self.btn_atras.clicked.connect(self.volver_atras)
        self.btn_salir.clicked.connect(QtWidgets.QApplication.quit)

    def ejecutar_consulta1(self):
        import qry_transport_TAISA
        try:
            qry_transport_TAISA.consulta_taisa(self.fecha_inicio, self.fecha_fin)
            QtWidgets.QMessageBox.information(self, "Fichero Taisa", "Consulta Taisa ejecutada correctamente y generado archivo.")
        except Exception as e:
            error_dialog = QtWidgets.QErrorMessage(self)
            error_dialog.setWindowTitle("Fichero Taisa")
            error_dialog.showMessage(f"Error en la consulta: servidor caído o sin permisos.\n\nDetalles: {e}")
            

    def ejecutar_consulta2(self):
        import qry_transport_XPO
        try:
            qry_transport_XPO.consulta_XPO(self.fecha_inicio, self.hora_inicio, self.fecha_fin, self.hora_fin)
            QtWidgets.QMessageBox.information(self, "Fichero XPO", "Consulta XPO ejecutada correctamente y generado archivo.")
        except Exception as e:
            error_dialog = QtWidgets.QErrorMessage(self)
            error_dialog.setWindowTitle("Fichero XPO")
            error_dialog.showMessage(f"Error en la consulta: servidor caído o sin permisos.\n\nDetalles: {e}")


    def ejecutar_consulta3(self):
        import qry_transport_DBS
        try:
            qry_transport_DBS.consulta_DBS(self.fecha_inicio, self.hora_inicio, self.fecha_fin, self.hora_fin)
            QtWidgets.QMessageBox.information(self, "Fichero DSV", "Consulta DSV ejecutada correctamente y generado archivo.")
        except Exception as e:
            error_dialog = QtWidgets.QErrorMessage(self)
            error_dialog.setWindowTitle("Fichero DSV")
            error_dialog.showMessage(f"Error en la consulta: servidor caído o sin permisos.\n\nDetalles: {e}")


    def volver_atras(self):
        """Cierra esta ventana y vuelve a mostrar la de selección de fechas."""
        self.close()  # Cerramos la ventana actual

        # Buscamos entre todas las ventanas abiertas la de fechas
        app = QtWidgets.QApplication.instance()
        for widget in app.topLevelWidgets():
            if widget.objectName() == "VentanaFechas":
                widget.show()
                widget.raise_()
                widget.activateWindow()
                break

# --- Clase que gestiona la ventana de administración ---  
class VentanaAdmin(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        # Convertir a bytes y crear QPixmap
        icon_base64 = "AAABAAEAICAAAAEAIACoEAAAFgAAACgAAAAgAAAAQAAAAAEAIAAAAAAAABAAAMMOAADDDgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABUaIwAUGiMAFBojABUaIwAVGiMAFRojABUaIwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFRojAAcABgAHAAIBNVtnAxwxPAQQDhYBDwgQABUaIwAVGiMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMRlQADElXAApSYQETIi0EFxMbARcSGgAVGiMAFRojAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABUaIwEOChIADgcOEx4vObQVFyCDKAAAECgAAAAVHycCFB4nAwZSYwD/AAAAFRojABMcIgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFRojAgAAAAAAAAAhR296+C6RpP8FMT/oHAwRbCoAAAcyAAAAFR0mAxYYIAEWFx8AFRojABUaIwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAVGiMAf+r3Apfd4gAwQUm3Ydnn/wCoxPoHYHP/ESgz2BsBBUITAAMAECIuAxUcJQMTIy4AEyEsABUaIwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABUaIwAUGCEDAAAAAAAAAFNfnqb/PPL/+wC31vsDiqL/C0NT/xUTG5QqAAAKNQAAABUaIwQXEhsAFxMbABUaIwAVGiMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFRojABQXIAEAAAAAAAAAAzFJUs907Pf/CeH//QDB3/0Aob37BWN3/xEjLtccAAU0GQAAABMcJgQVGSICFRojABUaIwAVGiMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAVGiMAGiMsABUbJAMAAAAAAAABYGOjrP9T+f/8AN/9/wLK5/8Aq8f7AYGZ/w03RPsYDRRyADFHAAVDVQIWGiIDEyItABMgKgAVGiMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFhkjABUaIwAVGiMAEhMcAQAAAAAAAAAGLUpU0oLs9v8c4//9AOP//wHT8f8AsMz9AJaw/AhOX/8UGCGwJAAAESkAAAAWGCEEGA4VABgQGAAVGiMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABUaIwAHAAUADQoSABceKAQ6Z3IEQFliBQAAAAAAAAJcX6Or/2v+//wA2/v/AOP//wDc+f8AtdH+AKG8+wRnfP8RJC/fHAUKNhsAAwAUGyQEFhcgARYYIQAVGiMAFRkiAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFRojABUaIwAVGiMBFRojAAAAAAA7AAEAt///AQAAAAYpOD/OieTw/zLq//0A3f3/AuL//wDh/v8AvNn/AKTA+wF+lf8NMj/6GQ0UYxESHAAPJzMDFhcgAhUaIwAVGiMAFRojAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQExoAAAAAABBAJgEKCQ9XHjA6pjZPWcczW2fZGWNy2wZNXe1Ot8f/X/X//gDd/f8B3///AOD+/wDk//8Aw+H/AKXA/QCOqPwKQVD/FhQdkeQAAAEAZXwBFxcfAhQcJQAVGyQAFRojAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABghKgMHAAkACgUNU0iBjf9+3+38Y+X3/xTk//8C4///AOj//wDh/v8E4P//AOD//wDg//8A4P//AN/+/wDl//8Ayuf/AKTA/gCYs/sHT2D/FBsltyYAAA49AAAAFxYeAxQcJgAVHCUAFRojAAAAAAAAAAAAAAAAAAAAAAAAAAAAGSMsBAQABQAGAAldZLO5/5L///ge4vz8AN7//QHf/v0A3v3+AeD//wDg//8A4P//AOD//wDf/v8A3/7/AN79/wDl//8AzOn/AKK+/wCduPoEWm7/EiIs0R8AAR0lAAAAFhUdAxUcJQAVGyQAFRojAAAAAAAAAAAAAAAAAAAAAAAUGCECAAAAAAAAAB5Bc3zzjP3//x7g/P4A3///AeD//wDg//8A4P//AOD//wDg//8A4v//AOX//wDj//8A4v//AOH+/wDp//8AyeX/AKC7/wCeufsDYHT/EScy4B4ABCYhAAAAFxMbAhUaIwAVGiMAAAAAAAAAAAAAAAAAAAAAABceKAA4YGsDKkZTABclL5950Nf/S/H/+wDd/v8C4P//AOD//wDg//8A4P//AOL//wDV9P8AyOb/ANLx/wDV9P8A1vT/ANTy/wDA3P8Anbj/AKO+/wCWsPsCYHT/ESo14h4AACEgAAAAGBEYAhcaIgAAAAAAAAAAAAAAAAAVGiMAFRojAA8PFwIAAAAAAAAAKkNye/eC/f//DN79/gDg//8B4P//AOD//wDg//8A4f//AN38/wCqxf8AnLf/AKG8/wCjvv8ApcD/AKG8/wCkv/8ApcH/AZy2/wBsgvsDW27/EiUww9AAAAFnAAAAFRojAQAAAAAAAAAAFRojAAAAAAAAAAAAHiw2BEFyfQYEAA0ADRIdiW68w/9Y+P/8ANz9/wLg//8A4P//AOD//wDf//8A4///ANn2/wCkv/8Aobz/AIae/wB8k/8Ah5//AImi/wCFnf0Ac4r7AGd9+wByif0LQVD/HQAALh0AAAAVGiMCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgEBAQAAAAAAAAALKkZP1Yfq9f8v6P/9AN7+/wHg//8A4P//AOD//wDf/v8A5P//AM3p/wCfuv8AmrX/AGuA/wRQY/8JQE//Bkpb/gdMXf8HTl/9CkFQ/xIlMLUsAAAEKwAAABUaIwEAAAAAAAAAABUaIwAAAAAAHAAAABUdJnAtQUq9OlJbyzVXYsQbND/hTJqo/3T6//4M3/z/AOD//wHg//8A4P//AOD//wDf/v8A5f//AL7b/wCfu/8AnLb/AGh9/hAtOf8aCxKHFhcfURgPF18cBAg2MQAABDEAAAAlAAAAAAAAAAAAAAAAAAAAFRojAgAAAAAAAAArSnmE/2Pr/v8f3ff/Gt75/w7f+/8C2ff/BuH//wXh//8A4P//AOD//wDg//8A4P//AOD//wDg/v8A4///ALHN/wCgu/8AlrD9AWN4/w8uOtkjAAAXJAAAABgOFQEUHSYCFRojARUaIwAVGiMAAAAAAAAAAAAVGiMBAAAAAAAAAAU3U13Sa+72/wPi//oA4P/8AOH//gDi//8A4P//AOD//wDg//8A4P//AOD//wDg//8A4P//AN///wDh//8A3Pn/AKbB/wCjvv8AjKX9A1ls/xIkLs4mAAANALrcARcSGgIVGSIAFRojABUaIgAAAAAAAAAAABUZIgARExsDAAAAAAAAAElQgIn/Y////ADb+/4A3/7/A+D//wLg//8B4P//AeD//wHg//8A4P//AOD//wDg//8A4P//AN/+/wDj//8A0u//AJ+6/wCjvv8Agpr7BVBi/xUcJaYDWm4ACUVUAx0AAwAVGiMAFRojAAAAAAAAAAAAFRojAGaDsQAnPUoDEBIgAAcIEHtem6b/a///+gvf/P4A3Pz/Ad39/wDd/f8A3f3/AN79/wDe/f8A3v3/AN79/wDf/v8B3/7/Ad79/wHk//8BxeL/AZ64/wGfuv8AdIv7CUVV/xgRGXQYEBcAEyAqAxMgKgAVGiMAAAAAAAAAAAAVGiMAFhwmAAAAAAA7XW8DPV95AA4WHY5alqP/gf3//FL2/vw27f//JOz//xnr//8Q6v//Cuj//wXn//8C5v//AOX//wDl//8A5P//AOP+/wDo//8At9T/AKG9/wCTrf4AaX/+DThF+xwBBTcdAAAAFxQdAhUaIwAAAAAAAAAAAAAAAAAVGiMAEhMbAAcHCwAuRVYDX3ugAA0SGG0wV2PzNo2e/zynuf0/rsD9QLXJ/UC90fw/w9f7P8jd+z3N4/s80ef7OdTq+zfW7fs01u37Mdnx/Cy91Pwmpbv8FJqx/ABrgfkCYXX/ESgzwQDU+wAA//8AFRojAAAAAAAAAAAAAAAAAAAAAAAVGiMAExUeABMVHgAQFh4EAwAAAAEAACQEGCPBADhI/wA7TP4APU7/AUJT/wNHWP8ES13/BlBi/wdVZ/8JWWv/Cl1v/wtfcv8LYXT/C2J2/wlkeP8EYHT/AV9z/gFjeP8MOUf/HQABKh0AAQAVGiMCAAAAAAAAAAAAAAAAAAAAABYaJwAVGiMAAAAAAAAAAAAkLzcDXAAAAHkAAAImDBE2Iw4TPSEPFUAdFBpRGRcfYBcaIm8UHCV9Eh4oixEgK5YPIy2iDiUwrA4nMrQNKDS5Dik1vQ8qNr4RKTW5EiUvsBQdJncXEhoFGA8XABUaIwEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAVGiMAFBwmABQdJwAVGyUCESs2AhQdJwAUHScAAOHmAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAVGiMAFRojABUaIgAVGiMAFRojAxUaIwMVGyQDFRwlAxQdJwQTICkEEyMtBBEnMgQQLDgEDjRBBAs9TAMISVkDBFZpAgFhdgIBY3gCBFdqAgs9TAMTIiwEGA4VABgOFQAVGiMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABYaJAAQGx8AHhkqABUaIwAVGiMAFRojABUaIwAVGiMAFRojABUaIwAVGiMAFRojABMbJQAOHi0AFRojAAAAAAAAAAAA/z////oX////Rf//+hN///oEv//5Ak//+QCX//kAS//8gCT//IAJf+hABL/oAAJf6AAAL+gAAFfoAAAr6AAAFeQAAAvkAAAFogAABfoAAAWgAAALoAAARaAAAAuQAAAjqAAAFcQAAAnSAAAJ6QAABfSAAAX5L////oAABf//wB8="
        icon_data = base64.b64decode(icon_base64)
        pixmap = QPixmap()
        pixmap.loadFromData(QByteArray(icon_data))
        # Crear QIcon y asignarlo
        self.setWindowIcon(QIcon(pixmap))
        self.setWindowTitle(f"Panel de Administración - {self.username}")
        self.setGeometry(200, 200, 400, 300)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Etiqueta superior
        label = QLabel(f"Bienvenido, {self.username} (Administrador)")
        label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(label)

        # Botones
        self.btn_fechas = QPushButton("Ir a Selector de Fechas")
        self.btn_crear = QPushButton("Crear Usuario")
        self.btn_modificar = QPushButton("Modificar Contraseña")
        self.btn_eliminar = QPushButton("Eliminar Usuario")
        self.btn_salir = QPushButton("Salir")

        # Añadir botones al layout
        for btn in [self.btn_fechas, self.btn_crear, self.btn_modificar, self.btn_eliminar, self.btn_salir]:
            btn.setFixedHeight(40)
            layout.addWidget(btn)

        self.setLayout(layout)

        # Conexiones
        self.btn_fechas.clicked.connect(self.abrir_selector_fechas)
        self.btn_crear.clicked.connect(self.abrir_crear_usuario)
        self.btn_modificar.clicked.connect(self.abrir_modificar_pwd)
        self.btn_eliminar.clicked.connect(self.abrir_eliminar_usuario)
        self.btn_salir.clicked.connect(QtWidgets.QApplication.quit)

    def abrir_selector_fechas(self):
        """Abre la ventana de selección de fechas desde el panel admin."""
        self.hide()
        self.ventana_fechas = VentanaFechas()
        self.ventana_fechas.setGeometry(self.geometry())
        self.ventana_fechas.show()
        
    def abrir_crear_usuario(self):
        self.hide()
        self.ventana_crear = VentanaCrearUsuario(self.username)
        self.ventana_crear.setGeometry(self.geometry())
        self.ventana_crear.show()
        
    def abrir_modificar_pwd(self):
        self.hide()
        self.ventana_modificar = VentanaModificarPasswordAdmin()
        self.ventana_modificar.setGeometry(self.geometry())
        self.ventana_modificar.show()
    
    def abrir_eliminar_usuario(self):
        self.hide()
        self.ventana_eliminar = VentanaEliminarUsuario()
        self.ventana_eliminar.setGeometry(self.geometry())
        self.ventana_eliminar.show()

# --- Clase para la creación de usuarios ---  
class VentanaCrearUsuario(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        # Convertir a bytes y crear QPixmap
        icon_base64 = "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N/8Az1P/AKxJ////////////AK1L/wDQVv8AyDv/AL4d/wC1A/8AsAD/AJEAswAAAA8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABUAngDkALQA/wCrBv8AlRb/AJsq/wCgPf8Aizf///////////8Aizj/AKFA/wCbLP8Alhn/AKsI/wC0AP8AoQDkAAAAFQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFQCgAPsAtAD/AIwE//////////////////////////////////////////////////////8AjAb/ALUA/wCjAPsAAAAVAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAPAJoA+gCyAP8AiwT//////////////////////////////////////////////////////wCMBv8AswD/AJ0A+gAAAA8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYAkQDfAK4A/wKtB/8QmiT/FJ83/xSkSP8OjTz///////////8OjT7/FKRK/xSgOv8Qmyb/Aq0J/wCuAP8AlADeAAAABgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQCJAJ4ApAD/KMUq/z7SUP8+2Wb/Pt57/yu1Yf///////////yu1Yv8+333/Ptpp/z7TU/8oxSv/AKQA/wCKAJ4AAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAH8ANgCVAP4fuh//XtZi/17bcf9e33//SMBq////////////SMBr/17fgf9e3HP/Xtdk/x+6H/8AlAD+AH8ANgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIkAngGfAf9dz13/ft6B/33hiv9qzHv///////////9qzHv/feGL/37fgv9d0F3/AZ8B/wCJAJ4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAfwAKAI0AwwqiCv921Hb/neWd/5bgmf+O2JL/jtiS/5bgmv+d5Z7/dtR2/wqiCv8AjQDDAH8ACgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAfwAKAIoAnAKVAv5FukX/itiK/6zlrP+s5az/itiK/0W6Rf8ClQL+AIoAnAB/AAoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIkAMgCMAJgAlADaAJgA+QCXAPoAlADaAI4AmACJADIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgACABwAAAAAAAAAAAAAAAIAAAACAAAABwAEAAfAHgAP8H/gf/B/4H/wP8B/4D/Af8AfgH/AH4B/wB8AP8AcAA/AHAAP4DgAB+AwAAP48AAD//AAA//wAAP/8AAD//AAA//wAAP/8AAD//gAB//8AA///AAP//4AH///gH/////8="
        icon_data = base64.b64decode(icon_base64)
        pixmap = QPixmap()
        pixmap.loadFromData(QByteArray(icon_data))
        # Crear QIcon y asignarlo
        self.setWindowIcon(QIcon(pixmap))
        self.setObjectName("VentanaCrearUsuario")
        self.setWindowTitle("Crear Usuario")
        self.resize(2500, 2500)

        # Layout principal
        main_layout = QVBoxLayout()
        form_layout = QHBoxLayout()

        # Izquierda: formulario
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Nombre de usuario:"))
        self.input_user = QLineEdit()
        left_layout.addWidget(self.input_user)

        left_layout.addWidget(QLabel("Contraseña:"))
        self.input_pass = QLineEdit()
        self.input_pass.setEchoMode(QLineEdit.EchoMode.Password)
        left_layout.addWidget(self.input_pass)

        self.chk_admin = QCheckBox("Administrador")
        left_layout.addWidget(self.chk_admin)
        self.chk_must_change = QCheckBox("Forzar cambio en siguiente login")
        self.chk_must_change.setChecked(True)
        left_layout.addWidget(self.chk_must_change)

        btn_crear = QPushButton("Crear Usuario")
        btn_crear.clicked.connect(self.crear_usuario)
        #self.btn_crear.clicked.connect(self.crear_usuario)

        self.btn_atras = QPushButton("Atrás")
        self.btn_atras.clicked.connect(self.volver_atras)

        left_layout.addWidget(btn_crear)
        left_layout.addWidget(self.btn_atras)
        left_layout.addStretch()

        # Derecha: tabla de usuarios
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Usuarios existentes:"))

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Usuario", "Administrador"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        right_layout.addWidget(self.table)

        form_layout.addLayout(left_layout, 2)
        form_layout.addLayout(right_layout, 3)

        main_layout.addLayout(form_layout)
        self.setLayout(main_layout)

        # Conexiones
        

        # Cargar datos iniciales
        self.fernet = None
        try:
            self.fernet = cargar_fernet()
        except Exception as e:
            QMessageBox.critical(self, "Error clave", f"No se pudo cargar '{KEY_FILE}': {e}")
        self.refrescar_tabla()

    def refrescar_tabla(self):
        """Lee la DB y rellena la QTableWidget con usuario (descifrado) y admin (0/1)."""
        self.table.setRowCount(0)
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("SELECT username, administrador FROM usuarios")
            filas = c.fetchall()
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Error BD", f"No se pudo leer la base de datos: {e}")
            return

        for row_idx, (u_cifrado, admin_flag) in enumerate(filas):
            if self.fernet:
                try:
                    usuario_desc = self.fernet.decrypt(u_cifrado.encode()).decode()
                except Exception:
                    usuario_desc = u_cifrado  # si ya está en texto plano o no puede descifrarse
            else:
                usuario_desc = u_cifrado
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(usuario_desc))
            self.table.setItem(row_idx, 1, QTableWidgetItem("Sí" if int(admin_flag) else "No"))

        self.table.resizeColumnsToContents()

    def crear_usuario(self):
        usuario = self.input_user.text().strip()
        pwd = self.input_pass.text().strip()
        admin_flag = 1 if self.chk_admin.isChecked() else 0
        #Êmust_change_flag = 1 if self.chk_must_change.isChecked() else 0

        if not usuario or not pwd:
            QMessageBox.warning(self, "Datos incompletos", "Rellena usuario y contraseña.")
            return

        # comprobar existencia
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("SELECT username FROM usuarios")
            filas = c.fetchall()
        except Exception as e:
            QMessageBox.critical(self, "Error BD", f"No se pudo acceder a la DB: {e}")
            return

        # comprobar duplicado (descifrando los existentes)
        for (u_cifrado,) in filas:
            if self.fernet:
                try:
                    u_desc = self.fernet.decrypt(u_cifrado.encode()).decode()
                    if u_desc == usuario:
                        QMessageBox.warning(self, "Usuario existe", "El usuario ya existe.")
                        conn.close()
                        return
                except Exception:
                    continue

        # insertar usuario
        try:
            u_cifrado = self.fernet.encrypt(usuario.encode()).decode() if self.fernet else usuario
            pwd_hash = hash_password(pwd)
            must_change_flag = 1 if self.chk_must_change.isChecked() else 0
            c.execute("INSERT INTO usuarios (username, password, administrador, must_change_pwd) VALUES (?, ?, ?, ?)",(u_cifrado, pwd_hash, admin_flag, must_change_flag))
                    

            conn.commit()
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Error BD", f"No se pudo insertar el usuario: {e}")
            return

        QMessageBox.information(self, "Usuario creado", f"Usuario '{usuario}' creado correctamente.")
        self.input_user.clear()
        self.input_pass.clear()
        self.chk_admin.setChecked(False)
        self.refrescar_tabla()
        
    def volver_atras(self):
        """Vuelve a la ventana de administración."""
        self.close()
        self.ventana_admin = VentanaAdmin(self.username)
        self.ventana_admin.setGeometry(self.geometry())  # opcional, mantiene posición/tamaño
        self.ventana_admin.show()

# --- Clase para la modificación de password ---  
class VentanaModificarPasswordAdmin(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modificar / Resetear Contraseña de Usuario")
        
        # Convertir a bytes y crear QPixmap
        icon_base64 = "AAABAAEAICAAAAEAIACoEAAAFgAAACgAAAAgAAAAQAAAAAEAIAAAAAAAABAAAHudAAB7nQAAAAAAAAAAAAAAAAACAAAAAAAAAAoAAAB5AAAA2gAAAPsAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAPsAAADaAAAAegAAAAoAAAAAAAAAAgAAAAAAAAAcAAAAzgAAAP8AAAD+AAAA/wAAAP4AAAD+AAAA/gAAAP4AAAD+AAAA/gAAAP4AAAD+AAAA/gAAAP4AAAD+AAAA/gAAAP4AAAD+AAAA/gAAAP4AAAD+AAAA/gAAAP4AAAD+AAAA/wAAAP4AAAD/AAAAzgAAAB0AAAAAAAAACQAAAMkAAAD/AAAA+wAAAPsAAAD+AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD+AAAA+wAAAPsAAAD/AAAAyQAAAAkAAAB6AAAA/wAAAPoAAAD/AAAA/wAAAPcAAADtAAAA7gAAAO4AAADuAAAA7gAAAO4AAADuAAAA7gAAAO4AAADuAAAA7gAAAO4AAADuAAAA7gAAAO4AAADuAAAA7gAAAO4AAADuAAAA7QAAAPcAAAD/AAAA/wAAAPoAAAD/AAAAegAAANUAAAD/AAAA+wAAAP8AAACtAAAAGgAAABAAAAARAAAAEgAAABEAAAARAAAAEQAAABEAAAARAAAAEQAAABEAAAARAAAAEQAAABEAAAARAAAAEQAAABEAAAARAAAAEQAAABIAAAARAAAAGQAAAK0AAAD/AAAA+wAAAP8AAADVAAAA+AAAAP8AAAD/AAAA+QAAACMAAAAAAAAABgAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAIwAAAPkAAAD/AAAA/wAAAPgAAAD+AAAA/gAAAP8AAADuAAAAEwAAAAAAAADEAAAAwwAAAAAAAAABAAAAAgAAAAEAAAABAAAAAQAAAAEAAAABAAAAAQAAAAEAAAABAAAAAQAAAAEAAAABAAAAAQAAAAEAAAABAAAAAgAAAAAAAAAUAAAA7QAAAP8AAAD+AAAA/gAAAP8AAAD+AAAA/wAAAO8AAAAOAAAADAAAAPMAAADyAAAAEQAAAAAAAAABAAAAAAAAAAEAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAAAAAAAABIAAADuAAAA/wAAAP4AAAD/AAAA/wAAAP4AAAD/AAAA7gAAAA8AAAAEAAAA5QAAAPwAAAAdAAAAAAAAAAIAAAADAAAAAAAAAAAAAAADAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEAAAAAAAAAEQAAAO4AAAD/AAAA/gAAAP8AAAD/AAAA/gAAAP8AAADuAAAAEgAAAAAAAADIAAAA/wAAAEgAAAAAAAAABQAAAAAAAAALAAAACwAAAAAAAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAAAAAAAAARAAAA7gAAAP8AAAD+AAAA/wAAAP8AAAD+AAAA/wAAAO4AAAAVAAAAAAAAAKEAAAD/AAAAkwAAAAAAAAALAAAAjwAAAOkAAADpAAAAkAAAAAcAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAAAAAAAABEAAADuAAAA/wAAAP4AAAD/AAAA/wAAAP4AAAD/AAAA7gAAABUAAAAAAAAAdAAAAP8AAADrAAAADAAAAIoAAAD/AAAA/AAAAPwAAAD/AAAAkAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEAAAAAAAAAEQAAAO4AAAD/AAAA/gAAAP8AAAD/AAAA/gAAAP8AAADuAAAAFAAAAAAAAABCAAAA/wAAAP8AAACgAAAA1wAAAP8AAAD8AAAA/AAAAP8AAADkAAAACgAAAAAAAAAEAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAAAAAAAAARAAAA7gAAAP8AAAD+AAAA/wAAAP8AAAD+AAAA/wAAAO4AAAATAAAAAAAAABQAAADsAAAA/wAAAPwAAAD9AAAA/wAAAP8AAAD9AAAA/wAAANwAAAARAAAACAAAAAAAAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAAAAAAAABEAAADuAAAA/wAAAP4AAAD/AAAA/wAAAP4AAAD/AAAA7gAAABIAAAAAAAAAAAAAALgAAAD/AAAA+gAAAP8AAAD/AAAA/wAAAP4AAAD/AAAA6gAAANwAAADsAAAAkAAAAAcAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAEAAAAAAAAAEQAAAOsAAAD/AAAA/QAAAP8AAAD/AAAA/gAAAP8AAADuAAAAEQAAAAAAAAAAAAAAcQAAAP8AAAD7AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAPwAAAD/AAAAkAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAAAQAAAAAAAAARAAAA7gAAAP8AAAD9AAAA/AAAAP8AAAD+AAAA/wAAAO4AAAARAAAAAAAAAAAAAAApAAAA+wAAAP8AAAD+AAAA/wAAAP8AAAD/AAAA/wAAAP4AAAD9AAAA/AAAAP8AAADkAAAACgAAAAAAAAAEAAAAAQAAAAAAAAAAAAAAAAAAAAIAAABNAAAApgAAAPYAAAD/AAAA/wAAAP4AAAD/AAAA7gAAABEAAAAAAAAAAgAAAAAAAADAAAAA/wAAAPwAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD9AAAA/wAAANwAAAARAAAACAAAAAAAAAACAAAAAAAAAAEAAAABAAAAAAAAAAEAAAAAAAAAJQAAAK0AAAD/AAAA/gAAAP8AAADuAAAAEQAAAAAAAAAFAAAAAAAAAGUAAAD/AAAA/AAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP4AAAD/AAAA6gAAANwAAADsAAAAiwAAAAUAAAABAAAAAAAAAAAAAAABAAAABwAAAAQAAAAAAAAAAgAAAP8AAAD+AAAA/wAAAO4AAAARAAAAAAAAAAIAAAAAAAAAEQAAAOUAAAD/AAAA/gAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAPwAAAD/AAAAggAAAAAAAAAQAAAADgAAAAAAAAAAAAAAAgAAAAQAAAACAAAA/wAAAP4AAAD/AAAA7gAAABEAAAAAAAAAAQAAAAQAAAAAAAAAgwAAAP8AAAD7AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAA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"
        icon_data = base64.b64decode(icon_base64)
        pixmap = QPixmap()
        pixmap.loadFromData(QByteArray(icon_data))
        # Crear QIcon y asignarlo
        self.setWindowIcon(QIcon(pixmap))
        
        self.resize(450, 250)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Nombre de usuario:"))
        self.input_user = QLineEdit()
        layout.addWidget(self.input_user)

        layout.addWidget(QLabel("Nueva contraseña temporal:"))
        self.input_pwd = QLineEdit()
        self.input_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.input_pwd)

        self.chk_forzar = QCheckBox("Forzar cambio en siguiente login")
        self.chk_forzar.setChecked(True)
        layout.addWidget(self.chk_forzar)

        self.btn_guardar = QPushButton("Guardar cambios")
        self.btn_guardar.clicked.connect(self.guardar)
        layout.addWidget(self.btn_guardar)

        self.btn_atras = QPushButton("Atrás")
        self.btn_atras.clicked.connect(self.volver_atras)
        layout.addWidget(self.btn_atras)

        self.setLayout(layout)

        # Cargar Fernet para descifrar usernames
        try:
            self.fernet = cargar_fernet()
        except Exception as e:
            QMessageBox.critical(self, "Error clave", f"No se pudo cargar '{KEY_FILE}': {e}")
            self.close()

    def guardar(self):
        usuario = self.input_user.text().strip()
        nueva = self.input_pwd.text().strip()
        if not usuario or not nueva:
            QMessageBox.warning(self, "Campos vacíos", "Introduce usuario y nueva contraseña.")
            return

        must_change = 1 if self.chk_forzar.isChecked() else 0

        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()

            pwd_hash = hash_password(nueva)

            # Buscar el username cifrado original en la DB
            c.execute("SELECT username FROM usuarios")
            filas = c.fetchall()
            u_cifrado_existente = None
            for (u_enc,) in filas:
                try:
                    if self.fernet.decrypt(u_enc.encode()).decode() == usuario:
                        u_cifrado_existente = u_enc
                        break
                except Exception:
                    continue

            if not u_cifrado_existente:
                QMessageBox.warning(self, "No encontrado", f"El usuario '{usuario}' no existe.")
                conn.close()
                return

            # UPDATE usando username cifrado original
            c.execute("""
                UPDATE usuarios
                SET password = ?, must_change_pwd = ?
                WHERE username = ?
            """, (pwd_hash, must_change, u_cifrado_existente))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Éxito", f"Contraseña temporal asignada a '{usuario}'.")
            self.input_user.clear()
            self.input_pwd.clear()
            self.chk_forzar.setChecked(True)

        except Exception as e:
            QMessageBox.critical(self, "Error BD", f"No se pudo actualizar la contraseña: {e}")

    def volver_atras(self):
        """Vuelve al panel de administración."""
        self.close()
        self.ventana_admin = VentanaAdmin("<ADMIN>")
        self.ventana_admin.setGeometry(self.geometry())
        self.ventana_admin.show()

# --- Clase para la ventana de cambio de pass en siguiente sesión ---  
class VentanaCambioPassword(QWidget):
    def __init__(self, username_cifrado, parent=None):
        super().__init__(parent)
        self.username_cifrado = username_cifrado  # Valor cifrado tal como está en la DB
        self.setWindowTitle("Cambio de Contraseña Obligatorio")
        
         # Convertir a bytes y crear QPixmap
        icon_base64 = "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AAD///8C3NzcFurq6jH///8Nf39/AgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/////////////////////4P//8EB//+AAP/+AAA//AAAB+AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAAABgAAAAcAAAAPAAAAD4AAAB/AAAA/4AAAf/B/4P/////////////////////8="
        icon_data = base64.b64decode(icon_base64)
        pixmap = QPixmap()
        pixmap.loadFromData(QByteArray(icon_data))
        # Crear QIcon y asignarlo
        self.setWindowIcon(QIcon(pixmap))
        
        self.resize(400, 220)

        layout = QVBoxLayout()

        # Cargamos Fernet para descifrar el username solo para mostrarlo
        try:
            self.fernet = cargar_fernet()
            username_plano = self.fernet.decrypt(self.username_cifrado.encode()).decode()
        except Exception:
            username_plano = "<error descifrado>"

        layout.addWidget(QLabel(f"Usuario: {username_plano}"))
        layout.addSpacing(10)

        # Inputs de contraseña
        self.input_nueva = QLineEdit()
        self.input_nueva.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_nueva.setPlaceholderText("Nueva contraseña")
        layout.addWidget(self.input_nueva)

        self.input_confirma = QLineEdit()
        self.input_confirma.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_confirma.setPlaceholderText("Confirmar nueva contraseña")
        layout.addWidget(self.input_confirma)

        # Botón guardar
        self.btn_guardar = QPushButton("Guardar nueva contraseña")
        self.btn_guardar.clicked.connect(self.guardar_cambio)
        layout.addWidget(self.btn_guardar)

        self.setLayout(layout)

    def guardar_cambio(self):
        nueva = self.input_nueva.text().strip()
        confirma = self.input_confirma.text().strip()

        if not nueva or not confirma:
            QMessageBox.warning(self, "Campos vacíos", "Rellena ambos campos.")
            return
        if nueva != confirma:
            QMessageBox.warning(self, "Error", "Las contraseñas no coinciden.")
            return

        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()

            # Calculamos el hash de la nueva contraseña
            pwd_hash = hash_password(nueva)

            # Actualizamos usando el username cifrado original
            c.execute("""
                UPDATE usuarios 
                SET password=?, must_change_pwd=0 
                WHERE username=?
            """, (pwd_hash, self.username_cifrado))

            conn.commit()
            conn.close()

            QMessageBox.information(
                self,
                "Contraseña actualizada",
                "Tu contraseña ha sido cambiada correctamente.\nPor favor, inicia sesión de nuevo."
            )

            self.close()

            # Volvemos al login
            self.ventana_login = LoginWindow()
            self.ventana_login.show()

        except Exception as e:
            QMessageBox.critical(self, "Error BD", f"No se pudo actualizar la contraseña: {e}")

# --- Clase para eliminación de usuarios ---  
class VentanaEliminarUsuario(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Eliminar Usuario")
        # Convertir a bytes y crear QPixmap
        icon_base64 = "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"
        icon_data = base64.b64decode(icon_base64)
        pixmap = QPixmap()
        pixmap.loadFromData(QByteArray(icon_data))
        # Crear QIcon y asignarlo
        self.setWindowIcon(QIcon(pixmap))
        
        self.resize(500, 400)

        layout = QVBoxLayout()

        # Input usuario
        layout.addWidget(QLabel("Nombre de usuario a eliminar:"))
        self.input_user = QLineEdit()
        layout.addWidget(self.input_user)

        # Botones
        self.btn_eliminar = QPushButton("Eliminar")
        self.btn_eliminar.clicked.connect(self.eliminar_usuario)
        self.btn_atras = QPushButton("Atrás")
        self.btn_atras.clicked.connect(self.volver_atras)

        layout.addWidget(self.btn_eliminar)
        layout.addWidget(self.btn_atras)

        layout.addSpacing(10)
        layout.addWidget(QLabel("Usuarios existentes:"))

        # Tabla de usuarios
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Usuario", "Administrador"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        self.setLayout(layout)

        # Cargar Fernet
        try:
            self.fernet = cargar_fernet()
        except Exception as e:
            QMessageBox.critical(self, "Error clave", f"No se pudo cargar '{KEY_FILE}': {e}")
            self.close()
            return

        # Cargar tabla inicial
        self.refrescar_tabla()

    def refrescar_tabla(self):
        """Carga usuarios desde la DB y los muestra descifrados en la tabla."""
        self.table.setRowCount(0)
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("SELECT username, administrador FROM usuarios")
            filas = c.fetchall()
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Error BD", f"No se pudo leer la base de datos: {e}")
            return

        for row_idx, (u_cifrado, admin_flag) in enumerate(filas):
            try:
                usuario_desc = self.fernet.decrypt(u_cifrado.encode()).decode()
            except Exception:
                usuario_desc = "<error descifrado>"
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(usuario_desc))
            self.table.setItem(row_idx, 1, QTableWidgetItem("Sí" if int(admin_flag) else "No"))

        self.table.resizeColumnsToContents()

    def eliminar_usuario(self):
        usuario = self.input_user.text().strip()
        if not usuario:
            QMessageBox.warning(self, "Campo vacío", "Introduce el nombre de usuario a eliminar.")
            return

        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()

            # Buscar el username cifrado correspondiente
            c.execute("SELECT username FROM usuarios")
            filas = c.fetchall()
            u_cifrado_existente = None
            for (u_enc,) in filas:
                try:
                    if self.fernet.decrypt(u_enc.encode()).decode() == usuario:
                        u_cifrado_existente = u_enc
                        break
                except Exception:
                    continue

            if not u_cifrado_existente:
                QMessageBox.warning(self, "No encontrado", f"El usuario '{usuario}' no existe.")
                conn.close()
                return

            # Confirmación antes de borrar
            reply = QMessageBox.question(
                self, "Confirmar eliminación",
                f"¿Seguro que quieres eliminar al usuario '{usuario}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                conn.close()
                return

            # Ejecutar borrado
            c.execute("DELETE FROM usuarios WHERE username = ?", (u_cifrado_existente,))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Éxito", f"Usuario '{usuario}' eliminado correctamente.")
            self.input_user.clear()

            # Refrescar tabla
            self.refrescar_tabla()

        except Exception as e:
            QMessageBox.critical(self, "Error BD", f"No se pudo eliminar el usuario: {e}")

    def volver_atras(self):
        """Vuelve al panel de administración."""
        self.close()
        self.ventana_admin = VentanaAdmin("<ADMIN>")
        self.ventana_admin.setGeometry(self.geometry())
        self.ventana_admin.show()

# --- Programa principal ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())
