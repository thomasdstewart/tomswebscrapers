#!/usr/bin/env python3
#    Barclays Bank Data Web Scraper
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


class BarclaysScraper(BankScraper):
    def config_check(self):
        section = self.config[self.basename]
        if('surname' not in section
           or 'membershipnum' not in section
           or 'passcode' not in section
           or 'password' not in section):
            logging.info(
                "could not find setting in %s section in %s"
                % (self.basename, self.configfile))
            sys.exit()

        self.surname = self.config[self.basename]['surname']
        self.membershipnum = self.config[self.basename]['membershipnum']
        self.passcode = self.config[self.basename]['passcode']
        self.password = self.config[self.basename]['password']

    def scrape(self):
        loginurl = "https://bank.barclays.co.uk/olb/auth/LoginLink.action"
        logging.info("getting page:%s", loginurl)
        self.driver.get(loginurl)
        self.shotnhtml()

        try:
            self.driver.find_element_by_class_name("bc-checkbox")
        except NoSuchElementException:
            logging.info("bc-checkbox class not found, browser compatible")
        else:
            self.driver.find_element_by_class_name("bc-checkbox").click()
            self.driver.find_element_by_id("bc-button").click()
            self.shotnhtml()

        time.sleep(5)
        logging.info("filling surname and membership number")
        self.driver.find_element_by_id("surname0").send_keys(self.surname)
        self.driver.find_element_by_id(
            "membershipNum0").send_keys(self.membershipnum)
        self.driver.find_element_by_xpath("//button").click()
        time.sleep(5)
        self.shotnhtml()

        logging.info("selecting passcode")
        self.driver.find_element_by_xpath(
            "//label[@for='radio-c2']/span").click()
        time.sleep(5)
        self.shotnhtml()

        logging.info("filling passcode and password")
        self.driver.find_element_by_id("passcode0").send_keys(self.passcode)

        first = self.driver.find_element_by_xpath(
            "//label[@id='label-memorableCharacters']/strong[1]").text
        second = self.driver.find_element_by_xpath(
            "//label[@id='label-memorableCharacters']/strong[2]").text
        first = int(first[0:1])
        second = int(second[0:1])

        first = str(self.password[first-1:first])
        second = str(self.password[second-1:second])

        self.driver.find_element_by_xpath(
            "//div[@name='firstMemorableCharacter']/div").send_keys(first)
        self.driver.find_element_by_xpath(
            "//div[@name='secondMemorableCharacter']/div").send_keys(second)
        self.driver.find_element_by_xpath("//button").click()
        time.sleep(5)
        self.shotnhtml()

        logging.info("getting account list")
        accounts = {}
        for account in self.driver.find_elements_by_xpath(
                "//*[@class='account-detail-wrapper summary']"):
            a = account.get_attribute("aria-label")
            pa = a.replace(' ', '')
            pa = "%s-%s-%s %s" % (pa[8:10], pa[10:12], pa[12:14], pa[27:35])
            accounts[pa] = a

        logging.info("found accounts %s" % ",".join(accounts.keys()))

        self.data = []
        for account in accounts:
            logging.info("getting account %s" % account)
            self.driver.find_element_by_xpath(
                "//*[@aria-label='%s']/..//*[@id='showStatements']"
                % accounts[account]).click()
            time.sleep(5)
            self.shotnhtml()

            rows = self.driver.find_elements_by_xpath(
                "//*[@id='filterable-ftb']/tbody/tr")
            logging.info("found %s trancastions" % (len(rows)))
            for row in rows:
                r = row.text.split('\n')
                date = r[0]
                year = date.split('/')[2]
                desc1 = r[1]

                r[2] = r[2].replace(',', '').replace('£', '')
                a = re.findall(r"[^ ]+", r[2])
                amount = a[0]
                balance = a[1]

                d = row.find_element_by_xpath("td[@class='description']/div")
                d = d.get_attribute("textContent").split('\n')

                desc2 = d[2].strip()
                desc3 = d[5].strip()

                sdesc3 = d[5].strip().split()

                desc3 = " ".join(sdesc3[:-1])
                desc4 = ""
                if(len(sdesc3) > 0 and desc4 != desc3):
                    desc4 = sdesc3[-1]

                d = [year, account, date, desc1, desc2,
                     desc3, desc4, amount, balance]
                self.data.append(d)
                logging.info("transaction act:%s, date:%s, desc:%s, amount:%s" %
                             (account, date, desc1, amount))

            self.savedata("%s-%s" % (self.basename, account.split()[1]))
            self.data = []

            logging.info("finished account %s" % account)
            self.shotnhtml()

            logging.info("scrolling up")
            self.driver.find_element_by_tag_name(
                'body').send_keys(Keys.CONTROL + Keys.HOME)
            self.shotnhtml()

            logging.info("returning home")
            self.driver.find_element_by_class_name("home").click()
            self.shotnhtml()

        logging.info("logging out")
        self.driver.find_element_by_id("logout").click()
        self.shotnhtml()

        self.finish()


parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config",
                    help="config file to use (eg barclaysscrape.ini)")
parser.add_argument("-d", "--debug",
                    help="log to stdout and save screenshots and html", action="store_true",
                    default=False)
parser.add_argument("-o", "--output",
                    help="output file basename (eg barclaycard to give barclaycard-2018.csv)")
parser.add_argument("-p", "--proxy",
                    help="http proxy to use (eg localhost:8888)", default="")
args = parser.parse_args()


b = BarclaysScraper('barclaysscraper', proxy=args.proxy, debug=args.debug)
b.scrape()
