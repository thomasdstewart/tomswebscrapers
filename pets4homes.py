#!/usr/bin/env python3
import urllib.request
import urllib.parse
import io
import lxml.etree
import re
import sys
from pprint import pprint as pp


def downloadparse(url):
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    #print('URL,' + url)
    raw = opener.open(url)
    html = raw.read().decode('utf-8')
    raw.close()
    html = io.StringIO(html)
    return lxml.etree.parse(html, lxml.etree.HTMLParser())

def getinfo(url):
    doc = downloadparse(url)
    #print(lxml.etree.tostring(doc, pretty_print=True))
    rows = doc.xpath('//h2[@class="headline"]/a')
    pets = []
    for r in rows:
        pet = {}
        pet['title'] = r.xpath('text()')[0]
        pet['link'] = r.xpath('@href')[0]
        
        img  = r.xpath('../../..//div[@class="imagecontainer"]//img/@src')
        if(len(img) != 1):
            continue

        pet['img'] = r.xpath('../../..//div[@class="imagecontainer"]//img/@src')[0]
        pet['desc'] = r.xpath('../../..//div[@class="description"]/text()')[0]

        pets.append(pet)

    return pets


url = 'https://www.pets4homes.co.uk/search/?type_id=3&breed_id=470&advert_type=1&location=AL7&results=20&sort=distance'
pets = getinfo(url)
#pp(pets)

entries = ''
for pet in pets:
    title = pet['title']
    link = pet['link']
    content = "<a href='%s'><img src='%s'/></a><p>%s</p>" % (link, pet['img'], pet['desc'])

    entries = entries + '''
    <entry>
        <title>%s</title>
        <link>%s</link>
        <content type="html">
            <![CDATA[
                %s
          ]]>
        </content>
    </entry>
    ''' % (title, link, content)


#http://atomenabled.org/developers/syndication/
url = 'https://www.pets4homes.co.uk/'
feed='''<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
<title>Pets 4 Homes Feed</title>
<link href="%s"/>
<author><name>Thomas Stewart</name></author>
<id>urn:uuid:76584d7f-1d23-48f5-b85f-278d182d8863</id>
%s
</feed>
''' % (url, entries)

print(feed)

