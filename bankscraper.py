#!/usr/bin/env python3
#    Bank Account Data Web Scraper
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

import logging
import configparser
import selenium.webdriver.chrome.options
import selenium.webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import os
import subprocess
import time
import datetime
import sys
import csv
from pprint import pprint as pp
# import ipdb; from IPython import embed; embed()

# apt-get install python3 python3-selenium chromium-driver chromium

class BankScraper:
    screenshotnumber = 1

    def __init__(self, basename, configfile="", proxy="", debug=False):
        self.basename = basename
        if(configfile == ""):
            self.configfile = 'bankscraper.ini'
        else:
            self.configfile = configfile
        self.proxy = proxy
        self.debug = debug

        if(debug):
            logging.basicConfig(level=logging.INFO,
                                format="%(levelname)s %(asctime)s %(message)s")
        else:
            logging.basicConfig(filename="%s.log" % basename,
                                level=logging.INFO, format='%(levelname)s %(asctime)s %(message)s')

        self.readconfig()
        self.startselenium()

    def readconfig(self):
        logging.info("reading config")
        self.config = configparser.ConfigParser()
        self.config.read(self.configfile)

        if(len(self.config.sections()) == 0):
            logging.info("could not read %s" % self.configfile)
            sys.exit()

        if(self.basename not in self.config):
            logging.info(
                'could not read {} section in {}'.format(
                    self.basename, self.configfile))
            sys.exit()

        self.config_check()

    def config_check(self):
        return

    def startselenium(self):
        logging.info("setting up selenium")
        chrome_options = selenium.webdriver.chrome.options.Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1300,1600")
        # default UA is HeadlessChrome rather than Chrome
        version = subprocess.run(["chromium", "--version"], capture_output=True)
        version = version.stdout.split()[1].decode('utf8')
        ua = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/%s Safari/537.36" % version
        chrome_options.add_argument("user-agent=%s" % ua)

        if(self.proxy):
            # if('http_proxy' in os.environ.keys()):
            #    args.proxy = os.environ['http_proxy']
            logging.info("using proxy: %s" % self.proxy)
            chrome_options.add_argument("--proxy-server=%s" % self.proxy)
        else:
            logging.info("not using proxy")

        logging.info("starting selenium chrome headless")
        self.driver = selenium.webdriver.Chrome(chrome_options=chrome_options)
        self.driver.implicitly_wait(5)

    def shotnhtml(self):
        if(not self.debug):
            return
        logging.info("saving %s-%02d.png and html"
                     % (self.basename, self.screenshotnumber))
        self.driver.save_screenshot("%s-%02d.png" %
                                    (self.basename, self.screenshotnumber))
        f = open("%s-%02d.html" % (self.basename, self.screenshotnumber), "w", encoding="utf-8")
        f.write(self.driver.page_source)
        f.close()
        self.screenshotnumber = self.screenshotnumber + 1

    def savedata(self, filename):
        logging.info("processing duplicates")
        # find duplicates and number them
        refs = {}
        for row in self.data:
            # create index of things to unique
            index = "%s" % "".join(row[:-1])
            if(index not in refs):
                # set the count to 1 and save the row
                refs[index] = [1, row]
            else:
                # increment the count and save the row
                refs[index] = [refs[index][0] + 1, row]

        # loop over all the uniq rows
        datacounted = []
        for index in refs:
            # loop for row count
            for count in range(1, refs[index][0] + 1):
                # append count to row
                row = refs[index][1]
                datacounted.append(row + [str(count)])

        logging.info("transactions: %s" % len(datacounted))

        years = {}
        for row in datacounted:
            year = row[0]
            years[year] = True

        for year in years:
            current_filename = '%s-%s.csv' % (filename, year)
            alldata = []

            with open(current_filename, 'a') as f:
                f.close()

            logging.info("reading %s" % current_filename)
            with open(current_filename, newline='') as csvfile:
                csvreader = csv.reader(
                    csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                for row in csvreader:
                    alldata.append(row)

            new = 0
            logging.info("merging with %s transactions" % len(alldata))
            for row in datacounted:
                if(int(row[0]) == int(year) and row not in alldata):
                    alldata.append(row)
                    new = new + 1

            logging.info("added %s transactions" % new)

            logging.info("reading %s" % current_filename)
            with open(current_filename, 'w', newline='') as csvfile:
                csvwriter = csv.writer(
                    csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                for row in alldata:
                    csvwriter.writerow(row)

            logging.info("wrote %s transactions" % len(alldata))

        logging.info("writting completion timestamp file")
        with open('%s.done' % filename, 'w') as donefile:
            donefile.write("%s" % datetime.datetime.now())

    def finish(self):
        self.driver.close()
        self.driver.quit()
        logging.info("finished")
