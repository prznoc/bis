import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

if sys.version_info[0] >= 3 and sys.version_info[1] >= 8:
    f = open("requirements.txt", "r")
    lines = f.readlines()
    for l in lines:
        install(l.split('\n')[0])
    f.close()
else:
    print("Must be using Python 3.8")