import token
from cryptography.fernet import Fernet
import socket

def retBanner(ip, port):
    try:
        socket.setdefaulttimeout(5)
        s= socket.socket()
        s.connect((ip, port))
        banner = s.recv(1024)
        return banner
    except Exception as e:
        print("[-] Error: "+str(e))
        return
    


def create_encrypt(message):
    key = Fernet.generate_key()
    f = Fernet(key)
    
    token = f.encrypt(message)
    return key, token

