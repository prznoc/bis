# bis


Commands to run NetLog.py

Check your network interface:

ip link show

install libraries:

pip3 install pyshark

sudo apt-get install tshark

apt-get install python3-dev

Command to run after installing tshark:

sudo chmod +x /usr/bin/dumpcap

run script:

python3 NetLog.py [interface] [filename] [number of packets]

run checker:

python3 Checker.py [filepath]
