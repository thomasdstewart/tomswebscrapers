#!/usr/bin/env python3
#    Wedding Venue from matrimonio.com Data Web Scraper
#    Copyright (C) 2018 Thomas Stewart <thomas@stewarts.org.uk>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import urllib.request, urllib.parse
import io
import lxml.etree
import re
import sys
import csv
from pprint import pprint as pp

#https://www.matrimonio.com/castelli-matrimoni/castello-di-rossino--e6433

def downloadparse (url):
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    #print('URL,' + url)
    raw = opener.open(url)
    html = raw.read().decode('utf-8')
    raw.close()
    html = io.StringIO(html)
    return lxml.etree.parse(html, lxml.etree.HTMLParser())

def getinfo (url):
    vi = {}
    vi['url'] = url
    doc = downloadparse(url)
    #pp(lxml.etree.tostring(doc, pretty_print=True))

    name = doc.xpath('//h1[@class="storefront-header-title"]/text()')
    vi['name'] = name[0].strip()

    price = doc.xpath(
        '//i[@class="icon-vendor icon-vendor-faq-price"]/../div/p/text()')
    if(len(price) == 1):
        price = price[0].replace('Da','').replace(' a ','-').replace('.','')
        price = price.replace('A partire da','')
        price = price.replace('Meno di','')
        price = price.strip()
        vi['price'] = price
    else:
        vi['price'] = '?'

    accommodation = doc.xpath(
        '//i[@class="icon-vendor icon-vendor-faq-home"]/../div/p/text()')
    if(len(accommodation) == 1):
        accommodation = accommodation[0].strip()
        accommodation = accommodation.replace('Sì','yes').replace('No','no')
        vi['accommodation'] = accommodation
    else:
        vi['accommodation'] = '?'

    guests = doc.xpath(
        '//i[@class="icon-vendor icon-vendor-faq-pax"]/../div/p/text()')
    if(len(guests) == 1):
        guests = guests[0]
        guests = guests.replace('Da','').replace(' a ','-')
        guests = guests.replace('Fino-','1-')
        guests = guests.replace('invitati','')
        guests = guests.strip()
        vi['guests'] = guests
    else:
        vi['guests'] = '?'

    address = doc.xpath('//div[@class="vendor-address"]/text()')
    address = address[0].split()
    address  = ' '.join(address)
    vi['address'] = address

    region = re.findall('\([^\(\)]*\)', address)
    if(len(region) > 0):
        region = region[-1]
        region = region[1:-1]
        vi['region'] = region
    else:
        vi['region'] = '?'

    #sub regions that we are interested in 
    closeregions = ['Bergamo', 'Brescia', 'Lecco', 'Lodi', 'Milano', 
        'Monza e Brianza']
    if(region in closeregions):
        vi['closeregion'] = 'yes'
    else:
        vi['closeregion'] = 'no'

    info = doc.xpath('//div[@class="storefront-description post mr40"]')[0]
    infohtml = str(lxml.etree.tostring(info, pretty_print=True))

    if(infohtml.find('cerimonia religiosa') > 0 
            or infohtml.find('chiesa') > 0 
            or infohtml.find('chiesette') > 0):
        vi['religious'] = 'yes'
    else:
        vi['religious'] = 'no'

    return(vi)

#pp(getinfo('https://www.matrimonio.com/castelli-matrimoni/castello-di-rossino--e6433')); sys.exit()
#pp(getinfo('https://www.matrimonio.com/ristoranti-ricevimenti/chalet-nel-parco--e117708')); sys.exit()
#pp(getinfo('')); sys.exit()

baseurl = 'https://www.matrimonio.com'
region = 'ricevimento/lombardia'

csvfile = open('wedven.csv', 'w')
csw = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
csw.writerow(['name', 'price', 'guests', 'accommodation', 'religious',
    'address', 'region', 'closeregion', 'url'])

doc = downloadparse('%s/%s' % (baseurl, region))
n = doc.xpath('//span[@class="title"]/text()')[0]
n = n.replace('aziende','').replace('.', '').strip()
n = int(int(n)/12) + 1

#n=2
for i in range(1, n):
    if(i == 1):
        url = '%s/%s' % (baseurl, region)
    else:
        url = '%s/%s--%s' % (baseurl, region, i)

    doc = downloadparse(url)
    venues = doc.xpath('//div[@class="directory-item-content"]/a/@href')
    for v in venues:
        info = getinfo(v)
        v = info
        csw.writerow([v['name'], v['price'], v['guests'], v['accommodation'],
            v['religious'], v['address'], v['region'], v['closeregion'],
            v['url']])

        print("%s\t%s" % (v['name'], v['url']))

