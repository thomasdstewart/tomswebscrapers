#!/usr/bin/env python3
#    Barclay Credit Card Account Data Web Scraper
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


class BarclaycardScraper(BankScraper):
    def config_check(self):
        section = self.config[self.basename]
        if('username' not in section
           or 'passcode' not in section
           or 'memorableword' not in section):
            logging.info(
                "could not find setting in %s section in %s"
                % (self.basename, self.configfile))
            sys.exit()

        self.username = self.config[self.basename]['username']
        self.passcode = self.config[self.basename]['passcode']
        self.memorableword = self.config[self.basename]['memorableword']

    def scrape(self):
        loginurl = "https://bcol.barclaycard.co.uk/ecom/as2/initialLogon.do"
        logging.info("getting page:%s", loginurl)
        self.driver.get(loginurl)
        self.shotnhtml()

        time.sleep(5)
        logging.info("filling username and passcode")
        self.driver.find_element_by_id("username").send_keys(self.username)
        self.driver.find_element_by_id("password").send_keys(self.passcode)
        self.driver.find_element_by_class_name("submit").click()
        time.sleep(5)
        self.shotnhtml()

        logging.info("filling memorableword")
        first = self.driver.find_element_by_xpath(
            "//label[@id='letter1Answer-label']").text
        second = self.driver.find_element_by_xpath(
            "//label[@id='letter2Answer-label']").text

        first = int(first[0:1])
        second = int(second[0:1])

        first = str(self.memorableword[first-1:first])
        second = str(self.memorableword[second-1:second])

        self.driver.find_element_by_xpath(
            "//input[@id='letter1Answer']").send_keys(first)
        self.driver.find_element_by_xpath(
            "//input[@id='letter2Answer']").send_keys(second)
        time.sleep(5)
        self.shotnhtml()

        logging.info("logging on")
        self.driver.find_element_by_id("btn-login").click()
        time.sleep(5)
        self.shotnhtml()

        logging.info("waiting for login to complete")
        time.sleep(10)
        self.shotnhtml()

        logging.info("selecting transactions")
        self.driver.find_element_by_xpath(
            "//a[@href='#section/a-recent-trans']/span").click()
        time.sleep(5)
        self.shotnhtml()

        logging.info("selecting view more transactions")
        self.driver.find_element_by_xpath(
            "//div[@data-webtrends-ref='home-recentTrans']/a").click()
        time.sleep(5)
        self.shotnhtml()

        logging.info("selecting Filter & Search")
        self.driver.find_element_by_xpath(
            "//ul[@class='tablist']/li[@id='tab1']").click()
        time.sleep(5)
        self.shotnhtml()

        logging.info("selecting 3 months")
        self.driver.find_element_by_xpath(
            "//div[@class='dateLinks']/ul/li").click()
        time.sleep(5)
        self.shotnhtml()

        logging.info("waiting for page load")
        time.sleep(10)
        self.shotnhtml()

        logging.info("selecting expand all")
        self.driver.find_element_by_xpath(
            "//a[@id='linkExpandAll']/..").click()
        time.sleep(5)
        self.shotnhtml()

        self.data = []
        rows = self.driver.find_elements_by_xpath("//td[@class='view']/..")
        logging.info("found %s transactions" % (len(rows)))
        for row in rows:
            r = row.text.split('\n')
            date = r[0]
            account = self.username
            year = "20%s" % date.split()[2]
            desc = r[1].strip()
            amount = r[-1:][0]

            d = [year, account, date, desc, amount, "0"]

            # import ipdb; from IPython import embed; embed()
            #    241 Business type
            #    241 Cardholder
            #    241 Country
            #    243 PIN Used
            #    243 Retailer name
            #    243 Town
            #    152 Exchange Rate
            #    152 Forex Amount
            #     34 Retailer number
            #     17 Payment method

            self.data.append(d)
            logging.info("transaction %s" % " ".join(d))

        logging.info("logging out")
        self.driver.find_element_by_id("logout").click()
        self.shotnhtml()

        self.savedata("%s-%s" % (self.basename, self.username))
        self.finish()


name = "barclaycardscraper"
parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config",
                    help="config file to use (eg %s.ini)" % name)
parser.add_argument("-d", "--debug",
                    help="log to stdout and save screenshots and html", action="store_true",
                    default=False)
parser.add_argument("-o", "--output",
                    help="output file basename (eg %s to give %s-2018.csv)" % (name, name))
parser.add_argument("-p", "--proxy",
                    help="http proxy to use (eg localhost:8888)", default="")
args = parser.parse_args()


b = BarclaycardScraper(name, proxy=args.proxy, debug=args.debug)
b.scrape()
