import NetLog
import unittest
import sys

class TestNetLog(unittest.TestCase):

    def test_packets_count(self):
        sum = 0
        num = 20
        dict = NetLog.capture_live_packets(network_interface, num)
        for i in dict:
            sum+=dict[i]
        self.assertEqual(sum,num)
    def test_is_source_localIp(self):
        self.assertEqual(list(NetLog.capture_live_packets(network_interface, 1).keys())[0].split(',')[0], local_ip)
    def test_writing_to_file(self):
        dict = {}
        dict[local_ip+"1.1.1.1"] = 9
        NetLog.write_to_file(dict,"testfile.csv","2020-02-02")
        f = open("testfile.csv", "r")
        lines = f.readlines()
        self.assertEqual(lines[0],"date,l_ipn,r_asn,f\n")
        self.assertEqual(lines[1],"2020-02-02,"+local_ip+"1.1.1.1"+",9\n")
        f.close()

network_interface = 'wlp2s0'
local_ip = '192.168.1.7'

if __name__ == '__main__':
    unittest.main()