import sys, pkgutil
from cx_Freeze import setup, Executable

BasicPackages = ["idna", "certifi", "collections", "encodings", "importlib", "functools", "urllib3", "xml", "et_xmlfile",
                 "os", "requests", "openpyxl", "json", "logging", "re", "http", "urllib", "pathlib", "zipfile"]

def AllPackage():
    return [i.name for i in list(pkgutil.iter_modules()) if i.ispkg]

def notFound(A, v):
    return v not in A

build_exe_options = {
    "includes": BasicPackages,
    "excludes": [i for i in AllPackage() if notFound(BasicPackages, i)],
    "zip_include_packages": BasicPackages,
    "build_exe": "Scrapper"
}

base = None
if sys.platform == "win32":
    base = "Console" 

setup(
    name="Carrefour API Scrapper",
    version="1.0",
    options={"build_exe": build_exe_options},
    executables=[Executable(
        "Carrefour API Scrapper.py",
        base=base,
        icon="pug_dog_animal_15965.ico",
        target_name="Scrapper",
        copyright="Copyright (C) 2900AD Mer",
    )]
)
