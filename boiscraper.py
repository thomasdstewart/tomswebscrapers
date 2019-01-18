#!/usr/bin/env python3
#    BOI Account Data Web Scraper
#    Copyright (C) 2019 Thomas Stewart <thomas@stewarts.org.uk>
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


class BoiScraper(BankScraper):
    def config_check(self):
        section = self.config[self.basename]
        if('userid' not in section
           or 'dob' not in section
           or 'contactnumber' not in section
           or 'pin' not in section):
            logging.info(
                "could not find setting in %s section in %s"
                % (self.basename, self.configfile))
            sys.exit()

        self.userid = self.config[self.basename]['userid']
        self.dob = self.config[self.basename]['dob']
        self.contactnumber = self.config[self.basename]['contactnumber']
        self.pin = self.config[self.basename]['pin']

    def scrape(self):
        loginurl = "https://www.365online.com/"
        logging.info("getting page:%s", loginurl)
        self.driver.get(loginurl)
        self.shotnhtml()
        logging.info("waiting")
        time.sleep(5)

        logging.info("filling userid")
        self.driver.find_element_by_id("form:userId").send_keys(self.userid)
        self.shotnhtml()

        logging.info("looking for form:phoneNumber")
        try:
            self.driver.find_element_by_id("form:phoneNumber")
        except NoSuchElementException:
            logging.info("form:phoneNumber not found")
        else:
            logging.info("filling contactnumber")
            self.driver.find_element_by_id(
                "form:phoneNumber").send_keys(self.contactnumber[-4:])
            self.shotnhtml()

        logging.info("looking for form:dateOfBirth_date")
        try:
            self.driver.find_element_by_id("form:dateOfBirth_date")
            self.driver.find_element_by_id("form:dateOfBirth_month")
            self.driver.find_element_by_id("form:dateOfBirth_year")
        except NoSuchElementException:
            logging.info("form:dateOfBirth_date,month,year not found")
        else:
            logging.info("filling date, month and year")
            day = self.dob.split('-')[0]
            month = self.dob.split('-')[1]
            year = self.dob.split('-')[2]
            #Javascript helpers seem to move cursor about to stop text entry
            #self.driver.find_element_by_id("form:dateOfBirth_date").send_keys(day)
            #self.driver.find_element_by_id("form:dateOfBirth_month").send_keys(month)
            #self.driver.find_element_by_id("form:dateOfBirth_year").send_keys(year)

            time.sleep(1)
            script = "return arguments[0].value = '%s'" % day
            self.driver.execute_script(script, self.driver.find_element_by_id("form:dateOfBirth_date"))
            time.sleep(1)
            script = "return arguments[0].value = '%s'" % month
            self.driver.execute_script(script, self.driver.find_element_by_id("form:dateOfBirth_month"))
            time.sleep(1)
            script = "return arguments[0].value = '%s'" % year
            self.driver.execute_script(script, self.driver.find_element_by_id("form:dateOfBirth_year"))
            time.sleep(1)

            self.shotnhtml()

        logging.info("clicking continue")
        self.driver.find_element_by_id("form:continue").click()
        logging.info("waiting")
        time.sleep(5)
        self.shotnhtml()

        logging.info("finding pin numbers")
        numbers = self.driver.find_element_by_class_name("security_numbers")
        first = numbers.find_elements_by_xpath("li/label")[0].text[:1]
        second = numbers.find_elements_by_xpath("li/label")[1].text[:1]
        third = numbers.find_elements_by_xpath("li/label")[2].text[:1]

        logging.info("found first:%s, second:%s, third:%s" %
                     (first, second, third))

        first = int(first)
        second = int(second)
        third = int(third)

        first = str(self.pin[first-1:first])
        second = str(self.pin[second-1:second])
        third = str(self.pin[third-1:third])

        logging.info("filling first:%s, second:%s, third:%s" %
                     (first, second, third))

        numbers.find_elements_by_xpath("li/input")[0].send_keys(first)
        numbers.find_elements_by_xpath("li/input")[1].send_keys(second)
        numbers.find_elements_by_xpath("li/input")[2].send_keys(third)
        self.shotnhtml()

        logging.info("clicking continue")
        self.driver.find_element_by_id("form:continue").click()
        logging.info("waiting")
        time.sleep(5)
        self.shotnhtml()

        logging.info("clicking statements")
        self.driver.find_element_by_id(
            "form:leftHandNavSubview:statements").click()
        logging.info("waiting")
        time.sleep(5)
        self.shotnhtml()

        logging.info("finding account")
        account = self.driver.find_element_by_id("form:accountNumber").text[2:]

        self.data = []
        rows = self.driver.find_elements_by_xpath(
            "//span[@id='form:completedTransactionPanel']//tr")
        logging.info("found %s transactions" % (len(rows)))
        for row in rows:
            date = row.find_element_by_xpath("td[contains(@id,'dateColumn')]").text
            year = date.split('/')[2]
            desc = row.find_element_by_xpath("td[contains(@id,'detailsColumn')]").text
            desc = desc.strip()

            debit = row.find_element_by_xpath("td[contains(@id,'debitColumn')]").text
            credit = row.find_element_by_xpath("td[contains(@id,'creditColumn')]").text

            if(debit != ''):
                amount = "-" + debit

            if(credit != ''):
                amount = credit

            d = [year, account, date, desc, amount, "0"]

            self.data.append(d)
            logging.info("transaction date:%s, desc:%s, amount:%s" %
                         (date, desc, amount))

        logging.info("logging out")
        self.driver.find_element_by_id("logoutLink").click()
        self.shotnhtml()

        self.savedata("%s-%s" % (self.basename, account))
        self.finish()


name = "boiscraper"
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


b = BoiScraper(name, proxy=args.proxy, debug=args.debug)
b.scrape()
