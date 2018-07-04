#!/usr/bin/env python3
from pprint import pprint as pp

alldata = [["date", "desc", "amount", "count"],
           ["01/06/2018", "coffee", "10"],
           ["01/06/2018", "milk", "10"],
           ["01/06/2018", "eggs", "20"],
           ["01/06/2018", "milk", "10"],
           ["02/06/2018", "bread", "40"]]

print("original data")
pp(alldata)

refs = {}
for r in alldata:
    index = "%s%s%s" % (r[0], r[1], r[2])
    if(index in refs):
        refs[index] = [refs[index][0] + 1, r]
    else:
        refs[index] = [1, r]

nalldata = []
for index in refs:
    for n in range(1, refs[index][0] + 1):
        d = refs[index][1]
        nalldata.append(d + [n])

print("new data")
pp(nalldata)
