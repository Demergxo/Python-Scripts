import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QLineEdit, QPushButton, QMessageBox, QCheckBox
from PyQt6.QtGui import QFont, QPixmap
from registro import RegistrarUsuarioView


class Login(QWidget):
    
    def __init__(self):
        super().__init__()
        self.iniciarUI()
    
    def mostrar_contrasena(self, clicked):
        if clicked:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
    
    def ventana_registro(self):
        self.new_user_form = RegistrarUsuarioView()
        self.new_user_form.show()
        
    
    def ventana_mainview(self):
        pass
    
        
    def iniciarUI(self):
        self.setGeometry(100, 100, 350, 250)
        self.setWindowTitle('Login')
        self.generar_formulario()
        self.show()
        
    def generar_formulario(self):
        self.is_logged = False
        
        user_label = QLabel(self)
        user_label.setText('Usuario:')
        user_label.setFont(QFont('Arial', 12))
        user_label.move(12, 20)
        
        user_input = QLineEdit(self)
        user_input.resize(235, 24)
        user_input.move(100, 20)
        
        password_label = QLabel(self)
        password_label.setText('Contraseña:')
        password_label.setFont(QFont('Arial', 12))
        password_label.move(12, 60)
        
        self.password_input = QLineEdit(self)
        self.password_input.resize(235, 24)
        self.password_input.move(100, 60)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.check_view_password = QCheckBox(self)
        self.check_view_password.setText('Ver contraseña')
        self.check_view_password.move(100, 90)
        self.check_view_password.toggled.connect(self.mostrar_contrasena)
        self.check_view_password.setChecked(False)
        self.check_view_password.setFont(QFont('Arial', 10))
        
        login_button = QPushButton(self)
        login_button.setText('Iniciar sesión')
        login_button.resize(150, 32)
        login_button.move(100, 130)
        login_button.clicked.connect(self.ventana_mainview)
        register_button = QPushButton(self)
        register_button.setText('Registrarse')
        register_button.resize(150, 32)
        register_button.move(100, 170)
        register_button.clicked.connect(self.ventana_registro)
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = Login()
    sys.exit(app.exec())
