import sys, os
from cx_Freeze import setup, Executable

project_name = "My Tkinter App"
exe_name = "MyTkinterApp"
version = "1"
main_script = "main.py"
optimization = 0
resources = []
packages = ["tkinter"]

base = None
if sys.platform == "win32":
    base = "Win32GUI"
    executables = [Executable("main.py", base=base, targetName=exe_name+".exe")]
    
    os.environ['TCL_LIBRARY'] = sys.exec_prefix + "\\tcl\\tcl8.6"
    os.environ['TK_LIBRARY'] = sys.exec_prefix + "\\tcl\\tk8.6"
    resources.extend([sys.exec_prefix + "\\DLLs\\tcl86t.dll", sys.exec_prefix + "\\DLLs\\tk86t.dll"])
    
elif sys.platform == "darwin":
    executables = [Executable("main.py", base=base)]

build_exe_options = {"optimize": optimization, "include_files": resources, "packages": packages}
mac_options = {"bundle_name": exe_name}


setup(  name = project_name,
        version = version,
        options = {"build_exe": build_exe_options},
        bdist_mac = mac_options,
        executables = [Executable(main_script, base=base, targetName=exe_name+".exe")]
)