# Author: Javier García-Merás Palacios
# version: 0.1
# Description: Archivo para gestión y generación de reportes para el equipo de GDS

import os
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QLineEdit, QPushButton, QMessageBox, QCheckBox, QVBoxLayout
from PyQt6.QtGui import QFont, QPixmap
import modulos as md


class Login(QWidget):
    
    def __init__(self):
        super().__init__()
        self.iniciarUI()
        
    def iniciarUI(self):
        self.setGeometry(100, 100, 350, 250)
        self.setWindowTitle('Archivo Relocations')
        self.lanzar_main()
        self.show()
        
    def lanzar_main(self):
        
        stb_label = QLabel(self)
        stb_label.setText('Relocation')
        stb_label.setFont(QFont('Arial', 16, QFont.Weight.Bold))
        stb_label.move(90, 20)
        
        carga_button = QPushButton(self)
        carga_button.setText('Cargar Archivos')
        carga_button.resize(150, 32)
        carga_button.move(20, 80)
        carga_button.clicked.connect(self.cargar_archivos)
        
        ventana_trabajo_button = QPushButton(self)
        ventana_trabajo_button.setText('Ventana de Trabajo')
        ventana_trabajo_button.resize(150, 32)
        ventana_trabajo_button.move(180, 80)
        ventana_trabajo_button.clicked.connect(self.ventana_trabajo)
        
        salir_button = QPushButton(self)
        salir_button.setText('Salir')
        salir_button.setStyleSheet("color: red")
        salir_button.resize(150, 32)
        salir_button.move(180, 195)
        salir_button.clicked.connect(self.salir)
    
    def cargar_archivos(self):
        self.cargar_archivos = md.CargarArchivos() #type: ignore
        self.cargar_archivos.show()
        
    def ventana_trabajo(self):
        
        
        print('Ventana de Trabajo')
 
        print(f"Ruta Stock by location: {cargar_archivos_instance.ruta_stock}")
        print(f"Ruta Stock by Relocation: {cargar_archivos_instance.ruta_relocation}")
        
    def salir(self):
        self.close()    
        
      
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = Login()
    cargar_archivos_instance = md.CargarArchivos()
    login.show()
    sys.exit(app.exec())
