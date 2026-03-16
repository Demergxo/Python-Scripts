import sys, pkgutil
#sys.setrecursionlimit(5000)
from cx_Freeze import setup, Executable

include_files = [
    (r"C:\Users\jgmeras\AppData\Roaming\Python\Python311\site-packages\pptx\templates", "templates")  # Copia la carpeta templates al directorio de salida
]
BasicPackages=["collections","encodings","importlib","functools", "tkinter", "os", "tempfile", "re", "PIL", "logging", "urllib","datetime", "pptx", "base64", "io", "qrcode", "hashlib", "sqlite3", "lxml", "xml", "http"]
def AllPackage(): return [i.name for i in list(pkgutil.iter_modules()) if i.ispkg]; # Return name of all package

def notFound(A,v): # Check if v outside A
    try: A.index(v); return False
    except: return True

build_exe_options = {
    "includes": BasicPackages,
    "excludes": [i for i in AllPackage() if notFound(BasicPackages,i)],
    "include_files": include_files,
    
    "zip_include_packages": [],
    "build_exe": "Generación de Carteles"
}
setup(  name = "Generación de Carteles",
        version="0.1",
        options = {"build_exe": build_exe_options},#"bdist_msi": build_msi_options},#,  
        executables = [Executable(
            "gui_cartel.py",
            base='Win32GUI',#Win64GUI
            icon="caja-de-entrega_1_.ico",
            target_name="Generación de Carteles",
            copyright="Copyright (C) 2900AD Mer",
            )]
)

