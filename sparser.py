import pyparsing as pyp
import itertools
import pyshark

from Queue import Queue
from threading import Thread

num_fetch_threads = 2
enclosure_queue = Queue()

def downloadEnclosures(q):
    while True:
        print '%s: Looking for the next enclosure' % i
        url = q.get()
        print '%s: Downloading:' % i, url
        # instead of really downloading the URL,
        # we just pretend and sleep
        time.sleep(i + 2)
        q.task_done()

integer = pyp.Word(pyp.nums)
ip_addr = pyp.Combine(integer+'.'+integer+'.'+integer+'.'+integer)

def snort_parse(logfile):
    header = (pyp.Suppress("[**] [")
        + pyp.Combine(integer + ":" + integer + ":" + integer)
        + pyp.Suppress(pyp.SkipTo("[**]", include = True)))
    cls = (
        pyp.Suppress(pyp.Optional(pyp.Literal("[Classification:")))
        + pyp.Regex("[^]]*") + pyp.Suppress(']'))

    pri = pyp.Suppress("[Priority:") + integer + pyp.Suppress("]")
    date = pyp.Combine(
        integer+"/"+integer+'-'+integer+':'+integer+':'+integer+'.'+integer)
    src_ip = ip_addr + pyp.Suppress("->")
    dest_ip = ip_addr

    bnf = header+cls+pri+date+src_ip+dest_ip

    with open(logfile) as snort_logfile:
        for has_content, grp in itertools.groupby(
                snort_logfile, key = lambda x: bool(x.strip())):
            if has_content:
                tmpStr = ''.join(grp)
                fields = bnf.searchString(tmpStr)
                print(fields)

def add_log_to_queue(pkt):
    global enclosure_queue
    try:
        protocol =  pkt.transport_layer
        src_addr = pkt.ip.src
        src_port = pkt[pkt.transport_layer].srcport
        dst_addr = pkt.ip.dst
        dst_port = pkt[pkt.transport_layer].dstport
        print '%s  %s:%s --> %s:%s' % (protocol, src_addr, src_port, dst_addr, dst_port)
    except AttributeError as e:
        #ignore packets that aren't TCP/UDP or IPv4
        pass

def FetchLogs():
    cap = pyshark.LiveCapture(interface='wlan0')
    cap.apply_on_packets(add_log_to_queue, timeout=100)

def Initialise():
    worker1 = Thread(target=downloadEnclosures, args=(enclosure_queue,))
    worker1.setDaemon(True)
    worker1.start()

    worker2 = Thread(target=FetchLogs, args=())
    worker2.setDaemon(True)
    worker2.start()

if __name__ == '__main__':
    #snort_parse('snort_file')
    Initialise()