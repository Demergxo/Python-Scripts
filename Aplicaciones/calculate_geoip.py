import pygeoip
import os

user = os.environ['USERNAME']
path = os.path.join("C:", os.sep, "Users", user, "Documents", "Python Scripts", "Aplicaciones", "GeoIP.dat")


gi =pygeoip.GeoIP(path)

def print_record(tgt):
    rec = gi.record_by_name(tgt)
    city = rec['city']
    region = rec['region_name']
    country = rec['country_name']
    long = rec['longitude']
    lat = rec['latitude']
    print("[*] Target: {} Geo-located".format(tgt))
    print("[+] {}, {}, {}".format(city, region, country))
    print("[+] Latitud: {} Longitud: {}".format(lat, long))
    
tgt = "173.255.226.98"
print_record(tgt)
