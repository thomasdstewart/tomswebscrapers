#!/usr/bin/env python
#Copyright (C) 2013 Thomas Stewart <thomas@stewarts.org.uk>
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

import getopt
import urllib2
import StringIO, lxml.etree
import time
import sys, pprint; pp = pprint.PrettyPrinter(depth=6)

try:
        opts, args = getopt.getopt(sys.argv[1:], "hs",
                ["help", "smu="])
except getopt.error, msg:
        print str(msg)
        sys.exit(2)

rsmu = ""
for o, a in opts:
        if o in ("-h", "--help"):
                print "smu [options...]"
                print "Utility to download and save sector master user data"
                print "bookings and ouput ical file"
                print "  -h --help        this info"
                print "  -s --smu         smu code"
                sys.exit()

        elif o in ("-s", "--smu"):
                rsmu = a

if(rsmu == ""):
        print "Error: smu not set"
        sys.exit()

def dump_doc(doc):
        f = open("t.html", "w")
        doc.write(f)
        f.close()
        sys.exit()

url = 'http://www.coaa.co.uk/smu-performance.php' 
#url = 'http://www.stewarts.org.uk/smu/t.html'
req = urllib2.urlopen(url)
html = req.read()
html = StringIO.StringIO(html)
doc = lxml.etree.parse(html, lxml.etree.HTMLParser())
#dump_doc(doc)

smus = {}
for row in doc.xpath('//table/tr'):
        smu = row.xpath('td[1]/text()|td[1]/a/text()')
        if(len(smu) != 1):
                continue
        smu = smu[0]

        total = row.xpath('td[2]/text()')
        if(len(total) == 0):
                continue
        total = total[0]

        smus[smu] = total

print '%s,%s' % (time.strftime("%c"), smus[rsmu])
