import pyshark
from datetime import datetime
import sys
import os

def capture_live_packets(network_interface, number):
    capture = pyshark.LiveCapture(interface=network_interface)
    for raw_packet in capture.sniff_continuously(number):
        save_to_dict(raw_packet)

def save_to_dict(packet):
    if("ip" not in packet):
        return
    str = packet.ip.src+','+packet.ip.dst
    if(str in dict):
        dict.update({str:dict[str]+1})
    else:
        dict[str] = 1

date = datetime.today().strftime('%Y-%m-%d')
dict = {}
capture_live_packets(str(sys.argv[1]),int(sys.argv[3]))
filename = str(sys.argv[2])
f = open(filename, "w")
#if(os.stat(filename).st_size == 0):
f.write("date,l_ipn,r_asn,f\n")
for d in dict:
    f.write(date+','+d+','+str(dict[d])+'\n')
f.close()
