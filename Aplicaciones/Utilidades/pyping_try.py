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
    
def main():
    ip1 = input("Ingrese IP: ")
    port = int(input("Ingrese puerto: "))
    banner = retBanner(ip1, port)
    if banner:
        print("[+] "+ip1+": "+ str(banner))

if __name__=='__main__':
    main()
    