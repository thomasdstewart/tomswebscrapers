#!/usr/bin/env python3
#    Barclay Card Account Data Web Scraper
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
parser.add_argument("-d", "--debug", \
    help="log to stdout and save screenshots and html", action="store_true", \
    default=False)
parser.add_argument("-p", "--proxy", \
    help="http proxy to use (eg localhost:8888)")
args = parser.parse_args()

if(args.debug):
    logging.basicConfig(level=logging.INFO, \
        format="%(levelname)s %(asctime)s %(message)s")
else:
    logging.basicConfig(filename="barclaycardscrape.log", \
        level=logging.INFO,format='%(levelname)s %(asctime)s %(message)s')

logging.info("reading config")
config = configparser.ConfigParser()
config.read("barclaycardscrape.ini")

username = config.get("barclaycardscrape", "username")
passcode = config.get("barclaycardscrape", "passcode")
memorableword = config.get("barclaycardscrape", "memorableword")

logging.info("setting up selenium")
chrome_options = selenium.webdriver.chrome.options.Options()  
chrome_options.add_argument("--headless")  
chrome_options.add_argument("--window-size=1300,1600")
#default UA is HeadlessChrome rather than Chrome
chrome_options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) " + \
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36")

#if ('http_proxy' in os.environ.keys()):
#    proxy = os.environ['http_proxy']
#    logging.info("using proxy %s" % proxy)
#    chrome_options.add_argument("--proxy-server=%s" % proxy)

if(args.proxy):
    logging.info("using proxy: %s" % args.proxy)
    chrome_options.add_argument("--proxy-server=%s" % args.proxy)
else:
    logging.info("not using proxy")

logging.info("starting selenium chrome headless")
driver = selenium.webdriver.Chrome(chrome_options=chrome_options)
driver.implicitly_wait(5)

n=1
def shotnhtml(d,n):
    if(not args.debug):
        return n
    logging.info("saving barclaycardscrape-%02d.png and barclaycardscrape-%02d.html" \
        % (n,n))
    d.save_screenshot("barclaycardscrape-%02d.png" % n)
    file = open("barclaycardscrape-%02d.html" % n, "w")
    file.write(d.page_source)
    file.close()
    return n + 1

loginurl = "https://bcol.barclaycard.co.uk/ecom/as2/initialLogon.do"
logging.info("getting page:%s", loginurl)
driver.get(loginurl)
n = shotnhtml(driver, n)

time.sleep(5)
logging.info("filling username and passcode")
driver.find_element_by_id("username").send_keys(username)
driver.find_element_by_id("password").send_keys(passcode)
driver.find_element_by_class_name("submit").click()
time.sleep(5)
n = shotnhtml(driver, n)

logging.info("filling memorableword")
first  = driver.find_element_by_xpath(\
    "//label[@id='letter1Answer-label']").text
second = driver.find_element_by_xpath(\
    "//label[@id='letter2Answer-label']").text

first = int(first[0:1])
second = int(second[0:1])

first = str(memorableword[first-1:first])
second = str(memorableword[second-1:second])

driver.find_element_by_xpath("//input[@id='letter1Answer']").send_keys(first)
driver.find_element_by_xpath("//input[@id='letter2Answer']").send_keys(second)
time.sleep(5)
n = shotnhtml(driver, n)

logging.info("logging on")
driver.find_element_by_id("btn-login").click()
time.sleep(5)
n = shotnhtml(driver, n)

logging.info("waiting for login to complete")
time.sleep(10)
n = shotnhtml(driver, n)

logging.info("selecting transactions")
driver.find_element_by_xpath("//a[@href='#section/a-recent-trans']/span").click()
time.sleep(5)
n = shotnhtml(driver, n)

logging.info("selecting view more transactions")
driver.find_element_by_xpath("//div[@data-webtrends-ref='home-recentTrans']/a").click()
time.sleep(5)
n = shotnhtml(driver, n)

logging.info("selecting Filter & Search")
driver.find_element_by_xpath("//ul[@class='tablist']/li[@id='tab1']").click()
time.sleep(5)
n = shotnhtml(driver, n)

logging.info("selecting 3 months")
driver.find_element_by_xpath("//div[@class='dateLinks']/ul/li").click()
time.sleep(5)
n = shotnhtml(driver, n)

logging.info("waiting for page load")
time.sleep(10)
n = shotnhtml(driver, n)

logging.info("selecting expand all")
driver.find_element_by_xpath("//a[@id='linkExpandAll']/..").click()
time.sleep(5)
n = shotnhtml(driver, n)

logging.info("opening barclaycardscrape.csv")
f = open('barclaycardscrape.csv', 'a')
c = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

rows=driver.find_elements_by_xpath("//td[@class='view']/..")
logging.info("found %s transactions" % (len(rows)))
for row in rows:
    r = row.text.split('\n')
    date = r[0]
    desc = r[1].strip()
    amount = r[-1:][0]

    data = [date, desc, amount]

    pp(r)

#    241 Business type
#    241 Cardholder
#    241 Country
#    152 Exchange Rate
#    152 Forex Amount
#     17 Payment method
#    243 PIN Used
#    243 Retailer name
#     34 Retailer number
#    243 Town

    logging.info("transaction %s" % " ".join(data))
    c.writerow(data)

logging.info("closing barclaycardscrape.csv")
f.close()

logging.info("logging out")
driver.find_element_by_id("logout").click()
n = shotnhtml(driver, n)
driver.close()
