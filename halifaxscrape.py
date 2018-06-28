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

import argparse
import logging
import configparser
import selenium.webdriver.chrome.options
import selenium.webdriver
from selenium.common.exceptions import NoSuchElementException
import re
import os
import time
import sys
import csv

from pprint import pprint as pp
#import ipdb
#from IPython import embed; embed()

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--debug",
                    help="log to stdout and save screenshots and html", action="store_true",
                    default=False)
parser.add_argument("-p", "--proxy",
                    help="http proxy to use (eg localhost:8888)")
args = parser.parse_args()

if(args.debug):
    logging.basicConfig(level=logging.INFO,
                        format="%(levelname)s %(asctime)s %(message)s")
else:
    logging.basicConfig(filename="halifaxscrape.log",
                        level=logging.INFO, format='%(levelname)s %(asctime)s %(message)s')

logging.info("reading config")
config = configparser.ConfigParser()
config.read("halifaxscrape.ini")

username = config.get("halifaxscrape", "username")
password = config.get("halifaxscrape", "password")
memorableword = config.get("halifaxscrape", "memorableword")

logging.info("setting up selenium")
chrome_options = selenium.webdriver.chrome.options.Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1300,1600")
# default UA is HeadlessChrome rather than Chrome
chrome_options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) " +
                            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36")

if(args.proxy):
    logging.info("using proxy: %s" % args.proxy)
    chrome_options.add_argument("--proxy-server=%s" % args.proxy)
else:
    logging.info("not using proxy")

logging.info("starting selenium chrome headless")
driver = selenium.webdriver.Chrome(chrome_options=chrome_options)
driver.implicitly_wait(5)

n = 1


def shotnhtml(d, n):
    if(not args.debug):
        return n
    logging.info("saving halifaxscrape-%02d.png and halifaxscrape-%02d.html"
                 % (n, n))
    d.save_screenshot("halifaxscrape-%02d.png" % n)
    file = open("halifaxscrape-%02d.html" % n, "w")
    file.write(d.page_source)
    file.close()
    return n + 1


loginurl = "https://www.halifax-online.co.uk/personal/logon/login.jsp"
logging.info("getting page:%s", loginurl)
driver.get(loginurl)
n = shotnhtml(driver, n)
time.sleep(5)

logging.info("filling username and password")
driver.find_element_by_id(
    "frmLogin:strCustomerLogin_userID").send_keys(username)
driver.find_element_by_id("frmLogin:strCustomerLogin_pwd").send_keys(password)
driver.find_element_by_xpath("//input[@name='frmLogin:btnLogin1']").click()
time.sleep(5)
n = shotnhtml(driver, n)

logging.info("filling memorableword")
first = driver.find_element_by_xpath(
    "//label[@for='frmentermemorableinformation1:strEnterMemorableInformation_memInfo1']").text
second = driver.find_element_by_xpath(
    "//label[@for='frmentermemorableinformation1:strEnterMemorableInformation_memInfo2']").text
third = driver.find_element_by_xpath(
    "//label[@for='frmentermemorableinformation1:strEnterMemorableInformation_memInfo3']").text

first = first.split()[1]
second = second.split()[1]
third = third.split()[1]

first = int(first)
second = int(second)
third = int(third)

first = str(memorableword[first-1:first])
second = str(memorableword[second-1:second])
third = str(memorableword[third-1:third])

driver.find_element_by_xpath(
    "//select[@id='frmentermemorableinformation1:strEnterMemorableInformation_memInfo1']").send_keys(first)
driver.find_element_by_xpath(
    "//select[@id='frmentermemorableinformation1:strEnterMemorableInformation_memInfo2']").send_keys(second)
driver.find_element_by_xpath(
    "//select[@id='frmentermemorableinformation1:strEnterMemorableInformation_memInfo3']").send_keys(third)
n = shotnhtml(driver, n)

logging.info("logging on")
driver.find_element_by_xpath("//input[@title='Continue']").click()
time.sleep(5)
n = shotnhtml(driver, n)

logging.info("searching for paperless message")
page = driver.find_element_by_id("page").text
if("We can help you with your filing" in page):
    logging.info("found paperless message and clicking no thanks")
    driver.find_element_by_xpath(
        "//a[@href='/personal/a/managepaperlesspreference/enhancedpaperlessinterstitial.jsp?lnkcmd=idEpi%3Anavigatetoaov&al=']").click()
    time.sleep(5)
    n = shotnhtml(driver, n)

else:
    logging.info("not found paperless message")

logging.info("searching for saving boost message")
page = driver.find_element_by_id("page").text
if("give your savings a boost" in page):
    logging.info("found saving boost message and clicking continue")
    driver.find_element_by_xpath("//input[@title='Continue']").click()
    time.sleep(5)
    n = shotnhtml(driver, n)

else:
    logging.info("not found saving boost message")

logging.info("selecting account")
driver.find_element_by_xpath("//a[@id='lnkAccName_des-m-sat-xx-1']").click()
time.sleep(5)
n = shotnhtml(driver, n)

logging.info("opening halifaxscrape.csv")
f = open('halifaxscrape.csv', 'a')
c = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

rows = driver.find_elements_by_xpath(
    "//table[@id='statement-table']/tbody/tr[@tabindex]/td[@transactionref]")
logging.info("found %s transactions" % (len(rows)))
for row in rows:
    date = row.text
    desc = row.get_attribute("merchantname").strip()
    ref = row.get_attribute("transactionref")
    amount = row.get_attribute("amount")

    data = [date, desc, ref, amount]
    logging.info("transaction %s" % " ".join(data))
    c.writerow(data)

logging.info("closing halifaxscrape.csv")
f.close()

logging.info("logging out")
driver.find_element_by_id(
    "ifCommercial:ifCustomerBar:ifMobLO:outputLinkLogOut").click()
n = shotnhtml(driver, n)
driver.close()
