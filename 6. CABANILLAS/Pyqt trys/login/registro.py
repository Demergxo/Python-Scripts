
import os
from PyQt6.QtWidgets import QDialog, QLabel, QPushButton, QLineEdit, QMessageBox, QWidget
from PyQt6.QtGui import QFont


path = os.path.join(os.getcwd(),"6. CABANILLAS", "Pyqt trys", "login", "users.txt")

class RegistrarUsuarioView(QDialog):

    def crear_usuario(self):
        user = self.user_input.text()
        password1 = self.password1_input.text()
        password2 = self.password2_input.text()
        
        if password1 == '' or password2 == '' or user == '':
            QMessageBox.warning(self, 'Error', 'Por favor, complete todos los campos.', QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Ok)
            return
        
        elif password1 == password2 and user != '':
            with open(path, 'a') as file:
                file.write(f'{user},{password1}\n')
            QMessageBox.information(self, 'Información', 'Usuario creado correctamente', QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Ok)
            self.close()
        else:
            QMessageBox.warning(self, 'Error', 'Las contraseñas no coinciden. Por favor, inténtelo de nuevo.', QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Ok)
    
    def cancelar_registro(self):
        self.close()


    
    def generar_formulario(self):
        self.setGeometry(100, 100, 450, 215)
        self.setWindowTitle('Registro de usuario')
                
        user_label = QLabel(self)
        user_label.setText('Usuario:')
        user_label.setFont(QFont('Arial', 10))
        user_label.move(20, 44)
        
        self.user_input = QLineEdit(self)
        self.user_input.resize(250, 24)
        self.user_input.move(150, 40)
        
        password1_label = QLabel(self)
        password1_label.setText('Contraseña:')
        password1_label.setFont(QFont('Arial', 10))
        password1_label.move(20, 74)
        
        self.password1_input = QLineEdit(self)
        self.password1_input.resize(250, 24)
        self.password1_input.move(150, 70)
        self.password1_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        password2_label = QLabel(self)
        password2_label.setText('Confirmar contraseña:')
        password2_label.setFont(QFont('Arial', 10))
        password2_label.move(20, 104)
        
        self.password2_input = QLineEdit(self)
        self.password2_input.resize(250, 24)
        self.password2_input.move(150, 100)
        self.password2_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        register_button = QPushButton(self)
        register_button.setText('Confirmar Registro')
        register_button.resize(150, 32)
        register_button.move(70, 150)
        register_button.clicked.connect(self.crear_usuario)
        
        cancel_button = QPushButton(self)
        cancel_button.setText('Cancelar')
        cancel_button.resize(150, 32)
        cancel_button.move(250, 150)
        cancel_button.clicked.connect(self.cancelar_registro)
        
    
    
    def __init__(self):
        super().__init__()
        self.setModal(True)
        self.generar_formulario()
    