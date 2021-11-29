import pyshark
from datetime import datetime
import sys
def capture_live_packets(network_interface, number):
    capture = pyshark.LiveCapture(interface=network_interface)
    for raw_packet in capture.sniff_continuously(number):
        save_to_dict(raw_packet)
dict = {}
def save_to_dict(packet):
    if("ip" not in packet):
        return
    str = packet.ip.src+','+packet.ip.dst
    if(str in dict):
        dict.update({str:dict[str]+1})
    else:
        dict[str] = 1
date = datetime.today().strftime('%Y-%m-%d')
print("start")
capture_live_packets(str(sys.argv[1]),int(sys.argv[3]))
f = open(str(sys.argv[2]), "w")
for d in dict:
    f.write(date+','+d+','+str(dict[d])+'\n')
f.close()
#print(dict)