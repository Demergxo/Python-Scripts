import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox


class VentanaVacia(QWidget):
    
    def iniciarUI(self):
        self.setGeometry(100, 100, 300, 200)
        self.setWindowTitle('Ventana Vacía')
        self.show()
    
    def __init__(self):
        super().__init__()
        self.iniciarUI()
        
    
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaVacia()
    sys.exit(app.exec())