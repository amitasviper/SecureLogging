import pyparsing as pyp
import itertools

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

snort_parse('snort_file')