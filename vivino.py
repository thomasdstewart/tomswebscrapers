#!/usr/bin/env python3
#    Wine info from vivino Web Scraper
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

import requests
import logging
import json
import io
import time
import sys
import csv
from pprint import pprint as pp

# import http; http.client.HTTPConnection.debuglevel = 5


def downloadparse(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:64.0) Gecko/20100101 Firefox/64.0'}
    raw = requests.get(url, headers=headers)
    print('URL,' + url)
    j = io.StringIO(raw.text)
    j = json.load(j)
    raw.close()
    return j


def getinfo(wineid):
    url = "https://www.vivino.com/api/wines/%s/wine_page_information" % wineid
    i = {}
    i['idurl'] = url
    doc = downloadparse(url)

    i['name'] = doc['wine_page_information']['vintage']['name']
    print(i['name'])
    #import ipdb; from IPython import embed; embed()
    i['rating'] = doc['wine_page_information']['vintage']['statistics']['ratings_average']
    i['ratingcount'] = doc['wine_page_information']['vintage']['statistics']['labels_count']
    i['vintages'] = len(doc['wine_page_information']
                        ['vintage']['wine']['vintages'])

    i['price'] = -1
    if(len(doc['wine_page_information']['recommended_vintages']) > 0):
        price = doc['wine_page_information']['recommended_vintages'][0]['price']
        if(price is not None):
            i['price'] = price['amount']

    i['region'] = doc['wine_page_information']['vintage']['wine']['region']['name']

    grapes = ""
    for g in doc['wine_page_information']['vintage']['wine']['grapes']:
        grapes = grapes + " " + g['name']
    i['grapes'] = grapes.strip()

    return(i)


#pp(getinfo(1858627)); sys.exit()
# pp(getinfo('')); sys.exit()

csvfile = open('vivino.csv', 'w')
csw = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
csw.writerow(['name', 'rating', 'ratingcount', 'vintages',
              'prices', 'region', 'grapes', 'url', 'idurl'])

wineurlss = """
https://www.vivino.com/borgo-magredo-refosco-dal-peduncolo-rosso/w/88515
https://www.vivino.com/banfi-collepino-merlot-sangiovese/w/22916
https://www.vivino.com/conti-d-arco-cabernet-sauvignon/w/1622211
https://www.vivino.com/kellerei-terlan-pinot-noir/w/1263919
https://www.vivino.com/wallenburg-ambasciatori-teroldego/w/5595563
https://www.vivino.com/wallenburg-trentino-lagrein/w/1858627
https://www.vivino.com/il-calepino-surie-valcalepio-riserva-rosso/w/1189610
https://www.vivino.com/barone-pizzini-curtefranca-rosso/w/1150700
https://www.vivino.com/it-ca-del-bosco-curtefranca-rosso/w/23132
https://www.vivino.com/nino-negri-le-tense-sassella-valtellina-superiore/w/28254
https://www.vivino.com/it-masi-bonacosta-valpolicella-classico/w/21975
https://www.vivino.com/giacomo-montresor-capitel-della-crosara-valpolicella-ripasso/w/75627
https://www.vivino.com/it-masi-costasera-amarone-della-valpolicella-classico/w/21929
https://www.vivino.com/torre-rosazzo-ronco-del-palazzo-pinot-nero/w/1537721
https://www.vivino.com/livon-picotis-schioppettino/w/92876
https://www.vivino.com/torre-rosazzo-pignolo/w/1204769
https://www.vivino.com/rossi-contini-rossi-contini-dolcetto-d-ovada/w/1370765
https://www.vivino.com/prunotto-barbera-d-alba/w/2364791
https://www.vivino.com/accornero-bricco-del-bosco/w/1643556
https://www.vivino.com/braida-montebruna-barbera-d-asti/w/15143
https://www.vivino.com/prunotto-occhetti-langhe-nebbiolo/w/6771048
https://www.vivino.com/prunotto-barolo-bussia/w/61064
https://www.vivino.com/banfi-chianti-superiore/w/1179049
https://www.vivino.com/giacomo-montresor-santa-dorotea-oratorio-della-duchessa-morellino-di-scansano/w/1923670
https://www.vivino.com/il-paggio-chianti-classico/w/1239826
https://www.vivino.com/banfi-rosso-di-montalcino/w/22918
https://www.vivino.com/ruffino-riserva-ducale-chianti-classico/w/1137925
https://www.vivino.com/banfi-brunello-di-montalcino/w/22917
https://www.vivino.com/casanova-di-neri-brunello-di-montalcino/w/9710
https://www.vivino.com/ruffino-tenuta-greppone-mazzi-brunello-di-montalcino/w/1137508
https://www.vivino.com/it-tasca-dalmerita-sallier-de-la-tour-syrah/w/1510423
https://www.vivino.com/casa-vinicola-firriato-le-sabbie-dell-etna-rosso/w/2324457
https://www.vivino.com/it-tasca-dalmerita-lamuri-nero-d-avola-regaleali/w/1516856
"""

for wineurl in wineurlss.split():
    wineid = wineurl.split('/')[5]
    i = getinfo(wineid)
    csw.writerow([i['name'], i['rating'], i['ratingcount'], i['vintages'],
                  i['price'], i['region'], i['grapes'], wineurl, i['idurl']])
