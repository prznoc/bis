import NetLog
import unittest

class TestNetLog(unittest.TestCase):

    def test_packets_count10(self):
        sum = 0
        num = 10
        dict = NetLog.capture_live_packets(network_interface, num)
        for i in dict:
            sum+=dict[i]
        self.assertEqual(sum,num)

    def test_packets_count100(self):
        sum = 0
        num = 100
        dict = NetLog.capture_live_packets(network_interface, num)
        for i in dict:
            sum+=dict[i]
        self.assertEqual(sum,num)
        
    def test_packets_count1000(self):
        sum = 0
        num = 1000
        dict = NetLog.capture_live_packets(network_interface, num)
        for i in dict:
            sum+=dict[i]
        self.assertEqual(sum,num)

    def test_is_source_localIp(self):
        self.assertEqual(list(NetLog.capture_live_packets(network_interface, 1).keys())[0].split(',')[0], local_ip)

    def test_writing_to_file_first_line(self):
        dict = {}
        dict[local_ip+"1.1.1.1"] = 9
        NetLog.write_to_file(dict,"testfile.csv","2020-02-02")
        f = open("testfile.csv", "r")
        lines = f.readlines()
        self.assertEqual(lines[0],"date,l_ipn,r_asn,f\n")
        f.close()

    def test_writing_to_file_second_line(self):
        dict = {}
        dict[local_ip+"1.1.1.1"] = 9
        NetLog.write_to_file(dict,"testfile.csv","2020-02-02")
        f = open("testfile.csv", "r")
        lines = f.readlines()
        self.assertEqual(lines[1],"2020-02-02,"+local_ip+"1.1.1.1"+",9\n")
        f.close()

    def test_datetime_good_format_len(self):
        self.assertEqual(len(NetLog.get_today_datetime()),10)
    def test_datetime_good_format_regex(self):
        self.assertRegex(NetLog.get_today_datetime(),r"\d{4}-\d{2}-\d{2}")

network_interface = 'wlp2s0'
local_ip = '192.168.1.7'

if __name__ == '__main__':
    unittest.main()