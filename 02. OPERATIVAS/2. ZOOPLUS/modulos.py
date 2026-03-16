import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,  QPushButton



class ZonaArrastre(QLabel):
    def __init__(self, texto, color, callback):
        super().__init__(texto)
        self.callback = callback  # Función para enviar la ruta al QLabel asociado

        self.setStyleSheet(f"""
            background-color: {color}; 
            border: 2px solid black; 
            color: black; 
            font: bold 18px Arial; 
            padding: 10px; 
        """)
        self.setFixedSize(300, 100)

        # Aceptar el arrastre en esta zona
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            # Obtener la ruta del primer archivo arrastrado
            file_path = event.mimeData().urls()[0].toLocalFile()
            self.callback(file_path)


class CargarArchivos(QWidget):
    def __init__(self):
        
        self._ruta_stock = ""  
        self._ruta_relocation = ""
        
        super().__init__()

        self.setWindowTitle("Cargar Archivos")
        self.setGeometry(100, 100, 600, 500)

        # Layout principal
        main_layout = QVBoxLayout()

        # Zona 1: Stock by Location
        self.label_stock_path = QLabel()
        self.label_stock_path.setFixedSize(300, 30)
        self.label_stock_path.setStyleSheet("background-color: white;font: 14px Arial; padding: 5px;")

        self.label_stock = ZonaArrastre("Stock by Location", "lightblue", self.mostrar_ruta_stock)

        layout_stock = QHBoxLayout()
        layout_stock.addWidget(self.label_stock)
        layout_stock.addWidget(self.label_stock_path)
        main_layout.addLayout(layout_stock)

        # Zona 2: Archivo Relocation
        self.label_relocation_path = QLabel()
        self.label_relocation_path.setFixedSize(300, 30)
        self.label_relocation_path.setStyleSheet("background-color: white;font: 14px Arial; padding: 5px;")

        
        self.label_relocation = ZonaArrastre("Archivo Relocation", "lightgreen", self.mostrar_ruta_relocation)

        layout_relocation = QHBoxLayout()
        layout_relocation.addWidget(self.label_relocation)
        layout_relocation.addWidget(self.label_relocation_path)
        main_layout.addLayout(layout_relocation)
        
        #botones  
        
        ok_button = QPushButton(self)
        ok_button.setText("OK")
        ok_button.resize(150, 32)
        ok_button.move(150, 450)
        ok_button.clicked.connect(self.salir)
        
        salir_button = QPushButton(self)
        salir_button.setText("Salir")
        salir_button.setStyleSheet("color: red")
        salir_button.resize(150, 32)
        salir_button.move(330, 450)
        salir_button.clicked.connect(self.salir)
        
         # Botón para comprobar rutas en consola
        self.btn_mostrar_rutas = QPushButton(self)
        self.btn_mostrar_rutas.setText("Mostrar Rutas")
        self.btn_mostrar_rutas.resize(150, 32)
        self.btn_mostrar_rutas.move(10, 450)
        self.btn_mostrar_rutas.clicked.connect(self.mostrar_rutas)

        self.setLayout(main_layout)
        
        
    def salir(self):
        self.close()

    #Metodos para actualalizar las rutas
    def mostrar_ruta_stock(self, ruta):
        """Mostrar la ruta del archivo arrastrado en la zona Stock."""
        self._ruta_stock = ruta
        self.label_stock_path.setText(f"{ruta}")

    def mostrar_ruta_relocation(self, ruta):
        """Mostrar la ruta del archivo arrastrado en la zona Relocation."""
        self._ruta_relocation = ruta
        self.label_relocation_path.setText(f"{ruta}")
    #Metodos para obtener las rutas desde otro modulo   
    
    @property
    def ruta_stock(self):
        """Obtener la ruta del archivo Stock."""
        return self._ruta_stock
    
    @ruta_stock.setter
    def ruta_stock(self, value):
        self._ruta_stock = value
    
    @property
    def ruta_relocation(self):
        """Obtener la ruta del archivo Relocation."""
        return self._ruta_relocation
    
    @ruta_relocation.setter
    def ruta_relocation(self, value):
        self._ruta_relocation = value   

    def dragEnterEvent(self, event):
        """Ignorar arrastres en la ventana principal."""
        event.ignore()

    def dropEvent(self, event):
        """Ignorar soltar archivos en la ventana principal."""
        event.ignore()

    def mostrar_rutas(self):
        print(f"Ruta Stock by location: {self._ruta_stock}")
        print(f"Ruta Stock by Relocation: {self._ruta_relocation}")

#cargar_archivos_instance = CargarArchivos()  

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CargarArchivos()
    window.show()
    sys.exit(app.exec())
