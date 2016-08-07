import pyparsing as pyp
import itertools
import pyshark

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

def print_conversation_header(pkt):
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

def Initialise():
    cap = pyshark.LiveCapture(interface='wlan0')
    cap.apply_on_packets(print_conversation_header, timeout=100)

if __name__ == '__main__':
    #snort_parse('snort_file')
    Initialise()