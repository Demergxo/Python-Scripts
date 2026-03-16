import optparse
from socket import *

from distributed import connect

def conect_scan(tgtHost, tgtPort):
    try:
        conn_sckt = socket(AF_INET, SOCK_STREAM)
        conn_sckt.connect((tgtHost, tgtPort))
        
        print("[+] TCP abierto: {}".format(tgtPort))
        conn_sckt.close()
    except:
        print("[-] TCP cerrado: {}".format(tgtPort))
        
def port_scan(tgtHost, tgtPorts):
    try:
        tgtIP = gethostbyname(tgtHost)
    except:
        print("[-] No se puede resolver la dirección: {}".format(tgtHost))
        return
    try:
        tgtName = gethostbyaddr(tgtIP)
        print("Resultado de escaneo en: {}".format(tgtName[0]))
    except:
        print("Resultado de escaneo en: {}".format(tgtIP))
    setdefaulttimeout(3)
    for tgtPort in tgtPorts:
        conect_scan(tgtHost=tgtHost, tgtPort=int(tgtPort))
        
    


parser = optparse.OptionParser('uso %prog -H' + '<target host> -p <target port>' )
parser.add_option('-H', dest='tgtHost', type='string', help='Especifica dirección del host')
parser.add_option('-p', dest='tgtPort', type='int', help='Especifica dirección del puerto')
options, args = parser.parse_args()
tgtHost = options.tgtHost
tgtPort = options.tgtPort

if tgtHost == None | tgtPort == None:
    print(parser, args)
    exit(0)