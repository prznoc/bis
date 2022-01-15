import pyshark
from datetime import datetime
import sys
from netifaces import interfaces, ifaddresses, AF_INET


def capture_live_packets(network_interface, number): #główna funkcja modułu, nasłuchuje ruchu sieciowego na określonym porcie i zapisuje N próbek do dziennika
    local_ip = ifaddresses(network_interface).setdefault(AF_INET)[0]['addr'] #pobranie lokalnego ip maszyny
    dict = {}
    capture = pyshark.LiveCapture(interface=network_interface)
    for raw_packet in capture.sniff_continuously():
        save_to_dict(raw_packet, local_ip, dict)
        sum = 0
        for i in dict:
            sum+=dict[i]
        if(sum>=number):
            return dict
    return dict

def save_to_dict(packet, local_ip, dict): #zapisuje pakiet do dziennika
    if("ip" not in packet or packet.ip.dst == local_ip):
        return
    str = packet.ip.src+','+packet.ip.dst
    if(str in dict):
        dict.update({str:dict[str]+1})
    else:
        dict[str] = 1

def get_today_datetime(): #zwraca aktualną datę
    return datetime.today().strftime('%Y-%m-%d')

def write_to_file(dict, filename, date): #zapisanie wewnętrznego dziennika do pliku o odpowiednim formacie
    f = open(filename, "w")
    f.write("date,l_ipn,r_asn,f\n")
    for d in dict:
        f.write(date+','+d+','+str(dict[d])+'\n')
    f.close()


def run_logger(interface, filename, number):
    date = get_today_datetime()
    dict = capture_live_packets(interface, number)
    write_to_file(dict, filename, date)


def run_from_gui(interface, filename, number):
    run_logger(interface, filename, number)
    return True

def main():
    interface = str(sys.argv[1])
    filename = str(sys.argv[2])
    number = int(sys.argv[3])
    run_logger(interface, filename, number)


if __name__ == '__main__':
    main()
