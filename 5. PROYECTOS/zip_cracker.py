from cmath import e
import zipfile
import os
from threading import Thread


def extract_file(z_file, password):
    try:
        z_file.extractall(pwd = bytes(password, 'utf-8'))
        print("\n[+] Password: "+ password + "\n")
    except:
        pass

def main():
    
    path = os.getcwd()
    #print(path)

    ori_file = input("Introduzca ruta y archivo Zip: ")

    z_file = zipfile.ZipFile(ori_file)
    passfile = open(path+r"\\rockyou.txt",encoding='utf-8')

    try:
        for line in passfile.readlines():
            password = line.strip('\n')
            t = Thread(target=extract_file, args=(z_file, password ))
            t.start()
    except:
        pass                            
if __name__ == '__main__':
    main()
    
    