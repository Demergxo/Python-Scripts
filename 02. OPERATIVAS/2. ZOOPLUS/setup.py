#python setup.py build
import sys, pkgutil
#sys.setrecursionlimit(5000)
from cx_Freeze import setup, Executable
import os



tkdnd_dir = os.path.join(os.path.dirname(sys.argv[0]), "tkdnd")

tkdnd_files = [
    (r"C:\Users\jgmeras\AppData\Roaming\Python\Python311\tcl\tkdnd\libtkdnd2.9.2.dll", "tcl/tkdnd/libtkdnd2.9.2.dll"),
    (r"C:\Users\jgmeras\AppData\Roaming\Python\Python311\tcl\tkdnd\tkdnd.tcl", "tcl/tkdnd/tkdnd.tcl"),

]


BasicPackages=["collections","encodings","importlib","functools", "tkinter", "os", "base64", "tempfile", "PIL", "logging", "urllib", "textwrap", "re", "base64", "io", "tkinterdnd2", "pandas", "datetime", "dateutil", "pytz", "numpy", "json", "ctypes", "zipfile"]
def AllPackage(): return [i.name for i in list(pkgutil.iter_modules()) if i.ispkg]; # Return name of all package

def notFound(A,v): # Check if v outside A
    try: A.index(v); return False
    except: return True

build_exe_options = {
    "includes": BasicPackages,
    "excludes": [i for i in AllPackage() if notFound(BasicPackages,i)],
    "include_files": tkdnd_files,
    "packages": ["tkinterdnd2"],
    "zip_include_packages": BasicPackages,
    "build_exe": "Relocation"
}
setup(  name = "Relocation",
        version="0.1",
        options = {"build_exe": build_exe_options},#"bdist_msi": build_msi_options},#,  
        executables = [Executable(
            "relocation.py",
            base= None,#'Win32GUI',#Win64GUI
            icon="Morti.ico",
            target_name="Relocation",
            copyright="Copyright (C) 2900AD Mer"
            )]
)