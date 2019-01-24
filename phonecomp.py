#!/usr/bin/env python3
import urllib.request, urllib.parse
import io
import lxml.etree
import re
import sys
from pprint import pprint as pp

def downloadparse (url):
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    raw = opener.open(url)
    html = raw.read().decode('utf-8')
    raw.close()
    html = io.StringIO(html)
    return lxml.etree.parse(html, lxml.etree.HTMLParser())


def getphone (model):
    #model = 'htc_one_m9-6891'
    url = 'http://webcache.googleusercontent.com/search?q=cache:www.gsmarena.com/%s.php' % model
    doc = downloadparse(url)

    sl = doc.xpath('//div[@id="specs-list"]')[0]

    ttl = sl.xpath('//td[@class="ttl"]')
    nfo = sl.xpath('//td[@class="nfo"]')

    #print(len(ttl))
    #print(len(nfo))

    n = 0
    pd = {}
    for i, t in enumerate(ttl):
        #print(lxml.etree.tostring(ttl[i], pretty_print=True))
        #print(lxml.etree.tostring(nfo[i], pretty_print=True))
        t = ttl[i].xpath('a/text()')
        i = nfo[i].xpath('text()')
        #print("t len:%s, i len:%s" % (len(t), len(i)))

        t = t[0] if t else ''
        i = i[0] if i else ''
        #print("t:%s, i:%s\n" % (t, i))
        pd[t] = i

    m = re.match( r'([\.0-9]*) x ([\.0-9]*) x ([\.0-9]*) mm',
        pd['Dimensions'])
    v = float(m.group(1)) * float(m.group(2)) * float(m.group(3))
    pd['Volume'] = v / 100

    m = re.match( r'([\.0-9]*) g',
        pd['Weight'])

    pd['Weightg'] = int(m.group(1))
    return(pd)

#p=getphone('huawei_nexus_6p-7588')
#sys.exit()

phones = [
    'sony_ericsson_t68i-325',           # Oct 2002
    'nokia_6230-566',                   # Summer 2004
    'nokia_6230i-1087',                 # Dec 2005
    'htc_p3300-1693',                   # Feb 2007
    'htc_touch_hd-2525',                # Feb 2009
    'htc_desire_hd-3468',               # Jan 2011
    'samsung_galaxy_note_ii_n7100-4854',# Summer 2013
    'huawei_nexus_6p-7588',             # Nov 2015
    'google_pixel_xl-8345'              # Sept 2017
    ]

allphones = {}
for p in phones:
    print("getting %s" % (p))
    allphones[p] = getphone(p)

for phone in phones:
    print("phone: %s" % (phone))
    print("dimentions: %s" % (allphones[phone]['Dimensions']))
    print("volume: %s cm^2" % (allphones[phone]['Volume']))
    print("size: %s" % (allphones[phone]['Size']))
    print("resolution: %s" % (allphones[phone]['Resolution']))
    print("weight: %s" % (allphones[phone]['Weight']))
    #print("internal: %s" % (allphones[phone]['Internal']))
    print("density: %s g/cm^2 "% \
        ((allphones[phone]['Weightg']) \
        / (allphones[phone]['Volume']) ))
    print("announced: %s" % (allphones[phone]['Announced']))
    print()
    
    
