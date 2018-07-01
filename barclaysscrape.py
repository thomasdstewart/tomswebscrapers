#!/usr/bin/env python3
#    Barclays Account Data Web Scraper
#    Copyright (C) 2017 Thomas Stewart <thomas@stewarts.org.uk>
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
#import ipdb; from IPython import embed; embed()

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
    logging.basicConfig(filename="barclaysscrape.log",
                        level=logging.INFO, format='%(levelname)s %(asctime)s %(message)s')

logging.info("reading config")
configfile = 'barclaysscrape.ini'
config = configparser.ConfigParser()
config.read(configfile)

if(len(config.sections()) == 0):
    logging.info("could not read %s" % configfile)
    sys.exit()

if('barclaysscrape' not in config):
    logging.info("could not read barclaysscrape section in %s" % configfile)
    sys.exit()

section = config['barclaysscrape']
if('surname' not in section or 'membershipnum' not in section or 'passcode' not in section or 'password' not in section):
    logging.info(
        "could not find setting in barclaysscrape section in %s" % configfile)
    sys.exit()

surname = config['barclaysscrape']['surname']
membershipnum = config['barclaysscrape']['membershipnum']
passcode = config['barclaysscrape']['passcode']
password = config['barclaysscrape']['password']

logging.info("setting up selenium")
chrome_options = selenium.webdriver.chrome.options.Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1300,1600")
# default UA is HeadlessChrome rather than Chrome
chrome_options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) " +
                            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36")

if(args.proxy):
    # if('http_proxy' in os.environ.keys()):
    #    args.proxy = os.environ['http_proxy']
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
    logging.info("saving barclaysscrape-%02d.png and barclaysscrape-%02d.html"
                 % (n, n))
    d.save_screenshot("barclaysscrape-%02d.png" % n)
    file = open("barclaysscrape-%02d.html" % n, "w")
    file.write(d.page_source)
    file.close()
    return n + 1


loginurl = "https://bank.barclays.co.uk/olb/auth/LoginLink.action"
logging.info("getting page:%s", loginurl)
driver.get(loginurl)
n = shotnhtml(driver, n)

try:
    driver.find_element_by_class_name("bc-checkbox")
except NoSuchElementException:
    logging.info("bc-checkbox class not found, browser compatable")
else:
    driver.find_element_by_class_name("bc-checkbox").click()
    driver.find_element_by_id("bc-button").click()
    n = shotnhtml(driver, n)

time.sleep(5)
logging.info("filling surname and membership number")
driver.find_element_by_id("surname0").send_keys(surname)
driver.find_element_by_id("membershipNum0").send_keys(membershipnum)
driver.find_element_by_xpath("//button").click()
time.sleep(5)
n = shotnhtml(driver, n)

logging.info("selecting passcode")
driver.find_element_by_xpath("//label[@for='radio-c2']/span").click()
time.sleep(5)
n = shotnhtml(driver, n)

logging.info("filling passcode and password")
driver.find_element_by_id("passcode0").send_keys(passcode)

first = driver.find_element_by_xpath(
    "//label[@id='label-memorableCharacters']/strong[1]").text
second = driver.find_element_by_xpath(
    "//label[@id='label-memorableCharacters']/strong[2]").text
first = int(first[0:1])
second = int(second[0:1])

first = str(password[first-1:first])
second = str(password[second-1:second])

driver.find_element_by_xpath(
    "//div[@name='firstMemorableCharacter']/div").send_keys(first)
driver.find_element_by_xpath(
    "//div[@name='secondMemorableCharacter']/div").send_keys(second)
driver.find_element_by_xpath("//button").click()
time.sleep(5)
n = shotnhtml(driver, n)

logging.info("opening barclaysscrape.csv")
f = open('barclaysscrape.csv', 'a')
c = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

logging.info("getting account list")
accounts = {}
for account in driver.find_elements_by_xpath(
        "//*[@class='account-detail-wrapper summary']"):
    a = account.get_attribute("aria-label")
    pa = a.replace(' ', '')
    pa = "%s-%s-%s %s" % (pa[8:10], pa[10:12], pa[12:14], pa[27:35])
    accounts[pa] = a

logging.info("found accounts %s" % ",".join(accounts.keys()))

for account in accounts:
    logging.info("getting account %s" % account)
    driver.find_element_by_xpath(
        "//*[@aria-label='%s']/..//*[@id='showStatements']"
        % accounts[account]).click()
    time.sleep(5)
    n = shotnhtml(driver, n)

    rows = driver.find_elements_by_xpath("//*[@id='filterable-ftb']/tbody/tr")
    logging.info("found %s trancastions" % (len(rows)))
    for row in rows:
        r = row.text.split('\n')
        date = r[0]
        desc1 = r[1]

        r[2] = r[2].replace(',', '').replace('£', '')
        a = re.findall(r"[^ ]+", r[2])
        ammount = a[0]
        balance = a[1]

        d = row.find_element_by_xpath("td[@class='description']/div")
        d = d.get_attribute("textContent").split('\n')

        desc2 = d[2].strip()
        desc3 = d[5].strip()

        data = [account, date, desc1, desc2, desc3, ammount, balance]
        logging.info("trancastion %s" % " ".join(data))
        c.writerow(data)

    logging.info("returning home")
    driver.find_element_by_class_name("home").click()
    n = shotnhtml(driver, n)

logging.info("closing barclaysscrape.csv")
f.close()

logging.info("logging out")
driver.find_element_by_id("logout").click()
n = shotnhtml(driver, n)
driver.close()
