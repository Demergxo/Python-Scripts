from PyInstaller.utils.hooks import collect_data_files

#pyinstaller --onefile --add-data "tkdnd;tkdnd" --icon=Morti.ico --additional-hooks-dir=. relocation.py


datas = []

datas += collect_data_files('tkinterdnd2')
datas += collect_data_files('openpyxl')
datas += collect_data_files('scikit-learn')
