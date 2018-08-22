#!/usr/bin/env python3
#    Dummy Data Web Scraper
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
import argparse
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import re
import os
import sys
import time
from bankscraper import BankScraper
from pprint import pprint as pp
# import ipdb; from IPython import embed; embed()


class DummyScraper(BankScraper):
    def readconfig(self):
        return

    def scrape(self):
        loginurl = "https://www.bbc.co.uk/"
        logging.info("getting page:%s", loginurl)
        self.driver.get(loginurl)
        self.shotnhtml()
        time.sleep(5)

        logging.info("looking for hp-banner__text")
        try:
            self.driver.find_element_by_class_name("hp-banner__text")
        except NoSuchElementException:
            logging.info("hp-banner__text class not found")

        banner = self.driver.find_element_by_class_name("hp-banner__text").text
        logging.info("found string:%s", banner)
        self.shotnhtml()
        time.sleep(5)

        self.finish()


parser = argparse.ArgumentParser()
parser.add_argument("-p", "--proxy",
                    help="http proxy to use (eg localhost:8888)", default="")
args = parser.parse_args()


b = DummyScraper("dummyscraper", proxy=args.proxy, debug=True)
b.scrape()
