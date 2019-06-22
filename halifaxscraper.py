#!/usr/bin/env python3
#    Halifax Credit Card Account Data Web Scraper
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
from selenium.common.exceptions import ElementNotVisibleException
from selenium.webdriver.common.keys import Keys
import re
import os
import sys
import time
from bankscraper import BankScraper
from pprint import pprint as pp
# import ipdb; from IPython import embed; embed()


class HalifaxScraper(BankScraper):
    def config_check(self):
        section = self.config[self.basename]
        if('username' not in section
           or 'password' not in section
           or 'memorableword' not in section):
            logging.info(
                "could not find setting in %s section in %s"
                % (self.basename, self.configfile))
            sys.exit()

        self.username = self.config[self.basename]['username']
        self.password = self.config[self.basename]['password']
        self.memorableword = self.config[self.basename]['memorableword']

    def scrape(self):
        loginurl = "https://www.halifax-online.co.uk/personal/logon/login.jsp"
        logging.info("getting page:%s", loginurl)
        self.driver.get(loginurl)
        self.shotnhtml()
        time.sleep(5)

        logging.info("filling username and password")
        self.driver.find_element_by_id(
            "frmLogin:strCustomerLogin_userID").send_keys(self.username)
        self.driver.find_element_by_id(
            "frmLogin:strCustomerLogin_pwd").send_keys(self.password)
        self.driver.find_element_by_xpath(
            "//input[@name='frmLogin:btnLogin1']").click()
        time.sleep(5)
        self.shotnhtml()

        logging.info("filling memorableword")
        first = self.driver.find_element_by_xpath(
            "//label[@for='frmentermemorableinformation1:strEnterMemorableInformation_memInfo1']").text
        second = self.driver.find_element_by_xpath(
            "//label[@for='frmentermemorableinformation1:strEnterMemorableInformation_memInfo2']").text
        third = self.driver.find_element_by_xpath(
            "//label[@for='frmentermemorableinformation1:strEnterMemorableInformation_memInfo3']").text

        first = first.split()[1]
        second = second.split()[1]
        third = third.split()[1]

        first = int(first)
        second = int(second)
        third = int(third)

        first = str(self.memorableword[first-1:first])
        second = str(self.memorableword[second-1:second])
        third = str(self.memorableword[third-1:third])

        self.driver.find_element_by_xpath(
            "//select[@id='frmentermemorableinformation1:strEnterMemorableInformation_memInfo1']").send_keys(first)
        self.driver.find_element_by_xpath(
            "//select[@id='frmentermemorableinformation1:strEnterMemorableInformation_memInfo2']").send_keys(second)
        self.driver.find_element_by_xpath(
            "//select[@id='frmentermemorableinformation1:strEnterMemorableInformation_memInfo3']").send_keys(third)
        self.shotnhtml()

        logging.info("logging on")
        self.driver.find_element_by_xpath("//input[@title='Continue']").click()
        time.sleep(5)
        self.shotnhtml()

#        logging.info("searching for paperless message")
#        page = self.driver.find_element_by_id("page").text
#        if("We can help you with your filing" in page):
#            logging.info("found paperless message and clicking no thanks")
#            self.driver.find_element_by_xpath(
#                "//a[@href='/personal/a/managepaperlesspreference/enhancedpaperlessinterstitial.jsp?lnkcmd=idEpi%3Anavigatetoaov&al=']").click()
#            time.sleep(5)
#            self.shotnhtml()
#        else:
#            logging.info("not found paperless message")
#
#        logging.info("searching for saving boost message")
#        page = self.driver.find_element_by_id("page").text
#        if("give your savings a boost" in page):
#            logging.info("found saving boost message and clicking continue")
#            self.driver.find_element_by_xpath(
#                "//input[@title='Continue']").click()
#            time.sleep(5)
#            self.shotnhtml()
#        else:
#            logging.info("not found saving boost message")

#        logging.info("searching for balance transfer message")
#        page = self.driver.find_element_by_id("page").text
#        if("balance transfer could save you money" in page):
#            logging.info("found balance transfer message and clicking continue")
#            self.driver.find_element_by_xpath(
#                "//input[@title='Continue']").click()
#            time.sleep(5)
#            self.shotnhtml()
#        else:
#            logging.info("not found balance transfer message")

        logging.info("searching for continue button")
        try:
            self.driver.find_element_by_xpath(
                "//li[@class='primaryAction']/input[@title='Continue']")
        except NoSuchElementException:
            logging.info("continue button not found")
        except ElementNotVisibleException:
            logging.info("continue button not visible")
        else:
            logging.info("clicking continue button")
            self.driver.find_element_by_xpath(
                "//input[@title='Continue']").click()
            time.sleep(5)
            self.shotnhtml()

        logging.info("selecting account")
        self.driver.find_element_by_xpath(
            "//a[@id='lnkAccName_des-m-sat-xx-1']").click()
        time.sleep(5)
        self.shotnhtml()

        self.data = []
        for x in range(3):
            logging.info("looping page %s" % x)

            rows = self.driver.find_elements_by_xpath(
                "//table[@id='statement-table']/tbody/tr[@tabindex]/td[@transactionref]")
            logging.info("found %s transactions" % (len(rows)))
            for row in rows:
                logging.info("clicking row")
                row.click()
                time.sleep(1)
                self.shotnhtml()

            rows = self.driver.find_elements_by_xpath(
                "//table[@id='statement-table']/tbody/tr[@tabindex]/td[@transactionref]")
            logging.info("found %s transactions" % (len(rows)))
            for row in rows:
                date = row.text
                year = "20%s" % date.split()[2]
                account = self.username
                desc1 = row.get_attribute("merchantname").strip()
                ref = row.get_attribute("transactionref")
                amount = row.get_attribute("amount")

                try:
                    nrow = row.find_element_by_xpath('../following-sibling::*')
                    d = nrow.find_element_by_xpath(
                        './td/div/table/tbody/tr/td').text
                except NoSuchElementException:
                    print("no element")
                    desc2 = ""
                    cat = ""
                else:
                    d = d.split('\n')
                    desc2 = d[1]
                    cat = d[2]

                d = [year, account, date, desc1, desc2, cat, ref, amount, "0"]
                self.data.append(d)
                logging.info("transaction date:%s, desc:%s, amount:%s" %
                             (date, desc1, amount))

            logging.info("selecting earlier")
            self.driver.find_element_by_id("lnkEarlierBtnMACC").click()
            time.sleep(5)
            self.shotnhtml()

        logging.info("logging out")
        self.driver.find_element_by_id(
            "ifCommercial:ifCustomerBar:ifMobLO:outputLinkLogOut").click()
        self.shotnhtml()

        self.savedata("%s-%s" % (self.basename, self.username))
        self.finish()


name = "halifaxscraper"
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


b = HalifaxScraper(name, proxy=args.proxy, debug=args.debug)
b.scrape()
