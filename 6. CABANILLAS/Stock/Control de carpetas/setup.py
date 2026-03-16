import sys, pkgutil
#sys.setrecursionlimit(5000)
from cx_Freeze import setup, Executable

BasicPackages=["collections","encodings","importlib","functools", "tkinter", "os", "tempfile", "re", "PIL", "logging", "urllib","datetime"]
def AllPackage(): return [i.name for i in list(pkgutil.iter_modules()) if i.ispkg]; # Return name of all package

def notFound(A,v): # Check if v outside A
    try: A.index(v); return False
    except: return True

build_exe_options = {
    "includes": BasicPackages,
    "excludes": [i for i in AllPackage() if notFound(BasicPackages,i)],
    #"include_files":UseFile,
    
    "zip_include_packages": BasicPackages,
    "build_exe": "Manejo Carpetas"
}
setup(  name = "Manejo Carpetas",
        version="1.1",
        options = {"build_exe": build_exe_options},#"bdist_msi": build_msi_options},#,  
        executables = [Executable(
            "carpetas_gui.py",
            base='Win32GUI',#Win64GUI
            icon="carpeta_1_.ico",
            target_name="Manejo Carpetas",
            copyright="Copyright (C) 2900AD Mer",
            )]
)