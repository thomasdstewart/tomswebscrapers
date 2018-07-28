#!/usr/bin/env python3
#    YBS Mort Account Data Web Scraper
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
import datetime
import re
import os
import sys
import time
from bankscraper import BankScraper
from pprint import pprint as pp
# import ipdb; from IPython import embed; embed()


class YbsmortScraper(BankScraper):
    def config_check(self):
        section = self.config[self.basename]
        if('username' not in section
           or 'dob' not in section
           or 'password' not in section):
            logging.info(
                "could not find setting in %s section in %s"
                % (self.basename, self.configfile))
            sys.exit()

        self.username = self.config[self.basename]['username']
        self.dob = self.config[self.basename]['dob']
        self.password = self.config[self.basename]['password']

    def scrape(self):
        loginurl = "https://online.ybs.co.uk/public/authentication/pre_login.do"
        logging.info("getting page:%s", loginurl)
        self.driver.get(loginurl)
        self.shotnhtml()
        time.sleep(5)

        logging.info("filling username")
        self.driver.find_element_by_id("uid-ID").send_keys(self.username)
        self.shotnhtml()

        logging.info("clicking continue")
        self.driver.find_element_by_xpath(
            "//input[@name='continueBtn.value']").click()
        time.sleep(5)

        logging.info("filling dob")
        day = self.dob.split('-')[0]
        month = self.dob.split('-')[1]
        year = self.dob.split('-')[2]

        self.driver.find_element_by_xpath(
            "//select[@name='dateOfBirth.day']").send_keys(day)
        self.driver.find_element_by_xpath(
            "//select[@name='dateOfBirth.month']").send_keys(month)
        self.driver.find_element_by_xpath(
            "//select[@name='dateOfBirth.year']").send_keys(year)

        logging.info("filling memorableword")
        pwdchars = self.driver.find_elements_by_xpath(
            "//div[@class='v-answer pwd-chars']")

        first = pwdchars[0].text[:-2]
        second = pwdchars[1].text[:-2]
        third = pwdchars[2].text[:-2]

        first = int(first)
        second = int(second)
        third = int(third)

        first = str(self.password[first-1:first])
        second = str(self.password[second-1:second])
        third = str(self.password[third-1:third])

        self.driver.find_element_by_xpath(
            "//input[@id='char1-ID']").send_keys(first)
        self.driver.find_element_by_xpath(
            "//input[@id='char2-ID']").send_keys(second)
        self.driver.find_element_by_xpath(
            "//input[@id='char3-ID']").send_keys(third)
        self.shotnhtml()

        logging.info("first:%s, second:%s, third:%s" % (first, second, third))

        logging.info("waiting")
        time.sleep(5)
        self.shotnhtml()

        logging.info("clicking continue")
        self.driver.find_element_by_xpath(
            "//input[@name='continueBtn.value']").click()
        self.shotnhtml()

        logging.info("waiting")
        time.sleep(5)
        self.shotnhtml()

        logging.info("finding account and balance")
        year = datetime.datetime.today().strftime('%Y')
        account = self.driver.find_element_by_xpath(
            "//tbody[@class='mortgageAccounts']/tr/td").text
        date = datetime.datetime.today().strftime('%Y/%m/%d')
        balance = self.driver.find_elements_by_xpath(
            "//tbody[@class='mortgageAccounts']/tr/td")[2].text

        self.data = []
        d = [year, account, date, balance, "0"]
        self.data.append(d)
        logging.info("transaction date:%s, amount:%s" %
                     (date, balance))

        logging.info("logging out")
        self.driver.find_element_by_xpath(
            "//input[@name='logOutBtn.value']").click()
        self.shotnhtml()

        self.savedata("%s-%s" % (self.basename, self.username))
        self.finish()


name = "ybsmortscraper"
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


b = YbsmortScraper(name, proxy=args.proxy, debug=args.debug)
b.scrape()
