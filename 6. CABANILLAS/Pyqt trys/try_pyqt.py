import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QMessageBox

# Clase para la ventana secundaria
class VentanaSecundaria(QWidget):
    def __init__(self):
        super().__init__()

        # Configurar la ventana secundaria
        self.setWindowTitle("Ventana Secundaria")
        self.setGeometry(150, 150, 250, 150)

        # Crear un layout vertical
        layout = QVBoxLayout()

        # Añadir un QLabel (etiqueta de texto)
        self.etiqueta = QLabel("Esta es la ventana secundaria.", self)
        layout.addWidget(self.etiqueta)

        # Añadir un QPushButton (botón para cerrar)
        self.boton_cerrar = QPushButton("Cerrar", self)
        self.boton_cerrar.clicked.connect(self.cerrar_ventana)  # Conectar el evento de clic
        layout.addWidget(self.boton_cerrar)

        # Establecer el layout en la ventana
        self.setLayout(layout)

    # Método para cerrar la ventana secundaria
    def cerrar_ventana(self):
        self.close()  # Cierra la ventana secundaria

# Clase para la ventana principal
class VentanaPrincipal(QWidget):
    def __init__(self):
        super().__init__()

        # Configurar la ventana principal
        self.setWindowTitle("Ventana Principal")
        self.setGeometry(100, 100, 300, 200)

        # Crear un layout vertical
        layout = QVBoxLayout()

        # Añadir un QLabel (etiqueta de texto)
        self.etiqueta = QLabel("Esta es la ventana principal.", self)
        layout.addWidget(self.etiqueta)

        # Añadir un QPushButton (botón para abrir la ventana secundaria)
        self.boton_abrir = QPushButton("Abrir Ventana Secundaria", self)
        self.boton_abrir.clicked.connect(self.abrir_ventana_secundaria)  # Conectar el evento de clic
        layout.addWidget(self.boton_abrir)

        # Establecer el layout en la ventana
        self.setLayout(layout)

    # Método para abrir la ventana secundaria
    def abrir_ventana_secundaria(self):
        self.hide()  # Oculta la ventana principal
        self.ventana_secundaria = VentanaSecundaria()  # Crea una instancia de la ventana secundaria
        self.ventana_secundaria.show()  # Muestra la ventana secundaria
        self.ventana_secundaria.closeEvent = self.volver_a_principal  # Conectar el evento de cierre

    # Método para volver a la ventana principal cuando se cierra la secundaria
    def volver_a_principal(self, event):
        self.show()  # Muestra la ventana principal nuevamente

# Función principal
if __name__ == "__main__":
    # Crear una aplicación de PyQt
    app = QApplication(sys.argv)

    # Crear una instancia de la ventana principal
    ventana_principal = VentanaPrincipal()

    # Mostrar la ventana principal
    ventana_principal.show()

    # Ejecutar la aplicación
    sys.exit(app.exec_())