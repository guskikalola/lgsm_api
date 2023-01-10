import csv
from urllib import request
from io import StringIO
def ServerList():
    url = "https://raw.githubusercontent.com/GameServerManagers/LinuxGSM/master/lgsm/data/serverlist.csv"
    with request.urlopen(url) as response:
        cr = csv.reader(StringIO(response.read().decode("utf-8")))
        return cr