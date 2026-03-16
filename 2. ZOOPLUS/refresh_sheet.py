import win32com.client
from keyboard import press
import time
import getpass


user = getpass.getuser()
excel  = win32com.client.Dispatch('Excel.Application')

libro = excel.Workbooks.Open(r"C:\Users\\"+user+r"\GXO\SPCABANILLAS - Cabanillas_Zooplus\1. Gestión Operativa\03. Devoluciones\Implantación Picking\Implantación Pick.xlsx")
#libro2 = excel.Workbooks.Open(r'C:\Users\jgmeras\GXO\SPCABANILLAS - Cabanillas_Zooplus\1. Gestión Operativa\03. Devoluciones\Implantación Picking\Implantación Pick.xlsx')

libro.RefreshAll()
time.sleep(10)
#press('Enter')

#libro2.RefreshAll()
#time.sleep(10)
#press('Enter')

libro.Save()


excel.Quit()
print("Programa Finalizado")
