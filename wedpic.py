#!/usr/bin/env python3
#    Wedding Photographer from matrimonio.com Data Web Scraper
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
import time
import sys
import csv
from pprint import pprint as pp

def downloadparse (url):
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    print('URL,' + url)
    raw = opener.open(url)
    html = raw.read().decode('utf-8')
    raw.close()
    html = io.StringIO(html)
    return lxml.etree.parse(html, lxml.etree.HTMLParser())

def getinfo (url):
    i = {}
    i['url'] = url
    doc = downloadparse(url)
    #pp(lxml.etree.tostring(doc, pretty_print=True))

    name = doc.xpath('//h1[@class="storefront-header-title"]/text()')
    i['name'] = name[0].strip()

    rating = doc.xpath('//span[@class="storefrontItemReviews__ratio--principal"]/text()')
    if(len(rating) == 1):
        i['rating'] = rating[0].strip()
    else:
        i['rating'] = '?'

    address = doc.xpath('//div[@class="vendor-address"]/text()')
    if(len(address) == 1):
        address = address[0].split()
        address = ' '.join(address)
    else:
        address = ''
    i['address'] = address


    region = re.findall('\([^\(\)]*\)', address)
    if(len(region) > 0):
        region = region[-1]
        region = region[1:-1]
        i['region'] = region
    else:
        i['region'] = '?'

    if(region in  ['Bergamo', 'Brescia', 'Lecco', 'Lodi', 'Milano',
            'Monza e Brianza']):
        i['closeregion'] = 'yes'
    else:
        i['closeregion'] = 'no'

    price = doc.xpath(
        '//i[@class="icon-vendor icon-vendor-faq-price"]/../div/p/text()')
    if(len(price) == 1):
        price = price[0].replace('Da', '').replace(' a ', '-').replace('.', '')
        price = price.replace('A partire da', '')
        price = price.replace('Meno di', '')
        price = price.strip()
        i['price'] = price
    else:
        i['price'] = '?'

    services = doc.xpath(
        '//i[@class="icon-vendor icon-vendor-faq-check"]/../div/p/text()')
    if(len(services) == 1):
        services = services[0].strip()
    else:
        services = ""
    serviceshide = doc.xpath(
        '//i[@class="icon-vendor icon-vendor-faq-check"]/../div/p/span/text()')
    if(len(serviceshide) == 2):
        services = services + serviceshide[1].strip()

    services = services
    i['services'] = services.replace('\n', ' ').replace('\r', ' ')

    weddingpack = doc.xpath(
        '//i[@class="icon-vendor icon-vendor-faq-rings"]/../div/p/text()')
    if(len(weddingpack) >= 1):
        weddingpack = weddingpack[0].strip()
    else:
        weddingpack = ""
    weddingpackhide = doc.xpath(
        '//i[@class="icon-vendor icon-vendor-faq-rings"]/../div/p/span/text()')
    if(len(weddingpackhide) == 2):
        weddingpack = weddingpack + weddingpackhide[1].strip()
    weddingpack = weddingpack.replace('\n', ' ').replace('\r', ' ')
    i['weddingpack'] = weddingpack

    transfer = doc.xpath(
        '//i[@class="icon-vendor icon-vendor-faq-car"]/../div/p/text()')
    if(len(transfer) == 1):
        transfer = transfer[0].strip()
        transfer = transfer.replace('Sì', 'yes').replace('No', 'no')
        i['transfer'] = transfer
    else:
        i['transfer'] = '?'

    location = doc.xpath(
        '//i[@class="icon-vendor icon-vendor-faq-location"]/../div/p/text()')
    if(len(location) == 1):
        location = location[0].strip()
        i['location'] = location
    else:
        i['location'] = '?'


    return(i)


#pp(getinfo('https://www.matrimonio.com/fotografo-matrimonio/nice-shot-art--e160346')); sys.exit()
#pp(getinfo('')); sys.exit()

baseurl = 'https://www.matrimonio.com/fotografo-matrimonio'
region = 'lombardia'

csvfile = open('wedpic.csv', 'w')
csw = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
csw.writerow(['name', 'rating', 'address', 'region', 'closeregion', 'price',
    'url', 'services', 'weddingpack', 'transfer', 'location'])

doc = downloadparse('%s/%s' % (baseurl, region))
n = doc.xpath('//span[@class="title"]/text()')[0]
n = n.replace('aziende', '').replace('.', '').strip()
n = int(int(n)/12) + 1

#n=2
for i in range(1, n):
    if(i == 1):
        url = '%s/%s' % (baseurl, region)
    else:
        url = '%s/%s--%s' % (baseurl, region, i)

    doc = downloadparse(url)
    things = doc.xpath('//div[@class="directory-item-content"]/a/@href')
    for t in things:
        i = getinfo(t)
        csw.writerow([i['name'], i['rating'], i['address'], i['region'],
            i['closeregion'], i['price'], i['url'], i['services'],
            i['weddingpack'], i['transfer'], i['location']])
        print("%s\t%s" % (i['name'], i['url']))

    time.sleep(3)
