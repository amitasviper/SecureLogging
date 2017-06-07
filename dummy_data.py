from datetime import datetime
from random import randrange


def getIpAddress():
    not_valid = [10, 127, 169, 172, 192]
    first = randrange(1, 2)
    while first in not_valid:
        first = randrange(1, 2)
    ip = ".".join([str(first), str(randrange(1, 2)), str(randrange(1, 2)), str(randrange(1, 10))])
    return ip


def GetDummydata():
    data = {}
    data['from_ip'] = getIpAddress()
    data['to_ip'] = getIpAddress()
    data['port'] = randrange(1, 65535)
    data['time'] = datetime.now()
    return data
